from __future__ import annotations

import re
from collections.abc import Iterator

from fastapi.testclient import TestClient

from app.main import create_app
from app.infrastructure.markdown import load_all_blog_posts, load_all_projects


def _extract_csrf_token(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match is not None
    return match.group(1)


def _build_client() -> Iterator[TestClient]:
    app = create_app()
    with TestClient(app) as client:
        yield client


def test_public_routes_return_success_status() -> None:
    for client in _build_client():
        for path in (
            "/",
            "/about",
            "/projects",
            "/contact",
            "/blog",
            "/blog/posts",
            "/blog/tags",
            "/blog/feed.xml",
        ):
            response = client.get(path)
            assert response.status_code == 200


def test_base_layout_includes_favicon() -> None:
    for client in _build_client():
        response = client.get("/")
        assert response.status_code == 200
        assert (
            'rel="icon" type="image/svg+xml" href="/static/favicon.svg"'
            in response.text
        )


def test_base_layout_exposes_frontend_telemetry_meta_and_no_legacy_script() -> None:
    for client in _build_client():
        response = client.get("/")

        assert response.status_code == 200
        assert 'name="frontend-telemetry-enabled"' in response.text
        assert 'name="frontend-telemetry-otlp-endpoint"' in response.text
        assert "/static/js/analytics.js" not in response.text


def test_contact_page_renders_htmx_and_alpine_form_enhancement() -> None:
    for client in _build_client():
        response = client.get("/contact", headers={"user-agent": "pytest-agent"})
        assert response.status_code == 200
        assert 'hx-post="/contact"' in response.text
        assert 'hx-target="#contact-form-section"' in response.text
        assert 'x-data="contactForm()"' in response.text
        assert '@submit.prevent="submit"' in response.text


def test_project_detail_existing_and_missing_slug() -> None:
    projects = load_all_projects()
    assert projects
    existing_slug = projects[0].slug

    for client in _build_client():
        ok_response = client.get(f"/projects/{existing_slug}")
        missing_response = client.get("/projects/slug-that-does-not-exist")
        assert ok_response.status_code == 200
        assert missing_response.status_code == 404


def test_blog_post_detail_existing_and_missing_slug() -> None:
    posts = load_all_blog_posts()
    assert posts
    existing_slug = posts[0].slug

    for client in _build_client():
        ok_response = client.get(f"/blog/posts/{existing_slug}")
        missing_response = client.get("/blog/posts/slug-that-does-not-exist")
        assert ok_response.status_code == 200
        assert missing_response.status_code == 404


def test_blog_tag_detail_route_returns_success() -> None:
    posts = load_all_blog_posts()
    assert posts
    first_tag = posts[0].tags[0]

    for client in _build_client():
        response = client.get(f"/blog/tags/{first_tag}")
        assert response.status_code == 200


def test_blog_posts_route_supports_pagination() -> None:
    posts = load_all_blog_posts()
    assert len(posts) > 10
    first_page_title = posts[0].title
    second_page_title = posts[10].title

    for client in _build_client():
        response = client.get("/blog/posts?page=2")
        assert response.status_code == 200
        assert second_page_title in response.text
        assert first_page_title not in response.text


def test_projects_route_supports_pagination() -> None:
    projects = load_all_projects()
    assert len(projects) > 10
    first_page_title = projects[0].title
    second_page_title = projects[10].title

    for client in _build_client():
        response = client.get("/projects?page=2")
        assert response.status_code == 200
        assert second_page_title in response.text
        assert first_page_title not in response.text


def test_blog_tags_route_returns_fragment_for_htmx_requests() -> None:
    posts = load_all_blog_posts()
    assert posts
    tag = posts[0].tags[0]

    for client in _build_client():
        response = client.get(
            f"/blog/tags/{tag}",
            headers={"HX-Request": "true"},
        )
        assert response.status_code == 200
        assert 'id="tag-posts"' in response.text
        assert "<html" not in response.text.lower()
        assert f">{tag} (" in response.text


def test_projects_route_returns_fragment_for_htmx_requests() -> None:
    for client in _build_client():
        response = client.get(
            "/projects",
            headers={"HX-Request": "true"},
        )
        assert response.status_code == 200
        assert 'id="projects-list"' in response.text
        assert "<html" not in response.text.lower()


def test_resume_download_returns_markdown_file() -> None:
    for client in _build_client():
        response = client.get("/about/resume.md")
        assert response.status_code == 200
        assert "text/markdown" in response.headers["content-type"]
        assert response.headers.get("content-disposition", "").startswith("attachment")


def test_blog_feed_returns_rss_xml() -> None:
    for client in _build_client():
        response = client.get("/blog/feed.xml")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/rss+xml")
        assert "<rss" in response.text
        assert "<channel>" in response.text


def test_contact_submission_success_flow() -> None:
    for client in _build_client():
        get_response = client.get("/contact", headers={"user-agent": "pytest-agent"})
        csrf_token = _extract_csrf_token(get_response.text)

        post_response = client.post(
            "/contact",
            data={
                "name": "Alice Example",
                "email": "alice@example.com",
                "subject": "Site Contact",
                "message": "Hello, I would like to discuss a project collaboration.",
                "csrf_token": csrf_token,
            },
            headers={"user-agent": "pytest-agent"},
        )

        assert post_response.status_code == 200
        assert "Message sent successfully" in post_response.text


def test_contact_submission_rejects_invalid_csrf() -> None:
    for client in _build_client():
        post_response = client.post(
            "/contact",
            data={
                "name": "Alice Example",
                "email": "alice@example.com",
                "subject": "Site Contact",
                "message": "Hello, I would like to discuss a project collaboration.",
                "csrf_token": "invalid-token",
            },
            headers={"user-agent": "pytest-agent"},
        )

        assert post_response.status_code == 403
        assert "Invalid or expired security token" in post_response.text


def test_contact_submission_returns_validation_errors() -> None:
    for client in _build_client():
        get_response = client.get("/contact", headers={"user-agent": "pytest-agent"})
        csrf_token = _extract_csrf_token(get_response.text)

        post_response = client.post(
            "/contact",
            data={
                "name": "A",
                "email": "not-an-email",
                "subject": "Hi",
                "message": "short",
                "csrf_token": csrf_token,
            },
            headers={"user-agent": "pytest-agent"},
        )

        assert post_response.status_code == 422
        assert "valid email address" in post_response.text


def test_contact_submission_returns_fragment_for_htmx_validation_errors() -> None:
    for client in _build_client():
        get_response = client.get("/contact", headers={"user-agent": "pytest-agent"})
        csrf_token = _extract_csrf_token(get_response.text)

        post_response = client.post(
            "/contact",
            data={
                "name": "A",
                "email": "not-an-email",
                "subject": "Hi",
                "message": "short",
                "csrf_token": csrf_token,
            },
            headers={
                "user-agent": "pytest-agent",
                "HX-Request": "true",
            },
        )

        assert post_response.status_code == 422
        assert 'id="contact-form-section"' in post_response.text
        assert "<html" not in post_response.text.lower()
