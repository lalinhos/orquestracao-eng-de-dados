import pytest
from src.core import PncpTransformer


def test_transform_contracts_valid_data():
    """Testa a transformação de dados de contrato válidos."""
    transformer = PncpTransformer()
    raw_contracts = [
        {
            "idContrato": "123",
            "numeroAviso": "001/2024",
            "anoCompra": 2024,
            "dataPublicacao": "2024-01-01T10:00:00",
            "objeto": "Contrato de Teste",
            "valorTotalHomologado": 1000.0,
            "modalidadeLicitacao": "Dispensa",
            "statusContrato": "Ativo",
            "cnpjContratada": "12345678000199",
            "razaoSocialContratada": "Empresa de Teste",
            "ufContratada": "PE",
            "municipioContratada": "Recife",
            "dataInicioVigencia": "2024-01-01T00:00:00",
            "dataFimVigencia": "2024-12-31T23:59:59",
        }
    ]

    transformed = transformer.transform_contracts(raw_contracts)

    assert len(transformed) == 1
    assert transformed[0]["id"] == "123"
    assert transformed[0]["numero_aviso"] == "001/2024"
    assert transformed[0]["valor_total_homologado"] == 1000.0


def test_transform_contracts_invalid_data_skips():
    """Testa se dados de contrato inválidos são pulados durante a transformação."""
    transformer = PncpTransformer()
    raw_contracts = [
        {
            "idContrato": "123",
            "valorTotalHomologado": "float_invalido",  # Isso deve causar um erro de validação
        },
        {
            "idContrato": "456",
            "valorTotalHomologado": 2000.0,
        }
    ]

    transformed = transformer.transform_contracts(raw_contracts)

    assert len(transformed) == 1
    assert transformed[0]["id"] == "456"
