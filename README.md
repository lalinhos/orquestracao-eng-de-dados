# Orion - Pipeline ETL de Dados do PNCP

## Integrantes do grupo

- Arllesson Gomes
- Hugo Ponciano
- João Miguel Freitas
- Larissa Lima
- Lucas Lima
- Vinicius Pazos

## Sobre o projeto

O **Orion** é um pipeline de **ETL (Extract, Transform, Load)** desenvolvido em Python para coletar dados do **Portal Nacional de Contratações Públicas (PNCP)**, tratar essas informações e persistí-las no **MongoDB Atlas**.

O projeto foi estruturado seguindo os requisitos da disciplina de **Engenharia de Dados**, com foco em:

- organização modular do pipeline;
- uso de **orientação a objetos**;
- uso de **docstrings**;
- separação clara entre extração, transformação e carga;
- configuração por variáveis de ambiente;
- documentação de execução e arquitetura.

---

## Objetivo da atividade

Adaptar o ETL desenvolvido anteriormente para utilizar a **API do PNCP**, mantendo uma estrutura de projeto organizada e aderente às boas práticas vistas em sala.

Ao final do fluxo, os dados coletados e tratados são armazenados no **MongoDB Atlas**, permitindo reaproveitamento em análises futuras, dashboards ou sistemas backend.

---

## O que o pipeline faz

O pipeline executa três etapas principais:

### 1. Extração

Consulta a API do PNCP de forma paginada, permitindo filtros por:

- intervalo de datas;
- UF;
- modalidade de contratação;
- limite de páginas.

### 2. Transformação

Normaliza os registros retornados pela API, validando campos relevantes e padronizando a estrutura dos dados com **Pydantic**.

### 3. Carga

Realiza a persistência dos documentos tratados no **MongoDB Atlas**, utilizando operações de **upsert**, evitando duplicidades com base no identificador do contrato.

---

## Arquitetura da solução

A aplicação segue uma arquitetura em camadas simples e modular:

- **Extractor**: responsável por consumir a API do PNCP;
- **Transformer**: responsável por validar, limpar e normalizar os dados;
- **Loader**: responsável por salvar os dados no MongoDB Atlas;
- **Config**: centraliza as variáveis de ambiente e regras de validação;
- **Models**: define o modelo de dados tratado;
- **Utils**: concentra logger e exceções customizadas;
- **Main**: coordena a execução completa do pipeline.

Essa separação facilita manutenção, testes e evolução do projeto.

---

## Estrutura do projeto

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
│   └── test_transformer.py
├── README.md
├── pyproject.toml
└── requirements.txt
```

---

## Tecnologias utilizadas

- **Python 3.11+**
- **requests** para consumo da API
- **pydantic** e **pydantic-settings** para validação e configuração
- **pymongo** para integração com o MongoDB Atlas
- **python-dotenv** para leitura de variáveis de ambiente
- **loguru** para logging
- **pytest** para testes
- **black** para formatação de código

---

## Fluxo de dados

O fluxo executado pelo Orion pode ser resumido assim:

```text
API do PNCP
   ↓
Extração paginada dos dados
   ↓
Validação e normalização
   ↓
Tratamento dos campos relevantes
   ↓
Carga no MongoDB Atlas com upsert
```

---

## Pré-requisitos

Antes de executar o projeto, você precisa ter instalado:

- **Python 3.11 ou superior**
- acesso à internet para consumir a API do PNCP
- uma conta no **MongoDB Atlas**
- uma string de conexão válida com o MongoDB

---

## Instalação

### 1. Clonar o repositório

```bash
git clone https://github.com/Joao-Miguel-F/orion-eng-de-dados.git
cd orion-eng-de-dados
```

### 2. Criar o ambiente virtual

No Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

No Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

---

## Configuração do ambiente

Crie um arquivo `.env` na raiz do projeto com as variáveis abaixo:

```env
MONGO_URI=mongodb+srv://usuario:senha@cluster.mongodb.net/?retryWrites=true&w=majority
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

### Descrição das principais variáveis

- `MONGO_URI`: string de conexão com o MongoDB Atlas
- `MONGO_DB_NAME`: nome do banco
- `MONGO_COLLECTION_NAME`: nome da coleção
- `PNCP_BASE_URL`: URL base da API do PNCP
- `PNCP_PAGE_SIZE`: quantidade de registros por página
- `PNCP_TIMEOUT`: timeout da requisição HTTP
- `PNCP_MAX_RETRIES`: número máximo de tentativas por requisição
- `ETL_DATE_INITIAL`: data inicial da extração
- `ETL_DATE_FINAL`: data final da extração
- `ETL_UF_FILTER`: filtro opcional por UF
- `ETL_MODALITY_CODE`: filtro opcional por modalidade
- `ETL_MAX_PAGES`: limite opcional de páginas por execução
- `MONGO_SERVER_SELECTION_TIMEOUT_MS`: timeout de seleção do servidor MongoDB
- `MONGO_CONNECT_TIMEOUT_MS`: timeout de conexão
- `MONGO_SOCKET_TIMEOUT_MS`: timeout de leitura/escrita

> As datas podem ser informadas nos formatos `YYYYMMDD` ou `YYYY-MM-DD`.

---

## Como executar

Com o ambiente virtual ativado e o `.env` configurado, execute:

```bash
python -m src.main
```

Durante a execução, o pipeline:

1. consulta a API do PNCP;
2. coleta os registros de forma paginada;
3. transforma os dados para um formato padronizado;
4. conecta ao MongoDB Atlas;
5. insere ou atualiza os contratos na coleção configurada.

Os logs da execução ajudam no acompanhamento do processo e no diagnóstico de falhas.

---

## Exemplo de execução

Exemplo para extrair publicações de uma data específica do estado de Alagoas:

```env
ETL_DATE_INITIAL=20240625
ETL_DATE_FINAL=20240625
ETL_UF_FILTER=AL
ETL_MODALITY_CODE=6
ETL_MAX_PAGES=1
```

Depois, execute:

```bash
python -m src.main
```

---

## Testes

Para executar os testes automatizados do projeto:

```bash
pytest
```

Atualmente, o projeto possui teste voltado para a etapa de transformação dos dados.

---

## Formatação de código

Para padronizar o código com o Black:

```bash
black src tests
```

---

## Persistência no MongoDB Atlas

A carga dos dados é feita no MongoDB Atlas utilizando operações de **upsert**. Isso significa que:

- se o contrato ainda não existir, ele será inserido;
- se já existir, ele será atualizado.

Esse comportamento evita duplicações e facilita reprocessamentos do ETL.

---

## Boas práticas aplicadas

Este projeto adota as seguintes práticas de Engenharia de Dados:

- separação do pipeline em responsabilidades bem definidas;
- orientação a objetos;
- docstrings em classes e métodos;
- validação de dados;
- tratamento de exceções;
- uso de logging;
- configuração externa por variáveis de ambiente;
- teste automatizado da transformação.

---

## Melhorias futuras

- ampliar a cobertura de testes para extração e carga;
- adicionar agendamento automático do ETL;
- armazenar também dados brutos para auditoria;
- disponibilizar uma camada de consumo para backend ou dashboard;
- criar monitoramento mais robusto para falhas de execução.

---

## Orquestração com Prefect e Spark

Este repositório também contém uma extensão do pipeline com orquestração avançada, processamento distribuído e monitoramento de execução.

> Veja a documentação completa em [ORQUESTRACAO.md](ORQUESTRACAO.md)

---

## Conclusão

O Orion entrega uma solução ETL modular para dados do PNCP, alinhada aos requisitos da disciplina de Engenharia de Dados. O projeto demonstra a aplicação de conceitos como arquitetura em camadas, orientação a objetos, validação, documentação e persistência em banco NoSQL na nuvem.
