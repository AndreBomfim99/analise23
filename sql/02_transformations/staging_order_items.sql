-- =====================================================
-- STAGING: ORDER ITEMS
-- =====================================================
-- Camada de staging para itens de pedidos com enriquecimento
-- Estilo dbt - fonte → staging → marts
-- Autor: Andre Bomfim
-- Data: Outubro 2025
-- =====================================================

-- =====================================================
-- STG_ORDER_ITEMS: Itens limpos e enriquecidos
-- =====================================================

CREATE OR REPLACE TABLE `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_order_items` AS

WITH source AS (
  SELECT * 
  FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.order_items`
),

cleaned AS (
  SELECT 
    -- Primary/Foreign keys
    order_id,
    order_item_id,
    product_id,
    seller_id,
    
    -- Timestamps
    shipping_limit_date,
    
    -- Financial (validação de valores positivos)
    CASE 
      WHEN price < 0 THEN 0 
      ELSE price 
    END AS price,
    
    CASE 
      WHEN freight_value < 0 THEN 0 
      ELSE freight_value 
    END AS freight_value,
    
    -- Validações
    CASE 
      WHEN price IS NULL OR price < 0 THEN FALSE
      WHEN freight_value IS NULL OR freight_value < 0 THEN FALSE
      ELSE TRUE
    END AS is_valid_financial,
    
    -- Metadata
    CURRENT_TIMESTAMP() AS _loaded_at
    
  FROM source
  WHERE order_id IS NOT NULL
    AND product_id IS NOT NULL
),

enriched_product AS (
  SELECT 
    c.*,
    
    -- ==========================================
    -- PRODUCT ENRICHMENT
    -- ==========================================
    
    -- Product details
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
    
    -- Product quality score (baseado em fotos e descrição)
    CASE 
      WHEN p.product_photos_qty >= 3 AND p.product_description_lenght > 500 THEN 'High Quality'
      WHEN p.product_photos_qty >= 2 AND p.product_description_lenght > 200 THEN 'Medium Quality'
      ELSE 'Low Quality'
    END AS product_quality_tier
    
  FROM cleaned c
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.products` p 
    ON c.product_id = p.product_id
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.product_category_translation` pct 
    ON p.product_category_name = pct.product_category_name
),

enriched_seller AS (
  SELECT 
    ep.*,
    
    -- ==========================================
    -- SELLER ENRICHMENT
    -- ==========================================
    
    -- Seller location
    s.seller_city,
    s.seller_state,
    
    -- Seller region
    CASE 
      WHEN s.seller_state IN ('AC', 'AP', 'AM', 'PA', 'RO', 'RR', 'TO') THEN 'Norte'
      WHEN s.seller_state IN ('AL', 'BA', 'CE', 'MA', 'PB', 'PE', 'PI', 'RN', 'SE') THEN 'Nordeste'
      WHEN s.seller_state IN ('DF', 'GO', 'MT', 'MS') THEN 'Centro-Oeste'
      WHEN s.seller_state IN ('ES', 'MG', 'RJ', 'SP') THEN 'Sudeste'
      WHEN s.seller_state IN ('PR', 'RS', 'SC') THEN 'Sul'
      ELSE 'Unknown'
    END AS seller_region
    
  FROM enriched_product ep
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.sellers` s 
    ON ep.seller_id = s.seller_id
),

enriched_order AS (
  SELECT 
    es.*,
    
    -- ==========================================
    -- ORDER ENRICHMENT
    -- ==========================================
    
    -- Order info
    o.customer_id,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_date,
    o.order_year,
    o.order_month,
    o.order_year_month,
    o.seasonal_period,
    
    -- Customer location
    c.customer_city,
    c.customer_state,
    c.customer_region
    
  FROM enriched_seller es
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_orders` o 
    ON es.order_id = o.order_id
  LEFT JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_customers` c 
    ON o.customer_id = c.customer_id
),

final AS (
  SELECT 
    -- ==========================================
    -- IDENTIFIERS
    -- ==========================================
    
    order_id,
    order_item_id,
    product_id,
    seller_id,
    customer_id,
    
    -- ==========================================
    -- ORDER CONTEXT
    -- ==========================================
    
    order_status,
    order_purchase_timestamp,
    order_date,
    order_year,
    order_month,
    order_year_month,
    seasonal_period,
    shipping_limit_date,
    
    -- ==========================================
    -- FINANCIAL METRICS
    -- ==========================================
    
    ROUND(price, 2) AS price,
    ROUND(freight_value, 2) AS freight_value,
    ROUND(price + freight_value, 2) AS total_item_value,
    
    -- Freight as % of price
    ROUND(SAFE_DIVIDE(freight_value, NULLIF(price, 0)) * 100, 2) AS freight_pct_of_price,
    
    -- Price tiers
    CASE 
      WHEN price >= 500 THEN 'Premium (500+)'
      WHEN price >= 200 THEN 'High (200-500)'
      WHEN price >= 100 THEN 'Medium (100-200)'
      WHEN price >= 50 THEN 'Low (50-100)'
      ELSE 'Very Low (<50)'
    END AS price_tier,
    
    -- ==========================================
    -- PRODUCT ATTRIBUTES
    -- ==========================================
    
    product_category_name,
    category_english,
    product_weight_g,
    product_volume_cm3,
    product_photos_qty,
    product_quality_tier,
    
    -- Weight tiers (para análise de frete)
    CASE 
      WHEN product_weight_g >= 10000 THEN 'Very Heavy (10kg+)'
      WHEN product_weight_g >= 5000 THEN 'Heavy (5-10kg)'
      WHEN product_weight_g >= 1000 THEN 'Medium (1-5kg)'
      WHEN product_weight_g >= 500 THEN 'Light (500g-1kg)'
      ELSE 'Very Light (<500g)'
    END AS weight_tier,
    
    -- ==========================================
    -- SELLER ATTRIBUTES
    -- ==========================================
    
    seller_city,
    seller_state,
    seller_region,
    
    -- ==========================================
    -- CUSTOMER ATTRIBUTES
    -- ==========================================
    
    customer_city,
    customer_state,
    customer_region,
    
    -- ==========================================
    -- LOGISTICS METRICS
    -- ==========================================
    
    -- Same state shipping
    CASE 
      WHEN seller_state = customer_state THEN TRUE 
      ELSE FALSE 
    END AS is_same_state_shipping,
    
    -- Same region shipping
    CASE 
      WHEN seller_region = customer_region THEN TRUE 
      ELSE FALSE 
    END AS is_same_region_shipping,
    
    -- Interstate shipping (Sul/Sudeste → Norte/Nordeste = mais complexo)
    CASE 
      WHEN seller_region IN ('Sul', 'Sudeste') 
           AND customer_region IN ('Norte', 'Nordeste') THEN 'Long Distance'
      WHEN seller_region IN ('Norte', 'Nordeste') 
           AND customer_region IN ('Sul', 'Sudeste') THEN 'Long Distance'
      WHEN seller_region != customer_region THEN 'Medium Distance'
      ELSE 'Short Distance'
    END AS shipping_distance_category,
    
    -- ==========================================
    -- MARGIN ESTIMATION (Simplificada)
    -- ==========================================
    
    -- Margem bruta estimada (preço - frete)
    ROUND(price - freight_value, 2) AS estimated_gross_margin,
    
    -- Margem % estimada
    ROUND(SAFE_DIVIDE(price - freight_value, NULLIF(price, 0)) * 100, 2) AS estimated_margin_pct,
    
    -- Classificação de margem
    CASE 
      WHEN SAFE_DIVIDE(price - freight_value, NULLIF(price, 0)) >= 0.80 THEN 'High Margin (80%+)'
      WHEN SAFE_DIVIDE(price - freight_value, NULLIF(price, 0)) >= 0.60 THEN 'Good Margin (60-80%)'
      WHEN SAFE_DIVIDE(price - freight_value, NULLIF(price, 0)) >= 0.40 THEN 'Medium Margin (40-60%)'
      WHEN SAFE_DIVIDE(price - freight_value, NULLIF(price, 0)) >= 0.20 THEN 'Low Margin (20-40%)'
      ELSE 'Very Low Margin (<20%)'
    END AS margin_tier,
    
    -- ==========================================
    -- FLAGS
    -- ==========================================
    
    is_valid_financial,
    
    -- High value item
    CASE WHEN price >= 500 THEN TRUE ELSE FALSE END AS is_high_value_item,
    
    -- Heavy item (logística complexa)
    CASE WHEN product_weight_g >= 5000 THEN TRUE ELSE FALSE END AS is_heavy_item,
    
    -- High freight cost
    CASE WHEN freight_value > 50 THEN TRUE ELSE FALSE END AS is_high_freight,
    
    -- Freight > Price (caso edge)
    CASE WHEN freight_value > price THEN TRUE ELSE FALSE END AS freight_exceeds_price,
    
    -- Missing product info
    CASE WHEN product_category_name IS NULL THEN TRUE ELSE FALSE END AS is_missing_category,
    
    -- ==========================================
    -- METADATA
    -- ==========================================
    
    _loaded_at
    
  FROM enriched_order
)

SELECT * FROM final;

-- =====================================================
-- ÍNDICES E PARTICIONAMENTO
-- =====================================================

-- Recriar com particionamento e clustering
CREATE OR REPLACE TABLE `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_order_items`
PARTITION BY order_date
CLUSTER BY category_english, seller_state, customer_state, price_tier
AS
SELECT * FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_order_items`;

-- =====================================================
-- TESTES DE QUALIDADE
-- =====================================================

/*
-- Teste 1: Nenhum order_id ou product_id nulo
SELECT COUNT(*) 
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_order_items`
WHERE order_id IS NULL OR product_id IS NULL;
-- Esperado: 0

-- Teste 2: Prices e freight devem ser não-negativos
SELECT COUNT(*) 
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_order_items`
WHERE price < 0 OR freight_value < 0;
-- Esperado: 0

-- Teste 3: Combinação order_id + order_item_id deve ser única
SELECT 
  order_id, 
  order_item_id, 
  COUNT(*) AS count
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_order_items`
GROUP BY order_id, order_item_id
HAVING COUNT(*) > 1;
-- Esperado: 0 linhas

-- Teste 4: Freight não deve exceder price (exceto casos raros)
SELECT COUNT(*) 
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_order_items`
WHERE freight_exceeds_price = TRUE;
-- Esperado: < 1% do total

-- Teste 5: Produtos devem ter categoria
SELECT COUNT(*) 
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_order_items`
WHERE is_missing_category = TRUE;
-- Esperado: < 1% do total
*/

-- =====================================================
-- QUERIES DE VALIDAÇÃO
-- =====================================================

-- Sumário da tabela
SELECT 
  'Total Items' AS metric,
  COUNT(*) AS value
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_order_items`

UNION ALL

SELECT 
  'Total Revenue',
  ROUND(SUM(price), 2)
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_order_items`

UNION ALL

SELECT 
  'Avg Item Price',
  ROUND(AVG(price), 2)
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_order_items`

UNION ALL

SELECT 
  'Same State Shipping %',
  ROUND(COUNTIF(is_same_state_shipping) / COUNT(*) * 100, 2)
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_order_items`

UNION ALL

SELECT 
  'High Margin Items %',
  ROUND(COUNTIF(margin_tier LIKE 'High%') / COUNT(*) * 100, 2)
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_order_items`;

-- =====================================================
-- EXEMPLO DE USO
-- =====================================================

/*
-- Análise de margem por categoria
SELECT 
  category_english,
  COUNT(*) AS items,
  ROUND(AVG(price), 2) AS avg_price,
  ROUND(AVG(freight_value), 2) AS avg_freight,
  ROUND(AVG(estimated_margin_pct), 2) AS avg_margin_pct
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_order_items`
WHERE order_status = 'delivered'
GROUP BY category_english
ORDER BY items DESC
LIMIT 20;

-- Análise de logística (distância vs freight)
SELECT 
  shipping_distance_category,
  COUNT(*) AS shipments,
  ROUND(AVG(freight_value), 2) AS avg_freight,
  ROUND(AVG(product_weight_g), 2) AS avg_weight_g
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_order_items`
GROUP BY shipping_distance_category
ORDER BY avg_freight DESC;

-- Top sellers por receita
SELECT 
  seller_id,
  seller_state,
  COUNT(DISTINCT order_id) AS orders,
  ROUND(SUM(price), 2) AS total_revenue
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_order_items`
WHERE order_status = 'delivered'
GROUP BY seller_id, seller_state
ORDER BY total_revenue DESC
LIMIT 50;
*/

-- =====================================================
-- DOCUMENTAÇÃO
-- =====================================================

-- Esta tabela staging serve como base para:
-- 1. Análises de categoria de produto
-- 2. Análises de margem e pricing
-- 3. Análises de logística e frete
-- 4. Performance de sellers
-- 5. Análises de cross-sell e basket

-- Grão: 1 linha por item de pedido (order_id + order_item_id)
-- Relacionamentos:
-- - N:1 com stg_orders (order_id)
-- - N:1 com products (product_id)
-- - N:1 com sellers (seller_id)
-- - N:1 com stg_customers (customer_id via orders)

-- Próximos passos:
-- - Criar mart_product_performance.sql
-- - Criar mart_seller_metrics.sql
-- - Usar em análises de basket (itens comprados juntos)

-- =====================================================