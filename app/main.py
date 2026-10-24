from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from app.auth import get_current_user_optional, router as auth_router
from app.database import create_db_and_tables, get_session
from app.routers.aicte import router as aicte_router
from app.routers.api import router as api_router
from app.routers.institution import router as institution_router
from app.routers.verify import router as verify_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database and tables on startup
    create_db_and_tables()
    yield


# Initialize FastAPI application
app = FastAPI(
    title="AICTE APAAR ID Verification Platform",
    description="Unified Student Data Management, Compliance, and Credential Verification Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Directories configuration
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Mount static files folder
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Register feature routers
app.include_router(auth_router)
app.include_router(institution_router)
app.include_router(aicte_router)
app.include_router(verify_router)
app.include_router(api_router)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, session: Session = Depends(get_session)):
    """
    Renders the platform landing page with role options and session state.
    """
    user = get_current_user_optional(request, session)
    return templates.TemplateResponse(
        request=request,
        name="base.html",
        context={"request": request, "title": "Home | AICTE APAAR Platform", "user": user}
    )


@app.get("/health")
async def health_check():
    """
    Basic health check endpoint returning API operational status.
    """
    return {"status": "ok", "platform": "AICTE APAAR Verification"}
