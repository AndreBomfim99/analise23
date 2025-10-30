-- =====================================================
-- CUSTOMER LIFETIME VALUE (LTV) ANALYSIS
-- =====================================================
-- Análise completa de LTV por cliente, estado e segmento
-- Autor: Andre Bomfim
-- Data: Outubro 2025
-- =====================================================

-- =====================================================
-- 1. LTV POR CLIENTE (Base)
-- =====================================================

WITH customer_orders AS (
  SELECT 
    c.customer_unique_id,
    c.customer_state,
    c.customer_city,
    o.order_id,
    o.order_purchase_timestamp,
    p.payment_value,
    r.review_score,
    
    -- Ordenação temporal
    ROW_NUMBER() OVER (
      PARTITION BY c.customer_unique_id 
      ORDER BY o.order_purchase_timestamp
    ) AS order_number,
    
    -- Data da primeira compra
    MIN(o.order_purchase_timestamp) OVER (
      PARTITION BY c.customer_unique_id
    ) AS first_purchase_date,
    
    -- Contagem total de pedidos
    COUNT(*) OVER (
      PARTITION BY c.customer_unique_id
    ) AS total_orders

  FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.orders` o
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.customers` c 
    ON o.customer_id = c.customer_id
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.payments` p 
    ON o.order_id = p.order_id
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.reviews` r 
    ON o.order_id = r.order_id
  WHERE o.order_status = 'delivered'
),

customer_ltv AS (
  SELECT 
    customer_unique_id,
    customer_state,
    customer_city,
    
    -- Métricas de LTV
    SUM(payment_value) AS lifetime_value,
    AVG(payment_value) AS avg_order_value,
    MAX(total_orders) AS total_orders,
    
    -- Métricas temporais
    MIN(first_purchase_date) AS first_purchase_date,
    MAX(order_purchase_timestamp) AS last_purchase_date,
    DATE_DIFF(
      MAX(order_purchase_timestamp), 
      MIN(first_purchase_date), 
      DAY
    ) AS customer_lifetime_days,
    
    -- Satisfação
    AVG(review_score) AS avg_review_score,
    
    -- Segmentação inicial
    CASE 
      WHEN MAX(total_orders) = 1 THEN 'One-time'
      WHEN MAX(total_orders) = 2 THEN 'Repeat'
      WHEN MAX(total_orders) >= 3 THEN 'Loyal'
    END AS customer_segment

  FROM customer_orders
  GROUP BY customer_unique_id, customer_state, customer_city
)

SELECT * FROM customer_ltv
ORDER BY lifetime_value DESC;

-- =====================================================
-- 2. LTV POR ESTADO (Análise Geográfica)
-- =====================================================

WITH customer_ltv AS (
  SELECT 
    c.customer_unique_id,
    c.customer_state,
    c.customer_city,
    SUM(p.payment_value) AS lifetime_value,
    AVG(p.payment_value) AS avg_order_value,
    COUNT(DISTINCT o.order_id) AS total_orders,
    MIN(o.order_purchase_timestamp) AS first_purchase_date,
    MAX(o.order_purchase_timestamp) AS last_purchase_date,
    DATE_DIFF(
      MAX(o.order_purchase_timestamp), 
      MIN(o.order_purchase_timestamp), 
      DAY
    ) AS customer_lifetime_days,
    AVG(r.review_score) AS avg_review_score,
    CASE 
      WHEN COUNT(DISTINCT o.order_id) = 1 THEN 'One-time'
      WHEN COUNT(DISTINCT o.order_id) = 2 THEN 'Repeat'
      WHEN COUNT(DISTINCT o.order_id) >= 3 THEN 'Loyal'
    END AS customer_segment
  FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.orders` o
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.customers` c 
    ON o.customer_id = c.customer_id
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.payments` p 
    ON o.order_id = p.order_id
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.reviews` r 
    ON o.order_id = r.order_id
  WHERE o.order_status = 'delivered'
  GROUP BY c.customer_unique_id, c.customer_state, c.customer_city
),

state_ltv AS (
  SELECT 
    customer_state,
    
    -- Agregações
    COUNT(DISTINCT customer_unique_id) AS total_customers,
    SUM(lifetime_value) AS total_gmv,
    AVG(lifetime_value) AS avg_ltv,
    APPROX_QUANTILES(lifetime_value, 100)[OFFSET(50)] AS median_ltv,
    APPROX_QUANTILES(lifetime_value, 100)[OFFSET(75)] AS p75_ltv,
    APPROX_QUANTILES(lifetime_value, 100)[OFFSET(90)] AS p90_ltv,
    
    -- Taxa de recompra
    SAFE_DIVIDE(
      SUM(CASE WHEN customer_segment != 'One-time' THEN 1 ELSE 0 END),
      COUNT(*)
    ) * 100 AS repeat_rate_pct,
    
    -- AOV
    AVG(avg_order_value) AS avg_order_value,
    
    -- Satisfação
    AVG(avg_review_score) AS avg_nps,
    
    -- Lifetime
    AVG(customer_lifetime_days) AS avg_lifetime_days

  FROM customer_ltv
  GROUP BY customer_state
),

state_ranking AS (
  SELECT 
    *,
    RANK() OVER (ORDER BY avg_ltv DESC) AS ltv_rank,
    RANK() OVER (ORDER BY repeat_rate_pct DESC) AS retention_rank,
    
    -- Calcular % do GMV total
    SAFE_DIVIDE(total_gmv, SUM(total_gmv) OVER ()) * 100 AS gmv_share_pct

  FROM state_ltv
)

SELECT 
  customer_state,
  total_customers,
  total_gmv,
  ROUND(avg_ltv, 2) AS avg_ltv,
  ROUND(median_ltv, 2) AS median_ltv,
  ROUND(p90_ltv, 2) AS p90_ltv,
  ROUND(repeat_rate_pct, 2) AS repeat_rate_pct,
  ROUND(avg_order_value, 2) AS avg_aov,
  ROUND(avg_nps, 2) AS avg_nps,
  ROUND(gmv_share_pct, 2) AS gmv_share_pct,
  ltv_rank,
  retention_rank

FROM state_ranking
ORDER BY avg_ltv DESC;

-- =====================================================
-- 3. LTV POR COHORT (Análise Temporal)
-- =====================================================

WITH customer_ltv AS (
  SELECT 
    c.customer_unique_id,
    c.customer_state,
    SUM(p.payment_value) AS lifetime_value,
    COUNT(DISTINCT o.order_id) AS total_orders,
    MIN(o.order_purchase_timestamp) AS first_purchase_date,
    CASE 
      WHEN COUNT(DISTINCT o.order_id) = 1 THEN 'One-time'
      WHEN COUNT(DISTINCT o.order_id) = 2 THEN 'Repeat'
      WHEN COUNT(DISTINCT o.order_id) >= 3 THEN 'Loyal'
    END AS customer_segment
  FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.orders` o
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.customers` c 
    ON o.customer_id = c.customer_id
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.payments` p 
    ON o.order_id = p.order_id
  WHERE o.order_status = 'delivered'
  GROUP BY c.customer_unique_id, c.customer_state
),

cohort_base AS (
  SELECT 
    customer_unique_id,
    DATE_TRUNC(first_purchase_date, MONTH) AS cohort_month,
    lifetime_value,
    total_orders,
    customer_segment

  FROM customer_ltv
),

cohort_analysis AS (
  SELECT 
    cohort_month,
    COUNT(DISTINCT customer_unique_id) AS cohort_size,
    
    -- LTV por cohort
    AVG(lifetime_value) AS avg_ltv,
    APPROX_QUANTILES(lifetime_value, 4)[OFFSET(2)] AS median_ltv,
    
    -- Comportamento
    AVG(total_orders) AS avg_orders_per_customer,
    SAFE_DIVIDE(
      SUM(CASE WHEN customer_segment != 'One-time' THEN 1 ELSE 0 END),
      COUNT(*)
    ) * 100 AS repeat_rate_pct,
    
    -- Classificação de cohort
    CASE 
      WHEN AVG(lifetime_value) > 200 THEN 'High Value'
      WHEN AVG(lifetime_value) > 150 THEN 'Medium Value'
      ELSE 'Low Value'
    END AS cohort_quality

  FROM cohort_base
  GROUP BY cohort_month
)

SELECT 
  cohort_month,
  cohort_size,
  ROUND(avg_ltv, 2) AS avg_ltv,
  ROUND(median_ltv, 2) AS median_ltv,
  ROUND(avg_orders_per_customer, 2) AS avg_orders,
  ROUND(repeat_rate_pct, 2) AS repeat_rate_pct,
  cohort_quality,
  
  -- Comparação com cohort anterior
  LAG(avg_ltv) OVER (ORDER BY cohort_month) AS prev_cohort_ltv,
  ROUND(
    SAFE_DIVIDE(
      avg_ltv - LAG(avg_ltv) OVER (ORDER BY cohort_month),
      LAG(avg_ltv) OVER (ORDER BY cohort_month)
    ) * 100, 
    2
  ) AS ltv_growth_pct

FROM cohort_analysis
ORDER BY cohort_month;

-- =====================================================
-- 4. LTV POR SEGMENTO RFM (Preview)
-- =====================================================

WITH customer_ltv AS (
  SELECT 
    c.customer_unique_id,
    SUM(p.payment_value) AS lifetime_value,
    COUNT(DISTINCT o.order_id) AS total_orders,
    AVG(p.payment_value) AS avg_order_value,
    CASE 
      WHEN COUNT(DISTINCT o.order_id) = 1 THEN 'One-time'
      WHEN COUNT(DISTINCT o.order_id) = 2 THEN 'Repeat'
      WHEN COUNT(DISTINCT o.order_id) >= 3 THEN 'Loyal'
    END AS customer_segment
  FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.orders` o
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.customers` c 
    ON o.customer_id = c.customer_id
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.payments` p 
    ON o.order_id = p.order_id
  WHERE o.order_status = 'delivered'
  GROUP BY c.customer_unique_id
),

rfm_ltv AS (
  SELECT 
    customer_segment,
    COUNT(DISTINCT customer_unique_id) AS customers,
    
    -- LTV metrics
    SUM(lifetime_value) AS total_revenue,
    AVG(lifetime_value) AS avg_ltv,
    APPROX_QUANTILES(lifetime_value, 100)[OFFSET(50)] AS median_ltv,
    
    -- Comportamento
    AVG(total_orders) AS avg_orders,
    AVG(avg_order_value) AS avg_aov,
    
    -- Share
    SAFE_DIVIDE(COUNT(*), SUM(COUNT(*)) OVER ()) * 100 AS customer_share_pct,
    SAFE_DIVIDE(SUM(lifetime_value), SUM(SUM(lifetime_value)) OVER ()) * 100 AS revenue_share_pct

  FROM customer_ltv
  GROUP BY customer_segment
)

SELECT 
  customer_segment,
  customers,
  ROUND(total_revenue, 2) AS total_revenue,
  ROUND(avg_ltv, 2) AS avg_ltv,
  ROUND(median_ltv, 2) AS median_ltv,
  ROUND(avg_orders, 2) AS avg_orders,
  ROUND(avg_aov, 2) AS avg_aov,
  ROUND(customer_share_pct, 2) AS customer_share_pct,
  ROUND(revenue_share_pct, 2) AS revenue_share_pct

FROM rfm_ltv
ORDER BY avg_ltv DESC;

-- =====================================================
-- 5. TOP 100 CLIENTES (Champions)
-- =====================================================

WITH customer_ltv AS (
  SELECT 
    c.customer_unique_id,
    c.customer_state,
    c.customer_city,
    SUM(p.payment_value) AS lifetime_value,
    AVG(p.payment_value) AS avg_order_value,
    COUNT(DISTINCT o.order_id) AS total_orders,
    DATE_DIFF(
      MAX(o.order_purchase_timestamp), 
      MIN(o.order_purchase_timestamp), 
      DAY
    ) AS customer_lifetime_days,
    AVG(r.review_score) AS avg_review_score,
    CASE 
      WHEN COUNT(DISTINCT o.order_id) = 1 THEN 'One-time'
      WHEN COUNT(DISTINCT o.order_id) = 2 THEN 'Repeat'
      WHEN COUNT(DISTINCT o.order_id) >= 3 THEN 'Loyal'
    END AS customer_segment
  FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.orders` o
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.customers` c 
    ON o.customer_id = c.customer_id
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.payments` p 
    ON o.order_id = p.order_id
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.reviews` r 
    ON o.order_id = r.order_id
  WHERE o.order_status = 'delivered'
  GROUP BY c.customer_unique_id, c.customer_state, c.customer_city
)

SELECT 
  customer_unique_id,
  customer_state,
  customer_city,
  ROUND(lifetime_value, 2) AS ltv,
  total_orders,
  ROUND(avg_order_value, 2) AS aov,
  ROUND(avg_review_score, 2) AS avg_nps,
  customer_lifetime_days,
  customer_segment,
  
  -- Percentil
  PERCENT_RANK() OVER (ORDER BY lifetime_value) * 100 AS ltv_percentile,
  
  -- Classificação
  CASE 
    WHEN lifetime_value > 1000 THEN '🏆 VIP'
    WHEN lifetime_value > 500 THEN '⭐ Premium'
    WHEN lifetime_value > 200 THEN '✅ High Value'
    ELSE '📊 Standard'
  END AS tier

FROM customer_ltv
ORDER BY lifetime_value DESC
LIMIT 100;

-- =====================================================
-- 6. ANÁLISE DE PARETO (80/20)
-- =====================================================

WITH customer_ltv AS (
  SELECT 
    c.customer_unique_id,
    SUM(p.payment_value) AS lifetime_value
  FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.orders` o
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.customers` c 
    ON o.customer_id = c.customer_id
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.payments` p 
    ON o.order_id = p.order_id
  WHERE o.order_status = 'delivered'
  GROUP BY c.customer_unique_id
),

pareto_analysis AS (
  SELECT 
    customer_unique_id,
    lifetime_value,
    SUM(lifetime_value) OVER (ORDER BY lifetime_value DESC) AS cumulative_revenue,
    SUM(lifetime_value) OVER () AS total_revenue,
    ROW_NUMBER() OVER (ORDER BY lifetime_value DESC) AS customer_rank,
    COUNT(*) OVER () AS total_customers

  FROM customer_ltv
),

pareto_segments AS (
  SELECT 
    customer_unique_id,
    lifetime_value,
    SAFE_DIVIDE(cumulative_revenue, total_revenue) * 100 AS cumulative_revenue_pct,
    SAFE_DIVIDE(customer_rank, total_customers) * 100 AS cumulative_customer_pct,
    
    CASE 
      WHEN SAFE_DIVIDE(cumulative_revenue, total_revenue) <= 0.80 THEN 'Top 80% Revenue'
      WHEN SAFE_DIVIDE(cumulative_revenue, total_revenue) <= 0.95 THEN 'Next 15% Revenue'
      ELSE 'Bottom 5% Revenue'
    END AS pareto_segment

  FROM pareto_analysis
)

SELECT 
  pareto_segment,
  COUNT(*) AS customers,
  ROUND(SUM(lifetime_value), 2) AS total_revenue,
  ROUND(AVG(lifetime_value), 2) AS avg_ltv,
  ROUND(AVG(cumulative_customer_pct), 2) AS avg_customer_percentile,
  ROUND(AVG(cumulative_revenue_pct), 2) AS avg_revenue_percentile

FROM pareto_segments
GROUP BY pareto_segment
ORDER BY total_revenue DESC;

-- =====================================================
-- 7. LTV FORECAST (Projeção Simples)
-- =====================================================

WITH customer_ltv AS (
  SELECT 
    c.customer_unique_id,
    SUM(p.payment_value) AS lifetime_value,
    COUNT(DISTINCT o.order_id) AS total_orders,
    DATE_DIFF(
      MAX(o.order_purchase_timestamp), 
      MIN(o.order_purchase_timestamp), 
      DAY
    ) AS customer_lifetime_days
  FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.orders` o
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.customers` c 
    ON o.customer_id = c.customer_id
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.payments` p 
    ON o.order_id = p.order_id
  WHERE o.order_status = 'delivered'
  GROUP BY c.customer_unique_id
),

customer_metrics AS (
  SELECT 
    customer_unique_id,
    lifetime_value,
    total_orders,
    customer_lifetime_days,
    
    -- Calcular valor por dia
    SAFE_DIVIDE(lifetime_value, NULLIF(customer_lifetime_days, 0)) AS value_per_day,
    
    -- Projeção para 365 dias
    SAFE_DIVIDE(lifetime_value, NULLIF(customer_lifetime_days, 0)) * 365 AS projected_annual_ltv

  FROM customer_ltv
  WHERE customer_lifetime_days > 30  -- Apenas clientes com histórico
)

SELECT 
  COUNT(*) AS active_customers,
  ROUND(AVG(lifetime_value), 2) AS current_avg_ltv,
  ROUND(AVG(projected_annual_ltv), 2) AS projected_avg_ltv,
  ROUND(SUM(projected_annual_ltv), 2) AS total_projected_revenue,
  
  -- Percentis
  ROUND(APPROX_QUANTILES(projected_annual_ltv, 100)[OFFSET(50)], 2) AS median_projected_ltv,
  ROUND(APPROX_QUANTILES(projected_annual_ltv, 100)[OFFSET(75)], 2) AS p75_projected_ltv,
  ROUND(APPROX_QUANTILES(projected_annual_ltv, 100)[OFFSET(90)], 2) AS p90_projected_ltv

FROM customer_metrics;

-- =====================================================
-- INSIGHTS E OBSERVAÇÕES:
-- =====================================================
-- 
-- 1. LTV Médio esperado: R$ 150-200
-- 2. Estados com maior LTV tendem a ser Sul/Sudeste
-- 3. Taxa de recompra crítica: normalmente < 10%
-- 4. Top 20% clientes geram ~70-80% da receita (Pareto)
-- 5. Cohorts mais antigas têm LTV 30-50% maior
-- 6. Clientes "Loyal" (3+ pedidos) têm LTV 5x maior que "One-time"
-- 
-- AÇÕES RECOMENDADAS:
-- - Focar retenção nos primeiros 30 dias
-- - Programa VIP para top 10% (LTV > R$ 400)
-- - Campanhas regionalizadas (SP vs Sul)
-- - Win-back para clientes inativos há 90+ dias
-- 
-- =====================================================