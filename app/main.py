from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import markdown
from datetime import datetime

app = FastAPI(title="Portfolio Jinja2+HTMX")

# Configuração de Arquivos Estáticos e Templates
# Mount static files. Assuming running from backend/ directory.
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# --- DADOS MOCKADOS (Simulando Banco de Dados/GitHub) ---

USER_DATA = {
    "name": "Fabio Souza",
    "role": "Software Engineer & VoIP Specialist",
    "location": "São Paulo, Brazil",
    "bio": "Experienced telecommunications engineer with a strong focus on voice and data services. Specialized in SIP, Python, and DevOps.",
    "social": {
        "github": "https://github.com/oornnery",
        "linkedin": "https://linkedin.com/in/fabiohcsouza",
        "email": "mailto:fabiohcsouza@outlook.com.br"
    },
    "skills": ["Python", "FastAPI", "React", "SIP", "DevOps", "Zabbix", "Grafana"]
}

PROJECTS = [
    {"id": 1, "title": "SIP Trunk Monitor", "tech": ["Python", "Zabbix"], "desc": "Automated monitoring system for SIP Trunks and VoIP services."},
    {"id": 2, "title": "Portfolio V2", "tech": ["FastAPI", "HTMX", "Tailwind"], "desc": "Modern server-side rendered portfolio with SPA-like experience."}
]

# Simulando posts que viriam do GitHub API
BLOG_POSTS = [
    {
        "slug": "ola-mundo",
        "title": "Olá Mundo com FastAPI e HTMX",
        "date": "2025-11-26",
        "content": "# Olá Mundo\n\nEste é um post escrito em **Markdown** renderizado pelo Jinja2.",
        "tags": ["python", "htmx"]
    },
    {
        "slug": "seguranca-osint",
        "title": "Segurança e OSINT em Portfólios",
        "date": "2025-11-25",
        "content": "## Protegendo seus dados\n\nNunca exponha seu endereço real no footer...",
        "tags": ["security", "osint"]
    }
]

# --- ROTAS DA LANDING PAGE ---

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("pages/home.html", {
        "request": request,
        "user": USER_DATA,
        "projects": PROJECTS,
        "posts": BLOG_POSTS[:3], # Show recent posts on home
        "year": datetime.now().year
    })

# --- ROTAS DO BLOG ---

@app.get("/blog", response_class=HTMLResponse)
async def blog_list(request: Request):
    # Aqui você chamaria: github_service.get_all_posts()
    return templates.TemplateResponse("blog/list.html", {
        "request": request,
        "posts": BLOG_POSTS,
        "year": datetime.now().year
    })

@app.get("/blog/{slug}", response_class=HTMLResponse)
async def blog_detail(request: Request, slug: str):
    # Busca o post pelo slug
    post = next((p for p in BLOG_POSTS if p["slug"] == slug), None)
    if not post:
        raise HTTPException(status_code=404, detail="Post não encontrado")
    
    # Converte Markdown para HTML
    html_content = markdown.markdown(post["content"])
    
    return templates.TemplateResponse("blog/detail.html", {
        "request": request, 
        "post": post, 
        "content": html_content,
        "year": datetime.now().year
    })
