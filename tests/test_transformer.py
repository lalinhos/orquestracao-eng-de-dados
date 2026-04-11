from src.core import PncpTransformer


def test_transform_contracts_publication_payload() -> None:
    """Deve transformar corretamente um payload realista do endpoint de publicações do PNCP."""
    transformer = PncpTransformer()

    raw_contracts = [
        {
            "numeroControlePNCP": "00394494000136-1-000616/2024",
            "numeroCompra": "90005",
            "anoCompra": 2024,
            "dataPublicacaoPncp": "2024-06-25T07:09:09",
            "objetoCompra": "Contratação de serviços de recepção.",
            "valorTotalHomologado": None,
            "modalidadeNome": "Pregão - Eletrônico",
            "situacaoCompraNome": "Divulgada no PNCP",
            "orgaoEntidade": {
                "cnpj": "00.394.494/0001-36",
                "razaoSocial": "MINISTERIO DA JUSTICA E SEGURANCA PUBLICA",
                "poderId": "E",
                "esferaId": "F",
            },
            "unidadeOrgao": {
                "ufSigla": "AL",
                "municipioNome": "Maceió",
                "codigoUnidade": "200358",
                "nomeUnidade": "SUPERINTENDENCIA REG.DEP.POLICIA FEDERAL - AL",
            },
            "dataAberturaProposta": "2024-06-25T08:00:00",
            "dataEncerramentoProposta": "2024-07-16T09:00:00",
        }
    ]

    transformed = transformer.transform_contracts(raw_contracts)

    assert len(transformed) == 1
    assert transformed[0]["id"] == "00394494000136-1-000616/2024"
    assert transformed[0]["numero_aviso"] == "90005"
    assert transformed[0]["objeto"] == "Contratação de serviços de recepção."
    assert transformed[0]["modalidade_licitacao"] == "Pregão - Eletrônico"
    assert transformed[0]["status_contrato"] == "Divulgada no PNCP"
    assert transformed[0]["cnpj_orgao_entidade"] == "00394494000136"
    assert transformed[0]["uf_unidade_orgao"] == "AL"


def test_transform_contracts_legacy_payload_still_works() -> None:
    """Deve manter compatibilidade com payloads antigos já usados no projeto."""
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
            "cnpjContratada": "12.345.678/0001-99",
            "razaoSocialContratada": "Empresa de Teste",
            "ufContratada": "pe",
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
    assert transformed[0]["cnpj_contratada"] == "12345678000199"
    assert transformed[0]["uf_contratada"] == "PE"