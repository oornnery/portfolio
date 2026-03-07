import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from app.core.dependencies import get_about_page_service
from app.rendering.engine import render_page
from app.services import AboutPageService

router = APIRouter(tags=["about"])
logger = logging.getLogger(__name__)

AboutPageServiceDep = Annotated[AboutPageService, Depends(get_about_page_service)]


@router.get("/about", response_class=HTMLResponse)
async def about(
    page_service: AboutPageServiceDep,
) -> HTMLResponse:
    page = page_service.build_page()
    logger.debug("About page rendered.")
    return render_page(page)
