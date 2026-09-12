from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Gchy"

    DATABASE_URL: str
    SECRET_KEY: str
    DEBUG: bool = True

    admin_username: str
    admin_password_hash: str
    frontend_origin: str

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


settings = Settings()