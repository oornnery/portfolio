from fastapi.responses import HTMLResponse

from app.core.dependencies import render_template
from app.services import PageRenderData


def render_page(page: PageRenderData, *, status_code: int = 200) -> HTMLResponse:
    context = {
        field_name: getattr(page.context, field_name)
        for field_name in type(page.context).model_fields
    }
    html = render_template(page.template, **context)
    return HTMLResponse(content=html, status_code=status_code)
