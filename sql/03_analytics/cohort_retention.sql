-- COHORT RETENTION ANALYSIS
-- Análise avançada de retenção de clientes usando cohorts
-- Window Functions complexas e análise temporal
-- Autor: Andre Bomfim
-- Data: Outubro 2025

-- 1. COHORT BASE (Primeira Compra)

WITH first_purchase AS (
  SELECT 
    c.customer_unique_id,
    c.customer_state,
    MIN(o.order_purchase_timestamp) AS first_purchase_date,
    DATE_TRUNC(MIN(o.order_purchase_timestamp), MONTH) AS cohort_month

  FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.orders` o
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.customers` c 
    ON o.customer_id = c.customer_id
  WHERE o.order_status = 'delivered'
  GROUP BY c.customer_unique_id, c.customer_state
),

-- 2. TODAS AS COMPRAS COM COHORT
all_purchases AS (
  SELECT 
    c.customer_unique_id,
    o.order_purchase_timestamp,
    DATE_TRUNC(o.order_purchase_timestamp, MONTH) AS purchase_month,
    fp.cohort_month,
    fp.customer_state,
    p.payment_value

  FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.orders` o
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.customers` c 
    ON o.customer_id = c.customer_id
  INNER JOIN first_purchase fp 
    ON c.customer_unique_id = fp.customer_unique_id
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.payments` p 
    ON o.order_id = p.order_id
  WHERE o.order_status = 'delivered'
),

-- 3. CÁLCULO DE MESES DESDE COHORT
cohort_data AS (
  SELECT 
    customer_unique_id,
    cohort_month,
    purchase_month,
    customer_state,
    payment_value,
    
    -- Calcular diferença em meses
    DATE_DIFF(purchase_month, cohort_month, MONTH) AS months_since_first_purchase

  FROM all_purchases
),


-- 4. MATRIZ DE RETENÇÃO (Retention Matrix)
retention_matrix AS (
  SELECT 
    cohort_month,
    months_since_first_purchase,
    COUNT(DISTINCT customer_unique_id) AS active_customers,
    SUM(payment_value) AS revenue,
    AVG(payment_value) AS avg_order_value

  FROM cohort_data
  GROUP BY cohort_month, months_since_first_purchase
),

-- Tamanho inicial de cada cohort
cohort_sizes AS (
  SELECT 
    cohort_month,
    COUNT(DISTINCT customer_unique_id) AS cohort_size,
    SUM(payment_value) AS initial_revenue

  FROM cohort_data
  WHERE months_since_first_purchase = 0
  GROUP BY cohort_month
),


-- 5. TAXA DE RETENÇÃO CALCULADA
retention_rates AS (
  SELECT 
    rm.cohort_month,
    rm.months_since_first_purchase,
    cs.cohort_size,
    rm.active_customers,
    rm.revenue,
    rm.avg_order_value,
    
    -- Taxa de retenção (%)
    ROUND(
      SAFE_DIVIDE(rm.active_customers, cs.cohort_size) * 100, 
      2
    ) AS retention_rate_pct,
    
    -- Receita por cliente do cohort
    ROUND(
      SAFE_DIVIDE(rm.revenue, cs.cohort_size), 
      2
    ) AS revenue_per_cohort_customer

  FROM retention_matrix rm
  INNER JOIN cohort_sizes cs 
    ON rm.cohort_month = cs.cohort_month
)

SELECT * FROM retention_rates
ORDER BY cohort_month, months_since_first_purchase;

-- 6. PIVOT TABLE - VISUALIZAÇÃO CLÁSSICA DE COHORT
WITH retention_pivot AS (
  SELECT 
    cohort_month,
    
    -- M0 a M11 (12 meses)
    MAX(CASE WHEN months_since_first_purchase = 0 THEN retention_rate_pct END) AS M0,
    MAX(CASE WHEN months_since_first_purchase = 1 THEN retention_rate_pct END) AS M1,
    MAX(CASE WHEN months_since_first_purchase = 2 THEN retention_rate_pct END) AS M2,
    MAX(CASE WHEN months_since_first_purchase = 3 THEN retention_rate_pct END) AS M3,
    MAX(CASE WHEN months_since_first_purchase = 4 THEN retention_rate_pct END) AS M4,
    MAX(CASE WHEN months_since_first_purchase = 5 THEN retention_rate_pct END) AS M5,
    MAX(CASE WHEN months_since_first_purchase = 6 THEN retention_rate_pct END) AS M6,
    MAX(CASE WHEN months_since_first_purchase = 7 THEN retention_rate_pct END) AS M7,
    MAX(CASE WHEN months_since_first_purchase = 8 THEN retention_rate_pct END) AS M8,
    MAX(CASE WHEN months_since_first_purchase = 9 THEN retention_rate_pct END) AS M9,
    MAX(CASE WHEN months_since_first_purchase = 10 THEN retention_rate_pct END) AS M10,
    MAX(CASE WHEN months_since_first_purchase = 11 THEN retention_rate_pct END) AS M11

  FROM retention_rates
  GROUP BY cohort_month
)

SELECT 
  FORMAT_DATE('%Y-%m', cohort_month) AS cohort,
  M0, M1, M2, M3, M4, M5, M6, M7, M8, M9, M10, M11

FROM retention_pivot
ORDER BY cohort_month DESC;


-- 7. ANÁLISE DE CHURN (Complemento da Retenção)
WITH churn_analysis AS (
  SELECT 
    cohort_month,
    months_since_first_purchase,
    retention_rate_pct,
    
    -- Churn rate
    100 - retention_rate_pct AS churn_rate_pct,
    
    -- Churn incremental (vs mês anterior)
    LAG(retention_rate_pct) OVER (
      PARTITION BY cohort_month 
      ORDER BY months_since_first_purchase
    ) - retention_rate_pct AS incremental_churn_pct

  FROM retention_rates
)

SELECT 
  cohort_month,
  months_since_first_purchase,
  ROUND(retention_rate_pct, 2) AS retention_pct,
  ROUND(churn_rate_pct, 2) AS churn_pct,
  ROUND(incremental_churn_pct, 2) AS incremental_churn_pct

FROM churn_analysis
WHERE months_since_first_purchase <= 12
ORDER BY cohort_month DESC, months_since_first_purchase;


-- 8. MÉTRICAS AGREGADAS POR COHORT
WITH cohort_summary AS (
  SELECT 
    cohort_month,
    
    -- Tamanho e receita inicial
    MAX(CASE WHEN months_since_first_purchase = 0 THEN active_customers END) AS initial_size,
    SUM(revenue) AS total_lifetime_revenue,
    AVG(avg_order_value) AS avg_aov,
    
    -- Retenção crítica
    MAX(CASE WHEN months_since_first_purchase = 1 THEN retention_rate_pct END) AS m1_retention,
    MAX(CASE WHEN months_since_first_purchase = 3 THEN retention_rate_pct END) AS m3_retention,
    MAX(CASE WHEN months_since_first_purchase = 6 THEN retention_rate_pct END) AS m6_retention,
    
    -- Receita por customer
    SAFE_DIVIDE(
      SUM(revenue), 
      MAX(CASE WHEN months_since_first_purchase = 0 THEN active_customers END)
    ) AS ltv_per_customer

  FROM retention_rates
  GROUP BY cohort_month
)

SELECT 
  FORMAT_DATE('%Y-%m', cohort_month) AS cohort,
  initial_size,
  ROUND(total_lifetime_revenue, 2) AS total_revenue,
  ROUND(avg_aov, 2) AS avg_aov,
  ROUND(m1_retention, 2) AS m1_retention_pct,
  ROUND(m3_retention, 2) AS m3_retention_pct,
  ROUND(m6_retention, 2) AS m6_retention_pct,
  ROUND(ltv_per_customer, 2) AS ltv_per_customer,
  
  -- Qualidade do cohort
  CASE 
    WHEN m1_retention > 5 AND m6_retention > 2 THEN ' Excelente'
    WHEN m1_retention > 3 AND m6_retention > 1 THEN ' Bom'
    ELSE ' Baixo'
  END AS cohort_quality

FROM cohort_summary
ORDER BY cohort_month DESC;


-- 9. RETENÇÃO POR ESTADO (Análise Geográfica)
WITH state_retention AS (
  SELECT 
    customer_state,
    months_since_first_purchase,
    COUNT(DISTINCT customer_unique_id) AS active_customers,
    
    -- Total de clientes do estado (M0)
    COUNT(DISTINCT customer_unique_id) OVER (
      PARTITION BY customer_state
    ) AS state_total_customers

  FROM cohort_data
  GROUP BY customer_state, months_since_first_purchase
)

SELECT 
  customer_state,
  months_since_first_purchase,
  active_customers,
  state_total_customers,
  
  ROUND(
    SAFE_DIVIDE(active_customers, state_total_customers) * 100, 
    2
  ) AS retention_rate_pct

FROM state_retention
WHERE months_since_first_purchase BETWEEN 0 AND 6
ORDER BY customer_state, months_since_first_purchase;


-- 10. CURVA DE RETENÇÃO MÉDIA (Benchmark)


WITH avg_retention_curve AS (
  SELECT 
    months_since_first_purchase,
    AVG(retention_rate_pct) AS avg_retention_rate,
    STDDEV(retention_rate_pct) AS stddev_retention,
    COUNT(DISTINCT cohort_month) AS num_cohorts,
    
    -- Percentis
    APPROX_QUANTILES(retention_rate_pct, 100)[OFFSET(25)] AS p25_retention,
    APPROX_QUANTILES(retention_rate_pct, 100)[OFFSET(50)] AS median_retention,
    APPROX_QUANTILES(retention_rate_pct, 100)[OFFSET(75)] AS p75_retention

  FROM retention_rates
  WHERE months_since_first_purchase <= 12
  GROUP BY months_since_first_purchase
)

SELECT 
  months_since_first_purchase AS month,
  ROUND(avg_retention_rate, 2) AS avg_retention_pct,
  ROUND(median_retention, 2) AS median_retention_pct,
  ROUND(stddev_retention, 2) AS stddev,
  num_cohorts,
  
  -- Interpretação
  CASE 
    WHEN months_since_first_purchase = 0 THEN 'Baseline (100%)'
    WHEN months_since_first_purchase = 1 THEN 'Crítico - Maior churn'
    WHEN months_since_first_purchase BETWEEN 2 AND 3 THEN 'Estabilização'
    WHEN months_since_first_purchase >= 4 THEN 'Clientes Fidelizados'
  END AS phase

FROM avg_retention_curve
ORDER BY months_since_first_purchase;

