"""
Admin profile views.

Why: Gerenciamento do perfil do usuário no admin.

How: CRUD de Profile usando JinjaX.
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.catalog import catalog
from app.core.utils import get_form_json, get_form_str
from app.db import get_session
from app.models.profile import Profile
from app.models.user import User
from app.views.admin.deps import get_admin_user

router = APIRouter(prefix="/profile")


@router.get("", response_class=HTMLResponse)
async def edit_profile(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_admin_user),
):
    """Página de edição do perfil."""
    query = select(Profile).where(Profile.user_id == user.id)
    result = await session.execute(query)
    profile = result.scalar_one_or_none()

    if not profile:
        profile = Profile(user_id=user.id)
        session.add(profile)
        await session.commit()
        await session.refresh(profile)

    return catalog.render(
        "admin/profile.jinja",
        request=request,
        user=user,
        profile=profile,
    )


@router.post("")
async def save_profile(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_admin_user),
) -> RedirectResponse:
    """Salva as alterações do perfil do usuário."""
    form = await request.form()

    query = select(Profile).where(Profile.user_id == user.id)
    result = await session.execute(query)
    profile = result.scalar_one_or_none()

    if not profile:
        profile = Profile(user_id=user.id)

    # Atualiza campos básicos usando helpers type-safe
    profile.name = get_form_str(form, "name")
    profile.location = get_form_str(form, "location")
    profile.short_bio = get_form_str(form, "short_bio")
    profile.email = get_form_str(form, "email")
    profile.phone = get_form_str(form, "phone")
    profile.website = get_form_str(form, "website")
    profile.github = get_form_str(form, "github")
    profile.linkedin = get_form_str(form, "linkedin")
    profile.twitter = get_form_str(form, "twitter")
    profile.about_markdown = get_form_str(form, "about_markdown")

    # Campos JSON estruturados (Work, Education, Skills)
    work_data = get_form_json(form, "work_experience_json")
    if work_data is not None:
        profile.work_experience = work_data

    education_data = get_form_json(form, "education_json")
    if education_data is not None:
        profile.education = education_data

    skills_data = get_form_json(form, "skills_json")
    if skills_data is not None:
        profile.skills = skills_data

    session.add(profile)
    await session.commit()

    return RedirectResponse(url="/admin/profile", status_code=303)
