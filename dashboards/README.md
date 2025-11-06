# 📊 Dashboards - Looker Studio

Dashboards interativos para visualização e análise dos dados do e-commerce Olist.

---

## 📋 Índice

1. [Visão Geral](#visao-geral)
2. [Dashboards Disponíveis](#dashboards)
3. [Como Acessar](#acesso)
4. [Arquitetura](#arquitetura)
5. [Customização](#customizacao)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral {#visao-geral}

Conjunto de 5 dashboards interativos construídos no **Google Looker Studio** conectados ao **BigQuery**.

**Características:**
- ✅ Acesso público (somente leitura)
- ✅ Atualização diária automática
- ✅ Filtros interativos
- ✅ Responsivo (desktop/tablet)
- ✅ Exportável (PDF/CSV)

---

## 📊 Dashboards Disponíveis {#dashboards}

### **1. 📈 Executive Dashboard**

**Objetivo:** Visão executiva de alto nível

**Principais Métricas:**
- Receita total e crescimento
- Volume de pedidos
- Ticket médio
- NPS médio
- Performance por região

**Público-alvo:** C-level, diretores

**[Acessar Dashboard →](looker_studio_links.md#1-executive-dashboard)**

---

### **2. 👥 Customer Analytics**

**Objetivo:** Análise profunda de clientes

**Seções:**
- **LTV Analysis:** Lifetime value por segmento
- **Cohort Retention:** Matriz de retenção e curvas
- **RFM Segmentation:** 11 segmentos de clientes

**Insights:**
- Retenção M1: 3,5%
- LTV médio: R$ 154
- Champions: 5-10% da base, 40% da receita

**Público-alvo:** Marketing, CRM, Customer Success

**[Acessar Dashboard →](looker_studio_links.md#2-customer-analytics)**

---

### **3. 📦 Product Performance**

**Objetivo:** Performance por categoria de produto

**Análises:**
- Curva de Pareto (80/20)
- Evolução temporal (sazonalidade)
- NPS por categoria
- Matriz preço vs volume

**Insights:**
- 20% categorias = 80% receita
- Black Friday: pico de 40% em eletrônicos
- Beleza & Saúde: maior NPS (4,2)

**Público-alvo:** Comercial, Compras, Produto

**[Acessar Dashboard →](looker_studio_links.md#3-product-performance)**

---

### **4. 🚚 Logistics Overview**

**Objetivo:** Performance logística e entregas

**KPIs:**
- SLA compliance: 75-85%
- Tempo médio entrega: 12 dias
- Taxa de atraso: 15-25%
- Correlação atraso vs NPS: r = -0,6

**Análises:**
- Heatmap de rotas problemáticas
- Performance por estado
- Pedidos críticos (>15 dias atraso)

**Público-alvo:** Operações, Logística

**[Acessar Dashboard →](looker_studio_links.md#4-logistics-overview)**

---

### **5. 💰 Financial Deep Dive**

**Objetivo:** Análise financeira detalhada

**Métricas:**
- GMV (Gross Merchandise Value)
- Receita líquida (após frete)
- Breakdown por método de pagamento
- Parcelamento médio

**Segmentações:**
- Por categoria
- Por região
- Por canal de pagamento

**Público-alvo:** Financeiro, Controladoria

**[Acessar Dashboard →](looker_studio_links.md#5-financial-deep-dive)**

---

## 🔗 Como Acessar {#acesso}

### **Opção 1: Acesso Público (Recomendado)**
```
1. Acesse: looker_studio_links.md
2. Clique no dashboard desejado
3. Explore livremente (somente leitura)
```

**Funcionalidades disponíveis:**
- ✅ Filtros interativos
- ✅ Drill-down em gráficos
- ✅ Exportar para PDF
- ✅ Compartilhar link
- ❌ Editar (somente leitura)

---

### **Opção 2: Fazer Cópia (Edição)**

Para criar sua própria versão editável:
```
1. Abra o dashboard público
2. Clique em ⋮ (menu) → "Fazer uma cópia"
3. Conecte à sua fonte de dados:
   - BigQuery: your-project.olist_ecommerce
4. Personalize conforme necessário
```

**Requisitos:**
- Conta Google (Gmail)
- Acesso ao BigQuery com os dados
- Permissões: BigQuery Data Viewer

---

### **Opção 3: Embedar no Site**
```html
<!-- Código de embed -->
<iframe 
  width="100%" 
  height="600" 
  src="https://lookerstudio.google.com/embed/reporting/YOUR-REPORT-ID/page/PAGE-ID" 
  frameborder="0" 
  style="border:0" 
  allowfullscreen>
</iframe>
```

---

## 🏗️ Arquitetura {#arquitetura}

### **Fluxo de Dados**
```
CSV Files (Kaggle)
    ↓
[ETL Pipeline] (Python)
    ↓
Google BigQuery
    ↓
Looker Studio Dashboards
    ↓
End Users (Web Browser)
```

---

### **Conexão BigQuery**
```yaml
Projeto: your-gcp-project
Dataset: olist_ecommerce
Modo: Direct Query (real-time)
Cache: 12 horas
Refresh: Diário (2:00 AM UTC)
```

**Tabelas utilizadas:**
- `orders`
- `customers`
- `order_items`
- `products`
- `sellers`
- `payments`
- `reviews`
- `geolocation`

**Views customizadas:**
- `rfm_segments`
- `cohort_retention`
- `category_performance`
- `delivery_metrics`

---

### **Diagrama de Arquitetura**
```
┌─────────────┐
│   Kaggle    │
│  (Raw CSVs) │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Python ETL   │
│ + Docker    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  BigQuery   │
│ Data Warehouse│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Looker Studio│
│ Dashboards  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  End Users  │
│(Web Browser)│
└─────────────┘
```

---

## 🎨 Customização {#customizacao}

### **1. Modificar Filtros**
```
1. Fazer cópia do dashboard
2. Edit → Add a control → Filter control
3. Configurar:
   - Campo: customer_state
   - Tipo: Dropdown
   - Multi-select: Sim
4. Aplicar a gráficos desejados
```

---

### **2. Adicionar Novos KPIs**
```
1. Data → Add a field
2. Nome: "Taxa de Conversão"
3. Fórmula: 
   (COUNT(DISTINCT customer_id) / 
    COUNT(DISTINCT session_id)) * 100
4. Tipo: Number
5. Formato: 0.0%
6. Aplicar
```

---

### **3. Criar Novos Gráficos**
```
1. Insert → Chart
2. Selecionar tipo (bar, line, pie, etc)
3. Configurar:
   - Data source: BigQuery connection
   - Dimension: product_category_name
   - Metric: SUM(revenue)
   - Sort: Descending
4. Style → Customizar cores
```

---

### **4. Temas e Cores**
```yaml
Tema Atual: Light
Paleta Primária:
  - Azul: #1A73E8
  - Verde: #34A853
  - Vermelho: #EA4335
  - Amarelo: #FBBC04

Para alterar:
1. Theme and layout → Current theme
2. Customize theme
3. Escolher cores, fontes, espaçamentos
```

---

## 📊 Filtros Disponíveis

### **Filtros Comuns (Todos Dashboards)**

| Filtro | Tipo | Valores | Default |
|--------|------|---------|---------|
| **Período** | Date range | 2016-09 a 2018-08 | Últimos 12 meses |
| **Estado** | Dropdown | 27 estados BR | Todos |
| **Categoria** | Dropdown | 71 categorias | Todos |
| **Status Pedido** | Checkbox | delivered, shipped, canceled | delivered |

### **Filtros Específicos**
**Customer Analytics:**

- RFM Segment (Champions, Loyal, At Risk, etc)
- Cohort Month
- LTV Range (faixas de valor)

**Product Performance:**

- Price Range (faixas de preço)
- NPS Range (1-5 estrelas)

**Logistics:**

- Delay Range (dias de atraso)
- Delivery Route (origem → destino)

## 📸 Screenshots
Prévia visual dos dashboards disponível em:

```yaml
dashboards/screenshots/
├── executive_dashboard.png
├── customer_analytics.png
├── product_performance.png
├── logistics_overview.png
└── financial_deep_dive.png
```

## 🔧 Troubleshooting {#troubleshooting}

### **Dashboard não carrega**
**Sintomas:**

- Tela em branco
- Erro "Unable to load"
- Timeout

**Soluções:**

```yaml
1. Verificar conexão internet
2. Limpar cache do navegador (Ctrl+Shift+Del)
3. Tentar modo anônimo/privado
4. Verificar se BigQuery está acessível:
   https://console.cloud.google.com/bigquery
5. Conferir logs de erro (F12 → Console)
```

### **Dados desatualizados**
**Sintomas:**

Métricas não refletem dados recentes
Última atualização >24h

**Soluções:**

```yaml
# 1. Forçar refresh do dashboard
Ctrl+F5 (force reload)

# 2. Verificar última execução ETL
tail -f logs/etl_bigquery.log

# 3. Re-executar ETL manualmente
python python/etl/load_to_bigquery.py --force-refresh

# 4. Verificar BigQuery
SELECT MAX(order_purchase_timestamp) 
FROM `project.dataset.orders`
```

---

### **Erro de permissão**

**Sintomas:**
- "You don't have access"
- "Permission denied"

**Soluções:**

**Para visualização pública:**
```
✓ Dashboards já configurados como públicos
✗ Se erro persistir, verificar firewall/proxy corporativo
```

**Para fazer cópia:**

```
1. Login com conta Google
2. Verificar permissões BigQuery:
   - IAM → your-email@gmail.com
   - Role: BigQuery Data Viewer (mínimo)
3. Se não tiver acesso aos dados:
   - Usar seus próprios dados
   - OU solicitar acesso ao projeto
```

### **Gráficos vazios**
**Sintomas:**

- Dashboard carrega mas gráficos sem dados
- "No data available"

Causas comuns:

- 1. Filtros muito restritivos
- 2. Dados não carregados no BigQuery
- 3. Query timeout

**Soluções:**

```
# 1. Resetar todos os filtros
Click em "Reset" em cada filtro

# 2. Verificar dados no BigQuery
SELECT COUNT(*) FROM `project.dataset.orders`
# Se retornar 0, recarregar dados

# 3. Simplificar queries complexas
Edit → Data source → Limit rows: 10000
```

### **Performance lenta**
**Sintomas:**

- Dashboard demora >5s para carregar
- Filtros lentos
- Timeout errors

**Otimizações:**

```
1. Criar views materializadas

CREATE MATERIALIZED VIEW daily_metrics AS
SELECT 
  DATE(order_purchase_timestamp) as date,
  COUNT(*) as orders,
  SUM(payment_value) as revenue
FROM orders
GROUP BY date

2. Particionar tabelas grandes

CREATE TABLE orders_partitioned
PARTITION BY DATE(order_purchase_timestamp)
AS SELECT * FROM orders

3. Agregar dados antes

Usar daily/weekly aggregates ao invés de row-level

```

**No Looker Studio:**

```
1. Resource → Manage added data sources
2. Para cada source:
   - Enable data freshness: 12 hours
   - Enable query cache
3. Limitar rows retornadas:
   - Style → Data → Rows per page: 100

```

---

**Sintomas:**
- PDF não gera
- CSV incompleto
- Download trava

**Soluções:**

1. Exportar página por página (não todas de uma vez)
2. Reduzir período de dados (ex: 1 mês ao invés de 2 anos)
3. Remover gráficos muito grandes antes de exportar
4. Usar "Print to PDF" do navegador como alternativa:
   - Ctrl+P → Destination: Save as PDF

## **📊 Manutenção**
### **Checklist Semanal**

- [ ] Verificar atualização de dados (última data)
- [ ] Testar todos os filtros
- [ ] Validar KPIs principais (comparar com SQL direto)
- [ ] Verificar logs de erro
- [ ] Conferir performance (tempo de carga)

### **Checklist Mensal**

- [ ] Revisar queries lentas (BigQuery → Query History)
- [ ] Otimizar views materializadas
- [ ] Atualizar documentação se houver mudanças
- [ ] Backup de configurações (Export → JSON)
- [ ] Revisar permissões de acesso

### **Versionamento**

#### Fazer backup do dashboard antes de mudanças
1. File → Make a copy
2. Renomear: "Dashboard Name - Backup YYYYMMDD"
3. Fazer alterações na versão principal
4. Se problemas, restaurar do backup

#### Histórico de versões
File → Version history → See version history

## **📚 Recursos Adicionais**

### **Documentação**

- Links dos Dashboards: looker_studio_links.md
- Especificações Técnicas: dashboard_specs.md
- Arquitetura do Projeto: ../docs/architecture.md
- SQL Queries: ../sql/README.md

### **Tutoriais**
**Looker Studio:**

- [Introdução ao Looker Studio](https://cloud.google.com/looker/docs/studio?visit_id=638979809339679586-3179601133&rd=1&hl=pt-br)
- [Conectar ao BigQuery](https://cloud.google.com/looker/docs/studio/connect-to-google-bigquery?visit_id=638979810259584930-3615354398&rd=1&hl=pt-br)
- [Criar campos calculados](https://cloud.google.com/looker/docs/studio/about-calculated-fields?visit_id=638979810565793291-1740166127&rd=1&hl=pt-br)
- [Fórmulas e funções](https://support.google.com/looker-studio/table/6379764)

**BigQuery:**

- [Query Optimization](https://cloud.google.com/bigquery/docs/best-practices-performance-overview)
- [Partitioned Tables](https://cloud.google.com/bigquery/docs/partitioned-tables)
- [Cost Optimization](https://cloud.google.com/bigquery/docs/best-practices-costs)

**Community & Support**

- Looker Studio Community: https://support.google.com/looker-studio/community
- Stack Overflow: Tag `google-data-studio`
- YouTube: Buscar "Looker Studio tutorials"

## **🔐 Segurança e Privacidade**
### **Dados Públicos**
Os dashboards públicos exibem dados anonimizados:

Dados Ocultos:
  - customer_email
  - customer_name
  - seller_name
  - order_id completo (apenas últimos 4 dígitos)
  - Qualquer PII (Personally Identifiable Information)

Dados Agregados:
  - Todas métricas exibidas são agregações
  - Não é possível identificar pedidos individuais

**Boas Práticas**

- ✓ Use dashboards públicos apenas para dados agregados
- ✓ Remova informações sensíveis antes de compartilhar
- ✓ Configure Row-Level Security para dados restritos
- ✓ Revise permissões periodicamente
- ✓ Monitore logs de acesso

- ✗ Não inclua PII em dashboards públicos
- ✗ Não compartilhe credenciais de acesso
- ✗ Não bypass de segurança do BigQuery

## **🚀 Próximos Passos**
Após explorar os dashboards:

- 1. Análises Detalhadas: Consulte os Notebooks Jupyter ../notebooks/README.md
- 2. Queries SQL: Acesse SQL Analytics ../sql/README.md
- 3. Insights de Negócio: Leia Business Insights  ../docs/business_insights.md
- 4. Replicar Projeto: Siga Setup Guide ../docs/setup_guide.md

## **Encontrou algum problema?**

1. Consulte a seção Troubleshooting  ?(não sei oq o claude se referiou a isso)
2. Verifique Issues no GitHub  https://github.com/AndreBomfim99/analise23/issues
3. Abra uma nova issue com:
    - Screenshot do erro
    - Passos para reproduzir
    - Navegador e versão
    - Console logs (F12 → Console)

## **🙏 Créditos**

- Dados: Olist - Brazilian E-Commerce Dataset  https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
- Plataforma: Google Looker Studio  https://lookerstudio.google.com/
- Infraestrutura: Google BigQuery  https://cloud.google.com/bigquery

## **✅ Dashboards Explorados? Continue para: Business Insights ../docs/business_insights.md **
- Última atualização: Novembro 2024
- Versão: 1.0
- Autor: André Bomfim

