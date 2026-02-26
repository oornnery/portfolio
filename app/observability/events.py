from enum import StrEnum


class LogEvent(StrEnum):
    REQUEST_STARTED = "request.started"
    REQUEST_COMPLETED = "request.completed"
    REQUEST_FAILED = "request.failed"

    CONTACT_PAGE_RENDERED = "contact.page.rendered"
    CONTACT_SUBMISSION_RECEIVED = "contact.submission.received"
    CONTACT_SUBMISSION_REJECTED = "contact.submission.rejected"
    CONTACT_SUBMISSION_SUCCEEDED = "contact.submission.succeeded"

    ANALYTICS_EVENT_ACCEPTED = "analytics.event.accepted"
    ANALYTICS_EVENT_REJECTED = "analytics.event.rejected"
