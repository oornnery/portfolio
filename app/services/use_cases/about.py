import logging

from app.services.markdown import load_about
from app.services.seo import seo_for_page
from app.services.use_cases.types import PageRenderData

logger = logging.getLogger(__name__)


class AboutPageService:
    def build_page(self) -> PageRenderData:
        about_content = load_about()
        frontmatter = about_content.frontmatter
        seo = seo_for_page(
            title="About",
            description=frontmatter.description or "About me",
            path="/about",
        )
        logger.debug(
            f"About use-case built with html_length={len(about_content.body_html)}"
        )
        return PageRenderData(
            template="pages/about.jinja",
            context={
                "seo": seo,
                "meta": frontmatter,
                "content_html": about_content.body_html,
                "current_path": "/about",
            },
        )

