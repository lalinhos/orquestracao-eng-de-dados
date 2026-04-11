from typing import Any, Dict, List, Optional
from loguru import logger
from pymongo import MongoClient, UpdateOne
from pymongo.errors import ConnectionFailure, PyMongoError

from src.config.settings import settings
from src.utils.exceptions import LoadingError


class MongoLoader:
    """
    Componente responsável pela persistência dos dados no MongoDB Atlas.
    Utiliza operações de bulk_write para eficiência e upsert para evitar duplicatas.
    """

    def __init__(self):
        self.mongo_uri = settings.MONGO_URI
        self.db_name = settings.MONGO_DB_NAME
        self.collection_name = settings.MONGO_COLLECTION_NAME
        self.client: Optional[MongoClient] = None
        self.collection = None
        logger.info(f"Carregador Orion inicializado para {self.db_name}.{self.collection_name}")

    def connect(self):
        """Estabelece conexão com o cluster MongoDB Atlas."""
        try:
            self.client = MongoClient(self.mongo_uri)
            self.client.admin.command("ping")
            self.collection = self.client[self.db_name][self.collection_name]
            logger.info("Conexão estabelecida com sucesso ao MongoDB Atlas.")
        except ConnectionFailure as e:
            logger.error(f"Falha na conexão com o MongoDB: {e}")
            raise LoadingError(f"Falha na conexão com o MongoDB: {e}")
        except PyMongoError as e:
            logger.error(f"Erro PyMongo inesperado durante a conexão: {e}")
            raise LoadingError(f"Erro PyMongo durante a conexão: {e}")

    def close(self):
        """Fecha a conexão com o MongoDB."""
        if self.client:
            self.client.close()
            logger.info("Conexão com o MongoDB fechada.")

    def load_contracts(self, contracts: List[Dict[str, Any]]):
        """Carrega os contratos transformados para o MongoDB Atlas."""
        if not contracts:
            logger.info("Nenhum contrato para carregar.")
            return

        if not self.collection:
            self.connect()

        try:
            # Upsert baseado no 'id' para evitar duplicatas e permitir atualizações
            operations = [
                UpdateOne({"id": contract["id"]}, {"$set": contract}, upsert=True)
                for contract in contracts
            ]
            result = self.collection.bulk_write(operations)
            logger.info(f"Carga concluída: {result.upserted_count} novos e {result.modified_count} atualizados.")
        except PyMongoError as e:
            logger.error(f"Erro ao carregar contratos no MongoDB: {e}")
            raise LoadingError(f"Erro ao carregar contratos no MongoDB: {e}")
        except Exception as e:
            logger.error(f"Erro inesperado durante o carregamento: {e}")
            raise LoadingError(f"Erro inesperado durante o carregamento: {e}")
