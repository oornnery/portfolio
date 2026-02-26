import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse

from app.dependencies import get_projects_page_service, render_template
from app.services.use_cases import ProjectsPageService

router = APIRouter(prefix="/projects")
logger = logging.getLogger(__name__)


@router.get("", response_class=HTMLResponse)
async def projects_list(
    page_service: ProjectsPageService = Depends(get_projects_page_service),
) -> HTMLResponse:
    page = page_service.build_list_page()
    html = render_template(page.template, **page.context)
    logger.info("Projects list page rendered.")
    return HTMLResponse(content=html)


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
    html = render_template(page.template, **page.context)
    logger.info(f"Project detail page rendered for slug={slug}.")
    return HTMLResponse(content=html)
