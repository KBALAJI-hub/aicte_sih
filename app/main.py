from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Initialize FastAPI application
app = FastAPI(
    title="APAAR ID Verification Platform",
    description="AICTE Student Data Management and Verification System",
    version="1.0.0",
)

# Resolve path to the templates folder
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Renders the base landing page using Jinja2 and Tailwind CSS.
    """
    return templates.TemplateResponse(
        request=request,
        name="base.html",
        context={"request": request, "title": "Home | AICTE APAAR Platform"}
    )


@app.get("/health")
async def health_check():
    """
    Basic health check endpoint returning API status.
    """
    return {"status": "ok", "platform": "AICTE APAAR Verification"}
