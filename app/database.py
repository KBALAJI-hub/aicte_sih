import os
import urllib.parse
from pathlib import Path
from dotenv import dotenv_values, load_dotenv
from sqlmodel import SQLModel, Session, create_engine
# Import models so SQLModel metadata registers all tables
import app.models  # noqa: F401

# Load environment variables from .env
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"

load_dotenv(dotenv_path=env_path)
raw_env = dotenv_values(dotenv_path=env_path) if env_path.exists() else {}

def get_database_url() -> str:
    # 1. Direct DATABASE_URL or database_url
    direct_url = raw_env.get("DATABASE_URL") or os.getenv("DATABASE_URL") or raw_env.get("database_url") or os.getenv("database_url")
    if direct_url:
        if direct_url.startswith("postgres://"):
            direct_url = direct_url.replace("postgres://", "postgresql+psycopg2://", 1)
        elif direct_url.startswith("postgresql://"):
            direct_url = direct_url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return direct_url


    # 2. Check for Supabase / Server configuration (.env file takes precedence over OS defaults)
    host = raw_env.get("Host") or os.getenv("Host") or raw_env.get("DB_HOST") or os.getenv("DB_HOST") or "localhost"
    port = raw_env.get("Port") or os.getenv("Port") or raw_env.get("DB_PORT") or os.getenv("DB_PORT") or "5432"
    dbname = raw_env.get("Database") or os.getenv("Database") or raw_env.get("DB_NAME") or os.getenv("DB_NAME") or "postgres"
    username = raw_env.get("Username") or raw_env.get("DB_USER") or os.getenv("DB_USER") or "postgres"
    password = raw_env.get("Password") or os.getenv("Password") or raw_env.get("DB_PASSWORD") or os.getenv("DB_PASSWORD") or ""
    
    # Check for SSL mode (e.g. require)
    ssl_mode = raw_env.get("SSL_MODE") or raw_env.get("SSL Mode") or os.getenv("SSL_MODE") or "require"


    if host:
        user_enc = urllib.parse.quote_plus(username)
        pwd_enc = urllib.parse.quote_plus(password)
        query_params = f"?sslmode={ssl_mode}" if ssl_mode and host != "localhost" else ""
        return f"postgresql+psycopg2://{user_enc}:{pwd_enc}@{host}:{port}/{dbname}{query_params}"

    # 3. Fallback to SQLite
    return "sqlite:///apaar.db"


database_url = get_database_url()

if database_url.startswith("sqlite"):
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
    # PostgreSQL engine with robust connection pooling
    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False
    )


def create_db_and_tables():
    """Create all registered tables in database if they don't exist."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency yielding a database session per request."""
    with Session(engine) as session:
        yield session

