from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configurações globais da aplicação Orion.
    Os valores são carregados prioritariamente de variáveis de ambiente ou do arquivo .env.
    """

    # MongoDB Atlas
    MONGO_URI: str
    MONGO_DB_NAME: str
    MONGO_COLLECTION_NAME: str

    # API PNCP
    PNCP_BASE_URL: str = "https://pncp.gov.br/api/consulta"
    PNCP_PAGE_SIZE: int = 50
    PNCP_TIMEOUT: int = 60

    # Parâmetros do Pipeline
    ETL_DATE_INITIAL: str | None = None
    ETL_DATE_FINAL: str | None = None
    ETL_UF_FILTER: str | None = None
    ETL_MODALITY_CODE: int | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
