import os

from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is required")

if not DATABASE_URL.startswith("postgresql+psycopg://"):
    raise RuntimeError(
        "DATABASE_URL must use the postgresql+psycopg:// SQLAlchemy dialect"
    )

# Avoid using os.environ["DEEPSEEK_API_KEY"]
# get deepseek api key from environment variable, raise error if not set
def get_deepseek_api_key() -> str:
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        raise RuntimeError("DEEPSEEK_API_KEY is not set (add it to backend/.env)")
    return key