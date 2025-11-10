-- DELIVERY & LOGISTICS ANALYSIS
-- Análise completa de performance de entrega e logística
-- SLA, atrasos, correlação com NPS, rotas críticas
-- Autor: Andre Bomfim
-- Data: Outubro 2025


-- 1. PERFORMANCE GERAL DE ENTREGA
WITH delivery_metrics AS (
  SELECT 
    COUNT(DISTINCT order_id) AS total_orders,
    
    -- Tempo médio de entrega
    AVG(days_to_delivery) AS avg_delivery_days,
    APPROX_QUANTILES(days_to_delivery, 100)[OFFSET(50)] AS median_delivery_days,
    APPROX_QUANTILES(days_to_delivery, 100)[OFFSET(90)] AS p90_delivery_days,
    
    -- Atraso
    AVG(delivery_delay_days) AS avg_delay_days,
    COUNTIF(delivery_status = 'Delayed') AS delayed_orders,
    COUNTIF(delivery_status = 'On Time') AS ontime_orders,
    
    -- SLA (% entregues no prazo)
    SAFE_DIVIDE(
      COUNTIF(delivery_status = 'On Time'),
      COUNT(*)
    ) * 100 AS sla_compliance_pct,
    
    -- Extremos
    MIN(days_to_delivery) AS fastest_delivery,
    MAX(days_to_delivery) AS slowest_delivery
    
  FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_orders`
  WHERE order_status = 'delivered'
    AND days_to_delivery IS NOT NULL
)

SELECT 
  total_orders,
  ROUND(avg_delivery_days, 1) AS avg_delivery_days,
  median_delivery_days,
  p90_delivery_days,
  ROUND(avg_delay_days, 1) AS avg_delay_days,
  delayed_orders,
  ontime_orders,
  ROUND(sla_compliance_pct, 2) AS sla_compliance_pct,
  fastest_delivery,
  slowest_delivery
FROM delivery_metrics;


-- 2. PERFORMANCE POR ROTA (Estado Seller → Cliente)
WITH route_performance AS (
  SELECT 
    oi.seller_state,
    oi.customer_state,
    CONCAT(oi.seller_state, ' → ', oi.customer_state) AS route,
    oi.is_same_state_shipping,
    oi.shipping_distance_category,
    
    -- Volume
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(oi.price) AS total_revenue,
    
    -- Delivery metrics
    AVG(o.days_to_delivery) AS avg_delivery_days,
    AVG(o.delivery_delay_days) AS avg_delay_days,
    
    -- SLA
    SAFE_DIVIDE(
      COUNTIF(o.delivery_status = 'On Time'),
      COUNT(*)
    ) * 100 AS sla_compliance_pct,
    
    -- Customer satisfaction
    AVG(r.review_score) AS avg_review_score,
    
    -- Freight cost
    AVG(oi.freight_value) AS avg_freight_cost
    
  FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_order_items` oi
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_orders` o 
    ON oi.order_id = o.order_id
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.reviews` r 
    ON o.order_id = r.order_id
  WHERE o.order_status = 'delivered'
    AND o.days_to_delivery IS NOT NULL
  GROUP BY 
    oi.seller_state, 
    oi.customer_state, 
    route,
    oi.is_same_state_shipping,
    oi.shipping_distance_category
)

SELECT 
  route,
  seller_state,
  customer_state,
  shipping_distance_category,
  total_orders,
  ROUND(total_revenue, 2) AS total_revenue,
  ROUND(avg_delivery_days, 1) AS avg_delivery_days,
  ROUND(avg_delay_days, 1) AS avg_delay_days,
  ROUND(sla_compliance_pct, 2) AS sla_compliance_pct,
  ROUND(avg_review_score, 2) AS avg_nps,
  ROUND(avg_freight_cost, 2) AS avg_freight,
  
  -- Classificação de performance
  CASE 
    WHEN sla_compliance_pct >= 90 AND avg_review_score >= 4.0 THEN ' Excelente'
    WHEN sla_compliance_pct >= 75 AND avg_review_score >= 3.5 THEN ' Bom'
    WHEN sla_compliance_pct >= 60 THEN 'Precisa Melhorar'
    ELSE 'Crítico'
  END AS route_performance_status

FROM route_performance
WHERE total_orders >= 10  -- Mínimo de volume para análise
ORDER BY total_orders DESC;


-- 3. ANÁLISE DE ATRASO POR REGIÃO


WITH regional_delays AS (
  SELECT 
    c.customer_region,
    s.seller_region,
    
    -- Volume
    COUNT(DISTINCT o.order_id) AS orders,
    
    -- Delivery performance
    AVG(o.days_to_delivery) AS avg_delivery_days,
    AVG(o.delivery_delay_days) AS avg_delay_days,
    
    -- Delay distribution
    COUNTIF(o.delivery_delay_days <= 0) AS early_or_ontime,
    COUNTIF(o.delivery_delay_days BETWEEN 1 AND 5) AS delay_1_5_days,
    COUNTIF(o.delivery_delay_days BETWEEN 6 AND 10) AS delay_6_10_days,
    COUNTIF(o.delivery_delay_days > 10) AS delay_over_10_days,
    
    -- SLA
    SAFE_DIVIDE(
      COUNTIF(o.delivery_status = 'On Time'),
      COUNT(*)
    ) * 100 AS sla_pct,
    
    -- NPS
    AVG(r.review_score) AS avg_nps
    
  FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_orders` o
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_customers` c 
    ON o.customer_id = c.customer_id
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_order_items` oi 
    ON o.order_id = oi.order_id
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.sellers` s 
    ON oi.seller_id = s.seller_id
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.reviews` r 
    ON o.order_id = r.order_id
  WHERE o.order_status = 'delivered'
  GROUP BY c.customer_region, s.seller_region
)

SELECT 
  seller_region,
  customer_region,
  orders,
  ROUND(avg_delivery_days, 1) AS avg_delivery_days,
  ROUND(avg_delay_days, 1) AS avg_delay_days,
  early_or_ontime,
  delay_1_5_days,
  delay_6_10_days,
  delay_over_10_days,
  ROUND(sla_pct, 2) AS sla_pct,
  ROUND(avg_nps, 2) AS avg_nps,
  
  -- % de atrasos graves
  ROUND(delay_over_10_days / orders * 100, 2) AS severe_delay_pct

FROM regional_delays
ORDER BY orders DESC;


-- 4. CORRELAÇÃO: TEMPO DE ENTREGA vs NPS


WITH delivery_nps_correlation AS (
  SELECT 
    -- Buckets de tempo de entrega
    CASE 
      WHEN days_to_delivery <= 7 THEN '0-7 days (Express)'
      WHEN days_to_delivery <= 14 THEN '8-14 days (Fast)'
      WHEN days_to_delivery <= 21 THEN '15-21 days (Normal)'
      WHEN days_to_delivery <= 30 THEN '22-30 days (Slow)'
      ELSE '31+ days (Very Slow)'
    END AS delivery_time_bucket,
    
    COUNT(DISTINCT o.order_id) AS orders,
    AVG(r.review_score) AS avg_nps,
    
    -- NPS distribution
    COUNTIF(r.review_score = 5) AS reviews_5_stars,
    COUNTIF(r.review_score = 4) AS reviews_4_stars,
    COUNTIF(r.review_score <= 3) AS reviews_3_or_less,
    
    -- Positive review rate
    SAFE_DIVIDE(
      COUNTIF(r.review_score >= 4),
      COUNT(*)
    ) * 100 AS positive_review_pct
    
  FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_orders` o
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.reviews` r 
    ON o.order_id = r.order_id
  WHERE o.order_status = 'delivered'
    AND o.days_to_delivery IS NOT NULL
    AND r.review_score IS NOT NULL
  GROUP BY delivery_time_bucket
)

SELECT 
  delivery_time_bucket,
  orders,
  ROUND(avg_nps, 2) AS avg_nps,
  reviews_5_stars,
  reviews_4_stars,
  reviews_3_or_less,
  ROUND(positive_review_pct, 2) AS positive_review_pct,
  
  -- Impact on NPS (vs baseline)
  ROUND(
    avg_nps - AVG(avg_nps) OVER (),
    2
  ) AS nps_vs_avg

FROM delivery_nps_correlation
ORDER BY 
  CASE delivery_time_bucket
    WHEN '0-7 days (Express)' THEN 1
    WHEN '8-14 days (Fast)' THEN 2
    WHEN '15-21 days (Normal)' THEN 3
    WHEN '22-30 days (Slow)' THEN 4
    ELSE 5
  END;


-- 5. ANÁLISE DE ATRASO vs NPS (Detalhado)

WITH delay_impact AS (
  SELECT 
    -- Buckets de atraso
    CASE 
      WHEN delivery_delay_days <= -5 THEN 'Antecipado (5+ dias)'
      WHEN delivery_delay_days <= 0 THEN 'No Prazo'
      WHEN delivery_delay_days <= 3 THEN 'Atraso Leve (1-3 dias)'
      WHEN delivery_delay_days <= 7 THEN 'Atraso Médio (4-7 dias)'
      WHEN delivery_delay_days <= 14 THEN 'Atraso Alto (8-14 dias)'
      ELSE 'Atraso Crítico (15+ dias)'
    END AS delay_bucket,
    
    COUNT(DISTINCT o.order_id) AS orders,
    AVG(r.review_score) AS avg_nps,
    
    -- Distribution
    ROUND(COUNT(*) / SUM(COUNT(*)) OVER () * 100, 2) AS pct_of_orders,
    
    -- Detractor rate (NPS ≤ 2)
    SAFE_DIVIDE(
      COUNTIF(r.review_score <= 2),
      COUNT(*)
    ) * 100 AS detractor_rate_pct
    
  FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_orders` o
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.reviews` r 
    ON o.order_id = r.order_id
  WHERE o.order_status = 'delivered'
    AND o.delivery_delay_days IS NOT NULL
    AND r.review_score IS NOT NULL
  GROUP BY delay_bucket
)

SELECT 
  delay_bucket,
  orders,
  pct_of_orders,
  ROUND(avg_nps, 2) AS avg_nps,
  ROUND(detractor_rate_pct, 2) AS detractor_rate_pct,
  
  -- NPS impact (diferença vs baseline)
  ROUND(avg_nps - LAG(avg_nps) OVER (ORDER BY avg_nps DESC), 2) AS nps_degradation

FROM delay_impact
ORDER BY avg_nps DESC;


-- 6. TOP 20 ROTAS CRÍTICAS (Maior Volume + Pior SLA)
WITH critical_routes AS (
  SELECT 
    oi.seller_state,
    oi.customer_state,
    CONCAT(oi.seller_state, ' → ', oi.customer_state) AS route,
    
    COUNT(DISTINCT o.order_id) AS orders,
    SUM(oi.price) AS revenue,
    
    -- Delivery metrics
    AVG(o.days_to_delivery) AS avg_delivery_days,
    
    -- SLA
    SAFE_DIVIDE(
      COUNTIF(o.delivery_status = 'On Time'),
      COUNT(*)
    ) * 100 AS sla_pct,
    
    -- Delay severity
    AVG(o.delivery_delay_days) AS avg_delay_days,
    COUNTIF(o.delivery_delay_days > 10) AS severe_delays,
    
    -- NPS impact
    AVG(r.review_score) AS avg_nps,
    
    -- Criticality score (volume * delay * nps_impact)
    COUNT(*) * AVG(o.delivery_delay_days) * (5 - AVG(r.review_score)) AS criticality_score
    
  FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_order_items` oi
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_orders` o 
    ON oi.order_id = o.order_id
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.reviews` r 
    ON o.order_id = r.order_id
  WHERE o.order_status = 'delivered'
    AND o.days_to_delivery IS NOT NULL
  GROUP BY oi.seller_state, oi.customer_state, route
  HAVING COUNT(DISTINCT o.order_id) >= 50  -- Rotas com volume significativo
)

SELECT 
  route,
  orders,
  ROUND(revenue, 2) AS revenue,
  ROUND(avg_delivery_days, 1) AS avg_delivery_days,
  ROUND(sla_pct, 2) AS sla_pct,
  ROUND(avg_delay_days, 1) AS avg_delay_days,
  severe_delays,
  ROUND(avg_nps, 2) AS avg_nps,
  ROUND(criticality_score, 2) AS criticality_score,
  
  -- Priority level
  CASE 
    WHEN sla_pct < 60 AND avg_nps < 3.5 THEN ' P0 - Urgente'
    WHEN sla_pct < 70 AND avg_nps < 4.0 THEN ' P1 - Alta'
    WHEN sla_pct < 80 THEN ' P2 - Média'
    ELSE ' P3 - Baixa'
  END AS priority

FROM critical_routes
ORDER BY criticality_score DESC
LIMIT 20;


-- 7. ANÁLISE TEMPORAL (Evolução Mensal de SLA)


WITH monthly_sla AS (
  SELECT 
    order_year_month,
    
    COUNT(DISTINCT order_id) AS orders,
    AVG(days_to_delivery) AS avg_delivery_days,
    
    -- SLA
    SAFE_DIVIDE(
      COUNTIF(delivery_status = 'On Time'),
      COUNT(*)
    ) * 100 AS sla_pct,
    
    -- Delays
    AVG(delivery_delay_days) AS avg_delay_days,
    COUNTIF(delivery_delay_days > 10) AS severe_delays,
    
    -- NPS
    AVG(r.review_score) AS avg_nps
    
  FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_orders` o
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.reviews` r 
    ON o.order_id = r.order_id
  WHERE order_status = 'delivered'
    AND days_to_delivery IS NOT NULL
  GROUP BY order_year_month
)

SELECT 
  order_year_month,
  orders,
  ROUND(avg_delivery_days, 1) AS avg_delivery_days,
  ROUND(sla_pct, 2) AS sla_pct,
  ROUND(avg_delay_days, 1) AS avg_delay_days,
  severe_delays,
  ROUND(avg_nps, 2) AS avg_nps,
  
  -- Month-over-month change
  ROUND(sla_pct - LAG(sla_pct) OVER (ORDER BY order_year_month), 2) AS sla_mom_change,
  ROUND(avg_nps - LAG(avg_nps) OVER (ORDER BY order_year_month), 2) AS nps_mom_change

FROM monthly_sla
ORDER BY order_year_month;


-- 8. ANÁLISE DE PESO vs TEMPO DE ENTREGA

SELECT 
  oi.weight_tier,
  
  COUNT(DISTINCT o.order_id) AS orders,
  AVG(oi.product_weight_g) AS avg_weight_g,
  AVG(o.days_to_delivery) AS avg_delivery_days,
  AVG(oi.freight_value) AS avg_freight,
  
  -- SLA
  SAFE_DIVIDE(
    COUNTIF(o.delivery_status = 'On Time'),
    COUNT(*)
  ) * 100 AS sla_pct,
  
  -- NPS
  AVG(r.review_score) AS avg_nps

FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_order_items` oi
INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_orders` o 
  ON oi.order_id = o.order_id
LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.reviews` r 
  ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
  AND oi.weight_tier IS NOT NULL
GROUP BY oi.weight_tier
ORDER BY avg_weight_g;

