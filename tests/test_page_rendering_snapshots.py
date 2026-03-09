from __future__ import annotations

from collections.abc import Iterator

from fastapi.testclient import TestClient

from app.infrastructure.markdown import load_all_blog_posts, load_all_projects
from app.main import create_app


def _build_client() -> Iterator[TestClient]:
    app = create_app()
    with TestClient(app) as client:
        yield client


def test_home_page_snapshot_sections() -> None:
    expected_fragments = (
        "View full resume",
        "Projects",
        "View all projects",
        "View all posts",
        "Contact",
        "Send a Message",
    )

    for client in _build_client():
        response = client.get("/")
        assert response.status_code == 200
        html = response.text
        for fragment in expected_fragments:
            assert fragment in html


def test_about_page_snapshot_sections() -> None:
    expected_fragments = (
        "About",
        "Resume",
        "On this page",
        "Work Experience",
        "Education",
        "Certificates",
        "Skills",
    )

    for client in _build_client():
        response = client.get("/about")
        assert response.status_code == 200
        html = response.text
        for fragment in expected_fragments:
            assert fragment in html


def test_contact_page_snapshot_sections() -> None:
    expected_fragments = (
        "Contact",
        "Connect",
        "Send a Message",
        "Name",
        "Email",
        "Message",
    )

    for client in _build_client():
        response = client.get("/contact")
        assert response.status_code == 200
        html = response.text
        for fragment in expected_fragments:
            assert fragment in html


def test_blog_home_page_snapshot_sections() -> None:
    expected_fragments = (
        "Blog",
        "Featured Posts",
        "Previous featured post",
        "Next featured post",
        "Latest Posts",
        "View all posts",
        "Tags",
        "View all tags",
    )

    for client in _build_client():
        response = client.get("/blog")
        assert response.status_code == 200
        html = response.text
        for fragment in expected_fragments:
            assert fragment in html


def test_blog_posts_page_snapshot_sections() -> None:
    expected_fragments = ("All Posts",)

    for client in _build_client():
        response = client.get("/blog/posts")
        assert response.status_code == 200
        html = response.text
        for fragment in expected_fragments:
            assert fragment in html


def test_blog_post_detail_page_snapshot_sections() -> None:
    posts = load_all_blog_posts()
    assert posts
    post = posts[0]

    expected_fragments = (
        post.title,
        "min read",
        "On this page",
        'data-reading-progress-target="bar"',
        "Comments",
    )

    for client in _build_client():
        response = client.get(f"/blog/posts/{post.slug}")
        assert response.status_code == 200
        html = response.text
        for fragment in expected_fragments:
            assert fragment in html


def test_project_detail_page_snapshot_sections() -> None:
    projects = load_all_projects()
    assert projects
    project = projects[0]

    expected_fragments = (
        project.title,
        "On this page",
        "Source Code",
    )

    for client in _build_client():
        response = client.get(f"/projects/{project.slug}")
        assert response.status_code == 200
        html = response.text
        for fragment in expected_fragments:
            assert fragment in html


def test_blog_tags_page_snapshot_sections() -> None:
    expected_fragments = ("Tags",)

    for client in _build_client():
        response = client.get("/blog/tags")
        assert response.status_code == 200
        html = response.text
        for fragment in expected_fragments:
            assert fragment in html
