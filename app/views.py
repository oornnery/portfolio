from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, or_
from app.db import get_session
from app.models.project import Project
from app.models.blog import Post
from app.models.user import User
from app.models.comment import Comment
from app.core.deps import get_current_user_optional
import markdown

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def home(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User | None = Depends(get_current_user_optional),
):
    # Fetch latest 3 projects
    projects_query = select(Project).order_by(Project.created_at.desc()).limit(3)
    projects_result = await session.execute(projects_query)
    projects_list = projects_result.scalars().all()

    # Fetch latest 3 posts
    posts_query = (
        select(Post)
        .where(Post.draft == False)  # noqa: E712
        .order_by(Post.published_at.desc())
        .limit(3)
    )
    posts_result = await session.execute(posts_query)
    posts_list = posts_result.scalars().all()

    return templates.TemplateResponse(
        "pages/home.html",
        {
            "request": request,
            "title": "Home",
            "user": user,
            "projects": projects_list,
            "posts": posts_list,
        },
    )


@router.get("/contact")
async def contact(
    request: Request, user: User | None = Depends(get_current_user_optional)
):
    return templates.TemplateResponse(
        "pages/contact.html", {"request": request, "title": "Contact", "user": user}
    )


@router.get("/about")
async def about(
    request: Request, user: User | None = Depends(get_current_user_optional)
):
    return templates.TemplateResponse(
        "pages/about.html", {"request": request, "title": "About", "user": user}
    )


@router.get("/projects")
async def projects(
    request: Request,
    category: str | None = None,
    tech: str | None = None,
    session: AsyncSession = Depends(get_session),
    user: User | None = Depends(get_current_user_optional),
):
    query = select(Project)
    if category:
        query = query.where(Project.category == category)

    # For tech stack filtering, we'd need a more complex query or filter in python
    # For now, let's just fetch all and filter in python if needed, or ignore tech filter for MVP

    result = await session.execute(query)
    projects_list = result.scalars().all()

    # Check if it's an HTMX request
    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            "partials/project_list.html",
            {"request": request, "projects": projects_list, "user": user},
        )

    return templates.TemplateResponse(
        "pages/projects.html",
        {
            "request": request,
            "title": "Projects",
            "projects": projects_list,
            "category": category,
            "user": user,
        },
    )


@router.get("/blog")
async def blog(
    request: Request,
    category: str | None = None,
    tag: str | None = None,
    search: str | None = None,
    session: AsyncSession = Depends(get_session),
    user: User | None = Depends(get_current_user_optional),
):
    query = select(Post).where(Post.draft == False).order_by(Post.published_at.desc())  # noqa: E712

    if category:
        query = query.where(Post.category == category)
    
    if search:
        query = query.where(
            or_(
                Post.title.ilike(f"%{search}%"),
                Post.description.ilike(f"%{search}%"),
                Post.content.ilike(f"%{search}%")
            )
        )

    # Tag filtering would require a join or specific logic depending on how tags are stored (JSON or relation)
    # Assuming tags is a JSON column or similar for now as per model
    
    result = await session.execute(query)
    posts = result.scalars().all()

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            "partials/post_list.html",
            {"request": request, "posts": posts, "user": user},
        )

    return templates.TemplateResponse(
        "blog/list.html", 
        {"request": request, "title": "Blog", "posts": posts, "user": user}
    )


@router.get("/blog/{slug}")
async def blog_post(
    slug: str, 
    request: Request, 
    session: AsyncSession = Depends(get_session),
    user: User | None = Depends(get_current_user_optional)
):
    query = select(Post).where(Post.slug == slug)
    result = await session.execute(query)
    post = result.scalar_one_or_none()
    
    if not post:
        # Handle 404
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Post not found")

    html_content = markdown.markdown(
        post.content,
        extensions=['fenced_code', 'codehilite', 'tables']
    )

    return templates.TemplateResponse(
        "blog/detail.html", 
        {
            "request": request, 
            "title": post.title, 
            "post": post, 
            "content": html_content,
            "user": user
        }
    )


@router.get("/comments/post/{slug}")
async def get_comments(
    slug: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User | None = Depends(get_current_user_optional),
):
    post_query = select(Post).where(Post.slug == slug)
    post_result = await session.execute(post_query)
    post = post_result.scalar_one_or_none()

    if not post:
        return "Post not found"

    query = (
        select(Comment, User)
        .join(User)
        .where(Comment.post_id == post.id)
        .order_by(Comment.created_at.desc())
    )
    result = await session.execute(query)
    comments = []
    for comment, comment_user in result.all():
        c_dict = comment.model_dump()
        c_dict["user_name"] = comment_user.name
        c_dict["user_avatar"] = comment_user.avatar_url
        comments.append(c_dict)

    return templates.TemplateResponse(
        "partials/comments.html",
        {"request": request, "comments": comments, "post": post, "user": user},
    )


@router.post("/comments/post/{slug}")
async def post_comment(
    slug: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User | None = Depends(get_current_user_optional),
):
    if not user:
        return "Please login to comment"

    form = await request.form()
    content = form.get("content")

    if not content:
        return "Content required"

    post_query = select(Post).where(Post.slug == slug)
    post_result = await session.execute(post_query)
    post = post_result.scalar_one_or_none()

    if not post:
        return "Post not found"

    comment = Comment(content=content, post_id=post.id, user_id=user.id)

    session.add(comment)
    await session.commit()

    # Return updated comments list
    return await get_comments(slug, request, session, user)


@router.get("/projects/{slug}")
async def project_detail(
    slug: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User | None = Depends(get_current_user_optional),
):
    query = select(Project).where(Project.slug == slug)
    result = await session.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Project not found")

    html_content = markdown.markdown(
        project.content,
        extensions=['fenced_code', 'codehilite', 'tables']
    )

    return templates.TemplateResponse(
        "pages/project_detail.html",
        {"request": request, "title": project.title, "project": project, "content": html_content, "user": user},
    )
