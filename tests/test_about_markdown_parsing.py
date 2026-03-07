from __future__ import annotations

from pathlib import Path
from textwrap import dedent

from app.infrastructure import markdown as markdown_infra


def test_about_loader_parses_frontmatter_and_markdown_sections(
    monkeypatch, tmp_path: Path
) -> None:
    content_dir = tmp_path / "content"
    content_dir.mkdir(parents=True, exist_ok=True)
    (content_dir / "about.md").write_text(
        dedent(
            """
            ---
            name: "Test Engineer"
            description: "Backend engineer focused on reliable systems."
            role: "Backend Engineer"
            location: "Sao Paulo, Brazil"
            social_links:
              github: "https://github.com/example"
            ---
            I build **reliable** backend systems.

            ## About

            I care about [maintainable delivery](https://example.com).

            ## Work Experience

            ### Senior Engineer

            **Company:** Example Co
            **Location:** Remote
            **Period:** 2020 - Present

            Built APIs with strong delivery defaults.

            - improved observability
            - simplified validation contracts

            ## Education

            ### University of Technology

            **Degree:** B.S. in Computer Science
            **Period:** 2014 - 2018

            ## Certificates

            ### AWS Certified Solutions Architect

            **Issuer:** Amazon Web Services
            **Date:** 2023
            **Credential ID:** AWS-SAA-123456

            ## Skills

            ### Backend

            - Python
            - FastAPI

            ### Infra

            - Docker
            - Linux
            """
        ).strip(),
        encoding="utf-8",
    )

    monkeypatch.setattr(markdown_infra, "CONTENT_DIR", content_dir)
    markdown_infra._content_cache.clear()

    about = markdown_infra.load_about()

    assert about.frontmatter.name == "Test Engineer"
    assert "<strong>reliable</strong>" in about.hero_html
    assert 'href="https://example.com"' in about.about_html

    assert len(about.work_experience) == 1
    experience = about.work_experience[0]
    assert experience.title == "Senior Engineer"
    assert experience.company == "Example Co"
    assert experience.location == "Remote"
    assert experience.start_date == "2020"
    assert experience.end_date == "Present"
    assert "<ul>" in experience.content_html

    assert len(about.education) == 1
    education = about.education[0]
    assert education.school == "University of Technology"
    assert education.degree == "B.S. in Computer Science"
    assert education.start_date == "2014"
    assert education.end_date == "2018"

    assert len(about.certificates) == 1
    certificate = about.certificates[0]
    assert certificate.name == "AWS Certified Solutions Architect"
    assert certificate.issuer == "Amazon Web Services"
    assert certificate.date == "2023"
    assert certificate.credential_id == "AWS-SAA-123456"

    assert len(about.skill_groups) == 2
    assert about.skill_groups[0].title == "Backend"
    assert about.skill_groups[0].skills == ["Python", "FastAPI"]
    assert about.skill_groups[1].title == "Infra"
    assert about.skill_groups[1].skills == ["Docker", "Linux"]

    markdown_infra._content_cache.clear()


def test_about_loader_allows_missing_optional_fields(
    monkeypatch, tmp_path: Path
) -> None:
    content_dir = tmp_path / "content"
    content_dir.mkdir(parents=True, exist_ok=True)
    (content_dir / "about.md").write_text(
        dedent(
            """
            ---
            name: "Test Engineer"
            description: "Backend engineer focused on reliable systems."
            social_links:
              github: "https://github.com/example"
            ---
            Intro paragraph.

            ## Work Experience

            ### Senior Engineer

            **Company:** Example Co

            Did useful work.

            ## Education

            ### University of Technology

            ## Certificates

            ### AWS Certified Solutions Architect

            ## Skills

            ### Backend

            - Python
            """
        ).strip(),
        encoding="utf-8",
    )

    monkeypatch.setattr(markdown_infra, "CONTENT_DIR", content_dir)
    markdown_infra._content_cache.clear()

    about = markdown_infra.load_about()

    experience = about.work_experience[0]
    assert experience.location == ""
    assert experience.start_date == ""
    assert experience.end_date == ""

    education = about.education[0]
    assert education.degree == ""
    assert education.start_date == ""
    assert education.end_date == ""

    certificate = about.certificates[0]
    assert certificate.issuer == ""
    assert certificate.date == ""
    assert certificate.credential_id == ""

    markdown_infra._content_cache.clear()
