import logging

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from app.dependencies import get_home_page_service
from app.render import render_page
from app.services.use_cases import HomePageService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    page_service: HomePageService = Depends(get_home_page_service),
) -> HTMLResponse:
    user_agent = request.headers.get("user-agent", "")
    page = page_service.build_page(user_agent=user_agent)
    logger.info("Home page rendered.")
    return render_page(page)
