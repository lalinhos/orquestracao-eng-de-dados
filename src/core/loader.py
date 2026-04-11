from typing import Any

from pymongo import MongoClient, UpdateOne
from pymongo.collection import Collection
from pymongo.errors import (
    ConfigurationError,
    ConnectionFailure,
    NetworkTimeout,
    OperationFailure,
    PyMongoError,
    ServerSelectionTimeoutError,
)

from src.config import settings
from src.utils import LoadingError, logger


class MongoLoader:
    """Responsável pela persistência dos dados tratados no MongoDB."""

    def __init__(self, client: MongoClient | None = None) -> None:
        """Inicializa o loader com cliente opcional para facilitar testes."""
        self.mongo_uri = settings.MONGO_URI
        self.db_name = settings.MONGO_DB_NAME
        self.collection_name = settings.MONGO_COLLECTION_NAME
        self.server_timeout_ms = settings.MONGO_SERVER_SELECTION_TIMEOUT_MS
        self.connect_timeout_ms = settings.MONGO_CONNECT_TIMEOUT_MS
        self.socket_timeout_ms = settings.MONGO_SOCKET_TIMEOUT_MS

        self.client = client
        self.collection: Collection[dict[str, Any]] | None = None
        self._owns_client = client is None

        logger.info(
            "Carregador Orion inicializado para {}.{}",
            self.db_name,
            self.collection_name,
        )

    def connect(self) -> None:
        """Abre conexão com o MongoDB e prepara a coleção alvo."""
        if self.collection is not None:
            return

        try:
            if self.client is None:
                self.client = MongoClient(
                    self.mongo_uri,
                    serverSelectionTimeoutMS=self.server_timeout_ms,
                    connectTimeoutMS=self.connect_timeout_ms,
                    socketTimeoutMS=self.socket_timeout_ms,
                    retryWrites=True,
                )

            logger.info("Validando conexão com MongoDB Atlas via ping.")
            self.client.admin.command("ping")

            self.collection = self.client[self.db_name][self.collection_name]
            self.collection.create_index("id", unique=True, name="uq_contract_id")

            logger.info(
                "Conexão com MongoDB estabelecida em {}.{}",
                self.db_name,
                self.collection_name,
            )

        except OperationFailure as exc:
            logger.error("Falha de autenticação/autorização no MongoDB: {}", exc)
            raise LoadingError(
                "Falha de autenticação/autorização no MongoDB Atlas. "
                "Verifique usuário, senha e permissões do Database User."
            ) from exc

        except ServerSelectionTimeoutError as exc:
            logger.error("Timeout ao localizar servidor MongoDB: {}", exc)
            raise LoadingError(
                "Timeout ao localizar o cluster MongoDB Atlas. "
                "Verifique Network Access, URI e status do cluster."
            ) from exc

        except NetworkTimeout as exc:
            logger.error("Timeout de rede/socket no MongoDB: {}", exc)
            raise LoadingError(
                "Timeout durante a comunicação com o MongoDB Atlas. "
                "Verifique conectividade, IP liberado e status do cluster."
            ) from exc

        except ConfigurationError as exc:
            logger.error("Erro de configuração da URI MongoDB: {}", exc)
            raise LoadingError(
                "A URI do MongoDB Atlas parece inválida. "
                "Revise o campo MONGO_URI no .env."
            ) from exc

        except ConnectionFailure as exc:
            logger.error("Falha de conexão com o MongoDB: {}", exc)
            raise LoadingError("Falha de conexão com o MongoDB Atlas.") from exc

        except PyMongoError as exc:
            logger.error("Erro PyMongo inesperado durante a conexão: {}", exc)
            raise LoadingError(f"Erro PyMongo durante a conexão: {exc}") from exc

    def close(self) -> None:
        """Fecha a conexão com o MongoDB quando o cliente pertence ao loader."""
        if self.client is not None and self._owns_client:
            self.client.close()
            logger.info("Conexão com o MongoDB fechada.")

    def load_contracts(self, contracts: list[dict[str, Any]]) -> dict[str, int]:
        """Realiza upsert em lote dos contratos tratados."""
        if not contracts:
            logger.info("Nenhum contrato recebido para carga.")
            return {
                "received": 0,
                "operations": 0,
                "inserted": 0,
                "updated": 0,
                "matched": 0,
            }

        if self.collection is None:
            self.connect()

        if self.collection is None:
            raise LoadingError("Coleção MongoDB não inicializada.")

        operations: list[UpdateOne] = []

        for contract in contracts:
            contract_id = contract.get("id")
            if not contract_id:
                logger.warning("Contrato ignorado na carga por ausência de id.")
                continue

            operations.append(
                UpdateOne(
                    {"id": contract_id},
                    {"$set": contract},
                    upsert=True,
                )
            )

        if not operations:
            logger.warning("Nenhuma operação válida foi gerada para carga.")
            return {
                "received": len(contracts),
                "operations": 0,
                "inserted": 0,
                "updated": 0,
                "matched": 0,
            }

        try:
            result = self.collection.bulk_write(operations, ordered=False)

            summary = {
                "received": len(contracts),
                "operations": len(operations),
                "inserted": result.upserted_count,
                "updated": result.modified_count,
                "matched": result.matched_count,
            }

            logger.info(
                "Carga concluída no MongoDB. Recebidos: {} | Operações: {} | Inseridos: {} | Atualizados: {}",
                summary["received"],
                summary["operations"],
                summary["inserted"],
                summary["updated"],
            )
            return summary

        except PyMongoError as exc:
            raise LoadingError("Erro ao executar a carga no MongoDB.") from exc