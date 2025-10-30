-- =====================================================
-- RFM SEGMENTATION ANALYSIS
-- =====================================================
-- Segmentação de clientes usando Recency, Frequency, Monetary
-- Análise completa com scores, segmentos e recomendações
-- Autor: Andre Bomfim
-- Data: Outubro 2025
-- =====================================================

-- =====================================================
-- 1. CÁLCULO BASE RFM
-- =====================================================

WITH rfm_base AS (
  SELECT 
    c.customer_unique_id,
    c.customer_state,
    
    -- RECENCY: Dias desde a última compra
    DATE_DIFF(
      CURRENT_DATE(),
      DATE(MAX(o.order_purchase_timestamp)),
      DAY
    ) AS recency,
    
    -- FREQUENCY: Número de compras
    COUNT(DISTINCT o.order_id) AS frequency,
    
    -- MONETARY: Valor total gasto
    SUM(p.payment_value) AS monetary,
    
    -- Métricas adicionais
    AVG(p.payment_value) AS avg_order_value,
    MAX(o.order_purchase_timestamp) AS last_purchase_date,
    MIN(o.order_purchase_timestamp) AS first_purchase_date

  FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.orders` o
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.customers` c 
    ON o.customer_id = c.customer_id
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.payments` p 
    ON o.order_id = p.order_id
  WHERE o.order_status = 'delivered'
  GROUP BY c.customer_unique_id, c.customer_state
),

-- =====================================================
-- 2. CÁLCULO DE SCORES RFM (1-5)
-- =====================================================

rfm_scores AS (
  SELECT 
    customer_unique_id,
    customer_state,
    recency,
    frequency,
    monetary,
    avg_order_value,
    last_purchase_date,
    first_purchase_date,
    
    -- R Score: Menor recência = melhor (5)
    CASE 
      WHEN recency <= 30 THEN 5
      WHEN recency <= 60 THEN 4
      WHEN recency <= 90 THEN 3
      WHEN recency <= 180 THEN 2
      ELSE 1
    END AS R_score,
    
    -- F Score: Maior frequência = melhor (5)
    CASE 
      WHEN frequency >= 5 THEN 5
      WHEN frequency = 4 THEN 4
      WHEN frequency = 3 THEN 3
      WHEN frequency = 2 THEN 2
      ELSE 1
    END AS F_score,
    
    -- M Score: Maior valor = melhor (5)
    NTILE(5) OVER (ORDER BY monetary) AS M_score

  FROM rfm_base
),

-- =====================================================
-- 3. SEGMENTAÇÃO DE CLIENTES
-- =====================================================

rfm_segmented AS (
  SELECT 
    *,
    
    -- RFM Score combinado (string)
    CONCAT(
      CAST(R_score AS STRING),
      CAST(F_score AS STRING),
      CAST(M_score AS STRING)
    ) AS rfm_score,
    
    -- RFM Score numérico (média ponderada)
    ROUND(
      (R_score * 0.4) + (F_score * 0.3) + (M_score * 0.3),
      2
    ) AS rfm_score_numeric,
    
    -- Segmentação por regras de negócio
    CASE 
      -- Champions: Melhores clientes
      WHEN R_score >= 4 AND F_score >= 4 AND M_score >= 4 THEN 'Champions'
      
      -- Loyal: Compram frequentemente
      WHEN F_score >= 4 THEN 'Loyal Customers'
      
      -- Potential Loyalist: Clientes recentes com potencial
      WHEN R_score >= 4 AND F_score >= 2 AND M_score >= 2 THEN 'Potential Loyalist'
      
      -- New Customers: Clientes novos
      WHEN R_score >= 4 AND F_score = 1 THEN 'New Customers'
      
      -- Promising: Compradores recentes, baixa frequência
      WHEN R_score >= 3 AND F_score = 1 AND M_score >= 2 THEN 'Promising'
      
      -- Need Attention: Clientes em risco
      WHEN R_score >= 2 AND F_score >= 2 AND M_score >= 2 THEN 'Need Attention'
      
      -- About to Sleep: Risco de churn
      WHEN R_score >= 2 AND F_score <= 2 AND M_score <= 2 THEN 'About To Sleep'
      
      -- At Risk: Alto risco de perda
      WHEN R_score <= 2 AND F_score >= 3 AND M_score >= 3 THEN 'At Risk'
      
      -- Cannot Lose Them: Clientes valiosos inativos
      WHEN R_score <= 2 AND F_score >= 4 AND M_score >= 4 THEN 'Cannot Lose Them'
      
      -- Hibernating: Inativos há muito tempo
      WHEN R_score <= 2 AND F_score <= 2 AND M_score <= 2 THEN 'Hibernating'
      
      -- Lost: Perdidos
      WHEN R_score = 1 THEN 'Lost'
      
      ELSE 'Others'
    END AS segment,
    
    -- Prioridade de ação
    CASE 
      WHEN R_score >= 4 AND F_score >= 4 AND M_score >= 4 THEN 1  -- Champions
      WHEN R_score <= 2 AND F_score >= 4 AND M_score >= 4 THEN 1  -- Cannot Lose
      WHEN F_score >= 4 THEN 2  -- Loyal
      WHEN R_score <= 2 AND F_score >= 3 AND M_score >= 3 THEN 2  -- At Risk
      WHEN R_score >= 2 AND F_score >= 2 THEN 3  -- Need Attention
      WHEN R_score >= 4 AND F_score >= 2 THEN 3  -- Potential Loyalist
      WHEN R_score >= 3 AND F_score = 1 THEN 4  -- Promising
      WHEN R_score >= 4 AND F_score = 1 THEN 4  -- New Customers
      ELSE 5
    END AS priority

  FROM rfm_scores
)

SELECT * FROM rfm_segmented
ORDER BY rfm_score_numeric DESC, monetary DESC;

-- =====================================================
-- 4. SUMÁRIO POR SEGMENTO
-- =====================================================

WITH rfm_segmented AS (
  -- [Repetir CTE acima se necessário - BigQuery não permite reusar CTEs entre queries]
  SELECT 
    c.customer_unique_id,
    c.customer_state,
    DATE_DIFF(CURRENT_DATE(), DATE(MAX(o.order_purchase_timestamp)), DAY) AS recency,
    COUNT(DISTINCT o.order_id) AS frequency,
    SUM(p.payment_value) AS monetary,
    AVG(p.payment_value) AS avg_order_value,
    
    CASE 
      WHEN DATE_DIFF(CURRENT_DATE(), DATE(MAX(o.order_purchase_timestamp)), DAY) <= 30 THEN 5
      WHEN DATE_DIFF(CURRENT_DATE(), DATE(MAX(o.order_purchase_timestamp)), DAY) <= 60 THEN 4
      WHEN DATE_DIFF(CURRENT_DATE(), DATE(MAX(o.order_purchase_timestamp)), DAY) <= 90 THEN 3
      WHEN DATE_DIFF(CURRENT_DATE(), DATE(MAX(o.order_purchase_timestamp)), DAY) <= 180 THEN 2
      ELSE 1
    END AS R_score,
    
    CASE 
      WHEN COUNT(DISTINCT o.order_id) >= 5 THEN 5
      WHEN COUNT(DISTINCT o.order_id) = 4 THEN 4
      WHEN COUNT(DISTINCT o.order_id) = 3 THEN 3
      WHEN COUNT(DISTINCT o.order_id) = 2 THEN 2
      ELSE 1
    END AS F_score,
    
    NTILE(5) OVER (ORDER BY SUM(p.payment_value)) AS M_score
    
  FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.orders` o
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.customers` c 
    ON o.customer_id = c.customer_id
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.payments` p 
    ON o.order_id = p.order_id
  WHERE o.order_status = 'delivered'
  GROUP BY c.customer_unique_id, c.customer_state
),

rfm_with_segment AS (
  SELECT 
    *,
    CASE 
      WHEN R_score >= 4 AND F_score >= 4 AND M_score >= 4 THEN 'Champions'
      WHEN F_score >= 4 THEN 'Loyal Customers'
      WHEN R_score >= 4 AND F_score >= 2 AND M_score >= 2 THEN 'Potential Loyalist'
      WHEN R_score >= 4 AND F_score = 1 THEN 'New Customers'
      WHEN R_score >= 3 AND F_score = 1 AND M_score >= 2 THEN 'Promising'
      WHEN R_score >= 2 AND F_score >= 2 AND M_score >= 2 THEN 'Need Attention'
      WHEN R_score >= 2 AND F_score <= 2 AND M_score <= 2 THEN 'About To Sleep'
      WHEN R_score <= 2 AND F_score >= 3 AND M_score >= 3 THEN 'At Risk'
      WHEN R_score <= 2 AND F_score >= 4 AND M_score >= 4 THEN 'Cannot Lose Them'
      WHEN R_score <= 2 AND F_score <= 2 AND M_score <= 2 THEN 'Hibernating'
      WHEN R_score = 1 THEN 'Lost'
      ELSE 'Others'
    END AS segment
  FROM rfm_segmented
)

SELECT 
  segment,
  COUNT(DISTINCT customer_unique_id) AS customers,
  
  -- Revenue metrics
  ROUND(SUM(monetary), 2) AS total_revenue,
  ROUND(AVG(monetary), 2) AS avg_revenue,
  ROUND(APPROX_QUANTILES(monetary, 100)[OFFSET(50)], 2) AS median_revenue,
  
  -- Behavior metrics
  ROUND(AVG(frequency), 2) AS avg_frequency,
  ROUND(AVG(recency), 2) AS avg_recency,
  ROUND(AVG(avg_order_value), 2) AS avg_aov,
  
  -- Share metrics
  ROUND(COUNT(*) / SUM(COUNT(*)) OVER () * 100, 2) AS customer_pct,
  ROUND(SUM(monetary) / SUM(SUM(monetary)) OVER () * 100, 2) AS revenue_pct

FROM rfm_with_segment
GROUP BY segment
ORDER BY total_revenue DESC;

-- =====================================================
-- 5. DISTRIBUIÇÃO DE SCORES
-- =====================================================

WITH rfm_base AS (
  SELECT 
    c.customer_unique_id,
    DATE_DIFF(CURRENT_DATE(), DATE(MAX(o.order_purchase_timestamp)), DAY) AS recency,
    COUNT(DISTINCT o.order_id) AS frequency,
    SUM(p.payment_value) AS monetary,
    
    CASE 
      WHEN DATE_DIFF(CURRENT_DATE(), DATE(MAX(o.order_purchase_timestamp)), DAY) <= 30 THEN 5
      WHEN DATE_DIFF(CURRENT_DATE(), DATE(MAX(o.order_purchase_timestamp)), DAY) <= 60 THEN 4
      WHEN DATE_DIFF(CURRENT_DATE(), DATE(MAX(o.order_purchase_timestamp)), DAY) <= 90 THEN 3
      WHEN DATE_DIFF(CURRENT_DATE(), DATE(MAX(o.order_purchase_timestamp)), DAY) <= 180 THEN 2
      ELSE 1
    END AS R_score,
    
    CASE 
      WHEN COUNT(DISTINCT o.order_id) >= 5 THEN 5
      WHEN COUNT(DISTINCT o.order_id) = 4 THEN 4
      WHEN COUNT(DISTINCT o.order_id) = 3 THEN 3
      WHEN COUNT(DISTINCT o.order_id) = 2 THEN 2
      ELSE 1
    END AS F_score,
    
    NTILE(5) OVER (ORDER BY SUM(p.payment_value)) AS M_score
    
  FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.orders` o
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.customers` c 
    ON o.customer_id = c.customer_id
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.payments` p 
    ON o.order_id = p.order_id
  WHERE o.order_status = 'delivered'
  GROUP BY c.customer_unique_id
)

SELECT 
  R_score,
  F_score,
  M_score,
  COUNT(*) AS customers,
  ROUND(AVG(monetary), 2) AS avg_monetary,
  ROUND(AVG(frequency), 2) AS avg_frequency,
  ROUND(AVG(recency), 2) AS avg_recency

FROM rfm_base
GROUP BY R_score, F_score, M_score
ORDER BY R_score DESC, F_score DESC, M_score DESC;

-- =====================================================
-- 6. TOP CLIENTES POR SEGMENTO
-- =====================================================

WITH rfm_segmented AS (
  SELECT 
    c.customer_unique_id,
    c.customer_state,
    c.customer_city,
    DATE_DIFF(CURRENT_DATE(), DATE(MAX(o.order_purchase_timestamp)), DAY) AS recency,
    COUNT(DISTINCT o.order_id) AS frequency,
    SUM(p.payment_value) AS monetary,
    
    CASE 
      WHEN DATE_DIFF(CURRENT_DATE(), DATE(MAX(o.order_purchase_timestamp)), DAY) <= 30 THEN 5
      WHEN DATE_DIFF(CURRENT_DATE(), DATE(MAX(o.order_purchase_timestamp)), DAY) <= 60 THEN 4
      WHEN DATE_DIFF(CURRENT_DATE(), DATE(MAX(o.order_purchase_timestamp)), DAY) <= 90 THEN 3
      WHEN DATE_DIFF(CURRENT_DATE(), DATE(MAX(o.order_purchase_timestamp)), DAY) <= 180 THEN 2
      ELSE 1
    END AS R_score,
    
    CASE 
      WHEN COUNT(DISTINCT o.order_id) >= 5 THEN 5
      WHEN COUNT(DISTINCT o.order_id) = 4 THEN 4
      WHEN COUNT(DISTINCT o.order_id) = 3 THEN 3
      WHEN COUNT(DISTINCT o.order_id) = 2 THEN 2
      ELSE 1
    END AS F_score,
    
    NTILE(5) OVER (ORDER BY SUM(p.payment_value)) AS M_score
    
  FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.orders` o
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.customers` c 
    ON o.customer_id = c.customer_id
  INNER JOIN `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.payments` p 
    ON o.order_id = p.order_id
  WHERE o.order_status = 'delivered'
  GROUP BY c.customer_unique_id, c.customer_state, c.customer_city
),

rfm_with_segment AS (
  SELECT 
    *,
    CASE 
      WHEN R_score >= 4 AND F_score >= 4 AND M_score >= 4 THEN 'Champions'
      WHEN F_score >= 4 THEN 'Loyal Customers'
      WHEN R_score >= 4 AND F_score >= 2 AND M_score >= 2 THEN 'Potential Loyalist'
      WHEN R_score >= 4 AND F_score = 1 THEN 'New Customers'
      WHEN R_score >= 3 AND F_score = 1 AND M_score >= 2 THEN 'Promising'
      WHEN R_score >= 2 AND F_score >= 2 AND M_score >= 2 THEN 'Need Attention'
      WHEN R_score >= 2 AND F_score <= 2 AND M_score <= 2 THEN 'About To Sleep'
      WHEN R_score <= 2 AND F_score >= 3 AND M_score >= 3 THEN 'At Risk'
      WHEN R_score <= 2 AND F_score >= 4 AND M_score >= 4 THEN 'Cannot Lose Them'
      WHEN R_score <= 2 AND F_score <= 2 AND M_score <= 2 THEN 'Hibernating'
      WHEN R_score = 1 THEN 'Lost'
      ELSE 'Others'
    END AS segment,
    
    ROW_NUMBER() OVER (
      PARTITION BY CASE 
        WHEN R_score >= 4 AND F_score >= 4 AND M_score >= 4 THEN 'Champions'
        WHEN F_score >= 4 THEN 'Loyal Customers'
        WHEN R_score >= 4 AND F_score >= 2 AND M_score >= 2 THEN 'Potential Loyalist'
        WHEN R_score >= 4 AND F_score = 1 THEN 'New Customers'
        WHEN R_score >= 3 AND F_score = 1 AND M_score >= 2 THEN 'Promising'
        WHEN R_score >= 2 AND F_score >= 2 AND M_score >= 2 THEN 'Need Attention'
        WHEN R_score >= 2 AND F_score <= 2 AND M_score <= 2 THEN 'About To Sleep'
        WHEN R_score <= 2 AND F_score >= 3 AND M_score >= 3 THEN 'At Risk'
        WHEN R_score <= 2 AND F_score >= 4 AND M_score >= 4 THEN 'Cannot Lose Them'
        WHEN R_score <= 2 AND F_score <= 2 AND M_score <= 2 THEN 'Hibernating'
        WHEN R_score = 1 THEN 'Lost'
        ELSE 'Others'
      END 
      ORDER BY monetary DESC
    ) AS rank_in_segment
    
  FROM rfm_segmented
)

SELECT 
  segment,
  customer_unique_id,
  customer_state,
  customer_city,
  ROUND(monetary, 2) AS revenue,
  frequency AS orders,
  recency AS days_since_purchase,
  CONCAT(R_score, F_score, M_score) AS rfm_score

FROM rfm_with_segment
WHERE rank_in_segment <= 10  -- Top 10 por segmento
ORDER BY segment, monetary DESC;

-- =====================================================
-- INSIGHTS E RECOMENDAÇÕES POR SEGMENTO:
-- =====================================================
--
-- 🏆 CHAMPIONS (R>=4, F>=4, M>=4)
--    Ação: Programa VIP, early access, benefícios exclusivos
--    ROI: Alto - São seus melhores clientes
--
-- ⭐ LOYAL CUSTOMERS (F>=4)
--    Ação: Upsell, cross-sell, peça reviews e referrals
--    ROI: Alto - Compram frequentemente
--
-- 🚨 CANNOT LOSE THEM (R<=2, F>=4, M>=4)
--    Ação: URGENTE! Oferta especial, contato direto
--    ROI: Crítico - Clientes valiosos em risco
--
-- ⚠️ AT RISK (R<=2, F>=3, M>=3)
--    Ação: Campanha win-back, cupom 20%, pesquisa
--    ROI: Médio/Alto - Vale investir para recuperar
--
-- 📈 POTENTIAL LOYALIST (R>=4, F>=2, M>=2)
--    Ação: Programa de fidelidade, email nurturing
--    ROI: Médio - Potencial de virar Loyal
--
-- 🔔 NEED ATTENTION (R>=2, F>=2, M>=2)
--    Ação: Ofertas limitadas, lembre que sentem falta
--    ROI: Médio - Ainda engajados
--
-- 🌟 PROMISING (R>=3, F=1, M>=2)
--    Ação: Incentive 2ª compra, cupom 15%
--    ROI: Médio - Primeira compra foi boa
--
-- 👋 NEW CUSTOMERS (R>=4, F=1)
--    Ação: Onboarding, sequência de boas-vindas
--    ROI: Médio - Construir relacionamento
--
-- 😴 ABOUT TO SLEEP (R>=2, F<=2, M<=2)
--    Ação: Email re-engajamento, novidades
--    ROI: Baixo/Médio - Últimas tentativas
--
-- 💤 HIBERNATING (R<=2, F<=2, M<=2)
--    Ação: Reativação massiva ou parar de investir
--    ROI: Baixo - Custo pode não compensar
--
-- ❌ LOST (R=1)
--    Ação: Considere não investir recursos
--    ROI: Muito baixo - Custo alto para recuperar
--
-- =====================================================