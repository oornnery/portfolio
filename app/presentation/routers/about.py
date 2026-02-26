import logging

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from app.presentation.dependencies import get_about_page_service
from app.presentation.render import render_page
from app.application.use_cases import AboutPageService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/about", response_class=HTMLResponse)
async def about(
    page_service: AboutPageService = Depends(get_about_page_service),
) -> HTMLResponse:
    page = page_service.build_page()
    logger.info("About page rendered.")
    return render_page(page)
