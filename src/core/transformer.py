from typing import Any, Dict, List
from loguru import logger
from pydantic import ValidationError

from src.models.contract import Contract
from src.utils.exceptions import TransformationError


class PncpTransformer:
    """
    Componente responsável pela transformação e validação dos dados brutos.
    Utiliza Pydantic para garantir que apenas dados válidos sejam processados.
    """

    def __init__(self):
        logger.info("Transformador Orion inicializado.")

    def transform_contracts(self, raw_contracts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Valida e normaliza a lista de contratos brutos."""
        transformed_contracts = []
        for i, raw_contract in enumerate(raw_contracts):
            try:
                # Validação e mapeamento automático via Pydantic
                contract = Contract(**raw_contract)
                transformed_contracts.append(contract.model_dump(by_alias=False))
            except ValidationError as e:
                logger.warning(f"Contrato inválido no índice {i} (pulando): {e}")
            except Exception as e:
                logger.error(f"Erro inesperado na transformação do registro {i}: {e}")
                raise TransformationError(f"Erro na transformação: {e}")

        logger.info(f"Transformação concluída. {len(transformed_contracts)} de {len(raw_contracts)} contratos válidos.")
        return transformed_contracts
