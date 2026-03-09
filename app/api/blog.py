import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Request
from fastapi.responses import HTMLResponse, Response

from app.core.dependencies import get_blog_page_service
from app.core.rendering import is_htmx, render_fragment, render_page
from app.services import BlogPageService
from app.services.types import BlogTagsPageContext

router = APIRouter(prefix="/blog", tags=["blog"])
logger = logging.getLogger(__name__)

BlogPageServiceDep = Annotated[BlogPageService, Depends(get_blog_page_service)]


@router.get("", response_class=HTMLResponse)
async def blog_home(page_service: BlogPageServiceDep) -> HTMLResponse:
    page = page_service.build_home_page()
    logger.debug("Blog home page rendered.")
    return render_page(page)


@router.get("/posts", response_class=HTMLResponse)
async def blog_posts(page_service: BlogPageServiceDep) -> HTMLResponse:
    page = page_service.build_posts_page()
    logger.debug("Blog posts page rendered.")
    return render_page(page)


@router.get("/posts/{slug}", response_class=HTMLResponse)
async def blog_post_detail(
    slug: Annotated[str, Path()],
    page_service: BlogPageServiceDep,
) -> HTMLResponse:
    post = page_service.get_post(slug)
    if post is None:
        logger.info(f"Blog post detail not found for slug={slug}.")
        raise HTTPException(status_code=404, detail="Blog post not found")
    page = page_service.build_post_page(post)
    logger.debug(f"Blog post detail page rendered for slug={slug}.")
    return render_page(page)


@router.get("/tags", response_class=HTMLResponse)
async def blog_tags(request: Request, page_service: BlogPageServiceDep) -> HTMLResponse:
    page = page_service.build_tags_page()
    logger.debug("Blog tags page rendered.")
    if is_htmx(request):
        ctx = page.context
        assert isinstance(ctx, BlogTagsPageContext)
        return render_fragment(
            "@features/blog/tag-posts-fragment.jinja",
            posts=ctx.posts,
        )
    return render_page(page)


@router.get("/tags/{tag}", response_class=HTMLResponse)
async def blog_tag_detail(
    tag: Annotated[str, Path()],
    request: Request,
    page_service: BlogPageServiceDep,
) -> HTMLResponse:
    page = page_service.build_tags_page(tag=tag)
    logger.debug(f"Blog tag page rendered for tag={tag}.")
    if is_htmx(request):
        ctx = page.context
        assert isinstance(ctx, BlogTagsPageContext)
        return render_fragment(
            "@features/blog/tag-posts-fragment.jinja",
            posts=ctx.posts,
        )
    return render_page(page)


@router.get("/feed.xml")
async def blog_feed(page_service: BlogPageServiceDep) -> Response:
    feed = page_service.build_rss_feed()
    logger.debug("Blog RSS feed rendered.")
    return Response(
        content=feed,
        media_type="application/rss+xml",
        headers={"Cache-Control": "public, max-age=900"},
    )
