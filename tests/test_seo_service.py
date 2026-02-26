from datetime import date

from app.core.config import settings
from app.domain.models import Project
from app.application.services.seo import seo_for_page, seo_for_project


def test_seo_for_page_builds_canonical_and_absolute_og_image() -> None:
    seo = seo_for_page(
        title="Home",
        description="x" * 200,
        path="/about",
        og_image="/static/images/custom.png",
        keywords=["python", "fastapi"],
    )

    assert seo.title == f"Home | {settings.site_name}"
    assert len(seo.description) == 160
    assert seo.canonical_url == "http://localhost:8000/about"
    assert seo.og_image == "http://localhost:8000/static/images/custom.png"
    assert seo.keywords == ["python", "fastapi"]


def test_seo_for_project_uses_article_type_and_project_path() -> None:
    project = Project(
        slug="secure-contact-pipeline",
        title="Secure Contact Pipeline",
        description="A secure contact pipeline.",
        content_html="<p>content</p>",
        thumbnail="/static/images/secure-contact.png",
        tags=["fastapi", "security"],
        tech_stack=["FastAPI", "Pydantic"],
        github_url="https://github.com/example/repo",
        live_url="https://example.com/demo",
        date=date(2026, 1, 1),
        featured=True,
    )

    seo = seo_for_project(project)

    assert seo.og_type == "article"
    assert seo.canonical_url == "http://localhost:8000/projects/secure-contact-pipeline"
    assert seo.og_image == "http://localhost:8000/static/images/secure-contact.png"
    assert seo.keywords == ["fastapi", "security"]
