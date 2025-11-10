-- VIEWS AUXILIARES - OLIST E-COMMERCE
-- Views para facilitar análises e reduzir duplicação de queries
-- Autor: Andre Bomfim
-- Data: Outubro 2025

-- 1. VW_ORDERS_COMPLETE

-- View principal com todos os dados de pedidos em um único lugar
CREATE OR REPLACE VIEW `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.vw_orders_complete` AS
SELECT 
  -- Order info
  o.order_id,
  o.order_status,
  o.order_purchase_timestamp,
  o.order_approved_at,
  o.order_delivered_carrier_date,
  o.order_delivered_customer_date,
  o.order_estimated_delivery_date,
  
  -- Customer info
  o.customer_id,
  c.customer_unique_id,
  c.customer_zip_code_prefix,
  c.customer_city,
  c.customer_state,
  
  -- Payment info
  p.payment_sequential,
  p.payment_type,
  p.payment_installments,
  p.payment_value,
  
  -- Review info
  r.review_id,
  r.review_score,
  r.review_comment_title,
  r.review_comment_message,
  r.review_creation_date,
  r.review_answer_timestamp,
  
  -- Calculated metrics
  DATE_DIFF(
    DATE(o.order_delivered_customer_date), 
    DATE(o.order_purchase_timestamp), 
    DAY
  ) AS delivery_days,
  
  DATE_DIFF(
    DATE(o.order_delivered_customer_date), 
    DATE(o.order_estimated_delivery_date), 
    DAY
  ) AS delivery_delay_days,
  
  CASE 
    WHEN DATE_DIFF(DATE(o.order_delivered_customer_date), DATE(o.order_estimated_delivery_date), DAY) > 0 
    THEN TRUE 
    ELSE FALSE 
  END AS is_delayed,
  
  -- Time dimensions
  EXTRACT(YEAR FROM o.order_purchase_timestamp) AS order_year,
  EXTRACT(MONTH FROM o.order_purchase_timestamp) AS order_month,
  EXTRACT(QUARTER FROM o.order_purchase_timestamp) AS order_quarter,
  FORMAT_DATE('%Y-%m', o.order_purchase_timestamp) AS order_year_month,
  FORMAT_DATE('%A', o.order_purchase_timestamp) AS order_day_of_week,
  EXTRACT(HOUR FROM o.order_purchase_timestamp) AS order_hour

FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.orders` o
LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.customers` c 
  ON o.customer_id = c.customer_id
LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.payments` p 
  ON o.order_id = p.order_id
LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.reviews` r 
  ON o.order_id = r.order_id;

-- 2. VW_ORDER_ITEMS_DETAIL

-- View com detalhes completos dos itens de pedidos
CREATE OR REPLACE VIEW `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.vw_order_items_detail` AS
SELECT 
  -- Order item info
  oi.order_id,
  oi.order_item_id,
  oi.product_id,
  oi.seller_id,
  oi.shipping_limit_date,
  oi.price,
  oi.freight_value,
  oi.price + oi.freight_value AS total_value,
  
  -- Product info
  p.product_category_name,
  pct.product_category_name_english AS category_english,
  p.product_name_lenght,
  p.product_description_lenght,
  p.product_photos_qty,
  p.product_weight_g,
  p.product_length_cm,
  p.product_height_cm,
  p.product_width_cm,
  
  -- Product volume (cm³)
  p.product_length_cm * p.product_height_cm * p.product_width_cm AS product_volume_cm3,
  
  -- Seller info
  s.seller_zip_code_prefix,
  s.seller_city,
  s.seller_state,
  
  -- Order info
  o.order_purchase_timestamp,
  o.order_status,
  o.customer_id,
  
  -- Customer info
  c.customer_state AS customer_state,
  c.customer_city AS customer_city,
  
  -- Calculated metrics
  CASE 
    WHEN s.seller_state = c.customer_state THEN TRUE 
    ELSE FALSE 
  END AS is_same_state,
  
  SAFE_DIVIDE(oi.freight_value, oi.price) * 100 AS freight_pct_of_price

FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.order_items` oi
LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.products` p 
  ON oi.product_id = p.product_id
LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.product_category_translation` pct 
  ON p.product_category_name = pct.product_category_name
LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.sellers` s 
  ON oi.seller_id = s.seller_id
LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.orders` o 
  ON oi.order_id = o.order_id
LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.customers` c 
  ON o.customer_id = c.customer_id;


-- 3. VW_CUSTOMER_SUMMARY

-- View com sumário agregado por cliente
CREATE OR REPLACE VIEW `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.vw_customer_summary` AS
WITH customer_orders AS (
  SELECT 
    c.customer_unique_id,
    c.customer_state,
    c.customer_city,
    o.order_id,
    o.order_purchase_timestamp,
    p.payment_value,
    r.review_score
    
  FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.orders` o
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.customers` c 
    ON o.customer_id = c.customer_id
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.payments` p 
    ON o.order_id = p.order_id
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.reviews` r 
    ON o.order_id = r.order_id
  WHERE o.order_status = 'delivered'
)

SELECT 
  customer_unique_id,
  customer_state,
  customer_city,
  
  -- Order metrics
  COUNT(DISTINCT order_id) AS total_orders,
  
  -- Revenue metrics
  SUM(payment_value) AS lifetime_value,
  AVG(payment_value) AS avg_order_value,
  MIN(payment_value) AS min_order_value,
  MAX(payment_value) AS max_order_value,
  
  -- Time metrics
  MIN(order_purchase_timestamp) AS first_purchase_date,
  MAX(order_purchase_timestamp) AS last_purchase_date,
  DATE_DIFF(CURRENT_DATE(), DATE(MAX(order_purchase_timestamp)), DAY) AS days_since_last_purchase,
  DATE_DIFF(DATE(MAX(order_purchase_timestamp)), DATE(MIN(order_purchase_timestamp)), DAY) AS customer_lifetime_days,
  
  -- Satisfaction
  AVG(review_score) AS avg_review_score,
  COUNTIF(review_score >= 4) / COUNT(review_score) * 100 AS positive_review_pct,
  
  -- Customer segment
  CASE 
    WHEN COUNT(DISTINCT order_id) = 1 THEN 'One-time'
    WHEN COUNT(DISTINCT order_id) = 2 THEN 'Repeat'
    WHEN COUNT(DISTINCT order_id) >= 3 THEN 'Loyal'
  END AS customer_segment,
  
  -- Customer status
  CASE 
    WHEN DATE_DIFF(CURRENT_DATE(), DATE(MAX(order_purchase_timestamp)), DAY) <= 90 THEN 'Active'
    WHEN DATE_DIFF(CURRENT_DATE(), DATE(MAX(order_purchase_timestamp)), DAY) <= 180 THEN 'At Risk'
    ELSE 'Inactive'
  END AS customer_status

FROM customer_orders
GROUP BY customer_unique_id, customer_state, customer_city;

-- 4. VW_CATEGORY_SUMMARY

-- View com sumário agregado por categoria
CREATE OR REPLACE VIEW `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.vw_category_summary` AS
SELECT 
  COALESCE(pct.product_category_name_english, 'Unknown') AS category,
  
  -- Volume metrics
  COUNT(DISTINCT oi.order_id) AS total_orders,
  COUNT(DISTINCT oi.order_item_id) AS total_items,
  COUNT(DISTINCT oi.product_id) AS unique_products,
  COUNT(DISTINCT oi.seller_id) AS unique_sellers,
  
  -- Revenue metrics
  SUM(oi.price) AS total_revenue,
  SUM(oi.freight_value) AS total_freight,
  SUM(oi.price + oi.freight_value) AS total_gmv,
  AVG(oi.price) AS avg_item_price,
  AVG(oi.price + oi.freight_value) AS avg_order_value,
  
  -- Customer satisfaction
  AVG(r.review_score) AS avg_review_score,
  COUNTIF(r.review_score >= 4) / COUNT(r.review_score) * 100 AS positive_review_pct,
  
  -- Market share
  SUM(oi.price) / SUM(SUM(oi.price)) OVER () * 100 AS revenue_share_pct

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
GROUP BY category;

-- 5. VW_SELLER_PERFORMANCE

-- View com performance agregada por seller
CREATE OR REPLACE VIEW `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.vw_seller_performance` AS
SELECT 
  s.seller_id,
  s.seller_city,
  s.seller_state,
  
  -- Volume metrics
  COUNT(DISTINCT oi.order_id) AS total_orders,
  COUNT(DISTINCT oi.product_id) AS unique_products,
  
  -- Revenue metrics
  SUM(oi.price) AS total_revenue,
  SUM(oi.price + oi.freight_value) AS total_gmv,
  AVG(oi.price) AS avg_item_price,
  
  -- Customer satisfaction
  AVG(r.review_score) AS avg_review_score,
  COUNTIF(r.review_score >= 4) / COUNT(r.review_score) * 100 AS positive_review_pct,
  COUNTIF(r.review_score <= 2) / COUNT(r.review_score) * 100 AS negative_review_pct,
  
  -- Delivery performance
  AVG(DATE_DIFF(DATE(o.order_delivered_customer_date), DATE(o.order_purchase_timestamp), DAY)) AS avg_delivery_days,
  COUNTIF(DATE(o.order_delivered_customer_date) > DATE(o.order_estimated_delivery_date)) / COUNT(*) * 100 AS delayed_order_pct,
  
  -- Seller tier
  CASE 
    WHEN SUM(oi.price) > 100000 AND AVG(r.review_score) >= 4.0 THEN 'Top Seller'
    WHEN SUM(oi.price) > 50000 THEN 'High Volume'
    WHEN AVG(r.review_score) >= 4.5 THEN 'High Quality'
    ELSE 'Standard'
  END AS seller_tier

FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.sellers` s
INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.order_items` oi 
  ON s.seller_id = oi.seller_id
INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.orders` o 
  ON oi.order_id = o.order_id
LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.reviews` r 
  ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
GROUP BY s.seller_id, s.seller_city, s.seller_state;

-- 6. VW_MONTHLY_METRICS

-- View com métricas agregadas por mês
CREATE OR REPLACE VIEW `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.vw_monthly_metrics` AS
SELECT 
  DATE_TRUNC(o.order_purchase_timestamp, MONTH) AS month,
  EXTRACT(YEAR FROM o.order_purchase_timestamp) AS year,
  EXTRACT(MONTH FROM o.order_purchase_timestamp) AS month_number,
  FORMAT_DATE('%Y-%m', o.order_purchase_timestamp) AS year_month,
  
  -- Volume metrics
  COUNT(DISTINCT o.order_id) AS total_orders,
  COUNT(DISTINCT o.customer_id) AS total_customers,
  COUNT(DISTINCT c.customer_unique_id) AS unique_customers,
  
  -- Revenue metrics
  SUM(p.payment_value) AS total_revenue,
  AVG(p.payment_value) AS avg_order_value,
  
  -- Customer metrics
  AVG(r.review_score) AS avg_review_score,
  
  -- Growth metrics (vs previous month)
  LAG(SUM(p.payment_value)) OVER (ORDER BY DATE_TRUNC(o.order_purchase_timestamp, MONTH)) AS prev_month_revenue,
  SAFE_DIVIDE(
    SUM(p.payment_value) - LAG(SUM(p.payment_value)) OVER (ORDER BY DATE_TRUNC(o.order_purchase_timestamp, MONTH)),
    LAG(SUM(p.payment_value)) OVER (ORDER BY DATE_TRUNC(o.order_purchase_timestamp, MONTH))
  ) * 100 AS mom_growth_pct

FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.orders` o
INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.customers` c 
  ON o.customer_id = c.customer_id
INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.payments` p 
  ON o.order_id = p.order_id
LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.reviews` r 
  ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
GROUP BY month, year, month_number, year_month;

-- 7. VW_STATE_METRICS

-- View com métricas agregadas por estado
CREATE OR REPLACE VIEW `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.vw_state_metrics` AS
SELECT 
  c.customer_state,
  
  -- Volume metrics
  COUNT(DISTINCT c.customer_unique_id) AS total_customers,
  COUNT(DISTINCT o.order_id) AS total_orders,
  
  -- Revenue metrics
  SUM(p.payment_value) AS total_revenue,
  AVG(p.payment_value) AS avg_order_value,
  SUM(p.payment_value) / COUNT(DISTINCT c.customer_unique_id) AS revenue_per_customer,
  
  -- Behavioral metrics
  COUNT(DISTINCT o.order_id) / COUNT(DISTINCT c.customer_unique_id) AS orders_per_customer,
  AVG(r.review_score) AS avg_review_score,
  
  -- Delivery metrics
  AVG(DATE_DIFF(DATE(o.order_delivered_customer_date), DATE(o.order_purchase_timestamp), DAY)) AS avg_delivery_days,
  COUNTIF(DATE(o.order_delivered_customer_date) > DATE(o.order_estimated_delivery_date)) / COUNT(*) * 100 AS delayed_order_pct,
  
  -- Market share
  SUM(p.payment_value) / SUM(SUM(p.payment_value)) OVER () * 100 AS revenue_share_pct

FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.customers` c
INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.orders` o 
  ON c.customer_id = o.customer_id
INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.payments` p 
  ON o.order_id = p.order_id
LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.reviews` r 
  ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state;

-- 8. VW_PAYMENT_ANALYSIS

-- View com análise de métodos de pagamento
CREATE OR REPLACE VIEW `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.vw_payment_analysis` AS
SELECT 
  p.payment_type,
  
  -- Volume metrics
  COUNT(DISTINCT p.order_id) AS total_orders,
  SUM(p.payment_value) AS total_revenue,
  
  -- Average metrics
  AVG(p.payment_value) AS avg_payment_value,
  AVG(p.payment_installments) AS avg_installments,
  
  -- Distribution
  COUNT(*) / SUM(COUNT(*)) OVER () * 100 AS order_pct,
  SUM(p.payment_value) / SUM(SUM(p.payment_value)) OVER () * 100 AS revenue_pct,
  
  -- Customer behavior
  COUNT(DISTINCT o.customer_id) / COUNT(DISTINCT p.order_id) AS customers_per_order,
  AVG(r.review_score) AS avg_review_score

FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.payments` p
INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.orders` o 
  ON p.order_id = o.order_id
LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.reviews` r 
  ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
GROUP BY p.payment_type;

