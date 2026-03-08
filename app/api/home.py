import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from app.core.dependencies import get_home_page_service
from app.core.rendering import render_page
from app.services import HomePageService

router = APIRouter(tags=["home"])
logger = logging.getLogger(__name__)

HomePageServiceDep = Annotated[HomePageService, Depends(get_home_page_service)]


@router.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    page_service: HomePageServiceDep,
) -> HTMLResponse:
    user_agent = request.headers.get("user-agent", "")
    page = page_service.build_page(user_agent=user_agent)
    logger.debug("Home page rendered.")
    return render_page(page)
