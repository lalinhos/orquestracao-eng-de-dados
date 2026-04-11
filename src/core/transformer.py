from typing import Any

from pydantic import ValidationError

from src.models import Contract
from src.utils import TransformationError, logger


class PncpTransformer:
    """Responsável por validar e normalizar os dados extraídos."""

    def transform_contract(self, raw_contract: dict[str, Any]) -> dict[str, Any] | None:
        """Transforma um único contrato bruto em um dicionário validado."""
        try:
            contract = Contract.model_validate(raw_contract)
            return contract.model_dump()
        except ValidationError as exc:
            logger.warning("Contrato inválido ignorado: {}", exc)
            return None
        except Exception as exc:
            raise TransformationError("Erro inesperado ao transformar contrato.") from exc

    def transform_contracts(self, raw_contracts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Transforma uma lista de contratos brutos em contratos normalizados."""
        transformed_contracts: list[dict[str, Any]] = []
        invalid_count = 0

        for raw_contract in raw_contracts:
            transformed_contract = self.transform_contract(raw_contract)
            if transformed_contract is None:
                invalid_count += 1
                continue

            transformed_contracts.append(transformed_contract)

        logger.info(
            "Transformação concluída. Válidos: {} | Inválidos: {} | Total: {}",
            len(transformed_contracts),
            invalid_count,
            len(raw_contracts),
        )
        return transformed_contracts