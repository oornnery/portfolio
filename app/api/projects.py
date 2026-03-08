import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.responses import HTMLResponse

from app.core.dependencies import get_projects_page_service
from app.core.rendering import render_page
from app.services import ProjectsPageService

router = APIRouter(prefix="/projects", tags=["projects"])
logger = logging.getLogger(__name__)

ProjectsPageServiceDep = Annotated[
    ProjectsPageService, Depends(get_projects_page_service)
]


@router.get("", response_class=HTMLResponse)
async def projects_list(
    page_service: ProjectsPageServiceDep,
) -> HTMLResponse:
    page = page_service.build_list_page()
    logger.debug("Projects list page rendered.")
    return render_page(page)


@router.get("/{slug}", response_class=HTMLResponse)
async def project_detail(
    slug: Annotated[str, Path()],
    page_service: ProjectsPageServiceDep,
) -> HTMLResponse:
    project = page_service.get_project(slug)
    if project is None:
        logger.info(f"Project detail not found for slug={slug}.")
        raise HTTPException(status_code=404, detail="Project not found")
    page = page_service.build_detail_page(project)
    logger.debug(f"Project detail page rendered for slug={slug}.")
    return render_page(page)
