import requests
from datetime import datetime, timedelta
from typing import Any, Dict, List
from loguru import logger

from src.config.settings import settings
from src.utils.exceptions import ExtractionError


class PncpExtractor:
    """
    Componente responsável pela extração de dados da API do PNCP.
    Gerencia paginação e filtros de data/UF.
    """

    def __init__(self):
        self.base_url = settings.PNCP_BASE_URL
        self.page_size = settings.PNCP_PAGE_SIZE
        self.timeout = settings.PNCP_TIMEOUT
        logger.info(f"Extrator Orion inicializado para {self.base_url}")

    def _get_params(self, page: int) -> Dict[str, Any]:
        """Gera os parâmetros de consulta para a API."""
        params = {
            "pagina": page,
            "tamanhoPagina": self.page_size,
        }

        # Lógica de datas padrão (ontem -> hoje)
        hoje = datetime.now()
        params["dataInicial"] = settings.ETL_DATE_INITIAL or (hoje - timedelta(days=1)).strftime("%Y%m%d")
        params["dataFinal"] = settings.ETL_DATE_FINAL or hoje.strftime("%Y%m%d")

        if settings.ETL_UF_FILTER:
            params["uf"] = settings.ETL_UF_FILTER
        if settings.ETL_MODALITY_CODE:
            params["codigoModalidadeContratacao"] = settings.ETL_MODALITY_CODE

        return params

    def extract_contracts(self) -> List[Dict[str, Any]]:
        """Executa a extração completa percorrendo as páginas disponíveis."""
        all_contracts = []
        page = 1
        total_pages = 1

        logger.info("Iniciando extração de contratos...")

        while page <= total_pages:
            try:
                params = self._get_params(page)
                response = requests.get(
                    f"{self.base_url}/v1/contratacoes/publicacao",
                    params=params,
                    timeout=self.timeout,
                )
                
                if response.status_code == 204:
                    logger.info(f"Fim dos dados na página {page} (HTTP 204).")
                    break
                
                response.raise_for_status()
                data = response.json()
                
                contracts = data.get("data", [])
                if not contracts:
                    break

                all_contracts.extend(contracts)
                
                # Atualiza o total de páginas na primeira iteração
                if page == 1:
                    total_pages = data.get("totalPaginas", 1)
                    logger.info(f"Total de páginas detectadas: {total_pages}")

                logger.info(f"Página {page}/{total_pages} extraída ({len(contracts)} registros).")
                page += 1

            except Exception as e:
                logger.error(f"Falha na extração da página {page}: {e}")
                raise ExtractionError(f"Erro na extração: {e}")

        logger.info(f"Extração concluída. Total: {len(all_contracts)} contratos.")
        return all_contracts
