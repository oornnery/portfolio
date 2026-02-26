from dataclasses import dataclass
import logging
from typing import Any, Callable

from pydantic import ValidationError

from app.models import Project
from app.schemas import ContactForm
from app.security import generate_csrf_token, validate_csrf_token
from app.services.markdown import get_project_by_slug, load_about, load_all_projects
from app.services.seo import seo_for_page, seo_for_project

logger = logging.getLogger(__name__)


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


class HomePageService:
    def __init__(
        self, csrf_token_factory: Callable[..., str] = generate_csrf_token
    ) -> None:
        self._csrf_token_factory = csrf_token_factory

    def build_page(self, *, user_agent: str = "") -> PageRenderData:
        all_projects = list(load_all_projects())
        featured_projects = [project for project in all_projects if project.featured]
        non_featured_projects = [
            project for project in all_projects if not project.featured
        ]
        featured = (featured_projects + non_featured_projects)[:3]
        csrf_token = self._csrf_token_factory(user_agent=user_agent)
        seo = seo_for_page(
            title="Home",
            description="Python developer portfolio with projects, experience, and contact details.",
            path="/",
        )
        logger.debug(
            f"Home use-case built with featured_count={len(featured)} total_projects={len(all_projects)}"
        )
        return PageRenderData(
            template="pages/home.jinja",
            context={
                "seo": seo,
                "featured": featured,
                "csrf_token": csrf_token,
                "current_path": "/",
            },
        )


class AboutPageService:
    def build_page(self) -> PageRenderData:
        about_content = load_about()
        frontmatter = about_content.frontmatter
        seo = seo_for_page(
            title="About",
            description=frontmatter.description or "About me",
            path="/about",
        )
        logger.debug(
            f"About use-case built with html_length={len(about_content.body_html)}"
        )
        return PageRenderData(
            template="pages/about.jinja",
            context={
                "seo": seo,
                "meta": frontmatter,
                "content_html": about_content.body_html,
                "current_path": "/about",
            },
        )


class ProjectsPageService:
    def build_list_page(self) -> PageRenderData:
        all_projects = load_all_projects()
        seo = seo_for_page(
            title="Projects",
            description="My projects and selected work.",
            path="/projects",
        )
        logger.debug(
            f"Projects list use-case built with project_count={len(all_projects)}"
        )
        return PageRenderData(
            template="pages/projects.jinja",
            context={
                "seo": seo,
                "projects": all_projects,
                "current_path": "/projects",
            },
        )

    def get_project(self, slug: str) -> Project | None:
        return get_project_by_slug(slug)

    def build_detail_page(self, project: Project) -> PageRenderData:
        seo = seo_for_project(project)
        return PageRenderData(
            template="pages/project_detail.jinja",
            context={
                "seo": seo,
                "project": project,
                "current_path": "/projects",
            },
        )


class ContactPageService:
    def __init__(
        self, csrf_token_factory: Callable[..., str] = generate_csrf_token
    ) -> None:
        self._csrf_token_factory = csrf_token_factory

    def build_page(
        self,
        *,
        user_agent: str = "",
        current_csrf: str | None = None,
        success: str = "",
        errors: dict[str, str] | None = None,
        form_data: dict[str, str] | None = None,
    ) -> PageRenderData:
        seo = seo_for_page(
            title="Contact",
            description="Get in touch with me.",
            path="/contact",
        )
        csrf_token = current_csrf or self._csrf_token_factory(user_agent=user_agent)
        return PageRenderData(
            template="pages/contact.jinja",
            context={
                "seo": seo,
                "csrf_token": csrf_token,
                "success": success,
                "errors": errors or {},
                "form_data": form_data or {},
                "current_path": "/contact",
            },
        )


class ContactSubmissionService:
    def __init__(
        self,
        csrf_validator: Callable[..., bool] = validate_csrf_token,
    ) -> None:
        self._csrf_validator = csrf_validator

    @staticmethod
    def _normalize_input(
        *,
        name: str,
        email: str,
        subject: str,
        message: str,
    ) -> dict[str, str]:
        return {
            "name": name.strip(),
            "email": email.strip(),
            "subject": subject.strip(),
            "message": message.strip(),
        }

    def process(
        self,
        *,
        name: str,
        email: str,
        subject: str,
        message: str,
        csrf_token: str,
        client_ip: str,
        user_agent: str,
    ) -> ContactSubmissionResult:
        form_data = self._normalize_input(
            name=name,
            email=email,
            subject=subject,
            message=message,
        )

        if not self._csrf_validator(csrf_token, user_agent=user_agent):
            logger.warning(
                f"Invalid or expired CSRF token for contact form submission from {client_ip}."
            )
            return ContactSubmissionResult(
                contact=None,
                form_data=form_data,
                errors={
                    "csrf": "Invalid or expired security token. Please reload the page."
                },
                status_code=403,
            )

        try:
            contact = ContactForm(
                name=form_data["name"],
                email=form_data["email"],
                subject=form_data["subject"],
                message=form_data["message"],
                csrf_token=csrf_token,
            )
            return ContactSubmissionResult(
                contact=contact,
                form_data=form_data,
                errors={},
                status_code=200,
            )
        except ValidationError as exc:
            errors: dict[str, str] = {}
            for err in exc.errors():
                loc = err.get("loc", ())
                field_name = str(loc[-1]) if loc else "form"
                errors[field_name] = err.get("msg", "Invalid value")
            logger.info(
                f"Contact form validation failed for {client_ip} with {len(errors)} error(s)."
            )
            return ContactSubmissionResult(
                contact=None,
                form_data=form_data,
                errors=errors,
                status_code=422,
            )
