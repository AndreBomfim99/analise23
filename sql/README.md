# 📊 SQL - Olist E-Commerce Analytics

Estrutura completa de SQL para análise de dados de e-commerce.

**Arquitetura:** `raw → staging → marts → analytics`

---

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Estrutura de Pastas](#estrutura-de-pastas)
- [Quick Start](#quick-start)
- [Arquitetura de Dados](#arquitetura-de-dados)
- [Recursos](#recursos)

---

## 🎯 Visão Geral

Este diretório contém toda a lógica SQL do projeto, organizada em camadas seguindo as **melhores práticas de Data Engineering**.

### Estatísticas

- **📁 3 camadas** de dados (schema, transformations, analytics)
- **🗄️ 8 tabelas** raw (fonte: Kaggle)
- **🔄 3 tabelas** staging (limpeza e enrichment)
- **📊 1 mart** principal (customer 360)
- **🔍 48 queries** analytics prontas
- **📈 8 views** auxiliares

### Tecnologias

- **Google BigQuery** - Data Warehouse
- **SQL Standard** - ANSI SQL com extensões BigQuery
- **Window Functions** - Análises temporais avançadas
- **CTEs** - Common Table Expressions para legibilidade
- **Particionamento** - Otimização de performance
- **Clustering** - Queries mais rápidas

---

## 📁 Estrutura de Pastas

```
sql/
│
├── 01_schema/                          # Schema & DDL
│   ├── create_tables_bigquery.sql      # DDL de 8 tabelas + 2 views
│   ├── create_views.sql                # 8 views auxiliares
│   └── README.md                       # Documentação do schema
│
├── 02_transformations/                 # Staging & Marts
│   ├── staging_orders.sql              # Pedidos limpos
│   ├── staging_customers.sql           # Clientes limpos + geo
│   ├── staging_order_items.sql         # Itens limpos + enrichment
│   ├── mart_customer_metrics.sql       # Customer 360 (60+ métricas)
│   └── README.md                       # Doc transformações
│
├── 03_analytics/                       # Análises de Negócio
│   ├── ltv_analysis.sql                # 7 análises LTV
│   ├── cohort_retention.sql            # 10 análises retenção
│   ├── rfm_segmentation.sql            # 6 análises RFM
│   ├── category_performance.sql        # 8 análises categoria
│   ├── delivery_analysis.sql           # 8 análises logística
│   ├── payment_analysis.sql            # 9 análises pagamento
│   └── README.md                       # Doc analytics
│
└── README.md                           # Esta documentação
```

---

## 🚀 Quick Start

### 1️⃣ Criar Schema (5 min)

```bash
# No BigQuery Console ou via bq CLI
bq query --use_legacy_sql=false < sql/01_schema/create_tables_bigquery.sql
bq query --use_legacy_sql=false < sql/01_schema/create_views.sql
```

**Ou via Python:**
```python
from python.utils.bigquery_helper import BigQueryHelper

helper = BigQueryHelper()
helper.run_sql_file('sql/01_schema/create_tables_bigquery.sql')
helper.run_sql_file('sql/01_schema/create_views.sql')
```

### 2️⃣ Carregar Dados (10 min)

```bash
# Via script Python ETL
docker exec -it ecommerce-python python python/etl/load_to_bigquery.py
```

### 3️⃣ Criar Transformações (5 min)

```bash
# Staging
bq query --use_legacy_sql=false < sql/02_transformations/staging_orders.sql
bq query --use_legacy_sql=false < sql/02_transformations/staging_customers.sql
bq query --use_legacy_sql=false < sql/02_transformations/staging_order_items.sql

# Marts
bq query --use_legacy_sql=false < sql/02_transformations/mart_customer_metrics.sql
```

### 4️⃣ Executar Análises

```bash
# Escolha uma análise
bq query --use_legacy_sql=false < sql/03_analytics/ltv_analysis.sql

# Ou todas
for file in sql/03_analytics/*.sql; do
  bq query --use_legacy_sql=false < "$file"
done
```

**Pronto!** 🎉 Você agora tem:
- ✅ 8 tabelas raw carregadas
- ✅ 3 stagings otimizadas
- ✅ 1 mart customer 360
- ✅ 48 queries analytics executadas

---

## 🏗️ Arquitetura de Dados

### Fluxo Completo

```
┌─────────────────────────────────────────────────────────────────┐
│                          KAGGLE                                 │
│                   brazilian-ecommerce                           │
│                     (8 arquivos CSV)                            │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ ETL (Python)
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                     01_SCHEMA (Raw Tables)                      │
│                                                                 │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ │
│  │ customers  │ │   orders   │ │order_items │ │  products  │ │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘ │
│                                                                 │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ │
│  │  sellers   │ │  payments  │ │  reviews   │ │translation │ │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘ │
│                                                                 │
│  + 8 views auxiliares (vw_orders_complete, etc.)               │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ Transformations
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              02_TRANSFORMATIONS (Staging & Marts)               │
│                                                                 │
│  STAGING (Limpeza + Enrichment):                               │
│  ┌─────────────────────────────────────────────────────┐       │
│  │ stg_orders                                          │       │
│  │  - Validação de timeline                           │       │
│  │  - Métricas temporais (delivery_days, delay)       │       │
│  │  - Sazonalidade (Black Friday, etc)                │       │
│  └─────────────────────────────────────────────────────┘       │
│                                                                 │
│  ┌─────────────────────────────────────────────────────┐       │
│  │ stg_customers + stg_customers_master                │       │
│  │  - Deduplicação (customer_unique_id)               │       │
│  │  - Geo enrichment (região, metro area)             │       │
│  │  - GDP tier, distância de SP                       │       │
│  └─────────────────────────────────────────────────────┘       │
│                                                                 │
│  ┌─────────────────────────────────────────────────────┐       │
│  │ stg_order_items                                     │       │
│  │  - Product + Seller + Customer enrichment          │       │
│  │  - Margem estimada, logística                      │       │
│  │  - Tiers (price, weight, margin)                   │       │
│  └─────────────────────────────────────────────────────┘       │
│                                                                 │
│  MARTS (Agregações de Negócio):                                │
│  ┌─────────────────────────────────────────────────────┐       │
│  │ mart_customer_metrics                               │       │
│  │  - 60+ métricas por customer_unique_id             │       │
│  │  - LTV, RFM scores, segmentação automática         │       │
│  │  - Churn probability, projected CLV                │       │
│  │  + 3 views: top/at_risk/churned customers          │       │
│  └─────────────────────────────────────────────────────┘       │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ Analytics
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                  03_ANALYTICS (Queries BI)                      │
│                                                                 │
│  48 queries prontas em 6 arquivos:                             │
│                                                                 │
│  📊 ltv_analysis.sql              (7 queries)                   │
│  📊 cohort_retention.sql          (10 queries)                  │
│  📊 rfm_segmentation.sql          (6 queries)                   │
│  📊 category_performance.sql      (8 queries)                   │
│  📊 delivery_analysis.sql         (8 queries)                   │
│  📊 payment_analysis.sql          (9 queries)                   │
│                                                                 │
│  Outputs: Dashboards Looker Studio, Reports, Insights          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📚 Recursos por Camada

### 🗄️ 01_SCHEMA

**O que tem:**
- DDL completo de 8 tabelas
- Schema otimizado (particionamento, clustering)
- 8 views auxiliares para queries comuns
- Documentação detalhada

**Quando usar:**
- Setup inicial do projeto
- Recrear tabelas
- Consultar estrutura de dados

**[📖 Ver documentação completa →](01_schema/README.md)**

---

### 🔄 02_TRANSFORMATIONS

**O que tem:**
- 3 stagings (orders, customers, order_items)
- 1 mart principal (customer_metrics)
- Lógica estilo dbt (modular, testável)
- 60+ métricas calculadas

**Quando usar:**
- Após carregar dados raw
- Para preparar dados para analytics
- Criar customer 360 view

**[📖 Ver documentação completa →](02_transformations/README.md)**

---

### 📊 03_ANALYTICS

**O que tem:**
- 48 queries de análise de negócio
- 6 arquivos temáticos
- Insights e recomendações
- Queries prontas para dashboard

**Quando usar:**
- Análises ad-hoc
- Criar dashboards no Looker Studio
- Gerar relatórios executivos
- Responder perguntas de negócio

**[📖 Ver documentação completa →](03_analytics/README.md)**

---

## 🎯 Casos de Uso

### 💼 Para Analistas de Negócio

```sql
-- LTV por estado (top 10)
SELECT customer_state, avg_ltv, total_customers, gmv_share_pct
FROM ltv_by_state
ORDER BY avg_ltv DESC LIMIT 10;

-- Clientes em risco (win-back campaign)
SELECT * FROM vw_at_risk_customers 
WHERE lifetime_value > 200
ORDER BY lifetime_value DESC;

-- Performance de categorias
SELECT category, revenue, avg_nps, category_status
FROM category_summary
WHERE revenue > 50000
ORDER BY revenue DESC;
```

### 👨‍💻 Para Engenheiros de Dados

```python
from python.utils.bigquery_helper import BigQueryHelper

helper = BigQueryHelper()

# Pipeline completo
helper.run_sql_file('sql/01_schema/create_tables_bigquery.sql')
helper.run_sql_file('sql/02_transformations/staging_orders.sql')
helper.run_sql_file('sql/02_transformations/mart_customer_metrics.sql')

# Validar
assert helper.count_rows('stg_orders') > 90000
assert helper.count_rows('mart_customer_metrics') > 90000
```

### 📊 Para Cientistas de Dados

```python
import pandas as pd
from python.utils.bigquery_helper import BigQueryHelper

helper = BigQueryHelper()

# Extrair dados limpos para ML
query = """
SELECT 
  recency_days,
  total_orders,
  lifetime_value,
  avg_review_score,
  churn_probability
FROM mart_customer_metrics
WHERE recency_days <= 365
"""

df = helper.query_to_dataframe(query)

# Treinar modelo de churn
from sklearn.ensemble import RandomForestClassifier
# ...
```

---

## ⚡ Performance Tips

### 1. Use Particionamento

```sql
-- ✅ BOM - Usa partição
WHERE DATE(order_purchase_timestamp) >= '2018-01-01'

-- ❌ RUIM - Full scan
WHERE EXTRACT(YEAR FROM order_purchase_timestamp) = 2018
```

### 2. Limite Resultados Exploratórios

```sql
-- Para testes
SELECT * FROM large_table LIMIT 1000;
```

### 3. Use APPROX_QUANTILES para Percentis

```sql
-- Mais rápido que percentil exato
APPROX_QUANTILES(value, 100)[OFFSET(90)]  -- P90
```

### 4. Aproveite Clustering

```sql
-- Queries eficientes em tabelas clustered
WHERE customer_state = 'SP'  -- stg_customers é clustered por state
```

### 5. Evite SELECT *

```sql
-- Específico = mais rápido
SELECT customer_id, lifetime_value 
FROM mart_customer_metrics;
```

---

## 🔗 Integração

### Looker Studio

1. Conectar BigQuery como fonte
2. Usar views ou queries customizadas
3. Criar dashboards interativos

**Queries recomendadas:**
- `vw_top_customers` (Champions)
- `mart_customer_metrics` (Customer 360)
- Queries de `03_analytics/` (KPIs)

### Python Analytics

```python
from python.analytics.ltv_calculator import LTVCalculator
from python.analytics.cohort_analysis import CohortAnalyzer
from python.analytics.rfm_segmentation import RFMAnalyzer

# LTV
ltv_calc = LTVCalculator(project_id, dataset_id)
ltv_df = ltv_calc.calculate_historical_ltv()

# Cohort
cohort = CohortAnalyzer(project_id, dataset_id)
retention = cohort.calculate_retention_matrix()

# RFM
rfm = RFMAnalyzer(project_id, dataset_id)
segments = rfm.run_full_analysis()
```

---

## 🧪 Testes de Qualidade

Cada arquivo SQL inclui testes comentados:

```sql
/*
-- Teste 1: Primary key única
SELECT COUNT(*) - COUNT(DISTINCT order_id) 
FROM stg_orders;
-- Esperado: 0

-- Teste 2: Valores válidos
SELECT COUNTIF(price < 0) 
FROM stg_order_items;
-- Esperado: 0
*/
```

**Executar todos os testes:**
```bash
python python/etl/data_validation.py
```

---

## 📈 Métricas do Projeto

| Métrica | Valor |
|---------|-------|
| **Tabelas Raw** | 8 |
| **Staging Tables** | 3 |
| **Marts** | 1 |
| **Views** | 11 |
| **Analytics Queries** | 48 |
| **Linhas de SQL** | ~5.000+ |
| **Queries Complexas** | 25+ |
| **CTEs Utilizadas** | 150+ |

---

## 🎓 Aprendizados & Best Practices

### ✅ O que Fizemos Certo

1. **Separação de Camadas** - raw/staging/marts/analytics
2. **Documentação Inline** - Cada query é autoexplicativa
3. **Otimização** - Particionamento e clustering
4. **Modularidade** - Queries reutilizáveis
5. **Testes** - Validações inline
6. **Nomenclatura** - Padrões consistentes

### 📚 Padrões Seguidos

- **dbt Style** - Staging → Marts
- **SQL Standard** - ANSI SQL com extensões BigQuery
- **Naming Convention** - snake_case, prefixos claros
- **CTEs** - Para legibilidade
- **Comments** - Explicar "porquê", não "o quê"

---

## 🔮 Próximos Passos

**Possíveis Expansões:**

- [ ] Adicionar `mart_product_metrics`
- [ ] Adicionar `mart_seller_metrics`
- [ ] Criar análises de NLP em reviews
- [ ] Implementar forecast com time series
- [ ] Adicionar análises de basket (market basket)
- [ ] Integrar dbt para orquestração
- [ ] CI/CD para testes automatizados

---

## 📞 Suporte

**Documentação Relacionada:**
- [Schema & Tables →](01_schema/README.md)
- [Transformations →](02_transformations/README.md)
- [Analytics →](03_analytics/README.md)

**Referências Externas:**
- [BigQuery SQL Reference](https://cloud.google.com/bigquery/docs/reference/standard-sql)
- [dbt Best Practices](https://docs.getdbt.com/guides/best-practices)
- [Data Warehouse Toolkit](https://www.kimballgroup.com/)

---

## 🤝 Contribuindo

Para adicionar novas queries:

1. ✅ Escolher camada correta (schema/transformations/analytics)
2. ✅ Seguir padrões de nomenclatura
3. ✅ Adicionar comentários inline
4. ✅ Incluir testes de validação
5. ✅ Documentar no README apropriado
6. ✅ Atualizar este README se necessário

---

**Autor:** Andre Bomfim  
**Última Atualização:** Outubro 2025  
**Versão:** 1.0  
**Status:** ✅ Production Ready