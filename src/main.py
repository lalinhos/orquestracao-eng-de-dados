from src.core import MongoLoader, PncpExtractor, PncpTransformer
from src.utils import LoadingError, OrionETLError, logger


def main() -> int:
    """Executa o fluxo principal do pipeline ETL Orion."""
    logger.info("Pipeline ETL Orion iniciado.")

    extractor = PncpExtractor()
    transformer = PncpTransformer()
    loader = MongoLoader()

    try:
        raw_contracts = extractor.extract_contracts()
        if not raw_contracts:
            logger.info("Nenhum contrato extraído. Encerrando execução.")
            return 0

        transformed_contracts = transformer.transform_contracts(raw_contracts)
        if not transformed_contracts:
            logger.warning("Nenhum contrato válido após transformação. Encerrando execução.")
            return 0

        loader.connect()
        result = loader.load_contracts(transformed_contracts)

        logger.info(
            "Pipeline concluído com sucesso. Recebidos: {} | Inseridos: {} | Atualizados: {}",
            result["received"],
            result["inserted"],
            result["updated"],
        )
        return 0

    except LoadingError as exc:
        logger.error("Falha na etapa de carga: {}", exc)
        return 1
    except OrionETLError as exc:
        logger.error("Falha controlada no pipeline: {}", exc)
        return 1
    except Exception as exc:
        logger.exception("Falha inesperada no pipeline: {}", exc)
        return 1
    finally:
        extractor.close()
        loader.close()
        logger.info("Pipeline ETL Orion finalizado.")


if __name__ == "__main__":
    raise SystemExit(main())