# Orion: Pipeline ETL de Dados do PNCP

## Visão Geral
Orion é um pipeline ETL (Extract, Transform, Load) robusto e modular, projetado para extrair eficientemente dados de contratações públicas da API do Portal Nacional de Contratações Públicas (PNCP), transformá-los em um formato padronizado e carregá-los em um banco de dados MongoDB Atlas. Este projeto enfatiza a adesão às melhores práticas em engenharia de dados, incluindo design orientado a objetos, logging abrangente e documentação completa, tornando-o adequado para ambientes de produção.

## Grupo:
Arllesson Gomes,
Hugo Ponciano,
João Miuel Freitas,
Larissa Lima,
Lucas Lima e
Vinicius Pazos.

## Objetivo
O objetivo principal do Orion é fornecer uma solução confiável e escalável para coletar e estruturar dados do PNCP. Ao automatizar os processos de extração, transformação e carregamento, o Orion permite que aplicações a jusante, como dashboards analíticos ou ferramentas de relatórios, utilizem informações atualizadas de contratações públicas para diversas finalidades, incluindo análise de mercado, monitoramento de conformidade e identificação de oportunidades de negócios.

## Arquitetura ETL
A arquitetura do Orion é projetada para clareza, manutenibilidade e extensibilidade, seguindo uma abordagem em camadas. Os componentes principais são:

-   **Extrator**: Responsável pela interface com a API do PNCP, gerenciando paginação, retentativas e recuperação inicial de dados.
-   **Transformador**: Padroniza e valida os dados brutos usando modelos Pydantic, garantindo a qualidade e consistência dos dados.
-   **Carregador**: Persiste os dados transformados no MongoDB Atlas, utilizando operações de upsert para um gerenciamento eficiente dos dados.

Este design modular permite o desenvolvimento e teste independentes de cada componente, facilitando atualizações e adaptações a mudanças na API de origem ou no banco de dados de destino.

## Fluxo de Dados

| Etapa       | Entrada                  | Saída                     | Operações Principais                                                                                             |
| :---------- | :----------------------- | :------------------------ | :--------------------------------------------------------------------------------------------------------------- |
| **Extração** | Configuração via `.env`  | `list[dict]` brutos        | Requisições paginadas à API PNCP, tratamento de erros HTTP, retry exponencial.                                   |
| **Transformação** | `list[dict]` brutos        | `list[dict]` normalizados | Validação e normalização de campos via Pydantic, conversão de tipos, renomeação de campos, descarte de registros inválidos. |
| **Carga**    | `list[dict]` normalizados | Documentos no MongoDB Atlas | Upsert via `bulk_write` (MongoDB), criação de índice único (`id` do contrato).                                   |

## Estrutura de Pastas

```text
orion/
├── src/
│   ├── __init__.py           # Metadados do pacote e exportações de alto nível
│   ├── config/
│   │   ├── __init__.py       # Exporta a instância de configurações (settings)
│   │   └── settings.py       # Gerenciamento de configurações (Pydantic Settings)
│   ├── core/
│   │   ├── __init__.py       # Exporta Extractor, Transformer, Loader
│   │   ├── extractor.py      # Lógica de extração da API do PNCP
│   │   ├── transformer.py    # Limpeza e normalização de dados
│   │   └── loader.py         # Persistência no MongoDB Atlas
│   ├── models/
│   │   ├── __init__.py       # Exporta o modelo Contract
│   │   └── contract.py       # Modelos Pydantic para validação de dados
│   ├── utils/
│   │   ├── __init__.py       # Exporta logger e classes de exceção
│   │   ├── logger.py         # Configuração do Loguru
│   │   └── exceptions.py     # Classes de exceção personalizadas
│   └── main.py               # Ponto de entrada da aplicação
├── tests/
│   └── test_transformer.py   # Testes unitários para transformação
├── .env.example              # Modelo para variáveis de ambiente
├── .gitignore                # Regras de ignorar do Git
├── pyproject.toml            # Metadados do projeto e dependências (Black, Pytest)
├── requirements.txt          # Lista de dependências
└── README.md                 # Documentação do projeto
```

**Nota sobre Importações:** Graças à configuração dos arquivos `__init__.py`, as classes e funções principais podem ser importadas de forma mais concisa, por exemplo: `from src.core import PncpExtractor`.

## Tecnologias Utilizadas

| Tecnologia         | Uso                                                                 |
| :----------------- | :------------------------------------------------------------------ |
| Python 3.11+       | Linguagem de programação principal.                                 |
| `requests`         | Requisições HTTP para a API do PNCP.                                |
| `pymongo`          | Driver MongoDB para Python, usado para carregamento de dados no MongoDB Atlas.  |
| `python-dotenv`    | Gerencia variáveis de ambiente para configurações sensíveis.         |
| `loguru`           | Logging estruturado com recursos avançados como rotação e retenção. |
| `pydantic`         | Validação de dados e gerenciamento de configurações.                |
| `pydantic-settings`| Gerencia configurações da aplicação a partir de variáveis de ambiente. |
| `Black`            | Formatador de código para estilo consistente.                       |
| `pytest`           | Framework para escrever e executar testes.                          |
| MongoDB Atlas      | Banco de dados NoSQL baseado em nuvem para persistência de dados.    |

## Instruções de Instalação

1.  **Clone o repositório (ou crie a estrutura do projeto manualmente):**
    ```bash
    git clone https://github.com/seu-usuario/orion.git
    cd orion
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv .venv
    # No Linux/macOS
    source .venv/bin/activate
    # No Windows
    .venv\Scripts\activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as variáveis de ambiente:**
    Copie o arquivo de exemplo de ambiente e preencha seus detalhes:
    ```bash
    cp .env.example .env
    ```
    Edite o arquivo `.env` com sua string de conexão do MongoDB Atlas e outras configurações necessárias.

## Configuração das Variáveis de Ambiente

Copie `.env.example` para `.env` e preencha-o com seus valores específicos. **Nunca envie seu arquivo `.env` para o controle de versão.**

| Variável                  | Descrição                                                                    | Obrigatório |
| :------------------------ | :----------------------------------------------------------------------------- | :-------- |
| `MONGO_URI`               | URI de conexão para o MongoDB Atlas.                                           | Sim       |
| `MONGO_DB_NAME`           | Nome do banco de dados no MongoDB Atlas.                                       | Sim       |
| `MONGO_COLLECTION_NAME`   | Nome da coleção para armazenar os contratos.                                   | Sim       |
| `PNCP_BASE_URL`           | URL base para a API do PNCP. (Padrão: `https://pncp.gov.br/api/consulta`)       | Não       |
| `PNCP_PAGE_SIZE`          | Número de registros por página para requisições da API (Máx: 50). (Padrão: `50`) | Não       |
| `PNCP_TIMEOUT`            | Timeout em segundos para requisições da API. (Padrão: `60`)                    | Não       |
| `ETL_DATE_INITIAL`        | Data de início para extração de dados no formato `AAAAMMDD`. (Padrão: ontem)      | Não       |
| `ETL_DATE_FINAL`          | Data de término para extração de dados no formato `AAAAMMDD`. (Padrão: hoje)     | Não       |
| `ETL_UF_FILTER`           | Filtro opcional para contratos por estado brasileiro (ex: `PE`).                 | Não       |
| `ETL_MODALITY_CODE`       | Filtro opcional para contratos por código de modalidade (ex: `8`).             | Não       |

## Como Executar

Execute o pipeline ETL a partir do diretório raiz do projeto:

```bash
python -m src.main
```

Os logs serão exibidos no console e salvos no diretório `logs/`.

## Usando Black para Formatação de Código

Black está integrado ao projeto para garantir um estilo de código consistente. Para formatar seu código, execute:

```bash
black src/
```

## Exemplos de Uso

Para extrair contratos de um intervalo de datas específico para um determinado estado:

1.  Atualize seu arquivo `.env`:
    ```dotenv
    ETL_DATE_INITIAL=20240301
    ETL_DATE_FINAL=20240331
    ETL_UF_FILTER=SP
    ```
2.  Execute o pipeline:
    ```bash
    python -m src.main
    ```

## Limitações e Melhorias Futuras

### Limitações Atuais
-   **Limites de Taxa da API**: O extrator atual não lida explicitamente com os limites de taxa da API do PNCP, o que pode levar a bloqueios temporários para requisições frequentes.
-   **Evolução do Esquema**: Embora o Pydantic forneça validação robusta, alterações no esquema da API do PNCP podem exigir atualizações manuais no modelo `Contract`.
-   **Cargas Incrementais**: O mecanismo de carregamento atual realiza upserts com base no `id`, o que lida com atualizações, mas uma estratégia de carregamento incremental mais sofisticada poderia ser implementada para conjuntos de dados muito grandes.

### Melhorias Futuras
-   **Integração com Agendador**: Integrar com um agendador (ex: Apache Airflow, Prefect ou um simples cron job) para execução automatizada e periódica do pipeline ETL.
-   **Relatórios de Erros**: Implementar integração com ferramentas de monitoramento de erros (ex: Sentry, stack ELK) para alertas em tempo real sobre falhas no ETL.
-   **Integração com Data Lake**: Adicionar suporte para armazenar dados brutos em um data lake (ex: S3, GCS) antes da transformação para arquivamento histórico e capacidade de repetição.
-   **Dashboards**: Desenvolver um dashboard interativo (ex: usando Streamlit, Dash ou Power BI) para visualizar os dados extraídos do PNCP e fornecer insights acionáveis.
-   **Otimização de Desempenho**: Para volumes de dados extremamente grandes, considerar chamadas de API assíncronas ou frameworks de processamento distribuído.
-   **Pesquisa de Texto Completo**: Implementar recursos de pesquisa de texto completo no campo `objeto` no MongoDB para permitir consultas mais flexíveis.

## Instruções de Configuração do MongoDB Atlas

Para usar o Orion, você precisa de uma conta no MongoDB Atlas e um cluster implantado. Siga estas etapas para configurar seu MongoDB Atlas:

1.  **Crie uma Conta no MongoDB Atlas**: Se você não tiver uma, inscreva-se em [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register).
2.  **Implante um Cluster Gratuito (Free Tier)**: Siga as instruções na tela para implantar um novo cluster. Um cluster M0 gratuito é suficiente para testes e uso em pequena escala.
3.  **Crie um Usuário de Banco de Dados**: Navegue até "Database Access" na seção "Security". Clique em "Add New Database User" e crie um nome de usuário e uma senha forte. Certifique-se de que este usuário tenha pelo menos privilégios de "Read and write to any database".
4.  **Configure o Acesso à Rede**: Vá para "Network Access" em "Security". Clique em "Add IP Address" e adicione seu endereço IP atual ou permita o acesso de qualquer lugar (`0.0.0.0/0`) para fins de desenvolvimento (seja cauteloso com isso em produção).
5.  **Obtenha a String de Conexão**: Vá para a página "Overview" do seu cluster. Clique em "Connect", depois em "Connect your application". Escolha Python como seu driver e copie a string de conexão fornecida. Ela será algo como:
    `mongodb+srv://<username>:<password>@<cluster-url>/<db-name>?retryWrites=true&w=majority`
6.  **Atualize o `.env`**: Cole esta string de conexão no seu arquivo `.env` para a variável `MONGO_URI`, substituindo `<username>`, `<password>`, `<cluster-url>` e `<db-name>` por suas credenciais reais e nome do banco de dados. Certifique-se de que `MONGO_DB_NAME` e `MONGO_COLLECTION_NAME` em seu `.env` correspondam aos nomes desejados para seu banco de dados e coleção.
