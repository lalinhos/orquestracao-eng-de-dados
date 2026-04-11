Segue o `README.md` unificado, com a segunda parte formatada no mesmo padrão da primeira:

````markdown
# Orion: Pipeline ETL de Dados do PNCP

## Visão geral

O Orion é um pipeline ETL em Python projetado para extrair dados de contratações públicas do Portal Nacional de Contratações Públicas (PNCP), transformar esses dados em um formato padronizado e persistí-los no MongoDB Atlas.

O projeto foi estruturado com foco em boas práticas de engenharia de dados:
- orientação a objetos;
- modularização por camadas;
- validação com Pydantic;
- logging estruturado;
- tratamento de erros;
- configuração por variáveis de ambiente;
- testes básicos;
- padronização de código com Black.

## Grupo

Arllesson Gomes, Hugo Ponciano, João Miguel Freitas, Larissa Lima, Lucas Lima e Vinicius Pazos.

## Objetivo da solução

O objetivo do Orion é disponibilizar uma base confiável e reutilizável de dados do PNCP para uso posterior em:
- dashboards;
- análises exploratórias;
- monitoramento;
- relatórios;
- aplicações analíticas ou operacionais.

## Arquitetura do ETL

A arquitetura foi dividida em camadas para melhorar manutenção, legibilidade, extensibilidade e testabilidade.

### Extract

Responsável por:
- consultar a API do PNCP;
- paginar os resultados;
- tratar erros HTTP;
- aplicar retentativas;
- registrar logs operacionais.

### Transform

Responsável por:
- validar o payload recebido;
- normalizar nomes de campos;
- converter tipos;
- padronizar valores;
- descartar registros inválidos.

### Load

Responsável por:
- conectar ao MongoDB Atlas;
- validar a conexão com `ping`;
- criar índice único em `id`;
- realizar operações de `upsert` com `bulk_write`;
- evitar duplicidade de documentos.

## Fluxo de dados

1. O pipeline lê as configurações do arquivo `.env`.
2. O extrator consulta a API do PNCP de forma paginada.
3. Os registros brutos são enviados ao transformador.
4. O transformador valida e normaliza os dados.
5. O loader persiste os dados tratados no MongoDB Atlas.
6. Logs são registrados em console e em arquivo.

## Tecnologias utilizadas

O projeto foi desenvolvido com as seguintes tecnologias e bibliotecas:
- Python 3.11+;
- requests;
- pymongo;
- dnspython;
- python-dotenv;
- loguru;
- pydantic;
- pydantic-settings;
- pytest;
- black;
- MongoDB Atlas.

## Estrutura de pastas

```text
orion-eng-de-dados/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── extractor.py
│   │   ├── transformer.py
│   │   └── loader.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── contract.py
│   └── utils/
│       ├── __init__.py
│       ├── exceptions.py
│       └── logger.py
├── tests/
│   ├── conftest.py
│   ├── test_extractor.py
│   ├── test_loader.py
│   └── test_transformer.py
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
````

## Instalação

### Clonar o repositório

Clone o repositório e acesse a pasta do projeto:

```bash
git clone https://github.com/Joao-Miguel-F/orion-eng-de-dados.git
cd orion-eng-de-dados
```

### Criar e ativar o ambiente virtual

#### Linux/macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

#### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Instalar as dependências

```bash
pip install -r requirements.txt
```

## Configuração das variáveis de ambiente

Copie o arquivo de exemplo para criar seu arquivo `.env`.

### Linux/macOS

```bash
cp .env.example .env
```

### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

Depois, edite o arquivo `.env` com os valores necessários.

### Variáveis principais

* `MONGO_URI`: string de conexão com o MongoDB Atlas;
* `MONGO_DB_NAME`: nome do banco de dados;
* `MONGO_COLLECTION_NAME`: nome da coleção;
* `PNCP_BASE_URL`: URL base da API do PNCP;
* `PNCP_PAGE_SIZE`: quantidade de registros por página;
* `PNCP_TIMEOUT`: timeout da requisição HTTP;
* `PNCP_MAX_RETRIES`: número de tentativas por consulta;
* `ETL_DATE_INITIAL`: data inicial no formato `YYYYMMDD` ou `YYYY-MM-DD`;
* `ETL_DATE_FINAL`: data final no formato `YYYYMMDD` ou `YYYY-MM-DD`;
* `ETL_UF_FILTER`: filtro opcional por UF;
* `ETL_MODALITY_CODE`: filtro opcional por modalidade;
* `ETL_MAX_PAGES`: limite opcional de páginas;
* `MONGO_SERVER_SELECTION_TIMEOUT_MS`: timeout de seleção do cluster;
* `MONGO_CONNECT_TIMEOUT_MS`: timeout de conexão;
* `MONGO_SOCKET_TIMEOUT_MS`: timeout de leitura e escrita.

## Forma de execução

Execute o pipeline a partir da raiz do projeto:

```bash
python -m src.main
```

## Uso do Black

Para formatar o projeto:

```bash
black src tests
```

## Executando os testes

Para executar os testes automatizados:

```bash
pytest
```

## Exemplo de uso

### Exemplo de `.env`

```env
MONGO_URI=mongodb+srv://usuario:senha@cluster.mongodb.net/?retryWrites=true&w=majority&appName=orion-cluster
MONGO_DB_NAME=orion
MONGO_COLLECTION_NAME=contracts

PNCP_BASE_URL=https://pncp.gov.br/api/consulta
PNCP_PAGE_SIZE=10
PNCP_TIMEOUT=30
PNCP_MAX_RETRIES=1

ETL_DATE_INITIAL=20240625
ETL_DATE_FINAL=20240625
ETL_UF_FILTER=AL
ETL_MODALITY_CODE=6
ETL_MAX_PAGES=1

MONGO_SERVER_SELECTION_TIMEOUT_MS=10000
MONGO_CONNECT_TIMEOUT_MS=10000
MONGO_SOCKET_TIMEOUT_MS=20000
```

### Exemplo de execução

```bash
python -m src.main
```

### Exemplo de logs esperados

```text
2026-04-11 03:25:00 | INFO     | src.core.extractor:extract_contracts - Extração concluída com 10 contratos.
2026-04-11 03:25:00 | INFO     | src.core.transformer:transform_contracts - Transformação concluída. Válidos: 10 | Inválidos: 0 | Total: 10
2026-04-11 03:25:01 | INFO     | src.core.loader:load_contracts - Carga concluída no MongoDB. Recebidos: 10 | Operações: 10 | Inseridos: 10 | Atualizados: 0
```

## Tratamento de erros e logging

O projeto possui mecanismos para aumentar a confiabilidade da execução, incluindo:

* exceções customizadas por etapa;
* logs em console;
* logs em arquivo na pasta `logs/`;
* mensagens de erro mais claras;
* encerramento seguro de conexões.

## MongoDB Atlas

O projeto foi preparado para gravar dados tratados no MongoDB Atlas.

A coleção recebe um índice único no campo:

```text
id
```

Isso permite realizar operações de `upsert` sem duplicidade e facilita reprocessamentos.

### Instruções para configurar e usar o MongoDB Atlas

Para configurar o ambiente no MongoDB Atlas:

1. crie um cluster no MongoDB Atlas;
2. crie um Database User;
3. libere seu IP em `Network Access`;
4. copie a connection string em `Connect > Drivers`;
5. atualize o valor de `MONGO_URI` no arquivo `.env`;
6. execute o pipeline com:

```bash
python -m src.main
```

## Diferenciais implementados

Entre os diferenciais já implementados no projeto, destacam-se:

* arquitetura modular por camadas;
* tratamento de erros por etapa;
* logging estruturado;
* validação e normalização com Pydantic;
* testes básicos;
* configuração por `.env`;
* persistência real no MongoDB Atlas.

## Limitações atuais

No estado atual, o projeto possui algumas limitações:

* o endpoint do PNCP pode apresentar variações de desempenho;
* a extração ainda é síncrona;
* o projeto está focado em uma entidade principal;
* ainda não há orquestração externa;
* os testes ainda são básicos.

## Melhorias futuras

Como evoluções futuras, o projeto pode receber:

* integração com Airflow ou Prefect;
* persistência adicional em PostgreSQL;
* expansão da suíte de testes;
* exposição de métricas operacionais;
* geração de datasets analíticos derivados;
* integração com dashboards ou análises exploratórias;
* CI/CD com GitHub Actions.
