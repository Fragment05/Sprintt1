from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "FriendlyEats FastAPI"
    ENVIRONMENT: str = "local"
    # Un ID "demo-*" permite usar el emulador sin un proyecto real de Firebase.
    FIREBASE_PROJECT_ID: str = "demo-friendlyeats"
    FIREBASE_CREDENTIALS_PATH: str | None = None
    FIRESTORE_EMULATOR_HOST: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
