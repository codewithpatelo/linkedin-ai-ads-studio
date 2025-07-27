import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # LangSmith Configuration
    LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    LANGCHAIN_ENDPOINT = os.getenv(
        "LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com"
    )
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
    LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "linkedin-ads-generator")

    # FastAPI Configuration
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))

    # Image Generation Settings
    MAX_IMAGES_PER_REQUEST = 5
    DEFAULT_IMAGE_SIZE = "1024x1024"
    SUPPORTED_IMAGE_FORMATS = ["png", "jpg", "jpeg"]


settings = Settings()
