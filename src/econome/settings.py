from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mistral_key: str = ""
    fal_key: str = ""
    mistral_model: str = "mistral-large-latest"
    flux_model: str = "fal-ai/flux-pro/v1.1-ultra"
    vision_model: str = "pixtral-12b-2409"
    MONGO_URL: str = "mongodb://root:example@mongodb:27017"

    class Config:
        env_file = ".env"


settings = Settings()
