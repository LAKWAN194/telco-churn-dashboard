import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


def _build_database_url() -> str:
    """
    Build the SQLAlchemy connection URL from the DB_* variables in .env.

    Returns:
        str: The connection URL. DATABASE_URL wins if it is set, which lets
        the tests point the app at a throwaway database.
    """
    if os.getenv("DATABASE_URL"):
        return os.environ["DATABASE_URL"]

    return (
        f"postgresql+psycopg2://{os.getenv('DB_USER', 'postgres')}:"
        f"{os.getenv('DB_PASSWORD', '')}@"
        f"{os.getenv('DB_HOST', 'localhost')}:"
        f"{os.getenv('DB_PORT', '5432')}/"
        f"{os.getenv('DB_NAME', 'telco_churn')}")


def _split_origins() -> list[str]:
    origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    return [origin.strip() for origin in origins.split(",") if origin.strip()]


@dataclass(frozen=True)
class Settings:
    database_url: str = field(default_factory=_build_database_url)
    model_path: str = field(
        default_factory=lambda: os.getenv("MODEL_PATH", "./models/artifacts/churn_model.joblib")
    )
    # The React dev server, which runs on a different port from the API
    cors_origins: list[str] = field(default_factory=_split_origins)


settings = Settings()
