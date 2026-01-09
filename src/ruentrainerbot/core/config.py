from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """
    Класс конфигурации приложения.
    Используется для загрузки и валидации переменных окружения
    из файла .env
    """
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
    )

    token: str = Field(alias='TOKEN')
    dsn: str = Field(alias='DSN')
    debug: bool = Field(default=True, alias='DEBUG')
    log_level: str = Field(alias='LOG_LEVEL')

settings = Settings()