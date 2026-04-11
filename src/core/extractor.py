import time
from datetime import datetime, timedelta
from typing import Any

import requests
from requests import Response, Session
from requests.exceptions import RequestException, Timeout

from src.config import settings
from src.utils import ExtractionError, logger


class PncpExtractor:
    """Responsável pela extração paginada de publicações de contratações no PNCP."""

    def __init__(self, session: Session | None = None) -> None:
        """Inicializa o extrator com sessão HTTP e parâmetros de configuração."""
        self.base_url = settings.PNCP_BASE_URL.rstrip("/")
        self.endpoint = f"{self.base_url}/v1/contratacoes/publicacao"
        self.page_size = settings.PNCP_PAGE_SIZE
        self.timeout = settings.PNCP_TIMEOUT
        self.max_retries = settings.PNCP_MAX_RETRIES
        self.max_pages = settings.ETL_MAX_PAGES
        self.session = session or requests.Session()
        self._owns_session = session is None

        self.session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": "orion-etl/0.1.0",
            }
        )

        logger.info("Extrator inicializado para o endpoint {}", self.endpoint)

    def close(self) -> None:
        """Fecha a sessão HTTP, se ela foi criada internamente pelo extrator."""
        if self._owns_session:
            self.session.close()

    def _build_params(self, page: int) -> dict[str, Any]:
        """Monta os parâmetros de consulta para a API do PNCP."""
        yesterday = datetime.now() - timedelta(days=1)
        default_date = yesterday.strftime("%Y%m%d")

        params: dict[str, Any] = {
            "pagina": page,
            "tamanhoPagina": self.page_size,
            "dataInicial": settings.ETL_DATE_INITIAL or default_date,
            "dataFinal": settings.ETL_DATE_FINAL or default_date,
        }

        if settings.ETL_UF_FILTER:
            params["uf"] = settings.ETL_UF_FILTER

        if settings.ETL_MODALITY_CODE is not None:
            params["codigoModalidadeContratacao"] = settings.ETL_MODALITY_CODE

        return params

    @staticmethod
    def _extract_error_detail(response: Response) -> str:
        """Extrai uma mensagem curta do corpo de erro HTTP."""
        try:
            payload = response.json()
            if isinstance(payload, dict):
                for key in ("message", "mensagem", "detail", "titulo", "error"):
                    if key in payload and payload[key]:
                        return str(payload[key])
                return str(payload)[:500]
        except ValueError:
            pass

        text = response.text.strip()
        return text[:500] if text else "Sem detalhe retornado no corpo da resposta."

    def _request_page(self, page: int) -> dict[str, Any]:
        """Faz a requisição de uma página com controle de retentativas."""
        params = self._build_params(page)
        last_error: Exception | None = None

        logger.info("Consultando PNCP | página={} | params={}", page, params)

        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.session.get(
                    self.endpoint,
                    params=params,
                    timeout=(10, self.timeout),  # conexão, leitura
                )

                logger.info(
                    "Resposta recebida | tentativa={} | página={} | status={} | url={}",
                    attempt,
                    page,
                    response.status_code,
                    response.url,
                )

                if response.status_code == 204:
                    logger.info("Página {} retornou HTTP 204 sem conteúdo.", page)
                    return {"data": [], "totalPaginas": page}

                if response.status_code >= 400:
                    detail = self._extract_error_detail(response)
                    raise ExtractionError(
                        f"HTTP {response.status_code} na página {page}. "
                        f"URL: {response.url} | Detalhe: {detail}"
                    )

                payload = response.json()

                if isinstance(payload, list):
                    return {"data": payload, "totalPaginas": page}

                if not isinstance(payload, dict):
                    raise ExtractionError("A API retornou um payload em formato inesperado.")

                return payload

            except Timeout as exc:
                last_error = exc
                logger.warning(
                    "Timeout na tentativa {}/{} da página {}. Params: {}",
                    attempt,
                    self.max_retries,
                    page,
                    params,
                )
                if attempt < self.max_retries:
                    time.sleep(attempt * 2)

            except ExtractionError as exc:
                last_error = exc
                logger.warning(
                    "Tentativa {}/{} falhou na página {}: {}",
                    attempt,
                    self.max_retries,
                    page,
                    exc,
                )
                if attempt < self.max_retries:
                    time.sleep(attempt)

            except RequestException as exc:
                last_error = exc
                logger.warning(
                    "Erro HTTP/rede na tentativa {}/{} da página {}: {}",
                    attempt,
                    self.max_retries,
                    page,
                    exc,
                )
                if attempt < self.max_retries:
                    time.sleep(attempt)

            except ValueError as exc:
                raise ExtractionError("A API retornou JSON inválido.") from exc

        raise ExtractionError(f"Falha ao consultar a página {page}.") from last_error

    def extract_contracts(self) -> list[dict[str, Any]]:
        """Executa a extração completa paginada dos registros."""
        all_contracts: list[dict[str, Any]] = []
        page = 1
        total_pages: int | None = None

        logger.info("Iniciando extração de contratos do PNCP.")

        while True:
            if self.max_pages is not None and page > self.max_pages:
                logger.info("Limite de páginas configurado atingido: {}", self.max_pages)
                break

            payload = self._request_page(page)
            contracts = payload.get("data", [])

            if not isinstance(contracts, list):
                raise ExtractionError("O campo 'data' da API não está em formato de lista.")

            if page == 1:
                raw_total_pages = payload.get("totalPaginas") or payload.get("totalPages")
                if raw_total_pages is not None:
                    try:
                        total_pages = int(raw_total_pages)
                        logger.info("Total de páginas identificado: {}", total_pages)
                    except (TypeError, ValueError):
                        total_pages = None
                        logger.warning("Não foi possível interpretar o total de páginas retornado.")

            if not contracts:
                logger.info("Nenhum registro encontrado na página {}.", page)
                break

            all_contracts.extend(contracts)
            logger.info("Página {} extraída com {} registros.", page, len(contracts))

            if total_pages is not None and page >= total_pages:
                break

            page += 1

        logger.info("Extração concluída com {} contratos.", len(all_contracts))
        return all_contracts
