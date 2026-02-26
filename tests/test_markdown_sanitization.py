from app.services.markdown import _render_md, _sanitize_html


def test_markdown_sanitization_strips_dangerous_html() -> None:
    raw_markdown = "Hello<script>alert('xss')</script>\n\n[click](javascript:alert(1))"

    rendered = _render_md(raw_markdown)
    sanitized = _sanitize_html(rendered)

    assert "<script" not in sanitized.lower()
    assert "javascript:" not in sanitized.lower()


def test_markdown_sanitization_preserves_table_markup() -> None:
    raw_markdown = "| col1 | col2 |\n| --- | --- |\n| a | b |"

    rendered = _render_md(raw_markdown)
    sanitized = _sanitize_html(rendered)

    assert "<table" in sanitized
    assert "<tr" in sanitized
    assert "<td" in sanitized
