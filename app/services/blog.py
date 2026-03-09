import logging
import math
import re
from collections import Counter
from datetime import datetime, time, timezone
from email.utils import format_datetime
from xml.sax.saxutils import escape

from app.core.config import settings
from app.models.models import BlogPost, BlogTag
from app.infrastructure.markdown import (
    get_blog_post_by_slug,
    load_about,
    load_all_blog_posts,
)
from app.services.seo import seo_for_page
from app.services.types import (
    BlogHomePageContext,
    BlogPostDetailPageContext,
    BlogPostsPageContext,
    BlogTagsPageContext,
    PageRenderData,
)

logger = logging.getLogger(__name__)


class BlogPageService:
    @staticmethod
    def _post_url(slug: str) -> str:
        return f"/blog/posts/{slug}"

    @staticmethod
    def _normalize_tag(tag: str) -> str:
        return tag.strip().lower()

    @staticmethod
    def _build_tag_stats(posts: tuple[BlogPost, ...]) -> tuple[BlogTag, ...]:
        counter: Counter[str] = Counter()
        for post in posts:
            for tag in post.tags:
                normalized = tag.strip()
                if normalized:
                    counter[normalized] += 1

        tags = tuple(
            BlogTag(name=name, count=count)
            for name, count in sorted(
                counter.items(), key=lambda item: (-item[1], item[0])
            )
        )
        return tags

    @staticmethod
    def _resolve_site_name() -> str:
        about_content = load_about()
        site_name = str(about_content.frontmatter.name or settings.site_name).strip()
        return site_name or settings.site_name

    @staticmethod
    def _estimate_read_time_minutes(content_html: str) -> int:
        plain_text = re.sub(r"<[^>]+>", " ", content_html)
        words = [word for word in plain_text.split() if word.strip()]
        return max(1, math.ceil(len(words) / 220))

    def _adjacent_posts(
        self, post: BlogPost
    ) -> tuple[BlogPost | None, BlogPost | None]:
        posts = load_all_blog_posts()
        for index, candidate in enumerate(posts):
            if candidate.slug != post.slug:
                continue
            previous_post = posts[index - 1] if index > 0 else None
            next_post = posts[index + 1] if index + 1 < len(posts) else None
            return previous_post, next_post
        return None, None

    def build_home_page(self) -> PageRenderData:
        posts = load_all_blog_posts()
        featured_candidates = [post for post in posts if post.featured]
        non_featured_candidates = [post for post in posts if not post.featured]
        featured_posts = tuple((featured_candidates + non_featured_candidates)[:3])
        recent_posts = posts[:3]
        tags = self._build_tag_stats(posts)[:10]

        seo = seo_for_page(
            title="Blog",
            description="Engineering notes, architecture decisions, and backend lessons learned.",
            path="/blog",
        )
        logger.debug(
            "Blog home use-case built with post_count=%s featured_count=%s.",
            len(posts),
            len(featured_posts),
        )
        return PageRenderData(
            template="pages/blog/home.jinja",
            context=BlogHomePageContext(
                seo=seo,
                featured_posts=featured_posts,
                recent_posts=recent_posts,
                tags=tags,
            ),
        )

    def build_posts_page(self, page: int = 1, page_size: int = 10) -> PageRenderData:
        all_posts = load_all_blog_posts()
        total = len(all_posts)
        total_pages = max(1, math.ceil(total / page_size))
        page = max(1, min(page, total_pages))
        start = (page - 1) * page_size
        posts = all_posts[start : start + page_size]

        seo = seo_for_page(
            title="Blog Posts",
            description="All published blog posts.",
            path="/blog/posts",
        )
        return PageRenderData(
            template="pages/blog/posts.jinja",
            context=BlogPostsPageContext(
                seo=seo,
                posts=posts,
                page=page,
                total_pages=total_pages,
            ),
        )

    def get_post(self, slug: str) -> BlogPost | None:
        return get_blog_post_by_slug(slug)

    def build_post_page(self, post: BlogPost) -> PageRenderData:
        seo = seo_for_page(
            title=post.title,
            description=post.description,
            path=self._post_url(post.slug),
            og_type="article",
            keywords=post.tags,
        )
        previous_post, next_post = self._adjacent_posts(post)
        read_time_minutes = self._estimate_read_time_minutes(post.content_html)
        return PageRenderData(
            template="pages/blog/detail.jinja",
            context=BlogPostDetailPageContext(
                seo=seo,
                post=post,
                previous_post=previous_post,
                next_post=next_post,
                read_time_minutes=read_time_minutes,
            ),
        )

    def build_tags_page(self, tag: str | None = None) -> PageRenderData:
        posts = load_all_blog_posts()
        tags = self._build_tag_stats(posts)
        selected_tag = tag.strip() if tag else ""
        selected_tag_normalized = self._normalize_tag(selected_tag)

        if selected_tag_normalized:
            filtered_posts = tuple(
                post
                for post in posts
                if selected_tag_normalized
                in {self._normalize_tag(post_tag) for post_tag in post.tags}
            )
            title = f"Tag: {selected_tag}"
            description = f"Posts tagged with {selected_tag}."
            path = f"/blog/tags/{selected_tag}"
        else:
            filtered_posts = posts
            title = "Blog Tags"
            description = "Browse posts by tag."
            path = "/blog/tags"

        seo = seo_for_page(
            title=title,
            description=description,
            path=path,
        )
        return PageRenderData(
            template="pages/blog/tags.jinja",
            context=BlogTagsPageContext(
                seo=seo,
                tags=tags,
                posts=filtered_posts,
                selected_tag=selected_tag,
            ),
        )

    def build_rss_feed(self) -> str:
        posts = load_all_blog_posts()
        site_name = self._resolve_site_name()
        base_url = str(settings.base_url).rstrip("/")
        blog_url = f"{base_url}/blog"
        feed_url = f"{base_url}/blog/feed.xml"

        items: list[str] = []
        for post in posts[:50]:
            post_url = f"{base_url}{self._post_url(post.slug)}"
            description = escape(post.description or "")
            if post.date is not None:
                published_dt = datetime.combine(
                    post.date, time.min, tzinfo=timezone.utc
                )
                pub_date = format_datetime(published_dt, usegmt=True)
                pub_date_tag = f"<pubDate>{pub_date}</pubDate>"
            else:
                pub_date_tag = ""

            categories = "".join(
                f"<category>{escape(tag)}</category>"
                for tag in post.tags
                if tag.strip()
            )
            items.append(
                "<item>"
                f"<title>{escape(post.title)}</title>"
                f"<link>{escape(post_url)}</link>"
                f'<guid isPermaLink="true">{escape(post_url)}</guid>'
                f"<description>{description}</description>"
                f"{pub_date_tag}"
                f"{categories}"
                "</item>"
            )

        feed = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">'
            "<channel>"
            f"<title>{escape(site_name)} Blog</title>"
            f"<link>{escape(blog_url)}</link>"
            "<description>Latest posts from the site blog.</description>"
            "<language>en-us</language>"
            f'<atom:link href="{escape(feed_url)}" rel="self" type="application/rss+xml"/>'
            f"{''.join(items)}"
            "</channel>"
            "</rss>"
        )
        return feed
