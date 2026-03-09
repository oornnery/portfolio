import { recordTelemetryEvent } from "../telemetry.js";

/**
 * Alpine data factory: contactForm
 *
 * Provides client-side validation for the contact form and submits valid
 * payloads through htmx.ajax so validation errors never trigger a full-page
 * navigation when JS is available.
 */
const FIELD_LABELS = {
    name: "Name",
    email: "Email",
    message: "Message",
};

const FIELD_ORDER = ["name", "email", "message"];

export default () => ({
    clientErrors: {
        name: "",
        email: "",
        message: "",
    },
    dirty: {
        name: false,
        email: false,
        message: false,
    },

    onFieldInput(event) {
        this._validateEventTarget(event, true);
    },

    onFieldBlur(event) {
        this._validateEventTarget(event, true);
    },

    submit() {
        if (!this.validateAll()) {
            recordTelemetryEvent("contact.validation.client_error", {
                "site.contact.error_count": Object.values(this.clientErrors).filter(
                    Boolean,
                ).length,
                "site.contact.invalid_fields": FIELD_ORDER.filter(
                    (fieldName) => this.clientErrors[fieldName],
                ).join(","),
                "url.path": window.location.pathname,
            });
            this._focusFirstInvalidField();
            return;
        }

        const form = this.$el;
        recordTelemetryEvent("contact.submit.attempt", {
            "site.contact.transport": "htmx",
            "url.path": window.location.pathname,
        });
        this._attachRequestTelemetry(form);
        const target = form.getAttribute("hx-target") || "#contact-form-section";
        const swap = form.getAttribute("hx-swap") || "outerHTML";
        const values = Object.fromEntries(new FormData(form).entries());

        window.htmx.ajax("POST", form.action, {
            source: form,
            target,
            swap,
            values,
        });
    },

    validateAll() {
        let isValid = true;

        for (const fieldName of FIELD_ORDER) {
            this.dirty[fieldName] = true;
            if (!this._validateField(fieldName)) {
                isValid = false;
            }
        }

        return isValid;
    },

    _validateEventTarget(event, markDirty) {
        const field = event.target;
        if (!(field instanceof HTMLInputElement || field instanceof HTMLTextAreaElement)) {
            return;
        }
        if (!(field.name in this.clientErrors)) {
            return;
        }
        if (markDirty) {
            this.dirty[field.name] = true;
        }
        this._validateField(field.name);
    },

    _validateField(fieldName) {
        const field = this.$el.elements.namedItem(fieldName);
        if (!(field instanceof HTMLInputElement || field instanceof HTMLTextAreaElement)) {
            return true;
        }

        const value = field.value.trim();
        let message = "";

        if (!value) {
            message = `${FIELD_LABELS[fieldName]} is required.`;
        } else if (fieldName === "name") {
            if (value.length < 2) {
                message = "Name must have at least 2 characters.";
            } else if (value.length > 100) {
                message = "Name must have at most 100 characters.";
            }
        } else if (fieldName === "email") {
            if (field.validity.typeMismatch) {
                message = "Enter a valid email address.";
            }
        } else if (fieldName === "message") {
            if (value.length < 10) {
                message = "Message must have at least 10 characters.";
            } else if (value.length > 5000) {
                message = "Message must have at most 5000 characters.";
            }
        }

        this.clientErrors[fieldName] = message;
        return !message;
    },

    _focusFirstInvalidField() {
        for (const fieldName of FIELD_ORDER) {
            if (!this.clientErrors[fieldName]) {
                continue;
            }
            const field = this.$el.elements.namedItem(fieldName);
            if (field instanceof HTMLElement) {
                field.focus();
            }
            return;
        }
    },

    _attachRequestTelemetry(form) {
        form.addEventListener(
            "htmx:afterRequest",
            (event) => {
                if (event.detail?.elt !== form) {
                    return;
                }
                const statusCode = event.detail?.xhr?.status || 0;
                recordTelemetryEvent("contact.submit.response", {
                    "site.contact.transport": "htmx",
                    "site.contact.status_code": statusCode,
                    "site.contact.outcome":
                        statusCode >= 200 && statusCode < 400 ? "success" : "error",
                    "url.path": window.location.pathname,
                });
            },
            { once: true },
        );
    },
});
