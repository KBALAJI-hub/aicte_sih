from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import bcrypt
from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from sqlmodel import Session, select

from app.database import get_session
from app.models import User

# JWT Secret and Configuration
SECRET_KEY = "aicte-hackathon-super-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # 8 hours session
COOKIE_NAME = "access_token"

# Template setup
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Router for Authentication
router = APIRouter(tags=["Authentication"])


# --- Password Hashing Utilities ---

def hash_password(password: str) -> str:
    """Hash plain password with bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


# --- JWT Token Utilities ---

def create_access_token(data: dict) -> str:
    """Create signed JWT token with expiration timestamp."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate JWT token."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


# --- Authentication & Role Dependencies ---

def get_current_user(
    request: Request,
    session: Session = Depends(get_session)
) -> User:
    """
    Dependency extracting JWT from cookie and fetching User from database.
    """
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in."
        )

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid token. Please log in again."
        )

    username: str = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials."
        )

    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found."
        )

    return user


def get_current_user_optional(
    request: Request,
    session: Session = Depends(get_session)
) -> Optional[User]:
    """
    Helper dependency to check logged-in user without throwing 401.
    """
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None

    payload = decode_access_token(token)
    if not payload:
        return None

    username = payload.get("sub")
    if not username:
        return None

    return session.exec(select(User).where(User.username == username)).first()


def require_role(*allowed_roles: str):
    """
    Dependency factory enforcing role-based access control (RBAC).
    Usage: Depends(require_role("AICTE_ADMIN", "INSTITUTION"))
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden. Access requires one of: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker


# --- Authentication Routes ---

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, session: Session = Depends(get_session)):
    """Render the login page."""
    user = get_current_user_optional(request, session)
    if user:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"request": request, "title": "Login | AICTE APAAR Platform", "error": None}
    )


@router.post("/login", response_class=HTMLResponse)
async def login_action(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session)
):
    """Authenticate user credentials and issue secure JWT cookie."""
    user = session.exec(select(User).where(User.username == username.strip())).first()

    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "request": request,
                "title": "Login | AICTE APAAR Platform",
                "error": "Invalid username or password. Please try again."
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Issue JWT token
    token = create_access_token({
        "sub": user.username,
        "role": user.role,
        "user_id": user.id,
        "full_name": user.full_name
    })

    # Redirect to home with cookie
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax"
    )
    return response


@router.get("/logout")
async def logout():
    """Clear session cookie and redirect to login."""
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key=COOKIE_NAME)
    return response
