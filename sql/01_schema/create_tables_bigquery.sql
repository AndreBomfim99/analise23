-- =====================================================
-- OLIST E-COMMERCE - BIGQUERY SCHEMA
-- =====================================================
-- Criação das tabelas no BigQuery
-- Dataset: olist_ecommerce
-- Autor: Andre Bomfim
-- Data: Outubro 2025
-- =====================================================

-- 1. CUSTOMERS
CREATE OR REPLACE TABLE `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.customers` (
  customer_id STRING NOT NULL,
  customer_unique_id STRING NOT NULL,
  customer_zip_code_prefix STRING,
  customer_city STRING,
  customer_state STRING,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(created_at)
OPTIONS(
  description="Tabela de clientes únicos do Olist",
  labels=[("domain", "customer"), ("source", "olist")]
);

-- 2. ORDERS
CREATE OR REPLACE TABLE `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.orders` (
  order_id STRING NOT NULL,
  customer_id STRING NOT NULL,
  order_status STRING,
  order_purchase_timestamp TIMESTAMP,
  order_approved_at TIMESTAMP,
  order_delivered_carrier_date TIMESTAMP,
  order_delivered_customer_date TIMESTAMP,
  order_estimated_delivery_date TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(order_purchase_timestamp)
CLUSTER BY customer_id, order_status
OPTIONS(
  description="Tabela principal de pedidos",
  labels=[("domain", "order"), ("source", "olist")]
);

-- 3. ORDER ITEMS
CREATE OR REPLACE TABLE `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.order_items` (
  order_id STRING NOT NULL,
  order_item_id INT64 NOT NULL,
  product_id STRING NOT NULL,
  seller_id STRING NOT NULL,
  shipping_limit_date TIMESTAMP,
  price FLOAT64,
  freight_value FLOAT64,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(created_at)
CLUSTER BY order_id, product_id
OPTIONS(
  description="Itens individuais dos pedidos",
  labels=[("domain", "order"), ("source", "olist")]
);

-- 4. PRODUCTS
CREATE OR REPLACE TABLE `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.products` (
  product_id STRING NOT NULL,
  product_category_name STRING,
  product_name_length INT64,
  product_description_length INT64,
  product_photos_qty INT64,
  product_weight_g INT64,
  product_length_cm INT64,
  product_height_cm INT64,
  product_width_cm INT64,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
OPTIONS(
  description="Catálogo de produtos",
  labels=[("domain", "product"), ("source", "olist")]
);

-- 5. SELLERS
CREATE OR REPLACE TABLE `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.sellers` (
  seller_id STRING NOT NULL,
  seller_zip_code_prefix STRING,
  seller_city STRING,
  seller_state STRING,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
OPTIONS(
  description="Cadastro de vendedores",
  labels=[("domain", "seller"), ("source", "olist")]
);

-- 6. PAYMENTS
CREATE OR REPLACE TABLE `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.payments` (
  order_id STRING NOT NULL,
  payment_sequential INT64 NOT NULL,
  payment_type STRING,
  payment_installments INT64,
  payment_value FLOAT64,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(created_at)
CLUSTER BY order_id, payment_type
OPTIONS(
  description="Informações de pagamento dos pedidos",
  labels=[("domain", "payment"), ("source", "olist")]
);

-- 7. REVIEWS
CREATE OR REPLACE TABLE `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.reviews` (
  review_id STRING NOT NULL,
  order_id STRING NOT NULL,
  review_score INT64,
  review_comment_title STRING,
  review_comment_message STRING,
  review_creation_date TIMESTAMP,
  review_answer_timestamp TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(review_creation_date)
CLUSTER BY order_id, review_score
OPTIONS(
  description="Avaliações dos clientes",
  labels=[("domain", "review"), ("source", "olist")]
);

-- 8. PRODUCT CATEGORY NAME TRANSLATION
CREATE OR REPLACE TABLE `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.product_category_translation` (
  product_category_name STRING NOT NULL,
  product_category_name_english STRING NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
OPTIONS(
  description="Tradução de categorias PT->EN",
  labels=[("domain", "product"), ("type", "reference")]
);

-- 9. GEOLOCATION (opcional - muito grande)
-- Comentado por padrão - descomente se necessário
/*
CREATE OR REPLACE TABLE `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.geolocation` (
  geolocation_zip_code_prefix STRING NOT NULL,
  geolocation_lat FLOAT64,
  geolocation_lng FLOAT64,
  geolocation_city STRING,
  geolocation_state STRING,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
CLUSTER BY geolocation_state, geolocation_city
OPTIONS(
  description="Dados de geolocalização por CEP",
  labels=[("domain", "geolocation"), ("source", "olist")]
);
*/

-- =====================================================
-- VIEWS AUXILIARES
-- =====================================================

-- View: Pedidos completos (JOIN principal)
CREATE OR REPLACE VIEW `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.vw_orders_complete` AS
SELECT 
  o.order_id,
  o.customer_id,
  c.customer_unique_id,
  c.customer_state,
  c.customer_city,
  o.order_status,
  o.order_purchase_timestamp,
  o.order_delivered_customer_date,
  o.order_estimated_delivery_date,
  
  -- Métricas calculadas
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
  
  -- Pagamentos
  p.payment_type,
  p.payment_installments,
  p.payment_value,
  
  -- Reviews
  r.review_score,
  r.review_creation_date

FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.orders` o
LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.customers` c 
  ON o.customer_id = c.customer_id
LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.payments` p 
  ON o.order_id = p.order_id
LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.reviews` r 
  ON o.order_id = r.order_id
WHERE o.order_status NOT IN ('canceled', 'unavailable');

-- View: Items com detalhes de produto
CREATE OR REPLACE VIEW `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.vw_order_items_detail` AS
SELECT 
  oi.order_id,
  oi.order_item_id,
  oi.product_id,
  oi.seller_id,
  oi.price,
  oi.freight_value,
  oi.price + oi.freight_value AS total_value,
  
  -- Produto
  p.product_category_name,
  pct.product_category_name_english,
  p.product_weight_g,
  
  -- Seller
  s.seller_state,
  s.seller_city

FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.order_items` oi
LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.products` p 
  ON oi.product_id = p.product_id
LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.product_category_translation` pct 
  ON p.product_category_name = pct.product_category_name
LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.sellers` s 
  ON oi.seller_id = s.seller_id;

-- =====================================================
-- ÍNDICES E CONSTRAINTS (Documentação - BigQuery não usa)
-- =====================================================

-- BigQuery usa PARTITION e CLUSTER ao invés de índices tradicionais
-- Já aplicados nas definições CREATE TABLE acima

-- Primary Keys (lógicas - para documentação):
-- customers: customer_id
-- orders: order_id
-- order_items: (order_id, order_item_id)
-- products: product_id
-- sellers: seller_id
-- payments: (order_id, payment_sequential)
-- reviews: review_id