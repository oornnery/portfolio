from fastapi.responses import HTMLResponse

from app.dependencies import render_template
from app.services.use_cases import PageRenderData


def render_page(page: PageRenderData, *, status_code: int = 200) -> HTMLResponse:
    html = render_template(page.template, **page.context)
    return HTMLResponse(content=html, status_code=status_code)
