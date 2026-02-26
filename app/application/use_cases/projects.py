import logging

from app.domain.models import Project
from app.infrastructure.markdown import get_project_by_slug, load_all_projects
from app.application.services.seo import seo_for_page, seo_for_project
from app.application.use_cases.types import (
    PageRenderData,
    ProjectDetailPageContext,
    ProjectsListPageContext,
)

logger = logging.getLogger(__name__)


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
            context=ProjectsListPageContext(
                seo=seo,
                projects=all_projects,
            ),
        )

    def get_project(self, slug: str) -> Project | None:
        return get_project_by_slug(slug)

    def build_detail_page(self, project: Project) -> PageRenderData:
        seo = seo_for_project(project)
        return PageRenderData(
            template="pages/project_detail.jinja",
            context=ProjectDetailPageContext(
                seo=seo,
                project=project,
            ),
        )
