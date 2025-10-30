-- =====================================================
-- STAGING: ORDERS
-- =====================================================
-- Camada de staging para pedidos com limpeza e enriquecimento
-- Estilo dbt - fonte → staging → marts
-- Autor: Andre Bomfim
-- Data: Outubro 2025
-- =====================================================

-- =====================================================
-- STG_ORDERS: Pedidos limpos e enriquecidos
-- =====================================================

CREATE OR REPLACE TABLE `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_orders` AS

WITH source AS (
  SELECT * 
  FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.orders`
),

cleaned AS (
  SELECT 
    -- Primary key
    order_id,
    
    -- Foreign keys
    customer_id,
    
    -- Status
    LOWER(TRIM(order_status)) AS order_status,
    
    -- Timestamps (validados)
    order_purchase_timestamp,
    order_approved_at,
    order_delivered_carrier_date,
    order_delivered_customer_date,
    order_estimated_delivery_date,
    
    -- Validação: timestamps devem estar em ordem lógica
    CASE 
      WHEN order_purchase_timestamp IS NULL THEN FALSE
      WHEN order_approved_at < order_purchase_timestamp THEN FALSE
      WHEN order_delivered_carrier_date < order_approved_at THEN FALSE
      WHEN order_delivered_customer_date < order_delivered_carrier_date THEN FALSE
      ELSE TRUE
    END AS is_valid_timeline,
    
    -- Metadata
    CURRENT_TIMESTAMP() AS _loaded_at
    
  FROM source
),

enriched AS (
  SELECT 
    *,
    
    -- ==========================================
    -- ENRICHMENT: Datas calculadas
    -- ==========================================
    
    -- Data extrações
    DATE(order_purchase_timestamp) AS order_date,
    EXTRACT(YEAR FROM order_purchase_timestamp) AS order_year,
    EXTRACT(MONTH FROM order_purchase_timestamp) AS order_month,
    EXTRACT(QUARTER FROM order_purchase_timestamp) AS order_quarter,
    EXTRACT(DAYOFWEEK FROM order_purchase_timestamp) AS order_day_of_week,
    EXTRACT(HOUR FROM order_purchase_timestamp) AS order_hour,
    FORMAT_DATE('%Y-%m', order_purchase_timestamp) AS order_year_month,
    FORMAT_DATE('%Y-Q%Q', order_purchase_timestamp) AS order_year_quarter,
    FORMAT_DATE('%A', order_purchase_timestamp) AS order_day_name,
    
    -- Períodos do dia
    CASE 
      WHEN EXTRACT(HOUR FROM order_purchase_timestamp) BETWEEN 0 AND 5 THEN 'Madrugada'
      WHEN EXTRACT(HOUR FROM order_purchase_timestamp) BETWEEN 6 AND 11 THEN 'Manhã'
      WHEN EXTRACT(HOUR FROM order_purchase_timestamp) BETWEEN 12 AND 17 THEN 'Tarde'
      ELSE 'Noite'
    END AS order_period_of_day,
    
    -- Fim de semana
    CASE 
      WHEN EXTRACT(DAYOFWEEK FROM order_purchase_timestamp) IN (1, 7) THEN TRUE
      ELSE FALSE
    END AS is_weekend,
    
    -- ==========================================
    -- ENRICHMENT: Métricas de tempo
    -- ==========================================
    
    -- Tempo até aprovação (em horas)
    TIMESTAMP_DIFF(order_approved_at, order_purchase_timestamp, HOUR) AS hours_to_approval,
    
    -- Tempo até envio à transportadora (em dias)
    DATE_DIFF(DATE(order_delivered_carrier_date), DATE(order_purchase_timestamp), DAY) AS days_to_carrier,
    
    -- Tempo de entrega total (em dias)
    DATE_DIFF(DATE(order_delivered_customer_date), DATE(order_purchase_timestamp), DAY) AS days_to_delivery,
    
    -- Atraso na entrega (em dias) - negativo = antecipado
    DATE_DIFF(
      DATE(order_delivered_customer_date), 
      DATE(order_estimated_delivery_date), 
      DAY
    ) AS delivery_delay_days,
    
    -- Tempo em trânsito (dias entre carrier e customer)
    DATE_DIFF(
      DATE(order_delivered_customer_date), 
      DATE(order_delivered_carrier_date), 
      DAY
    ) AS days_in_transit,
    
    -- ==========================================
    -- ENRICHMENT: Flags e categorias
    -- ==========================================
    
    -- Status categorizados
    CASE 
      WHEN order_status = 'delivered' THEN 'Completed'
      WHEN order_status IN ('shipped', 'invoiced', 'processing') THEN 'In Progress'
      WHEN order_status IN ('canceled', 'unavailable') THEN 'Not Completed'
      ELSE 'Other'
    END AS order_status_category,
    
    -- Entrega
    CASE 
      WHEN DATE(order_delivered_customer_date) <= DATE(order_estimated_delivery_date) THEN 'On Time'
      WHEN DATE(order_delivered_customer_date) > DATE(order_estimated_delivery_date) THEN 'Delayed'
      ELSE NULL
    END AS delivery_status,
    
    -- Flags de qualidade
    CASE 
      WHEN order_delivered_customer_date IS NULL AND order_status = 'delivered' THEN TRUE
      ELSE FALSE
    END AS is_missing_delivery_date,
    
    CASE 
      WHEN DATE_DIFF(DATE(order_delivered_customer_date), DATE(order_purchase_timestamp), DAY) > 60 THEN TRUE
      ELSE FALSE
    END AS is_extreme_delivery_time,
    
    -- Período de compra (para análise de sazonalidade)
    CASE 
      WHEN EXTRACT(MONTH FROM order_purchase_timestamp) IN (11, 12) THEN 'Black Friday / Natal'
      WHEN EXTRACT(MONTH FROM order_purchase_timestamp) IN (1, 2) THEN 'Pós-Natal / Carnaval'
      WHEN EXTRACT(MONTH FROM order_purchase_timestamp) IN (5, 6) THEN 'Dia das Mães / Dia dos Namorados'
      WHEN EXTRACT(MONTH FROM order_purchase_timestamp) IN (7, 8) THEN 'Dia dos Pais / Férias'
      ELSE 'Regular'
    END AS seasonal_period,
    
    -- ==========================================
    -- ENRICHMENT: Cohort (mês de primeira compra)
    -- ==========================================
    
    DATE_TRUNC(DATE(order_purchase_timestamp), MONTH) AS order_cohort_month

  FROM cleaned
)

SELECT * FROM enriched;

-- =====================================================
-- ÍNDICES E PARTICIONAMENTO
-- =====================================================

-- BigQuery: Recriar tabela com particionamento e clustering
CREATE OR REPLACE TABLE `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_orders`
PARTITION BY order_date
CLUSTER BY customer_id, order_status, order_year_month
AS
SELECT * FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_orders`;

-- =====================================================
-- TESTES DE QUALIDADE (Documentação)
-- =====================================================

/*
-- Teste 1: Nenhum order_id deve ser nulo
SELECT COUNT(*) AS null_order_ids
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_orders`
WHERE order_id IS NULL;
-- Esperado: 0

-- Teste 2: Nenhum order_id deve estar duplicado
SELECT 
  order_id, 
  COUNT(*) AS count
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_orders`
GROUP BY order_id
HAVING COUNT(*) > 1;
-- Esperado: 0 linhas

-- Teste 3: order_status deve ter valores válidos
SELECT DISTINCT order_status
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_orders`;
-- Esperado: delivered, shipped, canceled, unavailable, invoiced, processing

-- Teste 4: Pedidos entregues devem ter data de entrega
SELECT COUNT(*) AS delivered_without_date
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_orders`
WHERE order_status = 'delivered'
AND order_delivered_customer_date IS NULL;
-- Esperado: ~0 (poucos casos edge)

-- Teste 5: Timeline deve ser válida
SELECT COUNT(*) AS invalid_timelines
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_orders`
WHERE is_valid_timeline = FALSE;
-- Esperado: < 1% do total

-- Teste 6: Delivery delay extremo (> 60 dias)
SELECT COUNT(*) AS extreme_delays
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_orders`
WHERE is_extreme_delivery_time = TRUE;
-- Esperado: < 1% do total

-- Teste 7: Distribuição por status
SELECT 
  order_status,
  COUNT(*) AS count,
  ROUND(COUNT(*) / SUM(COUNT(*)) OVER () * 100, 2) AS pct
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_orders`
GROUP BY order_status
ORDER BY count DESC;
-- Esperado: delivered ~97%, outros ~3%
*/

-- =====================================================
-- QUERIES DE VALIDAÇÃO
-- =====================================================

-- Sumário da tabela staging
SELECT 
  'Total Orders' AS metric,
  COUNT(*) AS value
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_orders`

UNION ALL

SELECT 
  'Valid Timelines',
  COUNTIF(is_valid_timeline = TRUE)
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_orders`

UNION ALL

SELECT 
  'Delivered Orders',
  COUNTIF(order_status = 'delivered')
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_orders`

UNION ALL

SELECT 
  'Delayed Deliveries',
  COUNTIF(delivery_status = 'Delayed')
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_orders`

UNION ALL

SELECT 
  'Weekend Orders',
  COUNTIF(is_weekend = TRUE)
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_orders`

UNION ALL

SELECT 
  'Avg Days to Delivery',
  CAST(AVG(days_to_delivery) AS INT64)
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_orders`
WHERE order_status = 'delivered';

-- =====================================================
-- EXEMPLO DE USO
-- =====================================================

/*
-- Análise de performance de entrega por período
SELECT 
  seasonal_period,
  COUNT(*) AS orders,
  AVG(days_to_delivery) AS avg_delivery_days,
  COUNTIF(delivery_status = 'Delayed') / COUNT(*) * 100 AS delay_rate_pct
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_orders`
WHERE order_status = 'delivered'
GROUP BY seasonal_period
ORDER BY orders DESC;

-- Análise de horários de compra
SELECT 
  order_period_of_day,
  order_day_name,
  COUNT(*) AS orders
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_orders`
WHERE order_year = 2018
GROUP BY order_period_of_day, order_day_name
ORDER BY orders DESC;
*/

-- =====================================================
-- DOCUMENTAÇÃO
-- =====================================================

-- Esta tabela staging serve como base para:
-- 1. Análises de performance de entrega
-- 2. Análises de sazonalidade
-- 3. Análises de cohort
-- 4. Dashboards operacionais
-- 5. Camada intermediária para marts

-- Próximos passos:
-- - Criar stg_customers.sql
-- - Criar stg_order_items.sql
-- - Criar mart_customer_metrics.sql (usando estas stagings)

-- =====================================================