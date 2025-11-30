"""
Profile service for user profile/resume management.

Why: Centraliza operações de perfil, incluindo
     validações e transformações de dados estruturados.

How: Encapsula lógica de perfil usado em about page
     e admin panel.
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.profile import Profile


class ProfileService:
    """
    Serviço para operações de perfil do usuário.

    Why: O perfil contém dados estruturados (work experience,
         education, skills) que precisam de tratamento especial.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_profile_by_user_id(self, user_id: UUID) -> Profile | None:
        """Busca perfil pelo ID do usuário."""
        query = select(Profile).where(Profile.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_main_profile(self) -> Profile | None:
        """
        Busca o perfil principal do site.

        Why: Em um portfolio pessoal, geralmente há apenas um perfil
             principal que é exibido na página About.
        """
        query = select(Profile).limit(1)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_or_create_profile(self, user_id: UUID) -> Profile:
        """
        Busca ou cria um perfil para o usuário.

        Why: Garante que todo usuário admin tenha um perfil,
             criando um vazio se não existir.
        """
        profile = await self.get_profile_by_user_id(user_id)

        if not profile:
            profile = Profile(user_id=user_id)
            self.session.add(profile)
            await self.session.commit()
            await self.session.refresh(profile)

        return profile

    async def update_profile(
        self,
        profile: Profile,
        *,
        name: str | None = None,
        location: str | None = None,
        short_bio: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        website: str | None = None,
        github: str | None = None,
        linkedin: str | None = None,
        twitter: str | None = None,
        about_markdown: str | None = None,
        work_experience: list | None = None,
        education: list | None = None,
        skills: list | None = None,
    ) -> Profile:
        """
        Atualiza campos do perfil.

        Why: Aceita campos opcionais para permitir atualizações
             parciais sem sobrescrever dados existentes.
        """
        if name is not None:
            profile.name = name
        if location is not None:
            profile.location = location
        if short_bio is not None:
            profile.short_bio = short_bio
        if email is not None:
            profile.email = email
        if phone is not None:
            profile.phone = phone
        if website is not None:
            profile.website = website
        if github is not None:
            profile.github = github
        if linkedin is not None:
            profile.linkedin = linkedin
        if twitter is not None:
            profile.twitter = twitter
        if about_markdown is not None:
            profile.about_markdown = about_markdown
        if work_experience is not None:
            profile.work_experience = work_experience
        if education is not None:
            profile.education = education
        if skills is not None:
            profile.skills = skills

        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile
