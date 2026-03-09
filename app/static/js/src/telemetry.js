import { trace } from "@opentelemetry/api";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-http";
import { registerInstrumentations } from "@opentelemetry/instrumentation";
import { DocumentLoadInstrumentation } from "@opentelemetry/instrumentation-document-load";
import { FetchInstrumentation } from "@opentelemetry/instrumentation-fetch";
import { XMLHttpRequestInstrumentation } from "@opentelemetry/instrumentation-xml-http-request";
import { resourceFromAttributes } from "@opentelemetry/resources";
import {
    BatchSpanProcessor,
    TraceIdRatioBasedSampler,
    WebTracerProvider,
} from "@opentelemetry/sdk-trace-web";

const TELEMETRY_EVENT_SELECTOR = "[data-telemetry-event]";
const TELEMETRY_SECTION_SELECTOR = "[data-telemetry-section]";

const state = {
    initialized: false,
    enabled: false,
    tracer: trace.getTracer("site.frontend.noop"),
    sectionObserver: null,
};

const metaContent = (name) =>
    document.querySelector(`meta[name="${name}"]`)?.content?.trim() || "";

const parseBoolean = (value) => value === "true";

const clampSampleRatio = (value) => {
    const parsed = Number.parseFloat(value);
    if (Number.isNaN(parsed)) {
        return 1;
    }
    return Math.max(0, Math.min(1, parsed));
};

const escapeRegExp = (value) => value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

const toAbsoluteUrl = (value) => {
    if (!value) {
        return "";
    }
    try {
        return new URL(value, window.location.origin).toString();
    } catch {
        return "";
    }
};

const limit = (value, max = 256) => String(value || "").trim().slice(0, max);

const configFromMeta = () => {
    const enabled = parseBoolean(metaContent("frontend-telemetry-enabled"));
    const otlpEndpoint = toAbsoluteUrl(metaContent("frontend-telemetry-otlp-endpoint"));

    return {
        enabled: enabled && Boolean(otlpEndpoint),
        otlpEndpoint,
        sampleRatio: clampSampleRatio(metaContent("frontend-telemetry-sample-ratio")),
        serviceName:
            metaContent("frontend-telemetry-service-name") || "site-frontend",
        serviceNamespace: metaContent("frontend-telemetry-service-namespace"),
        environment: metaContent("frontend-telemetry-environment") || "production",
    };
};

const telemetryAttributes = (element) => ({
    "site.event.name": limit(element.dataset.telemetryEvent || "ui.event"),
    "site.element.id": limit(element.dataset.telemetryId || element.id || ""),
    "site.element.label": limit(
        element.dataset.telemetryLabel || element.textContent || "",
        512,
    ),
    "site.navigation.target": limit(
        element.dataset.telemetryTarget || element.getAttribute("href") || "",
        512,
    ),
    "url.path": window.location.pathname,
});

const sectionAttributes = (element) => ({
    "site.section.name": limit(
        element.dataset.telemetrySection || element.id || "section",
    ),
    "url.path": window.location.pathname,
});

const onReady = (fn) => {
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", fn, { once: true });
    } else {
        fn();
    }
};

const recordSpan = (name, attributes = {}) => {
    if (!state.enabled) {
        return;
    }
    const span = state.tracer.startSpan(name);
    span.setAttributes(attributes);
    span.end();
};

const initManualInteractionTelemetry = () => {
    document.addEventListener(
        "click",
        (event) => {
            const element = event.target.closest(TELEMETRY_EVENT_SELECTOR);
            if (!(element instanceof HTMLElement)) {
                return;
            }
            const eventName = limit(element.dataset.telemetryEvent || "ui.click");
            recordSpan(`ui.${eventName}`, telemetryAttributes(element));
        },
        { capture: true },
    );

    const observer = new IntersectionObserver(
        (entries) => {
            for (const entry of entries) {
                if (!entry.isIntersecting) {
                    continue;
                }
                const element = entry.target;
                if (!(element instanceof HTMLElement)) {
                    continue;
                }
                observer.unobserve(element);
                recordSpan("ui.section.visible", sectionAttributes(element));
            }
        },
        { threshold: 0.6 },
    );

    for (const section of document.querySelectorAll(TELEMETRY_SECTION_SELECTOR)) {
        observer.observe(section);
    }
    state.sectionObserver = observer;
};

const buildTracerProvider = (config) => {
    const provider = new WebTracerProvider({
        resource: resourceFromAttributes({
            "service.name": config.serviceName,
            "service.namespace": config.serviceNamespace || "site",
            "deployment.environment": config.environment,
        }),
        sampler: new TraceIdRatioBasedSampler(config.sampleRatio),
        spanProcessors: [
            new BatchSpanProcessor(
                new OTLPTraceExporter({
                    url: config.otlpEndpoint,
                }),
            ),
        ],
    });
    provider.register();

    const sameOriginPattern = new RegExp(`^${escapeRegExp(window.location.origin)}`);
    registerInstrumentations({
        tracerProvider: provider,
        instrumentations: [
            new DocumentLoadInstrumentation({
                ignoreNetworkEvents: true,
                semconvStabilityOptIn: "http",
                applyCustomAttributesOnSpan: {
                    documentLoad: (span) => {
                        span.setAttribute("url.path", window.location.pathname);
                    },
                },
            }),
            new FetchInstrumentation({
                clearTimingResources: true,
                ignoreNetworkEvents: true,
                ignoreUrls: [config.otlpEndpoint],
                measureRequestSize: true,
                propagateTraceHeaderCorsUrls: [sameOriginPattern],
                semconvStabilityOptIn: "http",
            }),
            new XMLHttpRequestInstrumentation({
                clearTimingResources: true,
                ignoreNetworkEvents: true,
                ignoreUrls: [config.otlpEndpoint],
                measureRequestSize: true,
                propagateTraceHeaderCorsUrls: [sameOriginPattern],
                semconvStabilityOptIn: "http",
            }),
        ],
    });

    return provider;
};

export const initFrontendTelemetry = () => {
    if (state.initialized) {
        return state.enabled;
    }
    state.initialized = true;

    const config = configFromMeta();
    if (!config.enabled) {
        return false;
    }

    try {
        const provider = buildTracerProvider(config);
        state.tracer = provider.getTracer("site.frontend.manual");
        state.enabled = true;
        onReady(initManualInteractionTelemetry);
        window.siteTelemetry = { recordSpan };
        return true;
    } catch (error) {
        console.error("Frontend telemetry init failed", error);
        state.enabled = false;
        return false;
    }
};

export const recordTelemetryEvent = (name, attributes = {}) => {
    recordSpan(name, attributes);
};
