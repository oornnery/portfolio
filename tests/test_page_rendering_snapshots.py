from __future__ import annotations

from collections.abc import Iterator

from fastapi.testclient import TestClient

from app.app import create_app


def _build_client() -> Iterator[TestClient]:
    app = create_app()
    with TestClient(app) as client:
        yield client


def test_home_page_snapshot_sections() -> None:
    expected_fragments = (
        "View full resume",
        "Projects",
        "View more projects",
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
