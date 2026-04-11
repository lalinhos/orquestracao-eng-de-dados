import re
from datetime import datetime
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator, model_validator


class Contract(BaseModel):
    """Modelo normalizado para registros de publicações/contratações do PNCP."""

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
        str_strip_whitespace=True,
    )

    id: str = Field(validation_alias=AliasChoices("idContrato", "numeroControlePNCP", "id"))
    numero_controle_pncp: str | None = Field(
        default=None,
        validation_alias=AliasChoices("numeroControlePNCP", "numero_controle_pncp"),
    )
    numero_aviso: str | None = Field(
        default=None,
        validation_alias=AliasChoices("numeroAviso", "numeroCompra", "numero_aviso"),
    )
    ano_compra: int | None = Field(
        default=None,
        validation_alias=AliasChoices("anoCompra", "ano_compra"),
    )
    objeto: str | None = Field(
        default=None,
        validation_alias=AliasChoices("objeto", "objetoCompra", "objeto_compra"),
    )
    valor_total_homologado: float | None = Field(
        default=None,
        validation_alias=AliasChoices("valorTotalHomologado", "valor_total_homologado"),
    )
    modalidade_licitacao: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "modalidadeLicitacao", "modalidadeNome", "modalidade_licitacao"
        ),
    )
    status_contrato: str | None = Field(
        default=None,
        validation_alias=AliasChoices("statusContrato", "situacaoCompraNome", "status_contrato"),
    )

    cnpj_contratada: str | None = Field(
        default=None,
        validation_alias=AliasChoices("cnpjContratada", "cnpj_contratada"),
    )
    razao_social_contratada: str | None = Field(
        default=None,
        validation_alias=AliasChoices("razaoSocialContratada", "razao_social_contratada"),
    )
    uf_contratada: str | None = Field(
        default=None,
        validation_alias=AliasChoices("ufContratada", "uf_contratada"),
    )
    municipio_contratada: str | None = Field(
        default=None,
        validation_alias=AliasChoices("municipioContratada", "municipio_contratada"),
    )

    cnpj_orgao_entidade: str | None = None
    razao_social_orgao_entidade: str | None = None
    poder_id: str | None = None
    esfera_id: str | None = None
    uf_unidade_orgao: str | None = None
    municipio_unidade_orgao: str | None = None
    codigo_unidade_orgao: str | None = None
    nome_unidade_orgao: str | None = None

    data_publicacao: datetime | None = Field(
        default=None,
        validation_alias=AliasChoices("dataPublicacao", "dataPublicacaoPncp", "data_publicacao"),
    )
    data_inicio_vigencia: datetime | None = Field(
        default=None,
        validation_alias=AliasChoices("dataInicioVigencia", "data_inicio_vigencia"),
    )
    data_fim_vigencia: datetime | None = Field(
        default=None,
        validation_alias=AliasChoices("dataFimVigencia", "data_fim_vigencia"),
    )
    data_abertura_proposta: datetime | None = Field(
        default=None,
        validation_alias=AliasChoices("dataAberturaProposta", "data_abertura_proposta"),
    )
    data_encerramento_proposta: datetime | None = Field(
        default=None,
        validation_alias=AliasChoices("dataEncerramentoProposta", "data_encerramento_proposta"),
    )

    @model_validator(mode="before")
    @classmethod
    def flatten_nested_fields(cls, data: Any) -> Any:
        """Achata campos aninhados comuns do payload do PNCP."""
        if not isinstance(data, dict):
            return data

        normalized = dict(data)

        orgao = normalized.get("orgaoEntidade")
        if isinstance(orgao, dict):
            normalized.setdefault("cnpj_orgao_entidade", orgao.get("cnpj"))
            normalized.setdefault("razao_social_orgao_entidade", orgao.get("razaoSocial"))
            normalized.setdefault("poder_id", orgao.get("poderId"))
            normalized.setdefault("esfera_id", orgao.get("esferaId"))

        unidade = normalized.get("unidadeOrgao")
        if isinstance(unidade, dict):
            normalized.setdefault("uf_unidade_orgao", unidade.get("ufSigla"))
            normalized.setdefault("municipio_unidade_orgao", unidade.get("municipioNome"))
            normalized.setdefault("codigo_unidade_orgao", unidade.get("codigoUnidade"))
            normalized.setdefault("nome_unidade_orgao", unidade.get("nomeUnidade"))

        return normalized

    @field_validator("id", mode="before")
    @classmethod
    def normalize_id(cls, value: str | int) -> str:
        """Garante que o identificador seja serializado como string."""
        if value in (None, ""):
            raise ValueError("O campo id é obrigatório.")
        return str(value)

    @field_validator(
        "numero_controle_pncp",
        "numero_aviso",
        "objeto",
        "modalidade_licitacao",
        "status_contrato",
        "razao_social_contratada",
        "municipio_contratada",
        "razao_social_orgao_entidade",
        "poder_id",
        "esfera_id",
        "municipio_unidade_orgao",
        "codigo_unidade_orgao",
        "nome_unidade_orgao",
        mode="before",
    )
    @classmethod
    def blank_to_none(cls, value: str | None) -> str | None:
        """Converte strings vazias em None."""
        if value is None:
            return None

        normalized = str(value).strip()
        return normalized or None

    @field_validator("cnpj_contratada", "cnpj_orgao_entidade", mode="before")
    @classmethod
    def normalize_cnpj(cls, value: str | None) -> str | None:
        """Remove caracteres não numéricos do CNPJ."""
        if value in (None, ""):
            return None

        digits = re.sub(r"\D", "", str(value))
        return digits or None

    @field_validator("uf_contratada", "uf_unidade_orgao", mode="before")
    @classmethod
    def normalize_uf(cls, value: str | None) -> str | None:
        """Normaliza a UF para letras maiúsculas."""
        if value in (None, ""):
            return None

        normalized = str(value).strip().upper()
        return normalized or None

    @field_validator("valor_total_homologado", mode="before")
    @classmethod
    def normalize_amount(cls, value: str | float | int | None) -> float | None:
        """Converte valores monetários para float."""
        if value in (None, ""):
            return None

        if isinstance(value, (int, float)):
            return float(value)

        normalized = str(value).strip().replace("R$", "").replace(" ", "")
        if "," in normalized and "." in normalized:
            normalized = normalized.replace(".", "").replace(",", ".")
        elif "," in normalized:
            normalized = normalized.replace(",", ".")

        return float(normalized)
