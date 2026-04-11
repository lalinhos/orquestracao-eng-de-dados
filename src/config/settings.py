from datetime import datetime

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Armazena e valida as configurações globais da aplicação."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    MONGO_URI: str = Field(
        default="mongodb://localhost:27017",
        description="URI de conexão com o MongoDB.",
    )
    MONGO_DB_NAME: str = Field(
        default="orion",
        description="Nome do banco de dados MongoDB.",
    )
    MONGO_COLLECTION_NAME: str = Field(
        default="contracts",
        description="Nome da coleção MongoDB para contratos.",
    )
    MONGO_SERVER_SELECTION_TIMEOUT_MS: int = Field(
        default=10000,
        ge=1000,
        description="Timeout de seleção do servidor MongoDB em milissegundos.",
    )
    MONGO_CONNECT_TIMEOUT_MS: int = Field(
        default=10000,
        ge=1000,
        description="Timeout de conexão TCP/TLS com MongoDB em milissegundos.",
    )
    MONGO_SOCKET_TIMEOUT_MS: int = Field(
        default=20000,
        ge=1000,
        description="Timeout de leitura/escrita do socket MongoDB em milissegundos.",
    )

    PNCP_BASE_URL: str = Field(
        default="https://pncp.gov.br/api/consulta",
        description="URL base da API do PNCP.",
    )
    PNCP_PAGE_SIZE: int = Field(
        default=50,
        ge=1,
        le=50,
        description="Quantidade de registros por página.",
    )
    PNCP_TIMEOUT: int = Field(
        default=60,
        ge=1,
        description="Timeout da requisição HTTP em segundos.",
    )
    PNCP_MAX_RETRIES: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Quantidade máxima de tentativas por requisição.",
    )

    ETL_DATE_INITIAL: str | None = Field(
        default=None,
        description="Data inicial no formato YYYYMMDD ou YYYY-MM-DD.",
    )
    ETL_DATE_FINAL: str | None = Field(
        default=None,
        description="Data final no formato YYYYMMDD ou YYYY-MM-DD.",
    )
    ETL_UF_FILTER: str | None = Field(
        default=None,
        description="Filtro opcional por UF.",
    )
    ETL_MODALITY_CODE: int | None = Field(
        default=None,
        description="Filtro opcional por código de modalidade.",
    )
    ETL_MAX_PAGES: int | None = Field(
        default=None,
        ge=1,
        description="Limite opcional de páginas por execução.",
    )

    @field_validator("ETL_DATE_INITIAL", "ETL_DATE_FINAL", mode="before")
    @classmethod
    def normalize_date(cls, value: str | None) -> str | None:
        """Normaliza datas para o formato YYYYMMDD."""
        if value in (None, ""):
            return None

        if isinstance(value, str):
            for fmt in ("%Y%m%d", "%Y-%m-%d"):
                try:
                    return datetime.strptime(value, fmt).strftime("%Y%m%d")
                except ValueError:
                    continue

        raise ValueError("A data deve estar no formato YYYYMMDD ou YYYY-MM-DD.")

    @field_validator("ETL_UF_FILTER", mode="before")
    @classmethod
    def normalize_uf(cls, value: str | None) -> str | None:
        """Normaliza a UF para letras maiúsculas."""
        if value in (None, ""):
            return None

        normalized = str(value).strip().upper()
        if len(normalized) != 2:
            raise ValueError("ETL_UF_FILTER deve conter uma UF válida com 2 caracteres.")
        return normalized

    @field_validator(
        "ETL_MODALITY_CODE",
        "ETL_MAX_PAGES",
        "MONGO_SERVER_SELECTION_TIMEOUT_MS",
        "MONGO_CONNECT_TIMEOUT_MS",
        "MONGO_SOCKET_TIMEOUT_MS",
        mode="before",
    )
    @classmethod
    def blank_to_none_for_integers(cls, value: int | str | None) -> int | None:
        """Converte strings vazias em None para campos inteiros opcionais."""
        if value in (None, ""):
            return None
        return int(value)


settings = Settings()
