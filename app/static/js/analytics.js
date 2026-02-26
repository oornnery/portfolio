(function () {
    "use strict";

    const endpoint = "/api/v1/analytics/track";
    const queue = [];
    const maxBatchSize = 20;
    const flushIntervalMs = 5000;

    function isEnabled() {
        const meta = document.querySelector('meta[name="analytics-enabled"]');
        if (!meta) {
            return true;
        }
        return meta.content !== "false";
    }

    function nowIso() {
        return new Date().toISOString();
    }

    function createEvent(eventName, fields) {
        return {
            event_name: eventName,
            page_path: fields.pagePath || window.location.pathname,
            element_id: fields.elementId || "",
            element_text: (fields.elementText || "").slice(0, 512),
            target_url: fields.targetUrl || "",
            metadata: fields.metadata || {},
            occurred_at: nowIso(),
        };
    }

    function enqueue(eventName, fields) {
        queue.push(createEvent(eventName, fields));
        if (queue.length >= maxBatchSize) {
            flush();
        }
    }

    function flush() {
        if (!isEnabled() || queue.length === 0) {
            return;
        }

        const events = queue.splice(0, maxBatchSize);
        const payload = JSON.stringify({ events: events });

        if (navigator.sendBeacon) {
            const blob = new Blob([payload], { type: "application/json" });
            navigator.sendBeacon(endpoint, blob);
            return;
        }

        fetch(endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: payload,
            keepalive: true,
            credentials: "same-origin",
        }).catch(() => {
            return;
        });
    }

    function trackPageView() {
        enqueue("page_view", {
            pagePath: window.location.pathname,
            metadata: {
                referrer: document.referrer || "",
            },
        });
    }

    function trackClicks() {
        document.addEventListener("click", (event) => {
            const trackedElement = event.target.closest("[data-analytics-event]");
            if (!trackedElement) {
                return;
            }

            const eventName = trackedElement.dataset.analyticsEvent || "click";
            const href = trackedElement.getAttribute("href") || "";
            const targetUrl = trackedElement.dataset.analyticsTarget || href;
            const elementText =
                trackedElement.dataset.analyticsLabel ||
                (trackedElement.textContent || "").trim();
            const elementId =
                trackedElement.dataset.analyticsId || trackedElement.id || "";
            const pagePath =
                trackedElement.dataset.analyticsPath || window.location.pathname;

            enqueue(eventName, {
                pagePath: pagePath,
                elementId: elementId,
                elementText: elementText,
                targetUrl: targetUrl,
                metadata: {},
            });
        });
    }

    function trackSectionScroll() {
        const trackedSections = Array.from(
            document.querySelectorAll("[data-analytics-section]")
        );
        if (trackedSections.length === 0) {
            return;
        }

        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (!entry.isIntersecting) {
                        return;
                    }

                    const sectionId =
                        entry.target.dataset.analyticsSection ||
                        entry.target.id ||
                        "section";
                    enqueue("section_scroll", {
                        pagePath: window.location.pathname,
                        elementId: sectionId,
                    });
                });
            },
            { threshold: 0.6 }
        );

        trackedSections.forEach((section) => {
            observer.observe(section);
        });
    }

    function init() {
        if (!isEnabled()) {
            return;
        }

        trackPageView();
        trackClicks();
        trackSectionScroll();

        window.setInterval(flush, flushIntervalMs);
        window.addEventListener("visibilitychange", () => {
            if (document.visibilityState === "hidden") {
                flush();
            }
        });
        window.addEventListener("beforeunload", flush);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
