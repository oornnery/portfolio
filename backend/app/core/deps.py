from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_session
from app.models.user import User
from app.core.security import decode_access_token
from typing import Optional
import uuid

async def get_current_user_optional(request: Request, session: AsyncSession = Depends(get_session)) -> Optional[User]:
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    try:
        scheme, _, param = token.partition(" ")
        payload = decode_access_token(param)
        if not payload:
            return None
        user_id = payload.get("sub")
        if not user_id:
            return None
            
        user = await session.get(User, uuid.UUID(user_id))
        return user
    except Exception:
        return None
