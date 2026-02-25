import logging

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from app.dependencies import get_about_page_service, render_or_fallback
from app.services.use_cases import AboutPageService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/about", response_class=HTMLResponse)
async def about(
    page_service: AboutPageService = Depends(get_about_page_service),
) -> HTMLResponse:
    page = page_service.build_page()
    html = render_or_fallback(
        page.template,
        page.fallback_html,
        **page.context,
    )
    logger.info("About page rendered.")
    return HTMLResponse(content=html)
