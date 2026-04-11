from src.core import PncpExtractor, PncpTransformer, MongoLoader
from src.utils import logger, OrionETLError


def main():
    """Orquestrador principal do pipeline ETL Orion."""
    logger.info("Pipeline ETL Orion iniciado.")

    extractor = PncpExtractor()
    transformer = PncpTransformer()
    loader = MongoLoader()

    try:
        # 1. Extração
        raw_contracts = extractor.extract_contracts()
        if not raw_contracts:
            logger.info("Nenhum contrato novo extraído. Pipeline finalizado.")
            return

        # 2. Transformação
        transformed_contracts = transformer.transform_contracts(raw_contracts)
        if not transformed_contracts:
            logger.info("Nenhum contrato transformado com sucesso. Pipeline finalizado.")
            return

        # 3. Carga
        loader.connect()
        loader.load_contracts(transformed_contracts)

    except OrionETLError as e:
        logger.error(f"Pipeline ETL falhou: {e}")
    except Exception as e:
        logger.error(f"Ocorreu um erro inesperado durante o pipeline ETL: {e}")
    finally:
        loader.close()
        logger.info("Pipeline ETL Orion finalizado.")


if __name__ == "__main__":
    main()
