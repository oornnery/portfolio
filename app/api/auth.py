from fastapi import APIRouter, Depends, Request, Response, Form, HTTPException
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.config import settings
from app.db import get_session
from app.models.user import User
from app.core.security import create_access_token, get_password_hash, verify_password
from datetime import timedelta, datetime, timezone

router = APIRouter(prefix="/auth", tags=["Auth"])

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


@router.get("/login/{provider}")
async def login(provider: str, request: Request):
    if provider == "dev" and settings.ENV == "development":
        # Dev login bypass
        return RedirectResponse(url="/api/auth/callback/dev")

    client = oauth.create_client(provider)
    if not client:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"OAuth provider '{provider}' not configured")

    redirect_uri = request.url_for("auth_callback", provider=provider)
    return await client.authorize_redirect(request, redirect_uri)


@router.get("/callback/{provider}", name="auth_callback")
async def auth_callback(
    provider: str,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session),
):
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

    # Find or create user
    query = select(User).where(User.email == user_info.get("email"))
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            email=user_info.get("email"),
            name=user_info.get("name") or user_info.get("login"),
            avatar_url=user_info.get("avatar_url"),
            provider=provider,
            provider_id=str(user_info.get("id")),
        )
        session.add(user)
    else:
        user.last_login = datetime.now(timezone.utc)
        user.avatar_url = user_info.get("avatar_url")
        session.add(user)

    await session.commit()
    await session.refresh(user)

    # Create JWT
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=timedelta(days=7)
    )

    # Set cookie
    response = RedirectResponse(url="/")
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=7 * 24 * 60 * 60,
        samesite="lax",
    )
    return response


@router.get("/logout")
async def logout(response: Response):
    response = RedirectResponse(url="/")
    response.delete_cookie("access_token")
    return response


@router.post("/register")
async def register(
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    name: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    # Check if user exists
    query = select(User).where(User.email == email)
    result = await session.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    hashed_pw = get_password_hash(password)
    user = User(
        email=email,
        name=name,
        hashed_password=hashed_pw,
        provider="email",
        provider_id=email,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    # Login (create token)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=timedelta(days=7)
    )

    # Set cookie
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=7 * 24 * 60 * 60,
        samesite="lax",
    )
    return response


@router.post("/login")
async def login_post(
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    query = select(User).where(User.email == email)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user or not user.hashed_password or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    user.last_login = datetime.now(timezone.utc)
    session.add(user)
    await session.commit()

    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=timedelta(days=7)
    )

    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=7 * 24 * 60 * 60,
        samesite="lax",
    )
    return response
