"""
Authentication API endpoints v1.

Why: Endpoints de autenticação separados por versão,
     permitindo evolução sem quebrar clientes.

How: Usa AuthService para lógica de negócio,
     expõe endpoints RESTful para OAuth e login tradicional.
"""

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_session
from app.services.auth import AuthService

router = APIRouter()

# OAuth client configuration
oauth = OAuth()

if settings.GITHUB_CLIENT_ID:
    oauth.register(
        name="github",
        client_id=settings.GITHUB_CLIENT_ID,
        client_secret=settings.GITHUB_CLIENT_SECRET,
        access_token_url="https://github.com/login/oauth/access_token",
        access_token_params=None,
        authorize_url="https://github.com/login/oauth/authorize",
        authorize_params=None,
        api_base_url="https://api.github.com/",
        client_kwargs={"scope": "user:email"},
    )

# Cookie settings
COOKIE_MAX_AGE = 7 * 24 * 60 * 60  # 7 days


def _set_auth_cookie(response: Response, token: str) -> None:
    """
    Define cookie de autenticação na resposta.

    Why: Centraliza configuração de cookie para garantir
         consistência de segurança em todos os endpoints.
    """
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=settings.ENV == "production",  # HTTPS only em prod
    )


# ==========================================
# OAuth Endpoints
# ==========================================


@router.get("/login/{provider}")
async def oauth_login(provider: str, request: Request):
    """
    Inicia fluxo OAuth com provider especificado.

    Providers suportados: github, google (quando configurado)
    """
    # Dev bypass para desenvolvimento local
    if provider == "dev" and settings.ENV == "development":
        return RedirectResponse(url="/api/v1/auth/callback/dev")

    client = oauth.create_client(provider)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth provider '{provider}' not configured",
        )

    redirect_uri = request.url_for("oauth_callback", provider=provider)
    return await client.authorize_redirect(request, redirect_uri)


@router.get("/callback/{provider}", name="oauth_callback")
async def oauth_callback(
    provider: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """
    Callback OAuth - processa resposta do provider.

    Why: Cria ou atualiza usuário baseado nos dados do provider,
         e emite JWT para autenticação subsequente.
    """
    auth_service = AuthService(session)

    # Dev bypass
    if provider == "dev" and settings.ENV == "development":
        user_info = {
            "email": "dev@example.com",
            "name": "Dev User",
            "avatar_url": "https://avatars.githubusercontent.com/u/1?v=4",
            "id": "dev-123",
        }
    else:
        token = await oauth.create_client(provider).authorize_access_token(request)
        resp = await oauth.create_client(provider).get("user", token=token)
        user_info = resp.json()

    # Busca ou cria usuário
    email = user_info.get("email") or ""
    name = user_info.get("name") or user_info.get("login") or "Unknown"
    avatar_url = user_info.get("avatar_url")
    provider_id = str(user_info.get("id", ""))

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not provided by OAuth provider",
        )

    user = await auth_service.get_or_create_oauth_user(
        email=email,
        name=name,
        avatar_url=avatar_url,
        provider=provider,
        provider_id=provider_id,
    )

    # Gera token e redireciona
    access_token = auth_service.create_token_for_user(user)

    response = RedirectResponse(url="/")
    _set_auth_cookie(response, access_token)
    return response


# ==========================================
# Traditional Auth Endpoints
# ==========================================


@router.post("/register")
async def register(
    email: str = Form(...),
    password: str = Form(..., min_length=8),
    name: str = Form(..., min_length=2),
    session: AsyncSession = Depends(get_session),
):
    """
    Registra novo usuário com email e senha.

    Validações:
        - Email deve ser único
        - Senha mínimo 8 caracteres
        - Nome mínimo 2 caracteres
    """
    auth_service = AuthService(session)

    # Verifica se email já existe
    existing = await auth_service.get_user_by_email(email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Cria usuário
    user = await auth_service.create_user(
        email=email,
        name=name,
        password=password,
    )

    # Gera token e redireciona
    access_token = auth_service.create_token_for_user(user)

    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    _set_auth_cookie(response, access_token)
    return response


@router.post("/login")
async def login(
    email: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    """
    Login com email e senha.

    Returns:
        Redirect para home com cookie de autenticação
    """
    auth_service = AuthService(session)

    user = await auth_service.authenticate_user(email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    access_token = auth_service.create_token_for_user(user)

    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    _set_auth_cookie(response, access_token)
    return response


@router.get("/logout")
async def logout():
    """
    Logout - remove cookie de autenticação.
    """
    response = RedirectResponse(url="/")
    response.delete_cookie("access_token")
    return response


@router.get("/me")
async def get_current_user_info(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """
    Retorna informações do usuário autenticado.

    Returns:
        Dados públicos do usuário ou 401 se não autenticado
    """
    from app.core.deps import get_current_user_optional

    user = await get_current_user_optional(request, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "avatar_url": user.avatar_url,
        "is_admin": user.is_admin,
    }
