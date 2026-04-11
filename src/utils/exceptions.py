class OrionETLError(Exception):
    """Exceção base para o pipeline Orion."""

    pass


class ExtractionError(OrionETLError):
    """Erro ao tentar extrair dados da API do PNCP."""

    pass


class TransformationError(OrionETLError):
    """Erro ao validar ou transformar os dados brutos."""

    pass


class LoadingError(OrionETLError):
    """Erro ao persistir os dados no MongoDB Atlas."""

    pass
