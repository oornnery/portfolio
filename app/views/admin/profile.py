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
from app.core.utils import get_form_str
from app.db import get_session
from app.models.profile import Profile
from app.models.user import User
from app.views.admin.deps import get_admin_user

router = APIRouter(prefix="/profile")


def get_form_list(form, key: str) -> list[str]:
    """
    Extrai uma lista de valores do formulário para campos com nome 'key[]'.

    Why: Formulários HTML com campos array (name="field[]") enviam múltiplos
         valores que precisam ser coletados como lista.
    """
    return form.getlist(key)


def build_work_experience(form) -> list[dict]:
    """
    Constrói a lista de work experience a partir dos campos do formulário.

    Why: Os campos vêm separados (work_title[], work_company[], etc.)
         e precisam ser agrupados em dicionários.
    """
    titles = get_form_list(form, "work_title[]")
    companies = get_form_list(form, "work_company[]")
    locations = get_form_list(form, "work_location[]")
    start_dates = get_form_list(form, "work_start_date[]")
    end_dates = get_form_list(form, "work_end_date[]")
    descriptions = get_form_list(form, "work_description[]")

    work_experience = []
    for i in range(len(titles)):
        # Pula entradas vazias
        if not titles[i].strip():
            continue
        work_experience.append(
            {
                "title": titles[i].strip(),
                "company": companies[i].strip() if i < len(companies) else "",
                "location": locations[i].strip() if i < len(locations) else "",
                "start_date": start_dates[i].strip() if i < len(start_dates) else "",
                "end_date": end_dates[i].strip() if i < len(end_dates) else "",
                "description": descriptions[i].strip() if i < len(descriptions) else "",
            }
        )
    return work_experience


def build_education(form) -> list[dict]:
    """
    Constrói a lista de education a partir dos campos do formulário.

    Why: Os campos vêm separados (edu_school[], edu_degree[], etc.)
         e precisam ser agrupados em dicionários.
    """
    schools = get_form_list(form, "edu_school[]")
    degrees = get_form_list(form, "edu_degree[]")
    start_dates = get_form_list(form, "edu_start_date[]")
    end_dates = get_form_list(form, "edu_end_date[]")

    education = []
    for i in range(len(schools)):
        # Pula entradas vazias
        if not schools[i].strip():
            continue
        education.append(
            {
                "school": schools[i].strip(),
                "degree": degrees[i].strip() if i < len(degrees) else "",
                "start_date": start_dates[i].strip() if i < len(start_dates) else "",
                "end_date": end_dates[i].strip() if i < len(end_dates) else "",
            }
        )
    return education


def build_skills(form) -> list[str]:
    """
    Constrói a lista de skills a partir dos campos do formulário.

    Why: Os campos vêm como 'skills[]' e precisam ser filtrados
         para remover entradas vazias.
    """
    skills_raw = get_form_list(form, "skills[]")
    return [s.strip() for s in skills_raw if s.strip()]


def build_certificates(form) -> list[dict]:
    """
    Constrói a lista de certificates a partir dos campos do formulário.

    Why: Os campos vêm separados (cert_name[], cert_issuer[], etc.)
         e precisam ser agrupados em dicionários.
    """
    names = get_form_list(form, "cert_name[]")
    issuers = get_form_list(form, "cert_issuer[]")
    dates = get_form_list(form, "cert_date[]")
    urls = get_form_list(form, "cert_url[]")
    credential_ids = get_form_list(form, "cert_credential_id[]")

    certificates = []
    for i in range(len(names)):
        # Pula entradas vazias
        if not names[i].strip():
            continue
        certificates.append(
            {
                "name": names[i].strip(),
                "issuer": issuers[i].strip() if i < len(issuers) else "",
                "date": dates[i].strip() if i < len(dates) else "",
                "url": urls[i].strip() if i < len(urls) and urls[i].strip() else None,
                "credential_id": credential_ids[i].strip()
                if i < len(credential_ids) and credential_ids[i].strip()
                else None,
            }
        )
    return certificates


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

    # Campos estruturados (Work, Education, Certificates, Skills) - agora parseados do form
    profile.work_experience = build_work_experience(form)
    profile.education = build_education(form)
    profile.certificates = build_certificates(form)
    profile.skills = build_skills(form)

    session.add(profile)
    await session.commit()

    return RedirectResponse(url="/admin/profile", status_code=303)
