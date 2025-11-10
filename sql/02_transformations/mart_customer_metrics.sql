-- MART: CUSTOMER METRICS
-- Camada analytics - Métricas consolidadas por cliente
-- Combina staging de customers + orders + payments + reviews
-- Estilo dbt - staging → marts
-- Autor: Andre Bomfim
-- Data: Outubro 2025

-- MART_CUSTOMER_METRICS: Visão 360 do cliente


CREATE OR REPLACE TABLE `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.mart_customer_metrics` AS

WITH customer_base AS (
  -- Pegar informações do cliente da master view (1 por customer_unique_id)
  SELECT 
    customer_unique_id,
    customer_state,
    customer_city,
    customer_region,
    customer_location_type,
    customer_metro_area,
    state_gdp_tier,
    distance_from_sp,
    total_customer_ids
  FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_customers_master`
),

order_facts AS (
  -- Agregar pedidos por customer_unique_id
  SELECT 
    c.customer_unique_id,
    
    
    -- MÉTRICAS DE PEDIDOS
    
    
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT CASE WHEN o.order_status = 'delivered' THEN o.order_id END) AS delivered_orders,
    COUNT(DISTINCT CASE WHEN o.order_status = 'canceled' THEN o.order_id END) AS canceled_orders,
    
    -- Taxa de cancelamento
    SAFE_DIVIDE(
      COUNT(DISTINCT CASE WHEN o.order_status = 'canceled' THEN o.order_id END),
      COUNT(DISTINCT o.order_id)
    ) * 100 AS cancel_rate_pct,
    
    
    -- MÉTRICAS TEMPORAIS
    
    
    MIN(o.order_purchase_timestamp) AS first_order_date,
    MAX(o.order_purchase_timestamp) AS last_order_date,
    
    -- Recência (dias desde última compra)
    DATE_DIFF(CURRENT_DATE(), DATE(MAX(o.order_purchase_timestamp)), DAY) AS recency_days,
    
    -- Lifetime (dias entre primeira e última compra)
    DATE_DIFF(
      DATE(MAX(o.order_purchase_timestamp)), 
      DATE(MIN(o.order_purchase_timestamp)), 
      DAY
    ) AS customer_lifetime_days,
    
    -- Cohort (mês da primeira compra)
    DATE_TRUNC(DATE(MIN(o.order_purchase_timestamp)), MONTH) AS cohort_month,
    FORMAT_DATE('%Y-%m', MIN(o.order_purchase_timestamp)) AS cohort_year_month,
    
    
    -- MÉTRICAS DE FREQUÊNCIA
    
    
    -- Frequência (pedidos por dia ativo)
    SAFE_DIVIDE(
      COUNT(DISTINCT o.order_id),
      NULLIF(DATE_DIFF(
        DATE(MAX(o.order_purchase_timestamp)), 
        DATE(MIN(o.order_purchase_timestamp)), 
        DAY
      ), 0)
    ) AS orders_per_day,
    
    -- Tempo médio entre pedidos (em dias)
    SAFE_DIVIDE(
      DATE_DIFF(
        DATE(MAX(o.order_purchase_timestamp)), 
        DATE(MIN(o.order_purchase_timestamp)), 
        DAY
      ),
      NULLIF(COUNT(DISTINCT o.order_id) - 1, 0)
    ) AS avg_days_between_orders,
    
    
    -- MÉTRICAS DE ENTREGA
    
    
    AVG(o.days_to_delivery) AS avg_delivery_days,
    AVG(o.delivery_delay_days) AS avg_delivery_delay,
    
    -- Taxa de atraso
    SAFE_DIVIDE(
      COUNTIF(o.delivery_status = 'Delayed'),
      COUNT(*)
    ) * 100 AS delivery_delay_rate_pct,
    
    
    -- MÉTRICAS DE SATISFAÇÃO
    
    
    COUNT(DISTINCT r.review_id) AS total_reviews,
    AVG(r.review_score) AS avg_review_score,
    
    -- Distribuição de reviews
    COUNTIF(r.review_score = 5) AS reviews_5_stars,
    COUNTIF(r.review_score = 4) AS reviews_4_stars,
    COUNTIF(r.review_score <= 3) AS reviews_3_or_less,
    
    -- Taxa de review positivo
    SAFE_DIVIDE(
      COUNTIF(r.review_score >= 4),
      COUNT(DISTINCT r.review_id)
    ) * 100 AS positive_review_rate_pct,
    
    
    -- MÉTRICAS DE SAZONALIDADE
    
    -- Pedidos em período sazonal
    COUNTIF(o.seasonal_period = 'Black Friday / Natal') AS orders_black_friday,
    COUNTIF(o.is_weekend = TRUE) AS orders_on_weekend,
    
    -- Horário preferido
    MODE(o.order_period_of_day) AS preferred_time_of_day
    
  FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_customers` c
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_orders` o 
    ON c.customer_id = o.customer_id
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.reviews` r 
    ON o.order_id = r.order_id
  GROUP BY c.customer_unique_id
),

payment_facts AS (
  -- Agregar pagamentos por customer_unique_id
  SELECT 
    c.customer_unique_id,
    
    -- MÉTRICAS MONETÁRIAS
    SUM(p.payment_value) AS lifetime_value,
    AVG(p.payment_value) AS avg_order_value,
    MIN(p.payment_value) AS min_order_value,
    MAX(p.payment_value) AS max_order_value,
    STDDEV(p.payment_value) AS stddev_order_value,
    
    -- Percentis
    APPROX_QUANTILES(p.payment_value, 4)[OFFSET(1)] AS p25_order_value,
    APPROX_QUANTILES(p.payment_value, 4)[OFFSET(2)] AS median_order_value,
    APPROX_QUANTILES(p.payment_value, 4)[OFFSET(3)] AS p75_order_value,
    
    
    -- MÉTRICAS DE PAGAMENTO
    
    -- Método de pagamento preferido
    MODE(p.payment_type) AS preferred_payment_method,
    
    -- Uso de parcelamento
    AVG(p.payment_installments) AS avg_installments,
    MAX(p.payment_installments) AS max_installments,
    
    -- Taxa de uso de cartão de crédito
    SAFE_DIVIDE(
      COUNTIF(p.payment_type = 'credit_card'),
      COUNT(*)
    ) * 100 AS credit_card_usage_pct,
    
    -- Taxa de uso de boleto
    SAFE_DIVIDE(
      COUNTIF(p.payment_type = 'boleto'),
      COUNT(*)
    ) * 100 AS boleto_usage_pct
    
  FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_customers` c
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_orders` o 
    ON c.customer_id = o.customer_id
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.payments` p 
    ON o.order_id = p.order_id
  WHERE o.order_status = 'delivered'
  GROUP BY c.customer_unique_id
),

final AS (
  SELECT 
    
    -- DIMENSÕES DO CLIENTE
    cb.customer_unique_id,
    cb.customer_state,
    cb.customer_city,
    cb.customer_region,
    cb.customer_location_type,
    cb.customer_metro_area,
    cb.state_gdp_tier,
    cb.distance_from_sp,
    
    
    -- MÉTRICAS DE PEDIDOS
    of.total_orders,
    of.delivered_orders,
    of.canceled_orders,
    ROUND(of.cancel_rate_pct, 2) AS cancel_rate_pct,
    
    
    -- MÉTRICAS TEMPORAIS
    of.first_order_date,
    of.last_order_date,
    of.recency_days,
    of.customer_lifetime_days,
    of.cohort_month,
    of.cohort_year_month,
    ROUND(of.orders_per_day, 4) AS orders_per_day,
    ROUND(of.avg_days_between_orders, 1) AS avg_days_between_orders,
    
    
    -- MÉTRICAS MONETÁRIAS
    ROUND(pf.lifetime_value, 2) AS lifetime_value,
    ROUND(pf.avg_order_value, 2) AS avg_order_value,
    ROUND(pf.min_order_value, 2) AS min_order_value,
    ROUND(pf.max_order_value, 2) AS max_order_value,
    ROUND(pf.median_order_value, 2) AS median_order_value,
    
    
    -- MÉTRICAS DE SATISFAÇÃO
    of.total_reviews,
    ROUND(of.avg_review_score, 2) AS avg_review_score,
    ROUND(of.positive_review_rate_pct, 2) AS positive_review_rate_pct,
    
    
    -- MÉTRICAS DE ENTREGA
    ROUND(of.avg_delivery_days, 1) AS avg_delivery_days,
    ROUND(of.avg_delivery_delay, 1) AS avg_delivery_delay,
    ROUND(of.delivery_delay_rate_pct, 2) AS delivery_delay_rate_pct,
    
    
    -- MÉTRICAS DE PAGAMENTO
    pf.preferred_payment_method,
    ROUND(pf.avg_installments, 1) AS avg_installments,
    ROUND(pf.credit_card_usage_pct, 2) AS credit_card_usage_pct,
    
    
    -- SEGMENTAÇÕES
    
    -- Segmento por número de pedidos
    CASE 
      WHEN of.total_orders = 1 THEN 'One-time'
      WHEN of.total_orders = 2 THEN 'Repeat'
      WHEN of.total_orders >= 3 AND of.total_orders <= 5 THEN 'Loyal'
      WHEN of.total_orders > 5 THEN 'Champion'
    END AS frequency_segment,
    
    -- Segmento por LTV
    CASE 
      WHEN pf.lifetime_value >= 1000 THEN 'VIP'
      WHEN pf.lifetime_value >= 500 THEN 'High Value'
      WHEN pf.lifetime_value >= 200 THEN 'Medium Value'
      ELSE 'Low Value'
    END AS ltv_segment,
    
    -- Segmento por recência
    CASE 
      WHEN of.recency_days <= 90 THEN 'Active'
      WHEN of.recency_days <= 180 THEN 'At Risk'
      WHEN of.recency_days <= 365 THEN 'Dormant'
      ELSE 'Lost'
    END AS recency_segment,
    
    -- RFM Score simplificado (1-5)
    CASE 
      WHEN of.recency_days <= 30 THEN 5
      WHEN of.recency_days <= 60 THEN 4
      WHEN of.recency_days <= 90 THEN 3
      WHEN of.recency_days <= 180 THEN 2
      ELSE 1
    END AS R_score,
    
    CASE 
      WHEN of.total_orders >= 5 THEN 5
      WHEN of.total_orders = 4 THEN 4
      WHEN of.total_orders = 3 THEN 3
      WHEN of.total_orders = 2 THEN 2
      ELSE 1
    END AS F_score,
    
    NTILE(5) OVER (ORDER BY pf.lifetime_value) AS M_score,
    
    
    -- STATUS DO CLIENTE
    CASE 
      WHEN of.recency_days <= 90 AND of.avg_review_score >= 4 THEN 'Healthy'
      WHEN of.recency_days <= 90 AND of.avg_review_score < 4 THEN 'Active but Unsatisfied'
      WHEN of.recency_days > 90 AND of.recency_days <= 180 THEN 'Needs Attention'
      WHEN of.recency_days > 180 THEN 'Inactive'
    END AS customer_health_status,
    
    
    -- FLAGS
    CASE WHEN of.avg_review_score >= 4.5 THEN TRUE ELSE FALSE END AS is_promoter,
    CASE WHEN of.avg_review_score <= 2.5 THEN TRUE ELSE FALSE END AS is_detractor,
    CASE WHEN of.delivery_delay_rate_pct > 50 THEN TRUE ELSE FALSE END AS has_delivery_issues,
    CASE WHEN of.cancel_rate_pct > 20 THEN TRUE ELSE FALSE END AS has_high_cancel_rate,
    CASE WHEN pf.lifetime_value > 1000 THEN TRUE ELSE FALSE END AS is_vip,
    CASE WHEN of.total_orders >= 3 THEN TRUE ELSE FALSE END AS is_repeat_customer,
    
    
    -- MÉTRICAS CALCULADAS AVANÇADAS
    
    -- CLV projetado (simples: LTV * multiplicador baseado em frequência)
    ROUND(
      pf.lifetime_value * (1 + (of.total_orders * 0.1)),
      2
    ) AS projected_clv,
    
    -- Churn probability (simplificado)
    CASE 
      WHEN of.recency_days > 365 THEN 0.95
      WHEN of.recency_days > 180 THEN 0.70
      WHEN of.recency_days > 90 THEN 0.40
      WHEN of.recency_days > 60 THEN 0.20
      ELSE 0.10
    END AS churn_probability,
    
    -- Metadata
    CURRENT_TIMESTAMP() AS _loaded_at
    
  FROM customer_base cb
  INNER JOIN order_facts of 
    ON cb.customer_unique_id = of.customer_unique_id
  INNER JOIN payment_facts pf 
    ON cb.customer_unique_id = pf.customer_unique_id
)

SELECT * FROM final;

-- ÍNDICES E PARTICIONAMENTO

-- Recriar com clustering
CREATE OR REPLACE TABLE `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.mart_customer_metrics`
CLUSTER BY customer_state, frequency_segment, ltv_segment, recency_segment
AS
SELECT * FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.mart_customer_metrics`;


-- VIEWS DERIVADAS

-- View: Top Customers (Champions)
CREATE OR REPLACE VIEW `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.vw_top_customers` AS
SELECT *
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.mart_customer_metrics`
WHERE frequency_segment = 'Champion'
   OR ltv_segment = 'VIP'
ORDER BY lifetime_value DESC;

-- View: At Risk Customers
CREATE OR REPLACE VIEW `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.vw_at_risk_customers` AS
SELECT *
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.mart_customer_metrics`
WHERE recency_segment = 'At Risk'
  AND frequency_segment IN ('Loyal', 'Champion')
ORDER BY lifetime_value DESC;

-- View: Churned Customers
CREATE OR REPLACE VIEW `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.vw_churned_customers` AS
SELECT *
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.mart_customer_metrics`
WHERE recency_segment = 'Lost'
  AND lifetime_value > 200
ORDER BY last_order_date DESC;


-- QUERIES DE ANÁLISE

-- Sumário geral
SELECT 
  COUNT(*) AS total_customers,
  ROUND(AVG(lifetime_value), 2) AS avg_ltv,
  ROUND(AVG(total_orders), 2) AS avg_orders,
  ROUND(AVG(avg_review_score), 2) AS avg_nps,
  COUNTIF(is_repeat_customer) AS repeat_customers,
  ROUND(COUNTIF(is_repeat_customer) / COUNT(*) * 100, 2) AS repeat_rate_pct
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.mart_customer_metrics`;

-- Distribuição por segmento
SELECT 
  frequency_segment,
  ltv_segment,
  COUNT(*) AS customers,
  ROUND(AVG(lifetime_value), 2) AS avg_ltv,
  ROUND(AVG(total_orders), 2) AS avg_orders
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.mart_customer_metrics`
GROUP BY frequency_segment, ltv_segment
ORDER BY customers DESC;

-- Top 100 clientes
SELECT 
  customer_unique_id,
  customer_state,
  lifetime_value,
  total_orders,
  avg_review_score,
  frequency_segment,
  ltv_segment,
  recency_segment
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.mart_customer_metrics`
ORDER BY lifetime_value DESC
LIMIT 100;

