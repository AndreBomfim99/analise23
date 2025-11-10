# 📘 Methodology - Olist E-Commerce Analysis

Documentação completa das metodologias, técnicas e frameworks aplicados no projeto.

---

## 📋 Índice

1. [Visão Geral](#visao-geral)
2. [Metodologias de Análise de Clientes](#metodologias-clientes)
3. [Metodologias de Análise de Dados](#metodologias-dados)
4. [Frameworks de Métricas](#frameworks-metricas)
5. [Técnicas Estatísticas](#tecnicas-estatisticas)
6. [Stack Tecnológico](#stack-tecnologico)
7. [Processo ETL](#processo-etl)
8. [Visualização de Dados](#visualizacao)
9. [Referências](#referencias)

---

## 🎯 Visão Geral {#visao-geral}

### **Abordagem Metodológica**

Este projeto utiliza uma abordagem **data-driven** combinando múltiplas metodologias consolidadas de análise de clientes e e-commerce:

```
Dados Brutos → ETL → Data Warehouse → Análises → Insights → Ações
```

**Princípios Norteadores:**

1. **Baseado em Evidências:** Todas as recomendações são suportadas por dados quantitativos
2. **Acionável:** Foco em insights que podem ser traduzidos em ações concretas
3. **Replicável:** Metodologias documentadas e reproduzíveis
4. **Escalável:** Arquitetura preparada para crescimento de volume de dados

---

## 👥 Metodologias de Análise de Clientes {#metodologias-clientes}

### **1. Segmentação RFM (Recency, Frequency, Monetary)**

#### **Origem:**
- Desenvolvida por Arthur Hughes (1994)
- Amplamente utilizada em marketing direto e CRM

#### **Conceito:**

A segmentação RFM classifica clientes com base em três dimensões comportamentais:

**R - Recency (Recência):**
- Quanto tempo desde a última compra?
- Clientes que compraram recentemente têm maior probabilidade de comprar novamente
- **Métrica:** Dias desde última transação

**F - Frequency (Frequência):**
- Quantas vezes o cliente comprou?
- Maior frequência = maior engajamento
- **Métrica:** Número total de pedidos

**M - Monetary (Valor Monetário):**
- Quanto o cliente gastou?
- Alto valor = maior importância estratégica
- **Métrica:** Soma total gasta (preço + frete)

#### **Implementação no Projeto:**

**Passo 1: Cálculo das Métricas**
```sql
-- Para cada cliente, calcular:
Recency = DIAS_HOJE - DATA_ULTIMA_COMPRA
Frequency = COUNT(pedidos)
Monetary = SUM(valor_total)
```

**Passo 2: Scoring (Quintis)**
```sql
-- Dividir cada métrica em 5 níveis (1 a 5)
R_Score = NTILE(5) OVER (ORDER BY recency DESC)  -- Inverso: menor recência = melhor
F_Score = NTILE(5) OVER (ORDER BY frequency)
M_Score = NTILE(5) OVER (ORDER BY monetary)
```

**Passo 3: Segmentação**

Combinando os scores, obtemos 11 segmentos estratégicos:

| Segmento | R | F | M | Descrição | Ação Recomendada |
|----------|---|---|---|-----------|------------------|
| **Champions** | 5 | 5 | 5 | Melhores clientes | Recompensar, programa VIP |
| **Loyal Customers** | 4-5 | 4-5 | 4-5 | Clientes fiéis | Upsell, cross-sell |
| **Potential Loyalist** | 4-5 | 2-3 | 2-3 | Potencial de crescimento | Programas de engajamento |
| **New Customers** | 4-5 | 1 | 1 | Recém-chegados | Onboarding, segunda compra |
| **Promising** | 3-4 | 1 | 1 | Início promissor | Nurturing, ofertas |
| **Need Attention** | 3-4 | 2-3 | 2-3 | Requerem atenção | Campanhas personalizadas |
| **About To Sleep** | 2-3 | 1-2 | 1-2 | Em risco de dormir | Reativação preventiva |
| **At Risk** | 1-2 | 3-4 | 3-4 | Alto valor em risco | Win-back agressivo |
| **Cannot Lose Them** | 1-2 | 4-5 | 4-5 | Crítico não perder | Contato direto, ofertas especiais |
| **Hibernating** | 1-2 | 1-2 | 1-2 | Dormentes | Campanhas de baixo custo |
| **Lost** | 1 | 1 | 1 | Perdidos | Remover da base ativa |

**Vantagens da Metodologia:**
- ✅ Simples de implementar
- ✅ Não requer machine learning complexo
- ✅ Resultados interpretáveis por não-técnicos
- ✅ Acionável para marketing

**Limitações:**
- ⚠️ Não considera sazonalidade
- ⚠️ Não captura mudanças de comportamento
- ⚠️ Pesos iguais para R, F e M (pode não ser ideal)

#### **Referência:**
> HUGHES, Arthur M. **Strategic Database Marketing**. 4th ed. McGraw-Hill, 2012.

---

### **2. Análise de Cohort (Cohort Retention Analysis)**

#### **Origem:**
- Utilizada em estudos epidemiológicos desde os anos 1950
- Adaptada para análise de produtos digitais e SaaS

#### **Conceito:**

Cohort é um grupo de usuários que compartilham uma característica comum em um período específico.

**Neste projeto:**
- **Cohort = Mês de primeira compra**
- Acompanhamos esses clientes ao longo do tempo

#### **Implementação:**

**Estrutura da Análise:**

```
           M0    M1    M2    M3    M6    M12
Jan/2017  100%  3.5%  2.1%  1.8%  1.5%  1.2%
Fev/2017  100%  3.7%  2.3%  1.9%  1.6%  1.3%
Mar/2017  100%  3.9%  2.4%  2.0%  1.7%  1.4%
...
```

**Fórmula de Retenção:**

```
Retenção Mês N = (Clientes Ativos no Mês N / Clientes no M0) × 100
```

**Exemplo:**
```
Cohort Janeiro 2017:
- M0 (Jan): 1.000 clientes (100%)
- M1 (Fev): 35 clientes retornaram (3,5%)
- M2 (Mar): 21 clientes ainda ativos (2,1%)
```

**Insights Extraídos:**

1. **Taxa de Churn:** 100% - Retenção
2. **Janela Crítica:** Primeiro mês (M0→M1)
3. **Estabilização:** Mês em que retenção se estabiliza
4. **Comparação Temporal:** Cohorts recentes vs antigos

**Vantagens:**
- ✅ Identifica padrões temporais
- ✅ Isola efeito de mudanças no produto/serviço
- ✅ Previsibilidade de churn

**Limitações:**
- ⚠️ Requer volume significativo de dados
- ⚠️ Sensível a sazonalidade
- ⚠️ Não explica "por que" do churn

#### **Referência:**
> CROLL, Alistair; YOSKOVITZ, Benjamin. **Lean Analytics**. O'Reilly Media, 2013.

---

### **3. Customer Lifetime Value (LTV / CLV)**

#### **Origem:**
- Conceito desenvolvido na literatura de marketing nos anos 1980
- Popularizado por Gupta & Lehmann (2005)

#### **Conceito:**

LTV é o **valor presente líquido** de todos os fluxos de caixa futuros atribuídos ao relacionamento com o cliente.

#### **Implementação no Projeto:**

Utilizamos a **abordagem histórica** (não preditiva):

**Fórmula Básica:**
```
LTV = Receita Total do Cliente - Custos Associados
```

**Fórmula Detalhada:**
```
LTV = Σ (Valor Pedido × Frequência) - CAC - Custos Operacionais
```

**No nosso caso:**
```sql
LTV_Cliente = SUM(price + freight_value)
              ÷ Lifetime_Days
              × 365
```

**LTV por Segmento:**

Calculamos LTV médio para cada:
- Segmento RFM
- Estado/Região
- Categoria de produto
- Cohort temporal

**Análise LTV vs CAC:**

```
ROI = (LTV - CAC) / CAC

Onde:
- CAC = Customer Acquisition Cost (custo de aquisição)
- Estimado em R$ 45 baseado em benchmarks de mercado
```

**Interpretação:**

| Ratio LTV:CAC | Significado | Ação |
|---------------|-------------|------|
| < 1:1 | Prejuízo | Reduzir CAC ou aumentar retenção |
| 1:1 a 3:1 | Breakeven a saudável | Otimizar margem |
| > 3:1 | Muito saudável | Investir em crescimento |

**Vantagens:**
- ✅ Quantifica valor do cliente
- ✅ Justifica investimentos em retenção
- ✅ Prioriza alocação de recursos

**Limitações:**
- ⚠️ LTV histórico ≠ LTV futuro
- ⚠️ Não considera churn futuro
- ⚠️ Difícil estimar custos reais

#### **Referência:**
> GUPTA, Sunil; LEHMANN, Donald. **Managing Customers as Investments**. Wharton School Publishing, 2005.

---

## 📊 Metodologias de Análise de Dados {#metodologias-dados}

### **1. Análise Exploratória de Dados (EDA)**

#### **Objetivo:**
Compreender a estrutura, distribuição e qualidade dos dados antes de análises avançadas.

#### **Técnicas Aplicadas:**

**1.1 Estatísticas Descritivas**
```
- Média, Mediana, Moda
- Desvio Padrão, Variância
- Percentis (P25, P50, P75, P90, P95)
- Valores min/max
```

**1.2 Identificação de Outliers**
```
Método IQR (Interquartile Range):
- Q1 = Percentil 25
- Q3 = Percentil 75
- IQR = Q3 - Q1
- Outliers: < Q1 - 1.5×IQR ou > Q3 + 1.5×IQR
```

**1.3 Análise de Missing Values**
```sql
SELECT 
  column_name,
  COUNT(*) as total,
  COUNT(column_name) as non_null,
  COUNT(*) - COUNT(column_name) as nulls,
  ROUND(100.0 * (COUNT(*) - COUNT(column_name)) / COUNT(*), 2) as pct_null
FROM table
```

**1.4 Análise de Distribuições**
- Histogramas
- Box plots
- Gráficos de densidade

---

### **2. Análise de Pareto (Regra 80/20)**

#### **Origem:**
- Princípio de Vilfredo Pareto (1906)
- Aplicado em gestão por Joseph Juran (1941)

#### **Conceito:**

**"80% dos efeitos vêm de 20% das causas"**

No e-commerce:
- 80% da receita vem de 20% dos clientes
- 80% da receita vem de 20% das categorias
- 80% dos problemas vêm de 20% das causas

#### **Implementação:**

**Cálculo da Curva de Pareto:**

```sql
WITH ranked_data AS (
  SELECT 
    category,
    revenue,
    SUM(revenue) OVER (ORDER BY revenue DESC) as cumulative_revenue,
    SUM(revenue) OVER () as total_revenue
  FROM category_performance
)
SELECT 
  category,
  revenue,
  ROUND(100.0 * cumulative_revenue / total_revenue, 2) as cumulative_pct
FROM ranked_data
ORDER BY revenue DESC;
```

**Visualização:**
- Gráfico de barras (receita individual)
- Linha acumulada (curva de Pareto)

**Aplicações no Projeto:**

1. **Clientes:** Identificar Champions (20% que geram 80% receita)
2. **Categorias:** Priorizar categorias de maior impacto
3. **Estados:** Focar em regiões mais lucrativas
4. **Problemas:** Resolver atrasos das rotas críticas primeiro

#### **Referência:**
> KOCH, Richard. **The 80/20 Principle**. Crown Business, 1998.

---

### **3. Análise de Correlação**

#### **Objetivo:**
Identificar relações entre variáveis (ex: atraso de entrega vs NPS).

#### **Técnica Utilizada:**

**Correlação de Pearson (r):**

```
r = Cov(X,Y) / (σx × σy)

Onde:
- Cov(X,Y) = Covariância entre X e Y
- σx, σy = Desvios padrão de X e Y
```

**Interpretação:**

| Valor de r | Interpretação |
|------------|---------------|
| r = 1 | Correlação positiva perfeita |
| 0.7 < r < 1 | Correlação forte positiva |
| 0.3 < r < 0.7 | Correlação moderada positiva |
| -0.3 < r < 0.3 | Correlação fraca/inexistente |
| -0.7 < r < -0.3 | Correlação moderada negativa |
| -1 < r < -0.7 | Correlação forte negativa |
| r = -1 | Correlação negativa perfeita |

**No Projeto:**

**Atraso de Entrega vs NPS:**
```
r = -0,63 (p < 0,001)
```

**Interpretação:**
- Correlação **negativa moderada-forte**
- Estatisticamente significante (p < 0,001)
- **Quanto maior o atraso, menor o NPS**

**Implementação SQL:**

```sql
SELECT 
  CORR(delay_days, review_score) as correlation_coefficient
FROM delivery_metrics
WHERE delay_days IS NOT NULL 
  AND review_score IS NOT NULL;
```

**Limitações:**
- ⚠️ Correlação ≠ Causalidade
- ⚠️ Sensível a outliers
- ⚠️ Assume relação linear

---

## 📈 Frameworks de Métricas {#frameworks-metricas}

### **1. Métricas AARRR (Pirate Metrics)**

Desenvolvido por Dave McClure (500 Startups), adaptado para e-commerce:

**A - Acquisition (Aquisição):**
- Novos clientes
- CAC (Customer Acquisition Cost)
- Canais de aquisição

**A - Activation (Ativação):**
- Taxa de conversão primeira compra
- Tempo até primeira compra
- Valor primeira compra

**R - Retention (Retenção):**
- Taxa de retenção M1, M3, M6
- Churn rate
- Cohort analysis

**R - Revenue (Receita):**
- GMV (Gross Merchandise Value)
- LTV (Lifetime Value)
- Ticket médio

**R - Referral (Referência):**
- NPS (Net Promoter Score)
- Taxa de indicação
- Viral coefficient

**No Projeto:**

| Métrica | Valor | Benchmark | Status |
|---------|-------|-----------|--------|
| CAC | R$ 45 | R$ 30-50 | 🟡 OK |
| Retenção M1 | 3,5% | 15-25% | 🔴 Crítico |
| LTV | R$ 154 | R$ 200+ | 🟡 Abaixo |
| NPS | 4,09/5 | 4,0+ | 🟢 Bom |
| Churn M1 | 96,5% | 75-85% | 🔴 Crítico |

---

### **2. North Star Metric**

#### **Conceito:**
Uma única métrica que melhor captura o valor entregue aos clientes.

**Para E-commerce:**
```
North Star = Número de Pedidos Mensais × Ticket Médio × % Recompra
```

**No nosso caso:**
```
North Star Atual = 4.143 pedidos/mês × R$ 154 × 3,5% recompra
                 = R$ 22.336/mês em receita recorrente
```

**Meta Aspiracional:**
```
North Star Meta = 4.143 × R$ 154 × 15% recompra
                = R$ 95.704/mês (+329%)
```

---

## 📐 Técnicas Estatísticas {#tecnicas-estatisticas}

### **1. Testes de Hipótese**

Embora não aplicados extensivamente neste projeto, os conceitos orientam análises:

**Hipótese Nula (H0):**
- "Não há diferença entre grupos"

**Hipótese Alternativa (H1):**
- "Há diferença significativa"

**Nível de Significância:**
- α = 0,05 (5%)
- p-value < 0,05 = Rejeitar H0

**Exemplo Aplicado:**
```
H0: Atraso de entrega não afeta NPS
H1: Atraso de entrega afeta NPS negativamente

Resultado: r = -0,63, p < 0,001
Conclusão: Rejeitar H0. Atraso impacta NPS.
```

---

### **2. Segmentação por Percentis (NTILE)**

**Técnica:**
Dividir distribuição em N grupos de tamanho igual.

**Implementação:**
```sql
NTILE(5) OVER (ORDER BY metric)
```

**Uso no RFM:**
- Divide clientes em quintis (5 grupos)
- Score de 1 (pior) a 5 (melhor)
- Permite classificação simples e eficaz

---

### **3. Análise de Séries Temporais**

**Componentes Analisados:**

**Tendência (Trend):**
- Crescimento ou declínio de longo prazo
- Medido por MoM (Month-over-Month growth)

**Sazonalidade (Seasonality):**
- Padrões repetitivos (ex: pico em novembro - Black Friday)
- Identificado por análise mensal

**Ruído (Noise):**
- Variações aleatórias
- Filtrado por médias móveis

**Cálculo de Crescimento:**

```sql
MoM Growth % = ((Valor_Atual - Valor_Anterior) / Valor_Anterior) × 100
YoY Growth % = ((Valor_Atual - Valor_Ano_Passado) / Valor_Ano_Passado) × 100
```

---

## 🔧 Stack Tecnológico {#stack-tecnologico}

### **1. Linguagens e Frameworks**

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| **SQL** | - | Queries analíticas no BigQuery |
| **Python** | 3.9+ | Scripts ETL e análises |
| **Pandas** | 2.0+ | Manipulação de dados |
| **NumPy** | 1.24+ | Cálculos numéricos |
| **Matplotlib** | 3.7+ | Visualizações |
| **Seaborn** | 0.12+ | Visualizações estatísticas |

---

### **2. Infraestrutura de Dados**

**Google BigQuery:**
- Data Warehouse serverless
- Processamento massivamente paralelo
- SQL ANSI 2011 compatível
- Escalável até petabytes

**Vantagens:**
- ✅ Performance em queries analíticas
- ✅ Custo-benefício (free tier generoso)
- ✅ Integração com Looker Studio
- ✅ Sem gerenciamento de infraestrutura

---

### **3. Visualização**

**Looker Studio (Google Data Studio):**
- Dashboards interativos
- Conectado ao BigQuery
- Compartilhamento fácil
- Atualização automática

**Matplotlib/Seaborn:**
- Gráficos estáticos de alta qualidade
- Exportação para documentação

---

## 🔄 Processo ETL {#processo-etl}

### **Arquitetura ETL**

```
Kaggle (CSV)
     ↓
[EXTRACT]
     ↓
Python Script (pandas)
     ↓
[TRANSFORM]
  - Limpeza
  - Tipagem
  - Validação
     ↓
[LOAD]
     ↓
Google BigQuery
     ↓
[ANALYTICS]
     ↓
Dashboards
```

### **Etapas Detalhadas**

**1. Extract (Extração):**
```python
df = pd.read_csv('data/raw/olist_orders.csv')
```

**2. Transform (Transformação):**
```python
# Limpeza
df = df.dropna(subset=['order_id'])

# Tipagem
df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])

# Validação
assert df['order_id'].is_unique
```

**3. Load (Carga):**
```python
client = bigquery.Client()
job = client.load_table_from_dataframe(df, 'olist_ecommerce.orders')
```

**4. Validação Pós-Carga:**
```sql
SELECT COUNT(*) FROM olist_ecommerce.orders;
-- Verificar se count == expected
```

---

## 📊 Visualização de Dados {#visualizacao}

### **Princípios de Design**

Baseado em **Stephen Few** ("Information Dashboard Design"):

**1. Clareza sobre Decoração:**
- Remover elementos desnecessários
- Ratio tinta-dados alto

**2. Contexto Sempre:**
- Benchmarks
- Metas
- Período comparativo

**3. Hierarquia Visual:**
- Métricas principais em destaque
- Cores com propósito

**4. Interatividade Útil:**
- Filtros relevantes
- Drill-down quando necessário

### **Paleta de Cores**

```
Status:
🟢 Verde: Acima da meta
🟡 Amarelo: Atenção necessária
🔴 Vermelho: Crítico

Segmentos:
Champions: Azul escuro
Loyal: Azul claro
At Risk: Laranja
Lost: Vermelho
```

---

## 📚 Referências {#referencias}

### **Livros Fundamentais**

1. **HUGHES, Arthur M.** Strategic Database Marketing. 4th ed. McGraw-Hill, 2012.
   - Base teórica RFM

2. **GUPTA, Sunil; LEHMANN, Donald.** Managing Customers as Investments. Wharton School Publishing, 2005.
   - LTV e Customer Equity

3. **CROLL, Alistair; YOSKOVITZ, Benjamin.** Lean Analytics. O'Reilly Media, 2013.
   - Métricas para startups e e-commerce

4. **FEW, Stephen.** Information Dashboard Design. 2nd ed. Analytics Press, 2013.
   - Princípios de visualização

5. **KNAFLIC, Cole Nussbaumer.** Storytelling with Data. Wiley, 2015.
   - Narrativa com dados

6. **KAUSHIK, Avinash.** Web Analytics 2.0. Sybex, 2009.
   - Métricas de e-commerce

### **Papers Acadêmicos**

1. **FADER, Peter; HARDIE, Bruce.** "RFM and CLV: Using Iso-Value Curves for Customer Base Analysis." Journal of Marketing Research, 2005.

2. **REICHHELD, Frederick F.** "The One Number You Need to Grow." Harvard Business Review, 2003.
   - NPS (Net Promoter Score)

### **Documentação Técnica**

1. Google Cloud BigQuery Documentation
   - https://cloud.google.com/bigquery/docs

2. Pandas User Guide
   - https://pandas.pydata.org/docs/

3. Kaggle Dataset: Brazilian E-Commerce Public Dataset by Olist
   - https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

---

## 🔄 Evolução Metodológica

### **Limitações Reconhecidas**

1. **LTV Histórico vs Preditivo:**
   - Atualmente usamos LTV histórico
   - Futuro: Implementar modelos preditivos (Prophet, ARIMA)

2. **Segmentação Estática:**
   - RFM é snapshot no tempo
   - Futuro: Segmentação dinâmica com ML

3. **Causalidade:**
   - Análises são majoritariamente correlacionais
   - Futuro: Testes A/B para causalidade

### **Próximos Passos Metodológicos**

1. **Machine Learning:**
   - Predição de churn (Random Forest, XGBoost)
   - Recomendação de produtos (Collaborative Filtering)
   - Clusterização avançada (K-Means, DBSCAN)

2. **Análise Preditiva:**
   - Forecasting de vendas (Prophet)
   - Estimativa de LTV futuro (Pareto/NBD)

3. **Experimentação:**
   - Framework de testes A/B
   - Análise de impacto causal

---

## ✅ Validação das Metodologias

Todas as metodologias aplicadas neste projeto são:

- ✅ **Consolidadas:** Amplamente utilizadas na indústria
- ✅ **Documentadas:** Referências acadêmicas e práticas
- ✅ **Replicáveis:** Código e queries disponíveis
- ✅ **Validadas:** Resultados checados e consistentes
- ✅ **Acionáveis:** Geram insights implementáveis

---

**Última atualização:** Novembro 2024  
**Versão:** 1.0  
**Autor:** Andre Bomfim  
**Contato:** [GitHub](https://github.com/AndreBomfim99/analise23)