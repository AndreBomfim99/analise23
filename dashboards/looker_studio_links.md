# 📊 Dashboards - Looker Studio

Links públicos para os dashboards interativos do projeto.

---

## 🔗 Acesso Rápido

| Dashboard | Descrição | Link |
|-----------|-----------|------|
| 📈 Executive Dashboard | Visão geral do negócio | [Acessar](https://lookerstudio.google.com/reporting/YOUR-REPORT-ID-1) |
| 👥 Customer Analytics | LTV, Cohort, RFM | [Acessar](https://lookerstudio.google.com/reporting/YOUR-REPORT-ID-2) |
| 📦 Product Performance | Análise por categoria | [Acessar](https://lookerstudio.google.com/reporting/YOUR-REPORT-ID-3) |
| 🚚 Logistics Overview | Performance de entregas | [Acessar](https://lookerstudio.google.com/reporting/YOUR-REPORT-ID-4) |
| 💰 Financial Deep Dive | Receita e margens | [Acessar](https://lookerstudio.google.com/reporting/YOUR-REPORT-ID-5) |

---

## 📈 1. Executive Dashboard

**URL:** https://lookerstudio.google.com/reporting/YOUR-REPORT-ID-1

**Objetivo:** Visão executiva de alto nível do e-commerce

**KPIs Principais:**
- Receita total e crescimento MoM
- Número de pedidos e ticket médio
- NPS médio e distribuição
- Taxa de retenção (M0→M1)
- GMV por região

**Filtros Disponíveis:**
- Período (data range picker)
- Estado
- Categoria de produto
- Status do pedido

**Atualização:** Dados carregados via BigQuery (refresh diário)

---

## 👥 2. Customer Analytics

**URL:** https://lookerstudio.google.com/reporting/YOUR-REPORT-ID-2

**Objetivo:** Análise profunda de comportamento do cliente

**Seções:**
1. **Lifetime Value (LTV)**
   - LTV médio, mediano, P90
   - LTV por estado
   - Top 10% clientes

2. **Cohort Analysis**
   - Matriz de retenção (heatmap)
   - Curvas de retenção por cohort
   - Taxa de churn mensal

3. **RFM Segmentation**
   - Distribuição de clientes por segmento
   - Revenue por segmento
   - Priority score e ações recomendadas

**Fonte de Dados:**
- `olist_ecommerce.customers`
- `olist_ecommerce.orders`
- `olist_ecommerce.payments`
- Views customizadas: `rfm_segments`, `cohort_retention`

---

## 📦 3. Product Performance

**URL:** https://lookerstudio.google.com/reporting/YOUR-REPORT-ID-3

**Objetivo:** Performance por categoria de produto

**Métricas:**
- Receita por categoria (Top 20)
- Ticket médio e margem estimada
- NPS por categoria
- Evolução temporal (sazonalidade)
- Curva de Pareto (80/20)

**Visualizações:**
- Treemap de categorias
- Time series de vendas
- Scatter plot: preço vs volume
- Heatmap geográfico

**Filtros:**
- Categoria
- Faixa de preço
- Estado
- Período

---

## 🚚 4. Logistics Overview

**URL:** https://lookerstudio.google.com/reporting/YOUR-REPORT-ID-4

**Objetivo:** Performance logística e entregas

**KPIs:**
- SLA compliance rate
- Tempo médio de entrega
- Taxa de atraso
- NPS vs atraso (correlação)

**Análises:**
- Heatmap de rotas (seller → customer)
- Performance por estado
- Distribuição de atrasos
- Pedidos críticos (>15 dias)

**Alertas:**
- Estados com SLA <70%
- Rotas com atraso >30%
- Tendência de piora

---

## 💰 5. Financial Deep Dive

**URL:** https://lookerstudio.google.com/reporting/YOUR-REPORT-ID-5

**Objetivo:** Análise financeira detalhada

**Métricas:**
- GMV (Gross Merchandise Value)
- Receita líquida (após frete)
- AOV (Average Order Value)
- Métodos de pagamento
- Parcelamento médio

**Segmentações:**
- Por categoria
- Por região
- Por canal de pagamento
- Por faixa de valor

---

## 🔧 Como Acessar

### **Opção 1: Visualização Pública**

Os dashboards estão configurados para acesso público (somente leitura).

1. Clique no link desejado
2. Explore os dados interativamente
3. Use filtros para análises customizadas

---

### **Opção 2: Fazer Cópia (Edição)**

Para criar sua própria versão:

1. Abra o dashboard
2. Clique em **⋮ (menu)** → **Fazer uma cópia**
3. Conecte à sua fonte de dados BigQuery
4. Personalize conforme necessário

---

## 📊 Fonte de Dados

Todos os dashboards estão conectados ao BigQuery:
```
Projeto: your-gcp-project
Dataset: olist_ecommerce
Tabelas:
  - orders
  - customers
  - order_items
  - products
  - sellers
  - payments
  - reviews
  
Views:
  - rfm_segments
  - cohort_retention
  - category_performance
```

---

## 🔄 Atualização de Dados

- **Frequência:** Diária (2:00 AM UTC)
- **Método:** ETL automatizado (Cloud Scheduler)
- **Lag:** Dados de D-1 disponíveis em D às 3:00 AM

Para forçar atualização manual:
```bash
python python/etl/load_to_bigquery.py --force-refresh
```

---

## 🎨 Personalização

### **Temas Disponíveis:**
- Light (padrão)
- Dark
- Custom (edite após copiar)

### **Exportações:**
- PDF (File → Download → PDF)
- CSV (dados de gráficos específicos)
- Imagens (screenshot)

---

## 🐛 Problemas Conhecidos

**Dashboard não carrega:**
- Verificar permissões BigQuery
- Confirmar conectividade internet
- Limpar cache do navegador

**Dados desatualizados:**
- Verificar última execução do ETL
- Consultar logs: `logs/etl_bigquery.log`

**Erro de permissão:**
- Dashboards públicos: somente leitura
- Para editar: fazer cópia própria

---

## 📸 Screenshots

Prévia dos dashboards disponível em: `dashboards/screenshots/`

---

## 📚 Documentação Adicional

- **Especificações Técnicas:** [dashboard_specs.md](dashboard_specs.md)
- **Guia de Uso:** [README.md](README.md)
- **Arquitetura:** [../docs/architecture.md](../docs/architecture.md)

---

## 🔗 Links Relacionados

- **GitHub Repository:** https://github.com/AndreBomfim99/analise23
- **BigQuery Dataset:** `your-project.olist_ecommerce`
- **Documentação Looker Studio:** https://support.google.com/looker-studio

---

**💡 Dica:** Adicione os dashboards aos favoritos do navegador para acesso rápido!

**Última atualização:** Novembro 2024