# 🏗️ Arquitetura do Projeto - Olist E-Commerce Analysis

Documentação técnica da arquitetura end-to-end do projeto de análise de dados.

---

## 📋 Índice

1. [Visão Geral](#visao-geral)
2. [Arquitetura de Alto Nível](#arquitetura-alto-nivel)
3. [Camadas da Arquitetura](#camadas)
4. [Fluxo de Dados](#fluxo-dados)
5. [Tecnologias Utilizadas](#tecnologias)
6. [Modelo de Dados](#modelo-dados)
7. [Infraestrutura](#infraestrutura)
8. [Segurança](#seguranca)
9. [Escalabilidade](#escalabilidade)

---

## 🎯 Visão Geral {#visao-geral}

Projeto de análise de dados de e-commerce implementando arquitetura moderna de Data Analytics com pipeline ETL, data warehouse na nuvem e dashboards interativos.

**Características:**
- ✅ Arquitetura serverless (Cloud-native)
- ✅ Pipeline ETL automatizado
- ✅ Data warehouse escalável (BigQuery)
- ✅ Análises reprodutíveis (Docker + Notebooks)
- ✅ Visualizações interativas (Looker Studio)

---

## 🏛️ Arquitetura de Alto Nível {#arquitetura-alto-nivel}
```
┌─────────────────────────────────────────────────────────────────────┐
│                          DATA SOURCES                                │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ Raw CSV Files
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       INGESTION LAYER                                │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐           │
│  │   Kaggle     │──▶│ Python ETL   │──▶│   Docker     │           │
│  │   Dataset    │   │  (pandas)    │   │  Container   │           │
│  └──────────────┘   └──────────────┘   └──────────────┘           │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ Structured Data
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      STORAGE LAYER                                   │
│  ┌────────────────────────────────────────────────────────┐         │
│  │            Google BigQuery (Data Warehouse)            │         │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │         │
│  │  │  orders  │ │customers │ │ products │ │ payments │ │         │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │         │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │         │
│  │  │  sellers │ │  reviews │ │  items   │ │geolocation│ │        │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │         │
│  └────────────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ SQL Queries
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    TRANSFORMATION LAYER                              │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐           │
│  │   Staging    │──▶│  Analytics   │──▶│ Materialized │           │
│  │    Views     │   │   Queries    │   │    Views     │           │
│  └──────────────┘   └──────────────┘   └──────────────┘           │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
┌─────────────────────────────┐   ┌─────────────────────────────┐
│     ANALYTICS LAYER         │   │   PRESENTATION LAYER        │
│  ┌────────────────────┐     │   │  ┌────────────────────┐    │
│  │  Jupyter Notebooks │     │   │  │  Looker Studio     │    │
│  │  - Cohort Analysis │     │   │  │  - Executive       │    │
│  │  - RFM Segment     │     │   │  │  - Customer        │    │
│  │  - LTV Analysis    │     │   │  │  - Product         │    │
│  │  - Category Perf   │     │   │  │  - Logistics       │    │
│  └────────────────────┘     │   │  │  - Financial       │    │
│  ┌────────────────────┐     │   │  └────────────────────┘    │
│  │  Python Scripts    │     │   │                             │
│  │  - rfm_seg.py      │     │   │  ┌────────────────────┐    │
│  │  - cohort_analysis │     │   │  │   Screenshots      │    │
│  └────────────────────┘     │   │  │   + Export PDF     │    │
└─────────────────────────────┘   │  └────────────────────┘    │
                                  └─────────────────────────────┘
                                              │
                                              ▼
                                    ┌───────────────────┐
                                    │   End Users       │
                                    │  (Web Browser)    │
                                    └───────────────────┘
```

---

## 🔄 Camadas da Arquitetura {#camadas}

### **1. Data Sources Layer**

**Fonte:** Kaggle - Brazilian E-Commerce Dataset (Olist)
```yaml
Formato: CSV files
Volume: ~117 MB (comprimido: ~35 MB)
Período: 2016-09 a 2018-08 (24 meses)
Registros: ~100k pedidos

Arquivos:
  - olist_orders_dataset.csv (99,441 registros)
  - olist_customers_dataset.csv (99,441 registros)
  - olist_order_items_dataset.csv (112,650 registros)
  - olist_products_dataset.csv (32,951 registros)
  - olist_sellers_dataset.csv (3,095 registros)
  - olist_order_payments_dataset.csv (103,886 registros)
  - olist_order_reviews_dataset.csv (99,224 registros)
  - olist_geolocation_dataset.csv (1,000,163 registros)
  - product_category_name_translation.csv (71 registros)
```

---

### **2. Ingestion Layer (ETL)**

**Pipeline ETL em Python:**
```python
# Componentes
Componentes:
├── extract_kaggle.py       # Download automático via Kaggle API
├── load_to_bigquery.py     # Carga para BigQuery
└── data_validation.py      # Validação de qualidade

Tecnologias:
- Python 3.11+
- pandas 2.0+
- google-cloud-bigquery 3.10+
- Docker 24+

Características:
✓ Idempotente (reruns seguros)
✓ Validação de schema
✓ Tratamento de erros
✓ Logging estruturado
✓ Containerizado (Docker)
```

**Fluxo ETL:**
```
1. EXTRACT
   └─ Kaggle API → Download CSVs → data/raw/

2. TRANSFORM
   ├─ Validar schema
   ├─ Remover duplicatas
   ├─ Tratar valores nulos
   ├─ Converter tipos de dados
   └─ Calcular métricas derivadas

3. LOAD
   ├─ Criar dataset BigQuery
   ├─ Definir schemas
   ├─ Carregar tabelas (batch)
   └─ Validar integridade referencial
```

---

### **3. Storage Layer (Data Warehouse)**

**Google BigQuery:**
```sql
-- Configuração
Project: your-gcp-project
Dataset: olist_ecommerce
Region: US (multi-region)
Storage: ~500 MB
Partitioning: DATE(order_purchase_timestamp)

Tabelas (8):
├── orders              # 99k rows
├── customers           # 99k rows
├── order_items         # 112k rows
├── products            # 32k rows
├── sellers             # 3k rows
├── payments            # 103k rows
├── reviews             # 99k rows
└── geolocation         # 1M rows

Views Customizadas:
├── rfm_segments        # Segmentação RFM pré-calculada
├── cohort_retention    # Matriz de retenção
├── category_performance # Performance por categoria
└── delivery_metrics    # Métricas de entrega
```

**Otimizações:**
```sql
-- 1. Particionamento
CREATE TABLE orders
PARTITION BY DATE(order_purchase_timestamp)
CLUSTER BY customer_state, order_status;

-- 2. Views Materializadas
CREATE MATERIALIZED VIEW rfm_segments AS
SELECT 
  customer_unique_id,
  recency, frequency, monetary,
  rfm_score, segment
FROM rfm_calculation;

-- 3. Clustering
CLUSTER BY customer_state, product_category_name;
```

---

### **4. Transformation Layer (SQL)**

**Estrutura:**
```
sql/
├── 01_schema/
│   ├── create_tables_bigquery.sql    # DDL: Criar tabelas
│   └── create_views.sql              # Views auxiliares
│
├── 02_transformations/
│   ├── staging_orders.sql            # Staging: Orders
│   ├── staging_customers.sql         # Staging: Customers
│   └── mart_customer_metrics.sql     # Mart: Métricas agregadas
│
└── 03_analytics/
    ├── ltv_analysis.sql              # Lifetime Value
    ├── cohort_retention.sql          # Cohort Analysis
    ├── rfm_segmentation.sql          # RFM Segments
    ├── category_performance.sql      # Categorias
    └── delivery_analysis.sql         # Logística
```

**Padrão Medallion Architecture:**
```
Bronze (Raw)          Silver (Staging)         Gold (Analytics)
─────────────────     ───────────────────      ─────────────────
olist_orders     ──▶  staging_orders      ──▶  mart_customer_ltv
olist_customers  ──▶  staging_customers   ──▶  mart_rfm_segments
olist_payments   ──▶  staging_payments    ──▶  mart_cohort_retention
```

---

### **5. Analytics Layer**

**Jupyter Notebooks:**
```
notebooks/
├── 01_exploratory_analysis.ipynb     # EDA inicial
├── 02_ltv_deep_dive.ipynb            # LTV detalhado
├── 03_cohort_retention.ipynb         # Retenção
├── 04_rfm_segmentation.ipynb         # Segmentação RFM
└── 05_category_performance.ipynb     # Categorias
```

**Python Scripts:**
```
python/analytics/
├── ltv_calculator.py                 # Scripts programáticos
├── cohort_analysis.py
├── rfm_segmentation.py
└── category_performance.py
```

**Análises Implementadas:**

| Análise | Método | Output |
|---------|--------|--------|
| **Cohort Retention** | Matriz retenção + curvas | PNG + CSV |
| **RFM Segmentation** | Quintis + regras negócio | CSV + segments |
| **LTV Analysis** | Cohort-based LTV | Métricas por estado |
| **Category Performance** | Pareto + temporal | Insights + gráficos |
| **Delivery Analysis** | Correlação atraso-NPS | Rotas problemáticas |

---

### **6. Presentation Layer**

**Looker Studio Dashboards:**
```
Dashboards (5):
├── Executive Dashboard          # KPIs alto nível
├── Customer Analytics           # LTV, Cohort, RFM
├── Product Performance          # Categorias, Pareto
├── Logistics Overview           # SLA, entregas
└── Financial Deep Dive          # Receita, pagamentos

Características:
✓ Conexão direta BigQuery
✓ Filtros interativos
✓ Auto-refresh (12h cache)
✓ Exportável (PDF/CSV)
✓ Mobile-friendly
```

---

## 🔄 Fluxo de Dados Detalhado {#fluxo-dados}

### **Pipeline Completo (End-to-End)**
```
FASE 1: INGEST (T+0h)
──────────────────────
Kaggle Dataset
    │
    ├─▶ kaggle datasets download
    │
    ▼
data/raw/*.csv (117 MB)
    │
    ├─▶ Python ETL
    │   ├── Validation
    │   ├── Type Conversion
    │   └── Deduplication
    │
    ▼
BigQuery Tables (8 tabelas)


FASE 2: TRANSFORM (T+0.5h)
──────────────────────────
BigQuery Tables
    │
    ├─▶ SQL: 01_schema/*.sql
    │   └── CREATE TABLES, VIEWS
    │
    ├─▶ SQL: 02_transformations/*.sql
    │   ├── staging_orders
    │   ├── staging_customers
    │   └── mart_customer_metrics
    │
    ├─▶ SQL: 03_analytics/*.sql
    │   ├── ltv_analysis
    │   ├── cohort_retention
    │   ├── rfm_segmentation
    │   ├── category_performance
    │   └── delivery_analysis
    │
    ▼
Analytical Views (5 views)


FASE 3: ANALYZE (T+1h)
──────────────────────
Analytical Views
    │
    ├─▶ Jupyter Notebooks
    │   ├── Load data from BigQuery
    │   ├── Advanced Analytics
    │   ├── Statistical Tests
    │   └── Generate Visualizations
    │
    ▼
Insights + Images (docs/images/)


FASE 4: VISUALIZE (T+1.5h)
──────────────────────────
BigQuery + Views
    │
    ├─▶ Looker Studio
    │   ├── Connect to BigQuery
    │   ├── Build Charts
    │   ├── Apply Filters
    │   └── Publish Dashboards
    │
    ▼
Interactive Dashboards (5 dashboards)
    │
    └─▶ End Users (Browser)
```

---

## 💻 Tecnologias Utilizadas {#tecnologias}

### **Stack Completo**

| Camada | Tecnologia | Versão | Uso |
|--------|-----------|--------|-----|
| **Data Source** | Kaggle Dataset | - | Fonte de dados |
| **Ingestion** | Python | 3.11+ | ETL scripts |
| **Ingestion** | pandas | 2.0+ | Data manipulation |
| **Ingestion** | Docker | 24+ | Containerização |
| **Storage** | Google BigQuery | - | Data Warehouse |
| **Transform** | SQL | - | Data transformation |
| **Analytics** | Jupyter | 1.0+ | Interactive analysis |
| **Analytics** | Python | 3.11+ | Statistical analysis |
| **Analytics** | scipy | 1.10+ | Correlações |
| **Analytics** | matplotlib | 3.7+ | Visualizações |
| **Analytics** | seaborn | 0.12+ | Visualizações |
| **Presentation** | Looker Studio | - | Dashboards |
| **Version Control** | Git/GitHub | - | Code versioning |
| **Documentation** | Markdown | - | Documentation |

---

### **Dependências Python**
```txt
# Core
pandas>=2.0.0
numpy>=1.24.0
google-cloud-bigquery>=3.10.0
python-dotenv>=1.0.0

# Analytics
scipy>=1.10.0
scikit-learn>=1.3.0
matplotlib>=3.7.0
seaborn>=0.12.0

# Jupyter
jupyter>=1.0.0
ipykernel>=6.25.0

# Dev/Test
pytest>=7.4.0
pytest-cov>=4.1.0
```

---

## 🗄️ Modelo de Dados {#modelo-dados}

### **Entity Relationship Diagram (ERD)**
```
┌─────────────────┐
│    customers    │
│─────────────────│
│ customer_id (PK)│◀────┐
│ customer_unique │     │
│ customer_state  │     │
└─────────────────┘     │
                        │
                        │
┌─────────────────┐     │
│     orders      │     │
│─────────────────│     │
│ order_id (PK)   │     │
│ customer_id (FK)│─────┘
│ order_status    │
│ purchase_date   │◀────┐
│ delivered_date  │     │
└─────────────────┘     │
         │              │
         │              │
         │              │
    ┌────┴────┐    ┌────┴────┐
    │         │    │         │
    ▼         ▼    ▼         ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│order_   │ │order_   │ │order_   │
│items    │ │payments │ │reviews  │
│─────────│ │─────────│ │─────────│
│order_id │ │order_id │ │order_id │
│product_ │ │payment_ │ │review_  │
│seller_id│ │type     │ │score    │
└─────────┘ └─────────┘ └─────────┘
    │
    │
    ▼
┌─────────────┐
│  products   │
│─────────────│
│ product_id  │
│ category    │
└─────────────┘
    
    
┌─────────────┐
│   sellers   │
│─────────────│
│ seller_id   │
│ seller_state│
└─────────────┘
```

---

### **Tabelas e Relacionamentos**

**1. customers (99k registros)**
```sql
customer_id (PK)              STRING
customer_unique_id            STRING
customer_zip_code_prefix      STRING
customer_city                 STRING
customer_state                STRING
```

**2. orders (99k registros)**
```sql
order_id (PK)                     STRING
customer_id (FK → customers)      STRING
order_status                      STRING
order_purchase_timestamp          TIMESTAMP
order_approved_at                 TIMESTAMP
order_delivered_carrier_date      TIMESTAMP
order_delivered_customer_date     TIMESTAMP
order_estimated_delivery_date     TIMESTAMP
```

**3. order_items (112k registros)**
```sql
order_id (FK → orders)        STRING
order_item_id                 INTEGER
product_id (FK → products)    STRING
seller_id (FK → sellers)      STRING
shipping_limit_date           TIMESTAMP
price                         FLOAT
freight_value                 FLOAT
```

**4. products (32k registros)**
```sql
product_id (PK)                   STRING
product_category_name             STRING
product_name_length               INTEGER
product_description_length        INTEGER
product_photos_qty                INTEGER
product_weight_g                  INTEGER
product_length_cm                 INTEGER
product_height_cm                 INTEGER
product_width_cm                  INTEGER
```

**5. sellers (3k registros)**
```sql
seller_id (PK)                STRING
seller_zip_code_prefix        STRING
seller_city                   STRING
seller_state                  STRING
```

**6. order_payments (103k registros)**
```sql
order_id (FK → orders)        STRING
payment_sequential            INTEGER
payment_type                  STRING
payment_installments          INTEGER
payment_value                 FLOAT
```

**7. order_reviews (99k registros)**
```sql
review_id (PK)                STRING
order_id (FK → orders)        STRING
review_score                  INTEGER
review_comment_title          STRING
review_comment_message        STRING
review_creation_date          TIMESTAMP
review_answer_timestamp       TIMESTAMP
```

**8. geolocation (1M registros)**
```sql
geolocation_zip_code_prefix   STRING
geolocation_lat               FLOAT
geolocation_lng               FLOAT
geolocation_city              STRING
geolocation_state             STRING
```

---

### **Cardinalidade dos Relacionamentos**
```
customers (1) ──< orders (N)
orders (1) ──< order_items (N)
orders (1) ──< order_payments (N)
orders (1) ──< order_reviews (N)
products (1) ──< order_items (N)
sellers (1) ──< order_items (N)
```

---

## 🏢 Infraestrutura {#infraestrutura}

### **Ambiente de Desenvolvimento**
```yaml
Local Development:
  OS: Linux/MacOS/Windows
  Python: 3.11+
  Docker: 24+
  Git: 2.40+
  IDE: VSCode/PyCharm/Jupyter Lab
  
Dependencies:
  - virtualenv (ambiente Python isolado)
  - Docker Compose (orquestração containers)
  - Kaggle CLI (download datasets)
```

---

### **Google Cloud Platform**
```yaml
Services Used:
  - BigQuery: Data Warehouse
  - Cloud Storage: Backup opcional
  - IAM: Gerenciamento de acesso
  - Cloud Scheduler: Automação (opcional)
  
Billing:
  - BigQuery Free Tier: 1TB queries/mês
  - Storage Free Tier: 10GB
  - Custo estimado: $0-5/mês (free tier)
```

---

### **Containerização (Docker)**
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "python/etl/load_to_bigquery.py"]
```
```yaml
# docker-compose.yml
version: '3.8'

services:
  etl:
    build: .
    env_file: .env
    volumes:
      - ./data:/app/data
      - ./keys:/app/keys
    command: python python/etl/load_to_bigquery.py
  
  jupyter:
    build: .
    ports:
      - "8888:8888"
    volumes:
      - ./notebooks:/app/notebooks
    command: jupyter lab --ip=0.0.0.0 --allow-root
```

---

## 🔒 Segurança {#seguranca}

### **Autenticação e Autorização**
```yaml
Google Cloud (IAM):
  Service Account:
    - Nome: ecommerce-etl-sa
    - Roles:
      - BigQuery Data Editor
      - BigQuery Job User
      - BigQuery Read Session User
  
  Credentials:
    - Tipo: JSON key file
    - Localização: keys/gcp-key.json
    - Git: .gitignore (não commitar)
```

---

### **Dados Sensíveis**
```yaml
PII (Personally Identifiable Information):
  Masking:
    - customer_id: Hash MD5
    - order_id: Últimos 4 dígitos apenas
    - email: Não disponível no dataset
  
  Acesso:
    - Produção: Row-level security
    - Desenvolvimento: Dados anonimizados
    - Dashboards públicos: Agregados apenas
```

---

### **Boas Práticas**
```bash
✓ Credenciais em .env (nunca hardcoded)
✓ Service accounts com menor privilégio
✓ Secrets não versionados (gitignore)
✓ HTTPS apenas para APIs
✓ Audit logs habilitados
✓ Backup regular dos dados

✗ Não commitar keys/tokens
✗ Não expor BigQuery publicamente
✗ Não usar credenciais pessoais em produção
```

---

## 📈 Escalabilidade {#escalabilidade}

### **Dimensionamento Vertical**
```yaml
BigQuery:
  Storage: Escalável automaticamente
  Compute: On-demand, pago por query
  Limits:
    - 1000 concurrent queries
    - 6 hours max query time
    - 100TB max table size
```

---

### **Otimizações de Performance**
```sql
-- 1. Particionamento
CREATE TABLE orders
PARTITION BY DATE(order_purchase_timestamp)
OPTIONS(
  partition_expiration_days=730,
  require_partition_filter=true
);

-- 2. Clustering
CREATE TABLE orders
PARTITION BY DATE(order_purchase_timestamp)
CLUSTER BY customer_state, order_status;

-- 3. Materialized Views
CREATE MATERIALIZED VIEW daily_metrics
OPTIONS(
  enable_refresh=true,
  refresh_interval_minutes=60
) AS
SELECT 
  DATE(order_purchase_timestamp) as date,
  COUNT(*) as orders,
  SUM(payment_value) as revenue
FROM orders
GROUP BY date;
```

---

### **Estratégia de Crescimento**
```yaml
Cenário Atual (100k pedidos):
  - Storage: ~500 MB
  - Query cost: ~$0/mês (free tier)
  - ETL time: ~5 min
  
Cenário 1M pedidos (10x):
  - Storage: ~5 GB
  - Query cost: ~$5/mês
  - ETL time: ~30 min
  - Solução: Batch processing, incremental loads
  
Cenário 10M pedidos (100x):
  - Storage: ~50 GB
  - Query cost: ~$50/mês
  - ETL time: ~3 hours
  - Solução: Airflow, Spark, streaming ETL
```

---

## 🔄 CI/CD e Automação

### **Pipeline Automatizado (Futuro)**
```yaml
GitHub Actions Workflow:
  Trigger: Push to main
  Steps:
    1. Run tests (pytest)
    2. Validate SQL syntax
    3. Deploy to BigQuery (staging)
    4. Run data quality checks
    5. Deploy to BigQuery (production)
    6. Refresh dashboards
    7. Send notification (Slack/Email)
```

---

## 📊 Monitoramento
```yaml
Métricas Monitoradas:
  - ETL success rate
  - Query performance (p50, p90, p95)
  - Storage size
  - Costs (BigQuery billing)
  - Dashboard usage (GA)
  - Data freshness
  
Alertas:
  - ETL failure → Email
  - Query cost > $50/mês → Email
  - Data lag > 24h → Slack
```

---

## 📚 Referências

- **BigQuery Docs:** https://cloud.google.com/bigquery/docs
- **Looker Studio:** https://support.google.com/looker-studio
- **Docker:** https://docs.docker.com/
- **pandas:** https://pandas.pydata.org/docs/
- **Kaggle API:** https://github.com/Kaggle/kaggle-api

---

## 🔗 Links Relacionados

- **Repositório GitHub:** https://github.com/AndreBomfim99/analise23
- **Dashboards:** [looker_studio_links.md](../dashboards/looker_studio_links.md)
- **Metodologia:** [methodology.md](methodology.md)
- **Business Insights:** [business_insights.md](business_insights.md)

---

**Última atualização:** Novembro 2024  
**Versão:** 1.0  
**Autor:** André Bomfim