from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "REEL_AI-MVP"
    JWT_SECRET: str = "CHANGE_ME_SUPER_SECRET"
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_MINUTES: int = 60 * 24 * 7  # 7 days

    DB_URL: str = "sqlite:///./app.db"

    STORAGE_ROOT: str = "./app/storage"
    UPLOADS_DIR: str = "./app/storage/uploads"
    OUTPUTS_DIR: str = "./app/storage/outputs"
    ASSETS_DIR: str = "./app/storage/assets"

    DEFAULT_BG_IMAGE: str = "./app/storage/assets/bg.jpg"

    # Credits
    STARTING_CREDITS: int = 5
    VIDEO_COST_CREDITS: int = 1

    # TTS (Edge-TTS voices; change anytime)
    EDGE_TTS_VOICE: str = "en-IN-NeerjaNeural"  # good Indian English
    EDGE_TTS_RATE: str = "+0%"
    EDGE_TTS_PITCH: str = "+0Hz"

settings = Settings()
