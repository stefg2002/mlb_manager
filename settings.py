from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class DBSettings(BaseModel):
    url: str

class AuthSettings(BaseModel):
    secret_key: SecretStr
    algorithm: str
    access_token_expire_minutes: int

class Settings(BaseSettings):
    db: DBSettings
    auth: AuthSettings

    model_config = SettingsConfigDict(env_file=".env",env_file_encoding="utf-8", env_nested_delimiter="__")

settings = Settings()