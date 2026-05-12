# Pipeline de Orquestração PNCP

Pipeline de coleta, transformação e armazenamento de dados de contratações públicas da [API do PNCP](https://pncp.gov.br), com orquestração via **Prefect** e processamento via **Apache Spark**.

## Tecnologias

- **Python 3.13**
- **Prefect** — orquestração e monitoramento das etapas do pipeline
- **Apache Spark (PySpark 4.1.1)** — transformação e classificação dos dados
- **MongoDB Atlas** — persistência dos dados brutos e processados
- **Java JDK 21**

## Fluxo do pipeline

```
API PNCP → MongoDB (raw) → Spark → MongoDB (processados)
```

1. **Coleta** — percorre todas as páginas da API do PNCP
2. **Armazenamento raw** — registros brutos salvos no MongoDB Atlas
3. **Processamento Spark** — lê do MongoDB, classifica por ramo do MEI e deduplica
4. **Armazenamento processado** — dados transformados salvos no MongoDB Atlas

## Classificação por ramo do MEI

Cada contratação é classificada automaticamente com base no campo `objetoCompra`:

| Ramo | Palavras-chave detectadas |
|---|---|
| Obras | obra, construção, reforma, pavimento... |
| TI | software, sistema, tecnologia, hardware... |
| Serviços | serviço, limpeza, vigilância, manutenção... |
| Compras | aquisição, fornecimento, material, equipamento... |
| Outros | demais casos |

## Resiliência

- Erros **5xx** do servidor PNCP: retry automático com backoff (10s, 20s)
- Erros **de rede**: retry com backoff (5s, 10s)
- Task de coleta com até **3 retries** automáticos pelo Prefect

## Pré-requisitos

- Python 3.13+
- Java JDK 21
- Conexão com internet (API PNCP + MongoDB Atlas)

## Configuração

Execute uma única vez para criar o ambiente virtual e instalar as dependências:

```powershell
.\setup_venv.ps1
```

## Como rodar

```powershell
.\rodar.ps1
```

Com parâmetros personalizados:

```powershell
.\rodar.ps1 -DataInicial 20260401 -DataFinal 20260430 -UF PE -Modalidade 8
```

Ou diretamente pelo Python:

```powershell
python main.py --data-inicial 20260401 --data-final 20260430 --uf PE --modalidade 8
```

### Parâmetros disponíveis

| Parâmetro | Padrão | Descrição |
|---|---|---|
| `--data-inicial` | obrigatório | Formato AAAAMMDD |
| `--data-final` | obrigatório | Formato AAAAMMDD |
| `--uf` | `PE` | Sigla do estado |
| `--modalidade` | `8` | Código da modalidade (8 = Dispensa) |
| `--tamanho-pagina` | `20` | Registros por página (máx. 500) |
| `--sem-resumo` | — | Suprime o resumo estatístico no console |

## Estrutura do projeto

```
├── main.py              # entrypoint CLI
├── rodar.ps1            # script de execução completa (Windows)
├── setup_venv.ps1       # configuração inicial do ambiente
├── requirements.txt
└── src/
    ├── config.py        # URLs, parâmetros e constantes
    ├── ingestion.py     # coleta paginada da API PNCP
    ├── processing.py    # transformações Spark
    ├── database.py      # acesso ao MongoDB Atlas
    └── orchestration.py # tasks e flow Prefect
```

## Coleções MongoDB

| Coleção | Conteúdo |
|---|---|
| `contratacoes_raw` | Dados brutos da API, sem transformação |
| `contratacoes_processadas` | Dados com `ramo_mei`, campos selecionados e deduplicados |

Ambas usam upsert por `numeroControlePNCP` — rodar o pipeline duas vezes não duplica registros.

## Evidências de execução

> Pipeline executado com sucesso — 3 tasks concluídas, dados coletados, processados pelo Spark e persistidos no MongoDB Atlas.

<img width="1596" height="785" alt="image" src="https://github.com/user-attachments/assets/0e6bce9e-6e7f-40b0-8f57-b1d43934e059" />
<img width="1568" height="591" alt="image" src="https://github.com/user-attachments/assets/0cb8cdca-c4e9-43c6-ba54-2377b9186ed0" />
<img width="860" height="185" alt="image" src="https://github.com/user-attachments/assets/e67335fe-0edc-4687-88d2-eeeae2c0f317" />


