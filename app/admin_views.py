from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.db import get_session
from app.models.user import User
from app.models.profile import Profile
from app.models.project import Project
from app.models.blog import Post
from app.core.deps import get_current_user_optional
from app.config import settings
import json

router = APIRouter(prefix="/admin", include_in_schema=False)
templates = Jinja2Templates(directory="app/templates")
templates.env.globals["settings"] = settings


async def get_admin_user(
    request: Request, user: User | None = Depends(get_current_user_optional)
):
    if not user:
        raise HTTPException(status_code=302, headers={"Location": "/login"})
    # In a real app, check if user.is_admin
    # For this portfolio, we assume the first user or specific email is admin
    # or just allow any logged in user for now (since it's personal)
    return user


@router.get("/")
async def admin_dashboard(
    request: Request, user: User = Depends(get_admin_user)
):
    return templates.TemplateResponse(
        "admin/dashboard.html", {"request": request, "user": user, "title": "Admin Dashboard"}
    )


@router.get("/profile")
async def edit_profile(
    request: Request, 
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_admin_user)
):
    # Get profile or create default
    query = select(Profile).where(Profile.user_id == user.id)
    result = await session.execute(query)
    profile = result.scalar_one_or_none()
    
    if not profile:
        profile = Profile(user_id=user.id)
        session.add(profile)
        await session.commit()
        await session.refresh(profile)

    return templates.TemplateResponse(
        "admin/profile.html", 
        {"request": request, "user": user, "profile": profile, "title": "Edit Profile"}
    )


@router.post("/profile")
async def save_profile(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_admin_user)
):
    form = await request.form()
    
    query = select(Profile).where(Profile.user_id == user.id)
    result = await session.execute(query)
    profile = result.scalar_one_or_none()
    
    if not profile:
        profile = Profile(user_id=user.id)
    
    # Update fields
    profile.name = form.get("name")
    profile.location = form.get("location")
    profile.short_bio = form.get("short_bio")
    profile.email = form.get("email")
    profile.phone = form.get("phone")
    profile.website = form.get("website")
    profile.github = form.get("github")
    profile.linkedin = form.get("linkedin")
    profile.twitter = form.get("twitter")
    profile.about_markdown = form.get("about_markdown")
    
    # Handle structured data (Work, Education, Skills)
    work_experience_json = form.get("work_experience_json")
    if work_experience_json:
        try:
            profile.work_experience = json.loads(work_experience_json)
        except json.JSONDecodeError:
            pass

    education_json = form.get("education_json")
    if education_json:
        try:
            profile.education = json.loads(education_json)
        except json.JSONDecodeError:
            pass

    skills_json = form.get("skills_json")
    if skills_json:
        try:
            profile.skills = json.loads(skills_json)
        except json.JSONDecodeError:
            pass
    
    session.add(profile)
    await session.commit()
    
    return RedirectResponse(url="/admin/profile", status_code=303)


# Projects Admin
@router.get("/projects")
async def list_projects(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_admin_user)
):
    projects = (await session.execute(select(Project).order_by(Project.created_at.desc()))).scalars().all()
    return templates.TemplateResponse(
        "admin/projects_list.html", 
        {"request": request, "user": user, "projects": projects, "title": "Manage Projects"}
    )

@router.get("/projects/new")
async def new_project(
    request: Request,
    user: User = Depends(get_admin_user)
):
    return templates.TemplateResponse(
        "admin/project_edit.html", 
        {"request": request, "user": user, "project": None, "title": "New Project"}
    )

@router.post("/projects/new")
async def create_project(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_admin_user)
):
    form = await request.form()
    project = Project(
        title=form.get("title"),
        slug=form.get("slug"),
        description=form.get("description"),
        content=form.get("content"),
        image=form.get("image"),
        category=form.get("category"),
        github_url=form.get("github_url"),
        demo_url=form.get("demo_url"),
        featured=bool(form.get("featured")),
    )
    
    tech_stack_str = form.get("tech_stack")
    if tech_stack_str:
        project.tech_stack = [t.strip() for t in tech_stack_str.split(",") if t.strip()]
        
    session.add(project)
    await session.commit()
    return RedirectResponse(url="/admin/projects", status_code=303)

@router.get("/projects/{project_id}")
async def edit_project(
    request: Request,
    project_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_admin_user)
):
    project = await session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    return templates.TemplateResponse(
        "admin/project_edit.html", 
        {"request": request, "user": user, "project": project, "title": "Edit Project"}
    )

@router.post("/projects/{project_id}")
async def update_project(
    request: Request,
    project_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_admin_user)
):
    project = await session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    form = await request.form()
    project.title = form.get("title")
    project.slug = form.get("slug")
    project.description = form.get("description")
    project.content = form.get("content")
    project.image = form.get("image")
    project.category = form.get("category")
    project.github_url = form.get("github_url")
    project.demo_url = form.get("demo_url")
    project.featured = bool(form.get("featured"))
    
    tech_stack_str = form.get("tech_stack")
    if tech_stack_str:
        project.tech_stack = [t.strip() for t in tech_stack_str.split(",") if t.strip()]
    else:
        project.tech_stack = []
        
    session.add(project)
    await session.commit()
    return RedirectResponse(url="/admin/projects", status_code=303)

@router.post("/projects/{project_id}/delete")
async def delete_project(
    request: Request,
    project_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_admin_user)
):
    project = await session.get(Project, project_id)
    if project:
        await session.delete(project)
        await session.commit()
    return RedirectResponse(url="/admin/projects", status_code=303)


# Blog Admin
@router.get("/blog")
async def list_posts(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_admin_user)
):
    posts = (await session.execute(select(Post).order_by(Post.created_at.desc()))).scalars().all()
    return templates.TemplateResponse(
        "admin/blog_list.html", 
        {"request": request, "user": user, "posts": posts, "title": "Manage Blog"}
    )

@router.get("/blog/new")
async def new_post(
    request: Request,
    user: User = Depends(get_admin_user)
):
    return templates.TemplateResponse(
        "admin/blog_edit.html", 
        {"request": request, "user": user, "post": None, "title": "New Post"}
    )

@router.post("/blog/new")
async def create_post(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_admin_user)
):
    form = await request.form()
    post = Post(
        title=form.get("title"),
        slug=form.get("slug"),
        description=form.get("description"),
        content=form.get("content"),
        image=form.get("image"),
        category=form.get("category"),
        reading_time=int(form.get("reading_time") or 5),
    )
    
    tags_str = form.get("tags")
    if tags_str:
        post.tags = [t.strip() for t in tags_str.split(",") if t.strip()]
        
    session.add(post)
    await session.commit()
    return RedirectResponse(url="/admin/blog", status_code=303)

@router.get("/blog/{post_id}")
async def edit_post(
    request: Request,
    post_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_admin_user)
):
    post = await session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    return templates.TemplateResponse(
        "admin/blog_edit.html", 
        {"request": request, "user": user, "post": post, "title": "Edit Post"}
    )

@router.post("/blog/{post_id}")
async def update_post(
    request: Request,
    post_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_admin_user)
):
    post = await session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    form = await request.form()
    post.title = form.get("title")
    post.slug = form.get("slug")
    post.description = form.get("description")
    post.content = form.get("content")
    post.image = form.get("image")
    post.category = form.get("category")
    post.reading_time = int(form.get("reading_time") or 5)
    
    tags_str = form.get("tags")
    if tags_str:
        post.tags = [t.strip() for t in tags_str.split(",") if t.strip()]
    else:
        post.tags = []
        
    session.add(post)
    await session.commit()
    return RedirectResponse(url="/admin/blog", status_code=303)

@router.post("/blog/{post_id}/delete")
async def delete_post(
    request: Request,
    post_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_admin_user)
):
    post = await session.get(Post, post_id)
    if post:
        await session.delete(post)
        await session.commit()
    return RedirectResponse(url="/admin/blog", status_code=303)
