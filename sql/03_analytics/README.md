# 📊 SQL Analytics - Business Intelligence Queries

Análises SQL avançadas para insights de negócio do e-commerce Olist.

**48 queries prontas para análise** em 6 arquivos principais.

---

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Arquivos de Análise](#arquivos-de-análise)
- [Como Usar](#como-usar)
- [Casos de Uso](#casos-de-uso)

---

## 🎯 Visão Geral

Esta pasta contém queries SQL prontas para análises de negócio complexas. Cada arquivo é independente e pode ser executado diretamente no BigQuery.

### Características

- ✅ **SQL Avançado**: Window Functions, CTEs recursivas, APPROX_QUANTILES
- ✅ **Auto-documentadas**: Comentários inline explicando lógica
- ✅ **Insights incluídos**: Seção final com recomendações de negócio
- ✅ **Otimizadas**: Uso eficiente de particionamento e clustering
- ✅ **Prontas para dashboard**: Resultados formatados para Looker Studio

---

## 📁 Arquivos de Análise

### 📂 Estrutura

```
03_analytics/
├── ltv_analysis.sql                 # 7 análises de LTV
├── cohort_retention.sql             # 10 análises de retenção
├── rfm_segmentation.sql             # 6 análises RFM
├── category_performance.sql         # 8 análises de categoria
├── delivery_analysis.sql            # 8 análises de logística
├── payment_analysis.sql             # 9 análises de pagamento
└── README.md                        # Esta documentação
```

**Total:** 48 queries prontas para uso

---

## 1️⃣ ltv_analysis.sql

**Customer Lifetime Value Analysis** - 7 análises

### Análises Incluídas

| # | Análise | Descrição |
|---|---------|-----------|
| 1 | LTV por Cliente | Base completa com métricas individuais |
| 2 | LTV por Estado | Análise geográfica (média, mediana, P90) |
| 3 | LTV por Cohort | Evolução temporal de LTV |
| 4 | LTV por Segmento RFM | Preview de segmentação |
| 5 | Top 100 Clientes | Champions com tier (VIP/Premium/High) |
| 6 | Análise de Pareto | 80/20 - concentração de receita |
| 7 | LTV Forecast | Projeção futura simples |

### Métricas Chave

- LTV médio, mediano, P25, P75, P90
- Taxa de recompra por região
- AOV (Average Order Value)
- NPS médio
- Customer lifetime (dias)

### Exemplo de Uso

```sql
-- Top 10 estados por LTV médio
SELECT customer_state, avg_ltv, total_customers, revenue_share_pct
FROM `project.dataset.ltv_by_state`
ORDER BY avg_ltv DESC
LIMIT 10;
```

### Insights Típicos

- SP: 42% do GMV, mas menor LTV per capita (R$ 142)
- Sul (RS/SC): LTV 18% maior que média nacional
- Top 20% clientes = 70-80% da receita (Pareto)

---

## 2️⃣ cohort_retention.sql

**Cohort Retention Analysis** - 10 análises

### Análises Incluídas

| # | Análise | Descrição |
|---|---------|-----------|
| 1 | Cohort Base | Primeira compra de cada cliente |
| 2 | Todas as Compras | Timeline completo |
| 3 | Cálculo de Meses | Meses desde primeira compra |
| 4 | Matriz de Retenção | Tabela cohort × período |
| 5 | Churn Incremental | Perda mês-a-mês |
| 6 | Pivot Table | Visualização clássica M0-M11 |
| 7 | Métricas Agregadas | Sumário por cohort |
| 8 | Retenção por Estado | Análise geográfica |
| 9 | Curva Média | Benchmark geral |
| 10 | Análise de Churn | Complemento da retenção |

### Métricas Chave

- Retention rate M1, M3, M6, M12
- Churn rate incremental
- Cohort size
- Revenue per cohort customer

### Exemplo de Uso

```sql
-- Retenção M1 por cohort
SELECT cohort_month, m1_retention, m3_retention, m6_retention
FROM cohort_summary
ORDER BY cohort_month DESC;
```

### Insights Típicos

- M0 → M1: Drop-off de 96.8% (apenas 3.2% retornam)
- M1 → M3: Estabilização gradual
- Clientes que passam de M3 tendem a ser leais

---

## 3️⃣ rfm_segmentation.sql

**RFM Customer Segmentation** - 6 análises

### Análises Incluídas

| # | Análise | Descrição |
|---|---------|-----------|
| 1 | Cálculo Base RFM | Recency, Frequency, Monetary |
| 2 | Scores RFM | Classificação 1-5 |
| 3 | Segmentação | 12 segmentos de negócio |
| 4 | Sumário por Segmento | Métricas agregadas |
| 5 | Distribuição de Scores | Heatmap R×F×M |
| 6 | Top por Segmento | Champions, At Risk, etc |

### Segmentos Criados

| Segmento | Descrição | Ação Recomendada |
|----------|-----------|------------------|
| 🏆 Champions | R≥4, F≥4, M≥4 | Programa VIP, early access |
| ⭐ Loyal Customers | F≥4 | Upsell, pedir reviews |
| 🚨 Cannot Lose Them | R≤2, F≥4, M≥4 | URGENTE! Oferta especial |
| ⚠️ At Risk | R≤2, F≥3, M≥3 | Win-back campaign |
| 📈 Potential Loyalist | R≥4, F≥2, M≥2 | Programa de fidelidade |
| 🔔 Need Attention | R≥2, F≥2, M≥2 | Ofertas limitadas |
| 🌟 Promising | R≥3, F=1, M≥2 | Incentivar 2ª compra |
| 👋 New Customers | R≥4, F=1 | Onboarding especial |
| 😴 About To Sleep | R≥2, F≤2, M≤2 | Email re-engajamento |
| 💤 Hibernating | R≤2, F≤2, M≤2 | Reativação massiva |
| ❌ Lost | R=1 | Custo alto - não investir |

### Exemplo de Uso

```sql
-- Champions por estado
SELECT customer_state, COUNT(*) as champions, AVG(monetary)
FROM rfm_segmented
WHERE segment = 'Champions'
GROUP BY customer_state
ORDER BY champions DESC;
```

### Insights Típicos

- Champions: 8% dos clientes = 38% da receita
- Hibernating: 46% dos clientes = 4% da receita
- Taxa de recompra crítica: < 10% (meta: 15%)

---

## 4️⃣ category_performance.sql

**Product Category Analysis** - 8 análises

### Análises Incluídas

| # | Análise | Descrição |
|---|---------|-----------|
| 1 | Performance Geral | Revenue, NPS, AOV por categoria |
| 2 | Top 10 Categorias | Ranking por receita |
| 3 | Sazonalidade | Tendências mensais |
| 4 | Ticket Médio | Distribuição AOV |
| 5 | NPS por Categoria | Satisfação do cliente |
| 6 | Margem Estimada | Frete vs Preço |
| 7 | Cross-Sell | Categorias compradas juntas |
| 8 | Ranking Composto | Score ponderado (revenue + NPS + margin) |

### Métricas Chave

- Revenue total e market share
- AOV (Average Order Value)
- NPS médio e distribuição (5★ a 1★)
- Margem estimada (price - freight)
- Unique products e sellers

### Exemplo de Uso

```sql
-- Top categorias por receita + NPS
SELECT category, revenue, avg_nps, category_status
FROM category_summary
WHERE revenue > 50000
ORDER BY revenue DESC;
```

### Insights Típicos

- Beleza & Saúde: NPS 4.3 ⭐ mas só 12% do mix (oportunidade)
- Móveis: Margem alta mas NPS baixo (problema logístico)
- Cross-sell: Beleza → Relógios (complementares)

---

## 5️⃣ delivery_analysis.sql

**Delivery & Logistics Performance** - 8 análises

### Análises Incluídas

| # | Análise | Descrição |
|---|---------|-----------|
| 1 | Performance Geral | SLA, atrasos, métricas globais |
| 2 | Performance por Rota | Estado seller → cliente |
| 3 | Atraso por Região | Distribuição geográfica |
| 4 | Tempo vs NPS | Correlação delivery × satisfação |
| 5 | Atraso vs NPS | Impacto do delay |
| 6 | Top 20 Rotas Críticas | Priorização (volume + SLA + NPS) |
| 7 | Evolução Temporal | SLA mês-a-mês |
| 8 | Peso vs Entrega | Produtos pesados |

### Métricas Chave

- SLA compliance % (entregas no prazo)
- Average delivery days
- Delay rate % (atrasos >10 dias)
- Correlação delay × NPS
- Rotas críticas (criticality score)

### Exemplo de Uso

```sql
-- Rotas com pior SLA
SELECT route, orders, sla_pct, avg_nps, priority
FROM critical_routes
WHERE priority LIKE '%P0%'
ORDER BY criticality_score DESC;
```

### Insights Típicos

- Entrega <7 dias: NPS 4.5 ⭐
- Entrega >21 dias: NPS 2.7 ⭐ (crítico!)
- Norte/Nordeste: 45% de atraso vs 12% Sul/Sudeste
- Produtos >5kg: +30% de atraso

---

## 6️⃣ payment_analysis.sql

**Payment Methods & Behavior** - 9 análises

### Análises Incluídas

| # | Análise | Descrição |
|---|---------|-----------|
| 1 | Overview | Volume, conversão, market share |
| 2 | Parcelamento | Análise 1x a 24x (cartão) |
| 3 | LTV por Método | Comparação cartão vs boleto |
| 4 | Múltiplos Métodos | Split payment |
| 5 | Evolução Temporal | Tendências mês-a-mês |
| 6 | Preferência Regional | Método por estado |
| 7 | Fraude e Risco | Patterns suspeitos |
| 8 | Ticket por Método | Distribuição de valores |
| 9 | Recomendações | Estratégias por segmento |

### Métricas Chave

- Market share por método (order % e revenue %)
- Conversion rate (delivered / total)
- LTV médio por método
- Parcelamento médio
- Taxa de cancelamento

### Exemplo de Uso

```sql
-- Comparação cartão vs boleto
SELECT payment_type, avg_ltv, conversion_rate_pct, loyal_customer_pct
FROM payment_ltv_comparison
WHERE payment_type IN ('credit_card', 'boleto');
```

### Insights Típicos

- Cartão: 76% dos pedidos, LTV 46% maior que boleto
- 6x parcelas: Sweet spot (35% das compras)
- Norte/Nordeste: 28% boleto vs 19% nacional
- 10-12x: Tickets 3x maiores

---

## 🚀 Como Usar

### 1. Executar no BigQuery Console

```sql
-- 1. Abra BigQuery Console
-- 2. Cole uma das queries
-- 3. Substitua ${GCP_PROJECT_ID} e ${GCP_DATASET_ID}
-- 4. Execute
```

### 2. Via Python (Recomendado)

```python
from python.utils.bigquery_helper import BigQueryHelper

helper = BigQueryHelper()

# Executar arquivo completo
helper.run_sql_file('sql/03_analytics/ltv_analysis.sql')

# Ou query específica
query = """
SELECT customer_state, avg_ltv, total_customers
FROM `project.dataset.ltv_by_state`
ORDER BY avg_ltv DESC LIMIT 10
"""
df = helper.query_to_dataframe(query)
print(df)
```

### 3. Via bq CLI

```bash
# Executar query
bq query --use_legacy_sql=false < sql/03_analytics/ltv_analysis.sql

# Com substituição de variáveis
cat sql/03_analytics/ltv_analysis.sql | \
  sed "s/\${GCP_PROJECT_ID}/seu-projeto/g" | \
  sed "s/\${GCP_DATASET_ID}/olist_ecommerce/g" | \
  bq query --use_legacy_sql=false
```

### 4. Agendar no BigQuery (Scheduled Queries)

```sql
-- 1. Execute a query manualmente
-- 2. Clique em "Schedule" no console
-- 3. Configure frequência (diária/semanal)
-- 4. Defina destino (tabela para dashboard)
```

---

## 📊 Casos de Uso por Departamento

### 🎯 Marketing

**Arquivos:** `rfm_segmentation.sql`, `cohort_retention.sql`

**Use cases:**
- Segmentar clientes para campanhas
- Identificar "At Risk" para win-back
- Calcular ROI de retenção vs aquisição
- Definir budget por segmento

**Query exemplo:**
```sql
-- Clientes para campanha de reativação
SELECT customer_unique_id, customer_state, lifetime_value, recency_days
FROM rfm_customers
WHERE segment IN ('At Risk', 'Cannot Lose Them')
  AND lifetime_value > 200
ORDER BY lifetime_value DESC;
```

---

### 💰 Finance

**Arquivos:** `ltv_analysis.sql`, `payment_analysis.sql`, `category_performance.sql`

**Use cases:**
- Forecasting de receita
- Análise de margem por categoria
- Projeção de CLV
- Análise de parcelamento

**Query exemplo:**
```sql
-- Projeção de receita por cohort
SELECT cohort_month, avg_ltv, cohort_size, 
       avg_ltv * cohort_size as projected_revenue
FROM cohort_ltv
WHERE cohort_month >= '2018-01-01';
```

---

### 🚚 Operations / Logistics

**Arquivos:** `delivery_analysis.sql`

**Use cases:**
- Identificar rotas problemáticas
- Priorizar melhorias logísticas
- Correlacionar SLA com NPS
- Otimizar alocação de recursos

**Query exemplo:**
```sql
-- Rotas prioritárias para melhoria
SELECT route, orders, sla_pct, avg_nps, severe_delays
FROM critical_routes
WHERE priority IN ('P0 - Urgente', 'P1 - Alta')
  AND orders > 100
ORDER BY criticality_score DESC;
```

---

### 🛍️ Product / Merchandising

**Arquivos:** `category_performance.sql`

**Use cases:**
- Identificar categorias com melhor performance
- Otimizar mix de produtos
- Análise de cross-sell
- Pricing strategy

**Query exemplo:**
```sql
-- Categorias oportunidade (alto NPS, baixo volume)
SELECT category, avg_nps, total_revenue, revenue_share_pct
FROM category_summary
WHERE avg_nps >= 4.2
  AND revenue_share_pct < 5
ORDER BY avg_nps DESC;
```

---

### 📈 C-Level / Strategy

**Arquivos:** Todos

**Use cases:**
- Dashboard executivo
- Decisões estratégicas data-driven
- Análise de Pareto
- ROI de iniciativas

**Query exemplo:**
```sql
-- KPIs executivos
WITH kpis AS (
  SELECT 
    AVG(lifetime_value) as avg_ltv,
    AVG(m1_retention) as retention_m1,
    SUM(CASE WHEN segment = 'Champions' THEN 1 ELSE 0 END) / COUNT(*) * 100 as champion_pct
  FROM mart_customer_metrics
)
SELECT * FROM kpis;
```

---

## 📐 Performance Tips

### Otimização de Queries

1. **Use particionamento:**
   ```sql
   WHERE DATE(order_purchase_timestamp) >= '2018-01-01'
   ```

2. **Limite resultados exploratórios:**
   ```sql
   SELECT * FROM large_table LIMIT 1000
   ```

3. **Use APPROX_QUANTILES para percentis:**
   ```sql
   APPROX_QUANTILES(value, 100)[OFFSET(90)]  -- P90
   ```

4. **Evite SELECT *:**
   ```sql
   SELECT customer_id, lifetime_value  -- Específico
   ```

5. **Use CTEs para legibilidade:**
   ```sql
   WITH base AS (...),
        aggregated AS (...)
   SELECT * FROM aggregated;
   ```

---

## 🔗 Integração com Dashboards

### Looker Studio

1. Conectar ao BigQuery
2. Usar queries como fonte (Custom Query)
3. Agendar refresh automático
4. Criar visualizações interativas

**Exemplo:**
```sql
-- Query otimizada para dashboard
SELECT 
  customer_state,
  COUNT(*) as customers,
  AVG(lifetime_value) as avg_ltv,
  SUM(lifetime_value) as total_revenue
FROM mart_customer_metrics
WHERE recency_segment = 'Active'
GROUP BY customer_state
ORDER BY total_revenue DESC;
```

---

## 📚 Recursos Adicionais

- [BigQuery SQL Reference](https://cloud.google.com/bigquery/docs/reference/standard-sql)
- [Window Functions Guide](https://cloud.google.com/bigquery/docs/reference/standard-sql/analytic-function-concepts)
- [Optimization Best Practices](https://cloud.google.com/bigquery/docs/best-practices-performance-overview)

---

## 🤝 Contribuindo

Ao adicionar novas análises:

1. ✅ Seguir estrutura com CTEs
2. ✅ Comentar lógica complexa
3. ✅ Incluir seção de insights
4. ✅ Adicionar exemplos de uso
5. ✅ Documentar no README

---

## 📝 Changelog

**v1.0 (Outubro 2025)**
- 48 queries analytics criadas
- 6 arquivos de análise
- Documentação completa
- Exemplos de uso por departamento

---

**Última atualização:** Outubro 2025  
**Total de Queries:** 48  
**Arquivos:** 6  
**Pronto para Produção:** ✅