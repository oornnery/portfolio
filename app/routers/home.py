import logging

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from app.dependencies import get_home_page_service, render_template
from app.services.use_cases import HomePageService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_class=HTMLResponse)
async def home(
    page_service: HomePageService = Depends(get_home_page_service),
) -> HTMLResponse:
    page = page_service.build_page()
    html = render_template(page.template, **page.context)
    logger.info("Home page rendered.")
    return HTMLResponse(content=html)
