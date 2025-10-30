# 🔄 SQL Transformations - Staging & Marts

Camada de transformação de dados seguindo padrão **dbt** (Data Build Tool).

**Arquitetura:** `raw → staging → marts`

---

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Camada Staging](#camada-staging)
- [Camada Marts](#camada-marts)
- [Fluxo de Dados](#fluxo-de-dados)
- [Como Usar](#como-usar)

---

## 🎯 Visão Geral

Esta pasta contém transformações SQL que convertem dados **raw** (brutos) em dados **analytics-ready** (prontos para análise).

### Princípios

1. **Staging**: Limpeza e enriquecimento dos dados brutos
2. **Marts**: Agregações e métricas de negócio
3. **Idempotência**: Queries podem ser executadas múltiplas vezes
4. **Documentação**: Cada query é auto-documentada
5. **Testes**: Queries incluem validações inline

---

## 📊 Camada Staging

**Objetivo:** Limpar, padronizar e enriquecer dados brutos.

### Arquivos

```
02_transformations/
├── staging_orders.sql              # Pedidos limpos + métricas temporais
├── staging_customers.sql           # Clientes limpos + geo enrichment
├── staging_order_items.sql         # Itens limpos + produto/seller details
└── README.md                       # Esta documentação
```

### staging_orders.sql

**Fonte:** `orders` (raw)  
**Destino:** `stg_orders`  
**Grão:** 1 linha por pedido

**Transformações:**
- ✅ Limpeza de status (lowercase, trim)
- ✅ Validação de timeline (purchase → approval → delivery)
- ✅ Cálculo de métricas de tempo (days_to_delivery, delay_days)
- ✅ Enrichment temporal (year, month, quarter, period_of_day)
- ✅ Flags de qualidade (is_delayed, is_weekend, is_extreme_delivery)
- ✅ Sazonalidade (Black Friday, Natal, etc)
- ✅ Cohort month (primeira compra)

**Particionamento:** `order_date`  
**Clustering:** `customer_id`, `order_status`, `order_year_month`

**Como usar:**
```sql
-- Pedidos entregues em 2018
SELECT * FROM stg_orders 
WHERE order_year = 2018 AND order_status = 'delivered';

-- Pedidos com atraso
SELECT * FROM stg_orders 
WHERE delivery_status = 'Delayed';

-- Black Friday
SELECT * FROM stg_orders 
WHERE seasonal_period = 'Black Friday / Natal';
```

---

### staging_customers.sql

**Fonte:** `customers` (raw)  
**Destino:** `stg_customers` + `stg_customers_master` (view)

**Grão:** 
- `stg_customers`: 1 linha por customer_id (~99k)
- `stg_customers_master`: 1 linha por customer_unique_id (~96k)

**Transformações:**
- ✅ Padronização (CEP com leading zeros, uppercase city/state)
- ✅ Categorização geográfica (região, capital/interior)
- ✅ Mapeamento de áreas metropolitanas (SP, RJ, BH, POA, Curitiba)
- ✅ Enrichment econômico (GDP tier, população, distância de SP)
- ✅ Deduplicação (tratamento de múltiplos customer_ids)
- ✅ Validação de CEP

**Features especiais:**
- Identifica 5 principais áreas metropolitanas do Brasil
- Classifica estados por PIB per capita
- Calcula distância lógica de São Paulo

**Como usar:**
```sql
-- Clientes únicos (para análise de LTV)
SELECT * FROM stg_customers_master;

-- Clientes de São Paulo capital
SELECT * FROM stg_customers 
WHERE customer_city = 'SAO PAULO' AND customer_location_type = 'Capital';

-- Área metropolitana de SP
SELECT * FROM stg_customers 
WHERE customer_metro_area = 'São Paulo Metro';

-- Clientes com múltiplos IDs (investigação)
SELECT * FROM stg_customers 
WHERE has_multiple_ids = TRUE;
```

---

### staging_order_items.sql

**Fonte:** `order_items`, `products`, `sellers`, `orders`, `customers` (raw)  
**Destino:** `stg_order_items`

**Grão:** 1 linha por item de pedido (~112k)

**Transformações:**
- ✅ Validação financeira (price >= 0, freight >= 0)
- ✅ Enrichment de produto (categoria, peso, volume, qualidade)
- ✅ Enrichment de seller (localização, região)
- ✅ Enrichment de customer (via order)
- ✅ Métricas de margem estimada (price - freight)
- ✅ Logística (same state, same region, distance category)
- ✅ Tiers (price, weight, margin)

**Particionamento:** `order_date`  
**Clustering:** `category_english`, `seller_state`, `customer_state`, `price_tier`

**Como usar:**
```sql
-- Itens por categoria
SELECT category_english, COUNT(*) as items, SUM(price) as revenue
FROM stg_order_items 
WHERE order_status = 'delivered'
GROUP BY category_english
ORDER BY revenue DESC;

-- Itens com alta margem
SELECT * FROM stg_order_items 
WHERE margin_tier LIKE 'High%';

-- Logística same-state
SELECT is_same_state_shipping, COUNT(*), AVG(freight_value)
FROM stg_order_items
GROUP BY is_same_state_shipping;

-- Produtos pesados
SELECT * FROM stg_order_items 
WHERE is_heavy_item = TRUE;
```

---

## 🏢 Camada Marts

**Objetivo:** Criar tabelas analytics-ready com métricas de negócio.

### Arquivos

```
02_transformations/
├── mart_customer_metrics.sql       # Customer 360 (LTV, RFM, behavior)
└── README.md
```

### mart_customer_metrics.sql

**Fontes:** `stg_customers_master`, `stg_orders`, `payments`, `reviews`  
**Destino:** `mart_customer_metrics`

**Grão:** 1 linha por customer_unique_id (~96k)

**Métricas incluídas (60+):**

**Pedidos:**
- total_orders, delivered_orders, canceled_orders
- cancel_rate_pct

**Temporais:**
- first_order_date, last_order_date
- recency_days, customer_lifetime_days
- cohort_month, orders_per_day, avg_days_between_orders

**Monetárias:**
- lifetime_value, avg_order_value, min/max/median
- stddev_order_value

**Satisfação:**
- avg_review_score, total_reviews, positive_review_rate_pct

**Entrega:**
- avg_delivery_days, avg_delivery_delay, delivery_delay_rate_pct

**Pagamento:**
- preferred_payment_method, avg_installments, credit_card_usage_pct

**Segmentações automáticas:**
- frequency_segment (One-time, Repeat, Loyal, Champion)
- ltv_segment (Low/Medium/High Value, VIP)
- recency_segment (Active, At Risk, Dormant, Lost)
- RFM scores (R_score, F_score, M_score: 1-5)
- customer_health_status

**Flags:**
- is_promoter, is_detractor, has_delivery_issues, is_vip

**Métricas avançadas:**
- projected_clv (LTV projetado)
- churn_probability (0.10 - 0.95)

**Clustering:** `customer_state`, `frequency_segment`, `ltv_segment`, `recency_segment`

**Views derivadas:**
- `vw_top_customers` - Champions e VIPs
- `vw_at_risk_customers` - Para campanhas de retenção
- `vw_churned_customers` - Para win-back campaigns

**Como usar:**
```sql
-- Customer 360
SELECT * FROM mart_customer_metrics 
WHERE customer_unique_id = 'abc123';

-- Top clientes
SELECT * FROM vw_top_customers 
ORDER BY lifetime_value DESC LIMIT 100;

-- Clientes em risco (alta prioridade)
SELECT * FROM vw_at_risk_customers 
WHERE ltv_segment IN ('High Value', 'VIP')
ORDER BY lifetime_value DESC;

-- Champions por estado
SELECT customer_state, COUNT(*), AVG(lifetime_value)
FROM mart_customer_metrics 
WHERE frequency_segment = 'Champion'
GROUP BY customer_state;

-- Análise de churn
SELECT 
  recency_segment,
  COUNT(*) as customers,
  AVG(churn_probability) as avg_churn_prob,
  SUM(lifetime_value) as revenue_at_risk
FROM mart_customer_metrics
GROUP BY recency_segment
ORDER BY avg_churn_prob DESC;
```

---

## 🔄 Fluxo de Dados

```
┌─────────────────────────────────────────────────────────────┐
│                         RAW LAYER                           │
│  (Tabelas originais carregadas do Kaggle via ETL)          │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                      STAGING LAYER                          │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │stg_orders    │  │stg_customers │  │stg_order_    │     │
│  │              │  │              │  │items         │     │
│  │- Limpeza     │  │- Limpeza     │  │- Limpeza     │     │
│  │- Validação   │  │- Geo enrich  │  │- Enrichment  │     │
│  │- Enrichment  │  │- Dedup       │  │- Logística   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                       MARTS LAYER                           │
│                                                             │
│  ┌──────────────────────────────────────────────────┐      │
│  │        mart_customer_metrics                     │      │
│  │                                                  │      │
│  │  - 60+ métricas agregadas                       │      │
│  │  - Segmentações automáticas                     │      │
│  │  - RFM scores                                   │      │
│  │  - Churn probability                            │      │
│  │  - Projected CLV                                │      │
│  └──────────────────────────────────────────────────┘      │
│                                                             │
│  Views:                                                     │
│  - vw_top_customers                                         │
│  - vw_at_risk_customers                                     │
│  - vw_churned_customers                                     │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                      ANALYTICS LAYER                        │
│          (sql/03_analytics/*.sql)                          │
│                                                             │
│  - ltv_analysis.sql                                         │
│  - cohort_retention.sql                                     │
│  - rfm_segmentation.sql                                     │
│  - category_performance.sql                                 │
│  - delivery_analysis.sql                                    │
│  - payment_analysis.sql                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Como Usar

### 1. Criar Staging Tables

```bash
# No BigQuery Console ou via bq CLI

# Staging Orders
bq query --use_legacy_sql=false < sql/02_transformations/staging_orders.sql

# Staging Customers
bq query --use_legacy_sql=false < sql/02_transformations/staging_customers.sql

# Staging Order Items
bq query --use_legacy_sql=false < sql/02_transformations/staging_order_items.sql
```

### 2. Criar Marts

```bash
# Customer Metrics Mart
bq query --use_legacy_sql=false < sql/02_transformations/mart_customer_metrics.sql
```

### 3. Uso via Python

```python
from python.utils.bigquery_helper import BigQueryHelper

helper = BigQueryHelper()

# Executar transformações
helper.run_sql_file('sql/02_transformations/staging_orders.sql')
helper.run_sql_file('sql/02_transformations/staging_customers.sql')
helper.run_sql_file('sql/02_transformations/staging_order_items.sql')
helper.run_sql_file('sql/02_transformations/mart_customer_metrics.sql')

# Validar
print(helper.count_rows('stg_orders'))
print(helper.count_rows('mart_customer_metrics'))
```

---

## 🧪 Testes de Qualidade

Cada arquivo SQL inclui seção de testes comentada. Descomente para validar:

```sql
/*
-- Teste 1: Nenhum order_id nulo
SELECT COUNT(*) FROM stg_orders WHERE order_id IS NULL;
-- Esperado: 0

-- Teste 2: Timeline válida
SELECT COUNT(*) FROM stg_orders WHERE is_valid_timeline = FALSE;
-- Esperado: < 1% do total
*/
```

---

## 📈 Frequência de Atualização Recomendada

| Tabela | Frequência | Motivo |
|--------|-----------|--------|
| `stg_orders` | Diária | Pedidos novos |
| `stg_customers` | Semanal | Cadastro estável |
| `stg_order_items` | Diária | Sincronizar com orders |
| `mart_customer_metrics` | Diária | Métricas de negócio |

---

## 🔍 Dependências

```
staging_orders
  └─ requires: orders (raw)

staging_customers
  └─ requires: customers (raw)

staging_order_items
  └─ requires: order_items, products, sellers, orders, customers (raw)

mart_customer_metrics
  └─ requires: stg_customers_master, stg_orders, payments, reviews
```

---

## 📚 Referências

- [dbt Best Practices](https://docs.getdbt.com/guides/best-practices)
- [BigQuery Partitioning](https://cloud.google.com/bigquery/docs/partitioned-tables)
- [BigQuery Clustering](https://cloud.google.com/bigquery/docs/clustered-tables)

---

## 🤝 Contribuindo

Ao adicionar novas transformações:

1. Seguir padrão `staging_*` ou `mart_*`
2. Incluir comentários inline
3. Adicionar seção de testes
4. Documentar no README
5. Definir particionamento/clustering apropriado

---

**Última atualização:** Outubro 2025  
**Versão:** 1.0