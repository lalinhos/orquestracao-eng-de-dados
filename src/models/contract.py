from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Contract(BaseModel):
    """
    Modelo de dados para um contrato do PNCP.
    Utiliza aliases para mapear os campos da API para nomes mais amigáveis em Python.
    """

    id: str = Field(..., alias="idContrato")
    numero_aviso: Optional[str] = Field(None, alias="numeroAviso")
    ano_compra: Optional[int] = Field(None, alias="anoCompra")
    data_publicacao: Optional[datetime] = Field(None, alias="dataPublicacao")
    objeto: Optional[str] = Field(None, alias="objeto")
    valor_total_homologado: Optional[float] = Field(None, alias="valorTotalHomologado")
    modalidade_licitacao: Optional[str] = Field(None, alias="modalidadeLicitacao")
    status_contrato: Optional[str] = Field(None, alias="statusContrato")
    cnpj_contratada: Optional[str] = Field(None, alias="cnpjContratada")
    razao_social_contratada: Optional[str] = Field(None, alias="razaoSocialContratada")
    uf_contratada: Optional[str] = Field(None, alias="ufContratada")
    municipio_contratada: Optional[str] = Field(None, alias="municipioContratada")
    data_inicio_vigencia: Optional[datetime] = Field(None, alias="dataInicioVigencia")
    data_fim_vigencia: Optional[datetime] = Field(None, alias="dataFimVigencia")

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
