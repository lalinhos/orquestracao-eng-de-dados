class OrionETLError(Exception):
    """Exceção base para erros do pipeline Orion."""


class ExtractionError(OrionETLError):
    """Erro durante a etapa de extração."""


class TransformationError(OrionETLError):
    """Erro durante a etapa de transformação."""


class LoadingError(OrionETLError):
    """Erro durante a etapa de carga."""