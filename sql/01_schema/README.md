# 📊 SQL Schema - Olist E-Commerce

Documentação completa do schema do banco de dados BigQuery.

---

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Tabelas](#tabelas)
- [Views](#views)
- [Relacionamentos](#relacionamentos)
- [Como Usar](#como-usar)

---

## 🎯 Visão Geral

O schema foi projetado para análise de dados de e-commerce, otimizado para BigQuery com:

- **Particionamento** por data para queries eficientes
- **Clustering** em campos frequentemente filtrados
- **Views materializadas** para agregações comuns
- **Nomenclatura padronizada** em inglês

### Arquivos

```
01_schema/
├── create_tables_bigquery.sql    # DDL das tabelas principais
├── create_views.sql               # Views auxiliares
└── README.md                      # Esta documentação
```

---

## 📊 Tabelas

### 1. **customers**
Dados cadastrais dos clientes.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `customer_id` | STRING | ID único do cliente (PK) |
| `customer_unique_id` | STRING | ID único real do cliente (mesmo cliente pode ter múltiplos IDs) |
| `customer_zip_code_prefix` | STRING | Prefixo do CEP (5 dígitos) |
| `customer_city` | STRING | Cidade do cliente |
| `customer_state` | STRING | Estado (UF) |

**Particularidades:**
- Um `customer_unique_id` pode ter vários `customer_id`
- Use `customer_unique_id` para análises de LTV e retenção

**Linhas esperadas:** ~99,441

---

### 2. **orders**
Pedidos realizados na plataforma.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `order_id` | STRING | ID único do pedido (PK) |
| `customer_id` | STRING | ID do cliente (FK → customers) |
| `order_status` | STRING | Status: delivered, shipped, canceled, etc. |
| `order_purchase_timestamp` | TIMESTAMP | Data/hora da compra |
| `order_approved_at` | TIMESTAMP | Data/hora de aprovação |
| `order_delivered_carrier_date` | TIMESTAMP | Data entrega à transportadora |
| `order_delivered_customer_date` | TIMESTAMP | Data entrega ao cliente |
| `order_estimated_delivery_date` | TIMESTAMP | Previsão de entrega |

**Particionamento:** `order_purchase_timestamp`  
**Clustering:** `customer_id`, `order_status`

**Status possíveis:**
- `delivered` - Entregue (use este para análises)
- `shipped` - Em trânsito
- `canceled` - Cancelado
- `unavailable` - Indisponível
- `invoiced` - Faturado
- `processing` - Processando

**Linhas esperadas:** ~99,441

---

### 3. **order_items**
Itens individuais de cada pedido.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `order_id` | STRING | ID do pedido (FK → orders) |
| `order_item_id` | INTEGER | Número sequencial do item no pedido |
| `product_id` | STRING | ID do produto (FK → products) |
| `seller_id` | STRING | ID do vendedor (FK → sellers) |
| `shipping_limit_date` | TIMESTAMP | Prazo limite para envio |
| `price` | FLOAT | Preço do item |
| `freight_value` | FLOAT | Valor do frete |

**Clustering:** `order_id`, `product_id`

**Observações:**
- Um pedido pode ter múltiplos itens
- `price` + `freight_value` = valor total do item
- Cada item tem seu próprio seller

**Linhas esperadas:** ~112,650

---

### 4. **products**
Catálogo de produtos.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `product_id` | STRING | ID único do produto (PK) |
| `product_category_name` | STRING | Nome da categoria (em português) |
| `product_name_lenght` | INTEGER | Tamanho do nome do produto |
| `product_description_lenght` | INTEGER | Tamanho da descrição |
| `product_photos_qty` | INTEGER | Quantidade de fotos |
| `product_weight_g` | INTEGER | Peso em gramas |
| `product_length_cm` | INTEGER | Comprimento em cm |
| `product_height_cm` | INTEGER | Altura em cm |
| `product_width_cm` | INTEGER | Largura em cm |

**Observações:**
- Dimensões físicas úteis para análise de frete
- Use `product_category_translation` para nomes em inglês

**Linhas esperadas:** ~32,951

---

### 5. **sellers**
Cadastro de vendedores.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `seller_id` | STRING | ID único do seller (PK) |
| `seller_zip_code_prefix` | STRING | Prefixo do CEP |
| `seller_city` | STRING | Cidade |
| `seller_state` | STRING | Estado (UF) |

**Observações:**
- Sellers podem estar em estados diferentes dos clientes
- Importante para análise de logística

**Linhas esperadas:** ~3,095

---

### 6. **payments**
Informações de pagamento dos pedidos.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `order_id` | STRING | ID do pedido (FK → orders) |
| `payment_sequential` | INTEGER | Sequencial do pagamento |
| `payment_type` | STRING | Tipo: credit_card, boleto, voucher, debit_card |
| `payment_installments` | INTEGER | Número de parcelas |
| `payment_value` | FLOAT | Valor do pagamento |

**Clustering:** `order_id`, `payment_type`

**Tipos de pagamento:**
- `credit_card` - Cartão de crédito (~73%)
- `boleto` - Boleto bancário (~19%)
- `voucher` - Voucher/Vale (~5%)
- `debit_card` - Cartão de débito (~1%)

**Observações:**
- Um pedido pode ter múltiplos pagamentos (payment_sequential)
- Somar `payment_value` para obter valor total do pedido

**Linhas esperadas:** ~103,886

---

### 7. **reviews**
Avaliações dos clientes sobre os pedidos.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `review_id` | STRING | ID único da review (PK) |
| `order_id` | STRING | ID do pedido (FK → orders) |
| `review_score` | INTEGER | Nota de 1 a 5 |
| `review_comment_title` | STRING | Título do comentário |
| `review_comment_message` | STRING | Texto do comentário |
| `review_creation_date` | TIMESTAMP | Data da avaliação |
| `review_answer_timestamp` | TIMESTAMP | Data da resposta (se houver) |

**Clustering:** `order_id`, `review_score`

**Distribuição de scores (aproximada):**
- 5 estrelas: ~57%
- 4 estrelas: ~19%
- 3 estrelas: ~8%
- 2 estrelas: ~3%
- 1 estrela: ~11%

**Linhas esperadas:** ~99,224

---

### 8. **product_category_translation**
Tradução de categorias PT → EN.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `product_category_name` | STRING | Nome em português |
| `product_category_name_english` | STRING | Nome em inglês |

**Observações:**
- Use esta tabela para exibir nomes em inglês
- JOIN com `products` via `product_category_name`

**Linhas esperadas:** 71

---

## 👁️ Views

### Views Principais

#### **vw_orders_complete**
Pedidos completos com todas as informações relacionadas.

```sql
SELECT * FROM `project.dataset.vw_orders_complete`
WHERE order_status = 'delivered'
AND order_year = 2018;
```

**Inclui:**
- Dados do pedido
- Dados do cliente
- Pagamento
- Review
- Métricas calculadas (delivery_days, delay, etc.)

---

#### **vw_order_items_detail**
Itens com detalhes completos de produto e seller.

```sql
SELECT * FROM `project.dataset.vw_order_items_detail`
WHERE category_english = 'health_beauty'
ORDER BY price DESC;
```

**Inclui:**
- Itens do pedido
- Categoria traduzida
- Dimensões do produto
- Localização do seller
- Métricas calculadas

---

#### **vw_customer_summary**
Sumário agregado por cliente.

```sql
SELECT * FROM `project.dataset.vw_customer_summary`
WHERE customer_segment = 'Loyal'
ORDER BY lifetime_value DESC;
```

**Métricas incluídas:**
- LTV (Lifetime Value)
- Total de pedidos
- AOV (Average Order Value)
- NPS médio
- Segmento do cliente
- Status (Active/At Risk/Inactive)

---

#### **vw_category_summary**
Performance agregada por categoria.

```sql
SELECT * FROM `project.dataset.vw_category_summary`
ORDER BY total_revenue DESC
LIMIT 10;
```

**Métricas incluídas:**
- Revenue total
- Número de pedidos
- AOV
- NPS médio
- Market share

---

#### **vw_seller_performance**
Performance de sellers.

```sql
SELECT * FROM `project.dataset.vw_seller_performance`
WHERE seller_tier = 'Top Seller'
ORDER BY total_revenue DESC;
```

---

#### **vw_monthly_metrics**
Métricas agregadas por mês com growth.

```sql
SELECT * FROM `project.dataset.vw_monthly_metrics`
ORDER BY month DESC;
```

---

#### **vw_state_metrics**
Métricas por estado (geográfico).

```sql
SELECT * FROM `project.dataset.vw_state_metrics`
ORDER BY total_revenue DESC;
```

---

#### **vw_payment_analysis**
Análise de métodos de pagamento.

```sql
SELECT * FROM `project.dataset.vw_payment_analysis`
ORDER BY total_revenue DESC;
```

---

## 🔗 Relacionamentos (ERD)

```
┌─────────────┐
│  customers  │
│  (PK: id)   │
└──────┬──────┘
       │
       │ 1:N
       ▼
┌─────────────┐      1:N      ┌──────────────┐
│   orders    │◄───────────────┤ order_items  │
│  (PK: id)   │                │   (PK: id)   │
└──────┬──────┘                └──────┬───────┘
       │                              │
       │ 1:1                          │ N:1
       ▼                              ▼
┌─────────────┐                ┌─────────────┐
│  payments   │                │  products   │
└─────────────┘                └──────┬──────┘
       │                              │
       │ 1:1                          │ N:1
       ▼                              ▼
┌─────────────┐                ┌─────────────┐
│   reviews   │                │   sellers   │
└─────────────┘                └─────────────┘
```

**Joins Comuns:**

```sql
-- Order completo
SELECT *
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id
INNER JOIN payments p ON o.order_id = p.order_id
LEFT JOIN reviews r ON o.order_id = r.order_id;

-- Item com detalhes
SELECT *
FROM order_items oi
INNER JOIN products p ON oi.product_id = p.product_id
INNER JOIN sellers s ON oi.seller_id = s.seller_id;
```

---

## 🚀 Como Usar

### 1. **Criar Tabelas**

```bash
# No BigQuery Console ou via CLI
bq query --use_legacy_sql=false < create_tables_bigquery.sql
```

Ou execute manualmente no [BigQuery Console](https://console.cloud.google.com/bigquery).

### 2. **Criar Views**

```bash
bq query --use_legacy_sql=false < create_views.sql
```

### 3. **Carregar Dados**

Via script Python (recomendado):

```bash
docker exec -it ecommerce-python python python/etl/load_to_bigquery.py
```

Ou manualmente via BigQuery Console (drag & drop CSVs).

### 4. **Validar Carregamento**

```sql
-- Verificar contagem de linhas
SELECT 
  'customers' as table_name, COUNT(*) as rows FROM `project.dataset.customers`
UNION ALL
SELECT 'orders', COUNT(*) FROM `project.dataset.orders`
UNION ALL
SELECT 'order_items', COUNT(*) FROM `project.dataset.order_items`
UNION ALL
SELECT 'products', COUNT(*) FROM `project.dataset.products`
UNION ALL
SELECT 'sellers', COUNT(*) FROM `project.dataset.sellers`
UNION ALL
SELECT 'payments', COUNT(*) FROM `project.dataset.payments`
UNION ALL
SELECT 'reviews', COUNT(*) FROM `project.dataset.reviews`;
```

**Resultado esperado:**
```
customers       →  99,441
orders          →  99,441
order_items     → 112,650
products        →  32,951
sellers         →   3,095
payments        → 103,886
reviews         →  99,224
```

---

## 📐 Queries de Exemplo

### Verificar integridade referencial

```sql
-- Pedidos sem cliente (não deve ter)
SELECT COUNT(*)
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;

-- Itens sem produto (não deve ter)
SELECT COUNT(*)
FROM order_items oi
LEFT JOIN products p ON oi.product_id = p.product_id
WHERE p.product_id IS NULL;
```

### Top 10 categorias

```sql
SELECT * 
FROM `project.dataset.vw_category_summary`
ORDER BY total_revenue DESC
LIMIT 10;
```

### Clientes VIP (Top 1%)

```sql
SELECT *
FROM `project.dataset.vw_customer_summary`
WHERE lifetime_value >= (
  SELECT APPROX_QUANTILES(lifetime_value, 100)[OFFSET(99)]
  FROM `project.dataset.vw_customer_summary`
)
ORDER BY lifetime_value DESC;
```

---

## ⚠️ Observações Importantes

### Performance

1. **Sempre filtre por data** quando possível (aproveita particionamento):
   ```sql
   WHERE DATE(order_purchase_timestamp) >= '2018-01-01'
   ```

2. **Use as views** ao invés de recriar JOINs:
   ```sql
   -- ✅ Bom
   SELECT * FROM vw_orders_complete WHERE ...
   
   -- ❌ Evite
   SELECT * FROM orders o JOIN customers c ON ... WHERE ...
   ```

3. **Limite resultados** em queries exploratórias:
   ```sql
   SELECT * FROM orders LIMIT 1000;
   ```

### Qualidade de Dados

1. **Valores nulos:**
   - `review_score`: ~0.5% dos pedidos não têm review
   - `product_category_name`: ~0.3% produtos sem categoria
   - `order_delivered_customer_date`: pedidos cancelados não têm

2. **Status de pedidos:**
   - Use `order_status = 'delivered'` para análises principais
   - Outros status representam ~3% dos dados

3. **Duplicatas:**
   - `customer_unique_id` é o ID real do cliente
   - Um cliente pode ter múltiplos `customer_id`

---

## 📚 Recursos Adicionais

- [BigQuery Best Practices](https://cloud.google.com/bigquery/docs/best-practices)
- [Dataset Original no Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
- [Análises SQL](../03_analytics/README.md)

---

## 🤝 Contribuindo

Para modificar o schema:

1. Edite os arquivos `.sql`
2. Teste no BigQuery sandbox
3. Documente mudanças neste README
4. Atualize ERD se necessário

---

**Última atualização:** Outubro 2025  
**Versão do Schema:** 1.0