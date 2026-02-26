import logging
from typing import Callable

from app.security import generate_csrf_token
from app.services.markdown import load_all_projects
from app.services.seo import seo_for_page
from app.services.use_cases.types import PageRenderData

logger = logging.getLogger(__name__)


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

