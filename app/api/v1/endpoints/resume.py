"""
Resume PDF generation endpoint.

Why: Fornece uma rota para gerar e baixar o currículo em PDF,
     permitindo que visitantes baixem o currículo formatado.

How: Usa WeasyPrint para converter HTML em PDF com estilos customizados.
"""

from io import BytesIO

import markdown
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db import get_session
from app.models.profile import Profile

router = APIRouter(prefix="/resume", tags=["resume"])


def generate_resume_html(profile: Profile, about_html: str) -> str:
    """
    Gera HTML do currículo para conversão em PDF.

    Why: Cria um HTML limpo e estilizado que será convertido em PDF,
         com estilos inline para garantir consistência.
    """
    work_experience_html = ""
    if profile.work_experience:
        work_items = ""
        for exp in profile.work_experience:
            work_items += f"""
            <div class="experience-item">
                <div class="experience-header">
                    <div>
                        <h3>{exp.get("title", "")}</h3>
                        <p class="company">{exp.get("company", "")} • {exp.get("location", "")}</p>
                    </div>
                    <span class="date">{exp.get("start_date", "")} - {exp.get("end_date", "Present")}</span>
                </div>
                <p class="description">{exp.get("description", "")}</p>
            </div>
            """
        work_experience_html = f"""
        <section>
            <h2>Work Experience</h2>
            {work_items}
        </section>
        """

    education_html = ""
    if profile.education:
        edu_items = ""
        for edu in profile.education:
            edu_items += f"""
            <div class="education-item">
                <div class="education-header">
                    <div>
                        <h3>{edu.get("school", "")}</h3>
                        <p class="degree">{edu.get("degree", "")}</p>
                    </div>
                    <span class="date">{edu.get("start_date", "")} - {edu.get("end_date", "")}</span>
                </div>
            </div>
            """
        education_html = f"""
        <section>
            <h2>Education</h2>
            {edu_items}
        </section>
        """

    skills_html = ""
    if profile.skills:
        skills_tags = " ".join(
            [f'<span class="skill-tag">{skill}</span>' for skill in profile.skills]
        )
        skills_html = f"""
        <section>
            <h2>Skills</h2>
            <div class="skills-grid">{skills_tags}</div>
        </section>
        """

    contact_info = []
    if profile.email:
        contact_info.append(f'<a href="mailto:{profile.email}">{profile.email}</a>')
    if profile.phone:
        contact_info.append(profile.phone)
    if profile.website:
        contact_info.append(f'<a href="{profile.website}">{profile.website}</a>')
    if profile.github:
        contact_info.append(
            f'<a href="https://github.com/{profile.github}">github.com/{profile.github}</a>'
        )
    if profile.linkedin:
        contact_info.append(
            f'<a href="https://linkedin.com/in/{profile.linkedin}">linkedin.com/in/{profile.linkedin}</a>'
        )

    contact_html = " • ".join(contact_info) if contact_info else ""

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{profile.name} - Resume</title>
        <style>
            @page {{
                size: A4;
                margin: 1.5cm 2cm;
            }}
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 10pt;
                line-height: 1.5;
                color: #1a1a1a;
                background: white;
            }}
            
            .container {{
                max-width: 100%;
            }}
            
            /* Header */
            header {{
                margin-bottom: 24px;
                padding-bottom: 16px;
                border-bottom: 2px solid #e5e7eb;
            }}
            
            h1 {{
                font-size: 24pt;
                font-weight: 700;
                color: #111;
                margin-bottom: 4px;
            }}
            
            .title {{
                font-size: 12pt;
                color: #4b5563;
                margin-bottom: 8px;
            }}
            
            .location {{
                font-size: 10pt;
                color: #6b7280;
                margin-bottom: 8px;
            }}
            
            .contact {{
                font-size: 9pt;
                color: #374151;
            }}
            
            .contact a {{
                color: #2563eb;
                text-decoration: none;
            }}
            
            /* Sections */
            section {{
                margin-bottom: 20px;
            }}
            
            h2 {{
                font-size: 14pt;
                font-weight: 600;
                color: #111;
                margin-bottom: 12px;
                padding-bottom: 4px;
                border-bottom: 1px solid #e5e7eb;
            }}
            
            /* About */
            .about-content {{
                font-size: 10pt;
                color: #374151;
            }}
            
            .about-content h1, .about-content h2, .about-content h3 {{
                font-size: 11pt;
                color: #111;
                margin-top: 12px;
                margin-bottom: 6px;
                border: none;
                padding: 0;
            }}
            
            .about-content ul, .about-content ol {{
                margin-left: 20px;
                margin-bottom: 8px;
            }}
            
            .about-content li {{
                margin-bottom: 2px;
            }}
            
            .about-content strong {{
                color: #111;
            }}
            
            .about-content code {{
                background: #f3f4f6;
                padding: 1px 4px;
                border-radius: 3px;
                font-size: 9pt;
            }}
            
            /* Experience */
            .experience-item, .education-item {{
                margin-bottom: 16px;
            }}
            
            .experience-header, .education-header {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 4px;
            }}
            
            .experience-item h3, .education-item h3 {{
                font-size: 11pt;
                font-weight: 600;
                color: #111;
            }}
            
            .company, .degree {{
                font-size: 10pt;
                color: #4b5563;
            }}
            
            .date {{
                font-size: 9pt;
                color: #6b7280;
                white-space: nowrap;
            }}
            
            .description {{
                font-size: 10pt;
                color: #374151;
                margin-top: 4px;
            }}
            
            /* Skills */
            .skills-grid {{
                display: flex;
                flex-wrap: wrap;
                gap: 6px;
            }}
            
            .skill-tag {{
                display: inline-block;
                background: #f3f4f6;
                color: #374151;
                padding: 4px 10px;
                border-radius: 4px;
                font-size: 9pt;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>{profile.name}</h1>
                <p class="title">{profile.short_bio}</p>
                <p class="location">{profile.location}</p>
                <p class="contact">{contact_html}</p>
            </header>
            
            <section>
                <h2>About</h2>
                <div class="about-content">
                    {about_html}
                </div>
            </section>
            
            {work_experience_html}
            {education_html}
            {skills_html}
        </div>
    </body>
    </html>
    """
    return html


@router.get("/pdf")
async def download_resume_pdf(
    session: AsyncSession = Depends(get_session),
):
    """
    Gera e retorna o currículo em PDF.

    Returns:
        StreamingResponse: PDF do currículo para download.
    """
    # Busca o profile
    result = await session.execute(select(Profile).limit(1))
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    # Renderiza markdown para HTML
    about_html = ""
    if profile.about_markdown:
        about_html = markdown.markdown(
            profile.about_markdown,
            extensions=["fenced_code", "codehilite", "tables", "nl2br"],
        )

    # Gera HTML do currículo
    html_content = generate_resume_html(profile, about_html)

    # Tenta usar WeasyPrint, se não disponível usa fallback
    try:
        from weasyprint import HTML

        pdf_buffer = BytesIO()
        HTML(string=html_content).write_pdf(pdf_buffer)
        pdf_buffer.seek(0)

        filename = f"{profile.name.replace(' ', '_')}_Resume.pdf"

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
            },
        )
    except ImportError:
        # Fallback: retorna HTML para o usuário imprimir como PDF
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="PDF generation requires WeasyPrint. Please use browser print (Ctrl+P) to save as PDF.",
        )


@router.get("/html")
async def get_resume_html(
    session: AsyncSession = Depends(get_session),
):
    """
    Retorna o currículo em HTML formatado para impressão.
    Útil como fallback quando WeasyPrint não está disponível.
    """
    from fastapi.responses import HTMLResponse

    result = await session.execute(select(Profile).limit(1))
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    about_html = ""
    if profile.about_markdown:
        about_html = markdown.markdown(
            profile.about_markdown,
            extensions=["fenced_code", "codehilite", "tables", "nl2br"],
        )

    html_content = generate_resume_html(profile, about_html)

    return HTMLResponse(content=html_content)
