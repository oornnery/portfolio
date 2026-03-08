from __future__ import annotations

from pathlib import Path
from textwrap import dedent

from app.models.models import BlogComment
from app.infrastructure import markdown as markdown_infra


def _write_blog_file(path: Path, frontmatter: str, body: str = "") -> None:
    path.write_text(
        "---\n" + frontmatter.strip() + "\n---\n" + body,
        encoding="utf-8",
    )


def test_blog_loader_prefers_local_markdown_over_gist_content(
    monkeypatch, tmp_path: Path
) -> None:
    blog_dir = tmp_path / "blog"
    blog_dir.mkdir(parents=True, exist_ok=True)
    _write_blog_file(
        blog_dir / "local-over-gist.md",
        frontmatter=dedent(
            """
            title: "Local Over Gist"
            slug: "local-over-gist"
            date: "2026-03-05"
            gist_url: "https://gist.github.com/octocat/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            """
        ),
        body="Local **markdown** content wins.",
    )

    payload_calls = {"count": 0}

    def _fake_payload(_: str) -> dict[str, object]:
        payload_calls["count"] += 1
        return {
            "files": {
                "post.md": {
                    "content": "Remote gist content",
                    "truncated": False,
                    "raw_url": "https://gist.githubusercontent.com/raw/example",
                }
            }
        }

    monkeypatch.setattr(markdown_infra, "BLOG_DIR", blog_dir)
    monkeypatch.setattr(markdown_infra, "_fetch_gist_payload", _fake_payload)
    monkeypatch.setattr(
        markdown_infra,
        "_fetch_gist_comments",
        lambda _: (
            BlogComment(
                author="octocat",
                body="Nice post",
                created_at="Mar 05, 2026",
                profile_url="https://github.com/octocat",
                html_url="https://gist.github.com/comment/1",
            ),
        ),
    )
    markdown_infra._content_cache.clear()

    posts = markdown_infra.load_all_blog_posts()

    assert len(posts) == 1
    post = posts[0]
    assert "<strong>markdown</strong>" in post.content_html
    assert payload_calls["count"] == 0
    assert post.gist_id == "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    assert post.discussion_url.endswith("#comments")
    assert len(post.comments) == 1
    markdown_infra._content_cache.clear()


def test_blog_loader_uses_gist_content_when_markdown_body_is_empty(
    monkeypatch, tmp_path: Path
) -> None:
    blog_dir = tmp_path / "blog"
    blog_dir.mkdir(parents=True, exist_ok=True)
    _write_blog_file(
        blog_dir / "gist-only.md",
        frontmatter=dedent(
            """
            title: "Gist Only"
            slug: "gist-only"
            date: "2026-03-05"
            gist_url: "https://gist.github.com/octocat/bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
            gist_file: "post.md"
            """
        ),
        body="",
    )

    monkeypatch.setattr(markdown_infra, "BLOG_DIR", blog_dir)
    monkeypatch.setattr(
        markdown_infra,
        "_fetch_gist_payload",
        lambda _: {
            "files": {
                "post.md": {
                    "content": "Remote gist **markdown** body.",
                    "truncated": False,
                    "raw_url": "https://gist.githubusercontent.com/raw/example",
                }
            }
        },
    )
    monkeypatch.setattr(markdown_infra, "_fetch_gist_comments", lambda _: ())
    markdown_infra._content_cache.clear()

    posts = markdown_infra.load_all_blog_posts()

    assert len(posts) == 1
    post = posts[0]
    assert "<strong>markdown</strong>" in post.content_html
    assert post.description.startswith("Remote gist")
    assert post.gist_id == "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    markdown_infra._content_cache.clear()
