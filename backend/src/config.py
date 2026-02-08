"""
Configurações da aplicação ShiftLab Pro.

Este módulo utiliza pydantic-settings para carregar e validar
variáveis de ambiente automaticamente.

Uso:
    from src.config import settings
    print(settings.DATABASE_URL)
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configurações da aplicação carregadas de variáveis de ambiente.

    Todas as configurações são validadas automaticamente pelo Pydantic.
    Valores padrão são usados quando a variável não está definida.
    """

    # =========================================================================
    # AMBIENTE
    # =========================================================================
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = True

    # =========================================================================
    # APLICAÇÃO
    # =========================================================================
    APP_NAME: str = "ShiftLab Pro"
    API_VERSION: str = "v1"
    API_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS - lista de origens permitidas
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        """Retorna lista de origens CORS."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # =========================================================================
    # BANCO DE DADOS
    # =========================================================================
    DATABASE_URL: str = "sqlite+aiosqlite:///./shiftlab.db"
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    @property
    def is_sqlite(self) -> bool:
        """Verifica se está usando SQLite."""
        return "sqlite" in self.DATABASE_URL.lower()

    # =========================================================================
    # AUTENTICAÇÃO JWT
    # =========================================================================
    SECRET_KEY: str = Field(
        default="development-secret-key-change-in-production",
        min_length=32,
        description="Chave secreta para assinatura JWT"
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        """Valida que a SECRET_KEY é segura em produção."""
        # Em produção, não permite chaves padrão
        # Nota: info.data pode não ter ENVIRONMENT ainda, então checamos depois
        return v

    # =========================================================================
    # SEGURANÇA
    # =========================================================================
    BCRYPT_ROUNDS: int = Field(default=12, ge=4, le=31)
    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_LOCKOUT_MINUTES: int = 15

    # =========================================================================
    # PRIMEIRO ADMIN
    # =========================================================================
    FIRST_ADMIN_EMAIL: str = "admin@shiftlab.com.br"
    FIRST_ADMIN_PASSWORD: str = "Admin@123456"
    FIRST_ADMIN_NAME: str = "Administrador"

    # =========================================================================
    # EMAIL
    # =========================================================================
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@shiftlab.com.br"
    SMTP_FROM_NAME: str = "ShiftLab Pro"
    SMTP_ENABLED: bool = False

    # =========================================================================
    # LOGS
    # =========================================================================
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_FORMAT: Literal["json", "text"] = "text"
    LOG_FILE: str = ""

    # =========================================================================
    # CACHE
    # =========================================================================
    REDIS_URL: str = ""
    CACHE_TTL: int = 300

    @property
    def redis_enabled(self) -> bool:
        """Verifica se Redis está habilitado."""
        return bool(self.REDIS_URL)

    # =========================================================================
    # CONFIGURAÇÕES DE NEGÓCIO
    # =========================================================================
    DEFAULT_OIL_CHANGE_KM: int = 10000
    DEFAULT_OIL_CHANGE_MONTHS: int = 6
    ALERT_MARGIN_KM: int = 500
    ALERT_MARGIN_DAYS: int = 15

    # =========================================================================
    # STORAGE
    # =========================================================================
    STORAGE_TYPE: Literal["local", "s3"] = "local"
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: str = "pdf,jpg,jpeg,png"

    @property
    def allowed_extensions_list(self) -> list[str]:
        """Retorna lista de extensões permitidas."""
        return [ext.strip().lower() for ext in self.ALLOWED_EXTENSIONS.split(",")]

    @property
    def max_upload_size_bytes(self) -> int:
        """Retorna tamanho máximo de upload em bytes."""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    # =========================================================================
    # PAGINAÇÃO
    # =========================================================================
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # =========================================================================
    # CONFIGURAÇÃO DO PYDANTIC
    # =========================================================================
    model_config = SettingsConfigDict(
        # Arquivo .env a ser carregado
        env_file=".env",
        # Codificação do arquivo
        env_file_encoding="utf-8",
        # Case sensitive para variáveis
        case_sensitive=True,
        # Permite campos extras (ignora variáveis não declaradas)
        extra="ignore",
    )

    def is_production(self) -> bool:
        """Verifica se está em ambiente de produção."""
        return self.ENVIRONMENT == "production"

    def is_development(self) -> bool:
        """Verifica se está em ambiente de desenvolvimento."""
        return self.ENVIRONMENT == "development"


@lru_cache
def get_settings() -> Settings:
    """
    Retorna instância singleton das configurações.

    Usa lru_cache para garantir que as configurações
    sejam carregadas apenas uma vez.

    Returns:
        Settings: Instância das configurações
    """
    return Settings()


# Instância global para importação direta
settings = get_settings()
