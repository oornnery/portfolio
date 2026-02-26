import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse

from app.core.dependencies import get_projects_page_service
from app.rendering.engine import render_page
from app.services import ProjectsPageService

router = APIRouter(prefix="/projects")
logger = logging.getLogger(__name__)


@router.get("", response_class=HTMLResponse)
async def projects_list(
    page_service: ProjectsPageService = Depends(get_projects_page_service),
) -> HTMLResponse:
    page = page_service.build_list_page()
    logger.info("Projects list page rendered.")
    return render_page(page)


@router.get("/{slug}", response_class=HTMLResponse)
async def project_detail(
    slug: str,
    page_service: ProjectsPageService = Depends(get_projects_page_service),
) -> HTMLResponse:
    project = page_service.get_project(slug)
    if project is None:
        logger.info(f"Project detail not found for slug={slug}.")
        raise HTTPException(status_code=404, detail="Project not found")
    page = page_service.build_detail_page(project)
    logger.info(f"Project detail page rendered for slug={slug}.")
    return render_page(page)
