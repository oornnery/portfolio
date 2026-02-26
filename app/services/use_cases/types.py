from dataclasses import dataclass
from typing import Any

from app.schemas import ContactForm


@dataclass(frozen=True)
class PageRenderData:
    template: str
    context: dict[str, Any]


@dataclass(frozen=True)
class ContactSubmissionResult:
    contact: ContactForm | None
    form_data: dict[str, str]
    errors: dict[str, str]
    status_code: int

    @property
    def is_valid(self) -> bool:
        return self.contact is not None and not self.errors

