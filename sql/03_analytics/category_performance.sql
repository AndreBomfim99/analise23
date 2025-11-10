-- PRODUCT CATEGORY PERFORMANCE ANALYSIS
-- Análise completa de performance por categoria de produto
-- Revenue, NPS, AOV, Sazonalidade e Margem
-- Autor: Andre Bomfim
-- Data: Outubro 2025

-- 1. PERFORMANCE GERAL POR CATEGORIA

WITH category_metrics AS (
  SELECT 
    COALESCE(pct.product_category_name_english, 'Unknown') AS category,
    
    -- Revenue metrics
    COUNT(DISTINCT oi.order_id) AS total_orders,
    COUNT(DISTINCT oi.order_item_id) AS total_items,
    SUM(oi.price) AS total_revenue,
    SUM(oi.freight_value) AS total_freight,
    SUM(oi.price + oi.freight_value) AS total_gmv,
    
    -- Average metrics
    AVG(oi.price) AS avg_item_price,
    AVG(oi.freight_value) AS avg_freight,
    AVG(oi.price + oi.freight_value) AS avg_order_value,
    
    -- Customer satisfaction
    AVG(r.review_score) AS avg_review_score,
    COUNTIF(r.review_score >= 4) / COUNT(r.review_score) * 100 AS positive_review_pct,
    
    -- Product metrics
    COUNT(DISTINCT oi.product_id) AS unique_products,
    COUNT(DISTINCT oi.seller_id) AS unique_sellers

  FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.order_items` oi
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.products` p 
    ON oi.product_id = p.product_id
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.product_category_translation` pct 
    ON p.product_category_name = pct.product_category_name
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.orders` o 
    ON oi.order_id = o.order_id
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.reviews` r 
    ON o.order_id = r.order_id
  WHERE o.order_status = 'delivered'
  GROUP BY category
)

SELECT 
  category,
  total_orders,
  total_items,
  ROUND(total_revenue, 2) AS revenue,
  ROUND(total_gmv, 2) AS gmv,
  ROUND(avg_item_price, 2) AS avg_price,
  ROUND(avg_order_value, 2) AS avg_aov,
  ROUND(avg_review_score, 2) AS avg_nps,
  ROUND(positive_review_pct, 2) AS positive_review_pct,
  unique_products,
  unique_sellers,
  
  -- Market share
  ROUND(total_revenue / SUM(total_revenue) OVER () * 100, 2) AS revenue_share_pct,
  
  -- Rank
  RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank,
  RANK() OVER (ORDER BY avg_review_score DESC) AS nps_rank

FROM category_metrics
ORDER BY total_revenue DESC;


-- 2. TOP 10 CATEGORIAS POR RECEITA
WITH category_revenue AS (
  SELECT 
    COALESCE(pct.product_category_name_english, 'Unknown') AS category,
    SUM(oi.price) AS total_revenue,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    AVG(r.review_score) AS avg_nps,
    COUNT(DISTINCT oi.product_id) AS unique_products
    
  FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.order_items` oi
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.products` p 
    ON oi.product_id = p.product_id
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.product_category_translation` pct 
    ON p.product_category_name = pct.product_category_name
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.orders` o 
    ON oi.order_id = o.order_id
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.reviews` r 
    ON o.order_id = r.order_id
  WHERE o.order_status = 'delivered'
  GROUP BY category
)

SELECT 
  category,
  ROUND(total_revenue, 2) AS revenue,
  total_orders,
  ROUND(avg_nps, 2) AS avg_nps,
  unique_products,
  ROUND(total_revenue / SUM(total_revenue) OVER () * 100, 2) AS market_share_pct,
  
  -- Classificação
  CASE 
    WHEN avg_nps >= 4.5 AND total_revenue > 100000 THEN '🏆 Star Category'
    WHEN avg_nps >= 4.0 AND total_revenue > 50000 THEN '⭐ High Performer'
    WHEN avg_nps < 3.5 AND total_revenue > 50000 THEN '⚠️ Needs Improvement'
    WHEN total_revenue < 10000 THEN '📉 Low Volume'
    ELSE '📊 Standard'
  END AS category_status

FROM category_revenue
ORDER BY total_revenue DESC
LIMIT 10;


-- 3. ANÁLISE DE SAZONALIDADE (Mensal)
WITH monthly_category AS (
  SELECT 
    DATE_TRUNC(o.order_purchase_timestamp, MONTH) AS month,
    COALESCE(pct.product_category_name_english, 'Unknown') AS category,
    SUM(oi.price) AS revenue,
    COUNT(DISTINCT oi.order_id) AS orders
    
  FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.order_items` oi
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.products` p 
    ON oi.product_id = p.product_id
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.product_category_translation` pct 
    ON p.product_category_name = pct.product_category_name
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.orders` o 
    ON oi.order_id = o.order_id
  WHERE o.order_status = 'delivered'
  GROUP BY month, category
),

top_categories AS (
  SELECT category
  FROM monthly_category
  GROUP BY category
  ORDER BY SUM(revenue) DESC
  LIMIT 5
)

SELECT 
  mc.month,
  mc.category,
  ROUND(mc.revenue, 2) AS revenue,
  mc.orders,
  
  -- Growth vs previous month
  ROUND(
    (mc.revenue - LAG(mc.revenue) OVER (PARTITION BY mc.category ORDER BY mc.month)) 
    / NULLIF(LAG(mc.revenue) OVER (PARTITION BY mc.category ORDER BY mc.month), 0) * 100,
    2
  ) AS mom_growth_pct,
  
  -- Share of category in that month
  ROUND(mc.revenue / SUM(mc.revenue) OVER (PARTITION BY mc.month) * 100, 2) AS month_share_pct

FROM monthly_category mc
INNER JOIN top_categories tc ON mc.category = tc.category
ORDER BY mc.month DESC, mc.revenue DESC;


-- 4. ANÁLISE DE TICKET MÉDIO POR CATEGORIA
WITH category_aov AS (
  SELECT 
    COALESCE(pct.product_category_name_english, 'Unknown') AS category,
    oi.order_id,
    SUM(oi.price + oi.freight_value) AS order_value
    
  FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.order_items` oi
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.products` p 
    ON oi.product_id = p.product_id
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.product_category_translation` pct 
    ON p.product_category_name = pct.product_category_name
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.orders` o 
    ON oi.order_id = o.order_id
  WHERE o.order_status = 'delivered'
  GROUP BY category, oi.order_id
)

SELECT 
  category,
  COUNT(DISTINCT order_id) AS total_orders,
  ROUND(AVG(order_value), 2) AS avg_order_value,
  ROUND(APPROX_QUANTILES(order_value, 100)[OFFSET(50)], 2) AS median_order_value,
  ROUND(APPROX_QUANTILES(order_value, 100)[OFFSET(75)], 2) AS p75_order_value,
  ROUND(APPROX_QUANTILES(order_value, 100)[OFFSET(90)], 2) AS p90_order_value,
  ROUND(MIN(order_value), 2) AS min_order_value,
  ROUND(MAX(order_value), 2) AS max_order_value,
  
  -- Classificação por AOV
  CASE 
    WHEN AVG(order_value) > 200 THEN 'High Ticket'
    WHEN AVG(order_value) > 100 THEN 'Medium Ticket'
    ELSE 'Low Ticket'
  END AS ticket_tier

FROM category_aov
GROUP BY category
ORDER BY avg_order_value DESC;


-- 5. ANÁLISE DE NPS POR CATEGORIA
WITH category_nps AS (
  SELECT 
    COALESCE(pct.product_category_name_english, 'Unknown') AS category,
    r.review_score,
    COUNT(*) AS review_count
    
  FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.order_items` oi
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.products` p 
    ON oi.product_id = p.product_id
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.product_category_translation` pct 
    ON p.product_category_name = pct.product_category_name
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.orders` o 
    ON oi.order_id = o.order_id
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.reviews` r 
    ON o.order_id = r.order_id
  WHERE o.order_status = 'delivered'
  GROUP BY category, r.review_score
)

SELECT 
  category,
  SUM(review_count) AS total_reviews,
  ROUND(AVG(review_score), 2) AS avg_nps,
  
  -- Distribuição de scores
  ROUND(SUM(CASE WHEN review_score = 5 THEN review_count ELSE 0 END) / SUM(review_count) * 100, 2) AS pct_5_stars,
  ROUND(SUM(CASE WHEN review_score = 4 THEN review_count ELSE 0 END) / SUM(review_count) * 100, 2) AS pct_4_stars,
  ROUND(SUM(CASE WHEN review_score = 3 THEN review_count ELSE 0 END) / SUM(review_count) * 100, 2) AS pct_3_stars,
  ROUND(SUM(CASE WHEN review_score <= 2 THEN review_count ELSE 0 END) / SUM(review_count) * 100, 2) AS pct_negative,
  
  -- NPS Score (Promoters - Detractors)
  ROUND(
    (SUM(CASE WHEN review_score >= 4 THEN review_count ELSE 0 END) / SUM(review_count) * 100) -
    (SUM(CASE WHEN review_score <= 2 THEN review_count ELSE 0 END) / SUM(review_count) * 100),
    2
  ) AS nps_score,
  
  -- Status
  CASE 
    WHEN AVG(review_score) >= 4.5 THEN '🟢 Excelente'
    WHEN AVG(review_score) >= 4.0 THEN '🟡 Bom'
    WHEN AVG(review_score) >= 3.5 THEN '🟠 Regular'
    ELSE '🔴 Ruim'
  END AS nps_status

FROM category_nps
GROUP BY category
HAVING SUM(review_count) >= 10  -- minimo de 10 reviews
ORDER BY avg_nps DESC;


-- 6. MARGEM ESTIMADA POR CATEGORIA (Frete vs Preço)
WITH category_margin AS (
  SELECT 
    COALESCE(pct.product_category_name_english, 'Unknown') AS category,
    
    -- Revenue breakdown
    SUM(oi.price) AS gross_revenue,
    SUM(oi.freight_value) AS freight_cost,
    SUM(oi.price + oi.freight_value) AS total_gmv,
    
    -- Margin estimation (simplificada)
    SUM(oi.price) - SUM(oi.freight_value) AS estimated_margin,
    
    -- Percentages
    SAFE_DIVIDE(SUM(oi.freight_value), SUM(oi.price)) * 100 AS freight_pct_of_price
    
  FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.order_items` oi
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.products` p 
    ON oi.product_id = p.product_id
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.product_category_translation` pct 
    ON p.product_category_name = pct.product_category_name
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.orders` o 
    ON oi.order_id = o.order_id
  WHERE o.order_status = 'delivered'
  GROUP BY category
)

SELECT 
  category,
  ROUND(gross_revenue, 2) AS revenue,
  ROUND(freight_cost, 2) AS freight_cost,
  ROUND(estimated_margin, 2) AS estimated_margin,
  ROUND(freight_pct_of_price, 2) AS freight_pct,
  
  -- Margin %
  ROUND(SAFE_DIVIDE(estimated_margin, gross_revenue) * 100, 2) AS margin_pct,
  
  -- Classification
  CASE 
    WHEN SAFE_DIVIDE(estimated_margin, gross_revenue) > 0.80 THEN '🟢 High Margin'
    WHEN SAFE_DIVIDE(estimated_margin, gross_revenue) > 0.70 THEN '🟡 Medium Margin'
    ELSE '🔴 Low Margin'
  END AS margin_tier,
  
  RANK() OVER (ORDER BY estimated_margin DESC) AS margin_rank

FROM category_margin
ORDER BY estimated_margin DESC;


-- 7. ANÁLISE DE CROSS-SELL (Categorias Compradas Juntas)
WITH order_categories AS (
  SELECT 
    o.order_id,
    COALESCE(pct.product_category_name_english, 'Unknown') AS category
    
  FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.orders` o
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.order_items` oi 
    ON o.order_id = oi.order_id
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.products` p 
    ON oi.product_id = p.product_id
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.product_category_translation` pct 
    ON p.product_category_name = pct.product_category_name
  WHERE o.order_status = 'delivered'
  GROUP BY o.order_id, category
),

category_pairs AS (
  SELECT 
    oc1.category AS category_a,
    oc2.category AS category_b,
    COUNT(DISTINCT oc1.order_id) AS co_occurrence_count
    
  FROM order_categories oc1
  INNER JOIN order_categories oc2 
    ON oc1.order_id = oc2.order_id 
    AND oc1.category < oc2.category  -- Evitar duplicatas
  GROUP BY oc1.category, oc2.category
)

SELECT 
  category_a,
  category_b,
  co_occurrence_count,
  
  -- Calcular lift (força da associação)
  ROUND(
    co_occurrence_count / 
    (SELECT COUNT(DISTINCT order_id) FROM order_categories) * 100,
    2
  ) AS co_occurrence_pct

FROM category_pairs
WHERE co_occurrence_count >= 10  -- Minimo de 10 co-ocorrências
ORDER BY co_occurrence_count DESC
LIMIT 20;


-- 8. RANKING GERAL DE CATEGORIAS (Score Composto)
WITH category_metrics AS (
  SELECT 
    COALESCE(pct.product_category_name_english, 'Unknown') AS category,
    SUM(oi.price) AS revenue,
    COUNT(DISTINCT oi.order_id) AS orders,
    AVG(r.review_score) AS avg_nps,
    AVG(oi.price + oi.freight_value) AS avg_aov,
    SAFE_DIVIDE(SUM(oi.price) - SUM(oi.freight_value), SUM(oi.price)) AS margin_pct
    
  FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.order_items` oi
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.products` p 
    ON oi.product_id = p.product_id
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.product_category_translation` pct 
    ON p.product_category_name = pct.product_category_name
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.orders` o 
    ON oi.order_id = o.order_id
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.reviews` r 
    ON o.order_id = r.order_id
  WHERE o.order_status = 'delivered'
  GROUP BY category
),

normalized_metrics AS (
  SELECT 
    category,
    revenue,
    orders,
    avg_nps,
    avg_aov,
    margin_pct,
    
    -- Normalizar métricas (0-100)
    PERCENT_RANK() OVER (ORDER BY revenue) * 100 AS revenue_score,
    PERCENT_RANK() OVER (ORDER BY orders) * 100 AS volume_score,
    PERCENT_RANK() OVER (ORDER BY avg_nps) * 100 AS nps_score,
    PERCENT_RANK() OVER (ORDER BY avg_aov) * 100 AS aov_score,
    PERCENT_RANK() OVER (ORDER BY margin_pct) * 100 AS margin_score
    
  FROM category_metrics
)

SELECT 
  category,
  ROUND(revenue, 2) AS revenue,
  orders,
  ROUND(avg_nps, 2) AS avg_nps,
  ROUND(avg_aov, 2) AS avg_aov,
  ROUND(margin_pct * 100, 2) AS margin_pct,
  
  -- Score composto (média ponderada)
  ROUND(
    (revenue_score * 0.35) +  -- Revenue peso 35%
    (nps_score * 0.25) +      -- NPS peso 25%
    (aov_score * 0.20) +      -- AOV peso 20%
    (margin_score * 0.20),    -- Margin peso 20%
    2
  ) AS composite_score,
  
  -- Classificação final
  CASE 
    WHEN (revenue_score * 0.35 + nps_score * 0.25 + aov_score * 0.20 + margin_score * 0.20) >= 80 THEN '🏆 Tier S'
    WHEN (revenue_score * 0.35 + nps_score * 0.25 + aov_score * 0.20 + margin_score * 0.20) >= 60 THEN '⭐ Tier A'
    WHEN (revenue_score * 0.35 + nps_score * 0.25 + aov_score * 0.20 + margin_score * 0.20) >= 40 THEN '✅ Tier B'
    ELSE '📊 Tier C'
  END AS tier

FROM normalized_metrics
ORDER BY composite_score DESC;

