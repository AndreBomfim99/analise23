# 📋 Dashboard Specifications - Looker Studio

Especificações técnicas detalhadas dos dashboards.

---

## 📊 1. Executive Dashboard

### **Informações Gerais**

| Propriedade | Valor |
|-------------|-------|
| **Nome** | Executive Dashboard - Olist E-Commerce |
| **ID** | YOUR-REPORT-ID-1 |
| **Páginas** | 1 (single-page) |
| **Dimensões** | 1920x1080 (16:9) |
| **Tema** | Light |
| **Refresh** | Diário (2:00 AM UTC) |

---

### **Fontes de Dados**
```sql
-- Conexão BigQuery
Project: your-gcp-project
Dataset: olist_ecommerce

-- Tabelas utilizadas
- orders (primary)
- customers
- payments
- reviews

-- Views customizadas
- executive_summary_view
```

---

### **KPIs e Scorecards**

| KPI | Cálculo | Formato | Fonte |
|-----|---------|---------|-------|
| **Receita Total** | `SUM(payment_value)` | R$ 15,0 M | payments |
| **Pedidos** | `COUNT(DISTINCT order_id)` | 99.441 | orders |
| **Ticket Médio** | `SUM(payment_value) / COUNT(orders)` | R$ 154,00 | payments / orders |
| **NPS Médio** | `AVG(review_score)` | 4,09 | reviews |
| **Taxa Retenção M1** | `(retained_customers / total_customers) * 100` | 3,5% | custom view |

---

### **Gráficos**

#### **1. Receita por Mês (Line Chart)**
- **Tipo:** Time series
- **Dimensão:** `order_purchase_timestamp` (MONTH)
- **Métrica:** `SUM(payment_value)`
- **Cor:** Gradiente azul
- **Anotações:** Picos de Black Friday

#### **2. Pedidos por Estado (Geo Chart)**
- **Tipo:** Mapa do Brasil
- **Dimensão:** `customer_state`
- **Métrica:** `COUNT(order_id)`
- **Escala de cor:** Verde (baixo) → Azul escuro (alto)

#### **3. Top 10 Categorias (Bar Chart)**
- **Tipo:** Horizontal bar
- **Dimensão:** `product_category_name`
- **Métrica:** `SUM(payment_value)`
- **Ordenação:** Descendente
- **Limite:** 10 categorias

#### **4. NPS Distribution (Pie Chart)**
- **Tipo:** Donut chart
- **Dimensão:** `review_score` (buckets: 1-2, 3, 4-5)
- **Métrica:** `COUNT(review_id)`
- **Cores:** Vermelho (1-2), Amarelo (3), Verde (4-5)

---

### **Filtros**
```yaml
Período (Date Range):
  - Tipo: Date range picker
  - Default: Últimos 12 meses
  - Min: 2016-09-01
  - Max: 2018-08-31

Estado:
  - Tipo: Dropdown list
  - Valores: Todos os estados BR
  - Multi-seleção: Sim
  - Default: Todos

Categoria:
  - Tipo: Dropdown list
  - Valores: Top 20 categorias
  - Multi-seleção: Sim
  - Default: Todos

Status do Pedido:
  - Tipo: Checkbox
  - Valores: delivered, shipped, processing, canceled
  - Default: delivered
```

---

### **Campos Calculados**
```sql
-- Ticket Médio
SUM(payment_value) / COUNT(DISTINCT order_id)

-- Growth Rate MoM
((current_month_revenue - previous_month_revenue) / previous_month_revenue) * 100

-- GMV por Região
CASE 
  WHEN customer_state IN ('SP','RJ','MG','ES') THEN 'Sudeste'
  WHEN customer_state IN ('RS','SC','PR') THEN 'Sul'
  WHEN customer_state IN ('GO','DF','MT','MS') THEN 'Centro-Oeste'
  ELSE 'Norte/Nordeste'
END
```

---

## 👥 2. Customer Analytics Dashboard

### **Informações Gerais**

| Propriedade | Valor |
|-------------|-------|
| **Nome** | Customer Analytics - LTV, Cohort, RFM |
| **ID** | YOUR-REPORT-ID-2 |
| **Páginas** | 3 (LTV / Cohort / RFM) |
| **Dimensões** | 1920x1080 por página |

---

### **Página 1: Lifetime Value**

#### **Scorecards**
- LTV Médio: `AVG(customer_ltv)`
- LTV Mediano: `MEDIAN(customer_ltv)`
- LTV P90: `PERCENTILE_CONT(customer_ltv, 0.9)`

#### **Visualizações**
1. **LTV por Estado** (Geo Chart)
   - Dimensão: `customer_state`
   - Métrica: `AVG(ltv)`

2. **Distribuição LTV** (Histogram)
   - Bins: R$ 0-100, 100-200, 200-500, 500+
   - Métrica: `COUNT(customers)`

3. **Top 10% Clientes** (Table)
   - Colunas: customer_id, ltv, total_orders, state
   - Ordenação: LTV DESC
   - Limite: Top 10%

---

### **Página 2: Cohort Retention**

#### **Matriz de Retenção (Heatmap)**
```yaml
Tipo: Pivot table com conditional formatting
Linhas: cohort_month (2016-09, 2016-10, ...)
Colunas: months_since_first_purchase (M0, M1, M2...M12)
Valores: retention_rate_pct
Escala de cor: 
  - 0%: Vermelho (#FF0000)
  - 50%: Amarelo (#FFFF00)
  - 100%: Verde (#00FF00)
Formato: 0.0%
```

#### **Curvas de Retenção (Line Chart)**
- Dimensão: `months_since_first_purchase`
- Métrica: `AVG(retention_rate)`
- Breakdown: Top 6 cohorts
- Anotação: M1 (ponto crítico)

---

### **Página 3: RFM Segmentation**

#### **Segmentos (Pie Chart)**
- Dimensão: `rfm_segment`
- Métrica: `COUNT(customers)`
- Cores customizadas:
  - Champions: Verde escuro
  - Loyal: Verde claro
  - At Risk: Laranja
  - Lost: Vermelho

#### **Revenue por Segmento (Stacked Bar)**
- Dimensão: `rfm_segment`
- Métrica: `SUM(revenue)`
- Ordenação: Por revenue DESC

---

## 📦 3. Product Performance Dashboard

### **Informações Gerais**

| Propriedade | Valor |
|-------------|-------|
| **Páginas** | 2 (Overview / Deep Dive) |
| **Atualização** | Diária |

---

### **Página 1: Category Overview**

#### **Curva de Pareto (Combo Chart)**
```yaml
Tipo: Bar + Line
Eixo primário (Bar): Receita por categoria
Eixo secundário (Line): % acumulado receita
Anotações:
  - Linha vertical: 20% categorias
  - Linha horizontal: 80% receita
```

#### **Treemap de Categorias**
- Dimensão: `product_category_name`
- Métrica: `SUM(revenue)`
- Cor: `AVG(review_score)` (verde=alto, vermelho=baixo)
- Tooltip: categoria, receita, NPS, % do total

---

### **Página 2: Temporal Analysis**

#### **Evolução Mensal por Categoria (Time Series)**
- Dimensão: `order_purchase_month`
- Métrica: `SUM(revenue)`
- Breakdown: Top 5 categorias
- Anotações: Black Friday (Novembro)

#### **Sazonalidade (Heatmap Calendário)**
- Linhas: Ano
- Colunas: Mês
- Valores: Revenue
- Escala: Gradiente

---

## 🚚 4. Logistics Dashboard

### **Principais Métricas**

| Métrica | SQL | Alvo |
|---------|-----|------|
| **SLA Compliance** | `SUM(CASE WHEN delay_days <= 0 THEN 1 ELSE 0 END) / COUNT(*)` | >80% |
| **Avg Delivery Time** | `AVG(DATE_DIFF(delivered_date, purchase_date, DAY))` | <12 dias |
| **Critical Orders** | `COUNT(CASE WHEN delay_days > 15 THEN 1 END)` | <5% |

---

### **Heatmap de Rotas**
```yaml
Tipo: Pivot table com cores
Linhas: seller_state
Colunas: customer_state
Valores: AVG(delay_days)
Formato condicional:
  - 0 dias: Verde
  - 5 dias: Amarelo
  - 10+ dias: Vermelho
```

---

## 💰 5. Financial Dashboard

### **Breakdown de Receita**

#### **Por Método de Pagamento (Pie Chart)**
- Dimensão: `payment_type`
- Métrica: `SUM(payment_value)`
- Valores: credit_card, boleto, debit_card, voucher

#### **Parcelamento Médio (Scorecard)**
```sql
AVG(payment_installments)
```

#### **Evolução Financeira (Area Chart)**
- Dimensão: `order_purchase_month`
- Métricas (stacked):
  - Receita bruta
  - Frete
  - Receita líquida estimada

---

## 🎨 Especificações de Design

### **Paleta de Cores**
```css
/* Cores Primárias */
--primary-blue: #1A73E8
--primary-green: #34A853
--primary-red: #EA4335
--primary-yellow: #FBBC04

/* Cores Secundárias */
--gray-100: #F8F9FA
--gray-300: #DADCE0
--gray-700: #5F6368
--gray-900: #202124

/* Gradientes */
--gradient-revenue: linear-gradient(90deg, #1A73E8, #34A853)
--gradient-alert: linear-gradient(90deg, #FBBC04, #EA4335)
```

---

### **Tipografia**
```yaml
Títulos: 
  - Font: Google Sans
  - Size: 24px
  - Weight: Bold
  - Color: #202124

KPIs:
  - Font: Roboto
  - Size: 36px
  - Weight: Medium
  - Color: #1A73E8

Labels:
  - Font: Roboto
  - Size: 14px
  - Weight: Regular
  - Color: #5F6368
```

---

## 🔧 Performance

### **Otimizações Implementadas**

1. **Views Materializadas**
```sql
-- Exemplo: RFM pre-calculado
CREATE MATERIALIZED VIEW rfm_segments AS
SELECT 
  customer_unique_id,
  recency, frequency, monetary,
  rfm_score, segment
FROM rfm_calculation
```

2. **Particionamento**
```sql
-- Tabelas particionadas por data
CREATE TABLE orders
PARTITION BY DATE(order_purchase_timestamp)
```

3. **Aggregations Pre-calculadas**
- Métricas diárias calculadas em batch
- Reduz queries on-demand

---

### **Limites e Constraints**

| Aspecto | Limite | Atual |
|---------|--------|-------|
| **Queries simultâneas** | 50 | ~10 |
| **Data refresh** | 1/dia | 1/dia |
| **Rows por query** | 1M | ~500k |
| **Cache TTL** | 12h | 12h |

---

## 📊 Métricas de Uso

### **Tracking (Google Analytics)**
```javascript
// Event tracking configurado
gtag('event', 'dashboard_view', {
  'dashboard_name': 'Executive',
  'user_type': 'public'
});
```

---

### **KPIs do Dashboard**

- Page views: ~500/mês
- Avg session duration: 4:30min
- Bounce rate: 25%
- Top interações: Filtros de data e estado

---

## 🔒 Segurança e Permissões

### **Acesso Público**
- Modo: View-only (somente leitura)
- Dados sensíveis: Anonimizados
- Rate limiting: 100 requests/min

### **Dados Ocultos**
```yaml
Campos não exibidos:
  - customer_email
  - customer_name
  - seller_name
  - order_id completo (masked)
```

---

## 📚 Referências

- **Looker Studio Docs:** https://support.google.com/looker-studio
- **BigQuery Best Practices:** https://cloud.google.com/bigquery/docs/best-practices
- **Data Viz Principles:** https://datavizcatalogue.com/

---

**Última revisão:** Novembro 2024  
**Versão:** 1.0  
**Mantainer:** André Bomfim