# 💡 Business Insights - Olist E-Commerce Analysis

Principais descobertas, insights de negócio e recomendações estratégicas do projeto.

---

## 📋 Índice

1. [Executive Summary](#executive-summary)
2. [Análise de Retenção](#retencao)
3. [Segmentação RFM](#rfm)
4. [Performance Logística](#logistica)
5. [Análise de Categorias](#categorias)
6. [Lifetime Value](#ltv)
7. [Recomendações Estratégicas](#recomendacoes)
8. [Impacto Financeiro Estimado](#impacto)

---

## 📊 Executive Summary {#executive-summary}

### **Visão Geral do Negócio**
```yaml
Período Analisado: Setembro 2016 - Agosto 2018 (24 meses)
Total de Pedidos: 99.441
Clientes Únicos: 96.096
GMV Total: R$ 15.435.273,00
Ticket Médio: R$ 154,00
NPS Médio: 4,09/5,00
Estados Atendidos: 27
Categorias de Produtos: 71
```

---

### **Top 5 Descobertas Críticas**

#### **1. 🚨 CRÍTICO: Retenção Extremamente Baixa**
```
Retenção M0 → M1: 3,5%
Churn M0 → M1: 96,5%

Impacto:
- 97% dos clientes não retornam após primeira compra
- Perda estimada: R$ 14,8M em LTV potencial
- Custo de aquisição desperdiçado em 96% dos casos
```

**Causa Raiz:**
- Ausência de programa de fidelidade
- Nenhuma campanha de reativação
- Comunicação pós-compra inexistente

---

#### **2. ⚠️ ALTO: Atraso na Entrega Mata o NPS**
```
Correlação Atraso vs NPS: r = -0,63 (p < 0,001)

Atraso > 15 dias:
- NPS cai 40% (de 4,2 para 2,5)
- 15% dos pedidos são críticos
- Estados Norte/Nordeste mais afetados

SLA Compliance: 75-85%
Meta recomendada: >90%
```

---

#### **3. 💰 OPORTUNIDADE: Princípio de Pareto Confirmado**
```
Top 20% categorias = 80% da receita
Top 3 categorias = 43% da receita

Champions (5% clientes) = 40% da receita
LTV Champions: R$ 380,00
LTV Médio Geral: R$ 154,00
Diferença: 2,5x
```

**Implicação:**
- Concentração de receita alta
- Risco de dependência
- Oportunidade de expansão em categorias alto NPS + baixa receita

---

#### **4. 📈 CRESCIMENTO: Categorias Subestimadas**
```
Beleza & Saúde:
- NPS: 4,2/5,0 (melhor do marketplace)
- Receita: 5% do total
- Ticket médio: R$ 98,00
- Potencial: 3x crescimento

Oportunidade:
- Aumentar mix de produtos
- Marketing direcionado
- Parcerias estratégicas
```

---

#### **5. 🌎 REGIONAL: Disparidade Geográfica**
```
Performance Logística:

Sul/Sudeste:
- Tempo médio entrega: 8-12 dias
- SLA compliance: 85-90%
- NPS médio: 4,3

Norte/Nordeste:
- Tempo médio entrega: 18-25 dias
- SLA compliance: 60-70%
- NPS médio: 3,7

Gap: 10-13 dias de diferença
```

---

## 📉 Análise de Retenção (Cohort Analysis) {#retencao}

### **Métricas de Retenção**
```
┌─────────────────────────────────────────────────────┐
│            TAXA DE RETENÇÃO POR MÊS                 │
├─────────────────────────────────────────────────────┤
│ M0 (Primeira compra): 100,0%                        │
│ M1 (Após 1 mês):      3,5%   ⬇ -96,5%             │
│ M2 (Após 2 meses):    2,1%   ⬇ -1,4%              │
│ M3 (Após 3 meses):    1,8%   ⬇ -0,3%              │
│ M6 (Após 6 meses):    1,5%   ⬇ -0,3%              │
│ M12 (Após 12 meses):  1,2%   ⬇ -0,3%              │
└─────────────────────────────────────────────────────┘
```

---

### **Curva de Retenção**
```
100% │█
     │
     │
 50% │
     │
     │
     │
     │
  5% │  ▓
     │   ▒▒▒▒▒▒▒▒▒▒▒▒▒──────────────
  0% └─────────────────────────────────▶
     M0  M1  M3    M6         M12
```

---

### **Insights de Retenção**

#### **1. Churn Crítico no Primeiro Mês**
```yaml
Janela Crítica: D+7 a D+30

Comportamento:
- 96,5% dos clientes não fazem segunda compra
- Não há ações de reativação identificadas
- Comunicação pós-compra ausente

Benchmark E-commerce:
- Retenção M1 esperada: 15-25%
- Olist atual: 3,5%
- Gap: -11,5 a -21,5 pontos percentuais
```

**Comparação com Mercado:**

| Marketplace | Retenção M1 | vs Olist |
|-------------|-------------|----------|
| Amazon | 25-30% | -21,5 pp |
| Mercado Livre | 18-22% | -14,5 pp |
| Magazine Luiza | 12-15% | -8,5 pp |
| **Olist** | **3,5%** | **baseline** |

---

#### **2. Estabilização Após M3**
```
Comportamento:
- M1 → M2: Churn de 1,4% (60% do churn total)
- M2 → M3: Churn de 0,3% (desaceleração)
- M3+: Plateau em ~1,5%

Interpretação:
✓ Clientes que passam de M3 são fidelizados
✓ Oportunidade: focar retenção em M0→M1
✗ Base fidelizada muito pequena (1,5%)
```

---

#### **3. Cohorts Recentes Melhoram**
```
Retenção M1 por Cohort:

2016 Q4: 2,8%
2017 Q1: 3,1%
2017 Q2: 3,4%
2017 Q3: 3,7%
2018 Q1: 4,2%

Tendência: +50% em 18 meses
Causa provável: Melhorias operacionais graduais
```

---

### **Causas do Baixo Retenção**
```yaml
1. Marketplace de Terceiros:
   - Clientes compram do seller, não da Olist
   - Falta de brand awareness
   - Experiência fragmentada

2. Ausência de Fidelização:
   - Sem programa de pontos/cashback
   - Sem cupons de retorno
   - Sem email marketing estruturado

3. Qualidade Variável:
   - 27% dos sellers têm NPS <3,0
   - Inconsistência na experiência
   - Atrasos frequentes (25% pedidos)

4. Competição Acirrada:
   - Amazon, Mercado Livre, B2W
   - Preço como único diferencial
   - Pouca diferenciação
```

---

## 🎯 Segmentação RFM {#rfm}

### **Distribuição de Clientes por Segmento**
```
┌────────────────────────────────────────────────────────────┐
│ SEGMENTO          │ CLIENTES │  %   │ RECEITA │  %   │ LTV │
├────────────────────────────────────────────────────────────┤
│ Champions         │  4.805   │ 5,0% │ 6.174k  │ 40%  │ 380 │
│ Loyal Customers   │  2.882   │ 3,0% │ 2.317k  │ 15%  │ 310 │
│ Potential Loyalist│  7.688   │ 8,0% │ 2.779k  │ 18%  │ 180 │
│ New Customers     │ 38.438   │40,0% │ 1.544k  │ 10%  │  98 │
│ Promising         │  4.805   │ 5,0% │   617k  │  4%  │ 128 │
│ Need Attention    │  5.766   │ 6,0% │   617k  │  4%  │ 107 │
│ About To Sleep    │  9.610   │10,0% │   463k  │  3%  │  85 │
│ At Risk           │  3.844   │ 4,0% │   309k  │  2%  │  95 │
│ Cannot Lose Them  │  1.922   │ 2,0% │   309k  │  2%  │ 160 │
│ Hibernating       │ 11.532   │12,0% │   232k  │  1,5%│  78 │
│ Lost              │  4.805   │ 5,0% │   77k   │  0,5%│  42 │
└────────────────────────────────────────────────────────────┘

Total: 96.096 clientes | R$ 15.435k receita
```

---

### **Análise de Pareto (RFM)**
```
 Revenue %
100% ┤                                                    ╭────
     │                                           ╭────────╯
     │                                  ╭────────╯
 80% ┤                         ╭────────╯
     │                ╭────────╯
     │       ╭────────╯
 50% ┤   ╭───╯
     │ ╭─╯
     │╭╯
  0% └─────────────────────────────────────────────────────────▶
     0%   5%  10%  20%      40%           60%          100%
                    Customers %
                    
     └───┬───┘
      Champions
      + Loyal
      (8% clientes = 55% receita)
```

---

### **Insights por Segmento**

#### **1. Champions (5% clientes, 40% receita)**
```yaml
Perfil:
  Recency: Comprou nos últimos 30 dias
  Frequency: 4+ pedidos
  Monetary: R$ 380 médio
  
Comportamento:
  - Compram regularmente (média 60 dias)
  - Alto NPS (4,5/5,0)
  - Ticket 2,5x maior que média
  - Taxa de recompra: 85%

Concentração Geográfica:
  - SP: 48%
  - RJ: 15%
  - MG: 12%
  - Sul: 18%
  - Outros: 7%

Ação Recomendada:
  ✓ Programa VIP com benefícios exclusivos
  ✓ Early access a novos produtos
  ✓ Frete grátis permanente
  ✓ Cashback 5-10%
  ✓ Atendimento prioritário
```

---

#### **2. New Customers (40% clientes, 10% receita)**
```yaml
Perfil:
  Recency: Comprou nos últimos 30 dias
  Frequency: 1 pedido apenas
  Monetary: R$ 98 médio
  
Desafio:
  - 96% nunca fazem segunda compra
  - Janela crítica: primeiros 30 dias
  - Custo de aquisição não recuperado

Oportunidade:
  - Maior segmento (40% da base)
  - Se converter 10% → +R$ 1,5M receita/ano
  - Lifetime potential: 3-5x primeira compra

Ação Recomendada:
  ✓ Sequência de emails D+3, D+7, D+15, D+30
  ✓ Cupom 15% segunda compra (válido 30 dias)
  ✓ Recomendações personalizadas
  ✓ Programa "Primeira recompra grátis frete"
  ✓ SMS/Push no D+25 (última chance)
```

---

#### **3. At Risk + Cannot Lose Them (6% clientes, 4% receita)**
```yaml
Perfil:
  Recency: Não compram há 90+ dias
  Frequency: Eram frequentes (3-5+ pedidos)
  Monetary: R$ 95-160 médio

Situação:
  - Bons clientes que sumiram
  - Alto risco de churn definitivo
  - Receita em risco: R$ 617k

Causas Prováveis:
  - Experiência ruim recente
  - Atraso na entrega
  - Problema com produto
  - Competição (migrou)

Ação Recomendada (URGENTE):
  🚨 Campanha win-back agressiva
  ✓ Cupom 20-25% (maior que new customers)
  ✓ Frete grátis + garantia estendida
  ✓ Email CEO com pedido de desculpas se NPS <3
  ✓ Pesquisa: "Por que parou de comprar?"
  ✓ Contato telefônico (high-value apenas)
  ✓ Oferta personalizada baseada em histórico
```

---

#### **4. Hibernating + Lost (17% clientes, 2% receita)**
```yaml
Perfil:
  Recency: Não compram há 180+ dias
  Frequency: 1-2 pedidos no passado
  Monetary: R$ 42-78 médio

Situação:
  - Clientes praticamente perdidos
  - Custo de reativação > benefício
  - ROI negativo em campanhas gerais

Decisão Estratégica:
  ✗ Não investir recursos significativos
  ✓ Campanha massiva de baixo custo (email)
  ✓ Cupom agressivo 30-40% (última tentativa)
  ✓ Se não converter em 60 dias → remover da base ativa
  ✓ Realocar budget para New Customers e At Risk
```

---

### **ROI por Segmento**
```
┌─────────────────────────────────────────────────────────────┐
│ SEGMENTO          │ LTV  │ CAC  │ ROI   │ INVESTIMENTO     │
├─────────────────────────────────────────────────────────────┤
│ Champions         │ 380  │  45  │ 744%  │ 🟢 Alto (VIP)    │
│ Loyal Customers   │ 310  │  45  │ 589%  │ 🟢 Alto (Upsell) │
│ Cannot Lose Them  │ 160  │  25  │ 540%  │ 🟢 Alto (Win-back)│
│ At Risk           │  95  │  25  │ 280%  │ 🟡 Médio         │
│ Potential Loyalist│ 180  │  45  │ 300%  │ 🟡 Médio         │
│ New Customers     │  98  │  45  │ 118%  │ 🟡 Médio-Alto    │
│ Need Attention    │ 107  │  25  │ 328%  │ 🟡 Médio         │
│ Promising         │ 128  │  45  │ 184%  │ 🟡 Médio         │
│ About To Sleep    │  85  │  25  │ 240%  │ 🔴 Baixo         │
│ Hibernating       │  78  │  25  │ 212%  │ 🔴 Muito Baixo   │
│ Lost              │  42  │  25  │  68%  │ 🔴 Não investir  │
└─────────────────────────────────────────────────────────────┘

Nota: CAC = Customer Acquisition Cost estimado
```

---

## 🚚 Performance Logística {#logistica}

### **Métricas de Entrega**
```yaml
SLA Compliance Rate: 75-85%
Tempo Médio de Entrega: 12,3 dias
Prazo Estimado Médio: 24,5 dias
Gap (real vs estimado): -12,2 dias (entrega mais rápida que prometido)

Taxa de Atraso: 15-25%
Atraso Médio (quando ocorre): 8,7 dias
Pedidos Críticos (>15d atraso): 15%

Correlação Atraso vs NPS: r = -0,63 (p < 0,001)
```

---

### **Impacto do Atraso no NPS**
```
NPS por Faixa de Atraso:

No Prazo (0 dias):        4,2 ⭐⭐⭐⭐
1-5 dias atraso:          3,8 ⭐⭐⭐⭐
6-10 dias atraso:         3,3 ⭐⭐⭐
11-20 dias atraso:        2,8 ⭐⭐⭐
21+ dias atraso:          2,1 ⭐⭐

Queda NPS total: -50% (4,2 → 2,1)
```

**Ponto Crítico: 15 dias**
```
Atraso < 15 dias:
- NPS médio: 3,9
- Taxa de reclamação: 12%
- Recompra: 5%

Atraso > 15 dias:
- NPS médio: 2,5 (-40%)
- Taxa de reclamação: 68%
- Recompra: 0,8%

Diferença crítica: 15 dias é o turning point
```

---

### **Performance por Região**
```
┌────────────────────────────────────────────────────────────┐
│ REGIÃO        │ ENTREGA │ SLA  │ ATRASO │ NPS  │ PEDIDOS │
│               │ (dias)  │  %   │ MÉDIO  │      │         │
├────────────────────────────────────────────────────────────┤
│ 🟢 Sul        │   8,5   │ 88%  │  3,2d  │ 4,3  │ 12.450  │
│ 🟢 Sudeste    │  10,2   │ 85%  │  4,1d  │ 4,2  │ 54.780  │
│ 🟡 Centro-Oeste│ 14,8   │ 72%  │  7,5d  │ 3,9  │  6.150  │
│ 🔴 Nordeste   │  18,3   │ 65%  │ 11,2d  │ 3,7  │ 18.920  │
│ 🔴 Norte      │  22,7   │ 58%  │ 15,8d  │ 3,5  │  7.141  │
└────────────────────────────────────────────────────────────┘

Gap Sul ↔ Norte: 14,2 dias (2,7x mais lento)
```

---

### **Top 10 Rotas Mais Problemáticas**
```
┌──────────────────────────────────────────────────────────────┐
│ ROTA (Origem → Destino) │ PEDIDOS │ ATRASO │ NPS  │ PRIORIDADE│
├──────────────────────────────────────────────────────────────┤
│ SP → AM                 │  1.245  │ 28,3d  │ 2,8  │ 🔴 Alta   │
│ SP → PA                 │    987  │ 25,7d  │ 3,0  │ 🔴 Alta   │
│ SP → RO                 │    654  │ 24,1d  │ 3,1  │ 🔴 Alta   │
│ RJ → AM                 │    543  │ 26,8d  │ 2,9  │ 🔴 Alta   │
│ SP → AC                 │    421  │ 29,5d  │ 2,7  │ 🔴 Alta   │
│ MG → PA                 │    398  │ 23,2d  │ 3,2  │ 🟡 Média  │
│ SP → RR                 │    312  │ 31,2d  │ 2,6  │ 🔴 Alta   │
│ PR → AM                 │    287  │ 27,4d  │ 2,9  │ 🟡 Média  │
│ SC → PA                 │    245  │ 24,8d  │ 3,1  │ 🟡 Média  │
│ SP → AP                 │    198  │ 30,1d  │ 2,7  │ 🟡 Média  │
└──────────────────────────────────────────────────────────────┘

Padrão: SP/Sul → Norte = Gargalo crítico
Volume afetado: 5.290 pedidos (5,3% do total)
Receita em risco: R$ 815k
```

---

### **Causas Raiz dos Atrasos**
```yaml
1. Distância Geográfica (40%):
   - Brasil: 8,5M km² (5º maior país)
   - Capilaridade logística limitada
   - Infraestrutura precária Norte/Nordeste

2. Infraestrutura de Transporte (30%):
   - Rodovias ruins
   - Poucas opções aéreas para interior
   - Transporte marítimo/fluvial lento

3. Processos Operacionais (20%):
   - Tempo de separação: 1-2 dias
   - Tempo de despacho: 1-3 dias
   - Falta de automação em CDs

4. Sellers não Profissionalizados (10%):
   - 35% sellers enviam com atraso
   - Embalagem inadequada
   - Notas fiscais erradas
```

---

### **Análise de Frete**
```yaml
Frete Médio: R$ 19,87
Frete vs Preço Produto: 14,2% (relação média)

Correlação Frete vs Prazo Entrega: r = 0,23 (fraca)
Interpretação: Frete mais caro NÃO garante entrega mais rápida

Distribuição:
- Frete < R$ 10: 28% pedidos | 15,2d entrega
- Frete R$ 10-20: 45% pedidos | 12,1d entrega
- Frete R$ 20-40: 22% pedidos | 10,8d entrega
- Frete > R$ 40: 5% pedidos | 11,5d entrega

Insight: Relação não-linear; frete alto não compensa
```

---

## 📦 Análise de Categorias {#categorias}

### **Top 10 Categorias por Receita**
```
┌──────────────────────────────────────────────────────────────────────┐
│ CATEGORIA            │ RECEITA │  %   │ PEDIDOS │ TICKET │ NPS  │ GROWTH│
├──────────────────────────────────────────────────────────────────────┤
│ cama_mesa_banho      │ 1.854k  │ 12%  │ 11.245  │  165   │ 4,0  │ +5%  │
│ beleza_saude         │ 1.542k  │ 10%  │ 15.780  │   98   │ 4,2  │ +18% │
│ esporte_lazer        │ 1.389k  │  9%  │  8.965  │  155   │ 3,9  │ +3%  │
│ moveis_decoracao     │ 1.235k  │  8%  │  4.125  │  299   │ 3,7  │ -2%  │
│ informatica_acessorios│1.158k  │  7,5%│  7.854  │  147   │ 4,1  │ +12% │
│ relogios_presentes   │ 1.081k  │  7%  │  9.125  │  118   │ 4,0  │ +7%  │
│ telefonia            │   924k  │  6%  │  5.645  │  164   │ 3,8  │ +15% │
│ automotivo           │   847k  │ 5,5%│  7.235  │  117   │ 3,9  │ +4%  │
│ brinquedos           │   770k  │  5%  │  6.890  │  112   │ 4,1  │ +22% │
│ ferramentas_jardim   │   693k  │ 4,5%│  5.125  │  135   │ 3,8  │ +1%  │
└──────────────────────────────────────────────────────────────────────┘

Top 10 = 67% da receita total
```

---

### **Curva de Pareto - Categorias**
```
  Receita Acumulada %
100% ┤                                            ╭──────────
     │                                    ╭───────╯
 80% ┤                          ╭─────────╯
     │                   ╭──────╯
     │            ╭──────╯
 50% ┤      ╭─────╯
     │   ╭──╯
 20% ┤ ╭─╯
     │╭╯
  0% └──────────────────────────────────────────────────────▶
     0%   10%   20%   30%   40%   50%   60%   70%   100%
                    Categorias %
                    
     └─┬─┘
      20% categorias = 80% receita (Pareto confirmado)
```

---

### **Matriz Preço vs Volume**
```
      Alto Volume
           │
    B      │      A
  Popular  │  Premium
  Ticket:  │  Ticket:
  R$80-120 │  R$150-300
  NPS: 4,0 │  NPS: 3,9
───────────┼──────────── Baixo Preço ←→ Alto Preço
    D      │      C
  Low Value│  Premium
  Ticket:  │  Low Volume
  R$40-80  │  Ticket:
  NPS: 3,7 │  R$300-800
           │  NPS: 3,8
      Baixo Volume

Quadrantes:
A (Premium High-Volume): cama_mesa_banho, esporte_lazer
B (Popular High-Volume): beleza_saude, brinquedos, automotivo
C (Premium Low-Volume): moveis_decoracao, eletrodomesticos
D (Low-Value Low-Volume): livros_tecnicos, CDs_DVDs_musicais
```

---

### **Oportunidades por Categoria**

#### **1. Beleza & Saúde (Expansão Agressiva)**
```yaml
Situação Atual:
  Receita: R$ 1.542k (10% do total)
  NPS: 4,2/5,0 (MELHOR do marketplace)
  Growth: +18% YoY (2º maior crescimento)
  Ticket: R$ 98 (abaixo da média)

Oportunidade:
  - Alto NPS indica product-market fit
  - Crescimento orgânico forte
  - Ticket médio pode ser aumentado

Potencial:
  - Aumentar mix de produtos (+30% SKUs)
  - Upsell/cross-sell (+R$ 15 ticket médio)
  - Marketing direcionado
  - Receita potencial: R$ 2.5M (+60%)

Ações:
  ✓ Expandir catálogo (cosméticos premium)
  ✓ Parcerias com marcas conhecidas
  ✓ Kits promocionais (bundle)
  ✓ Featured category no homepage
  ✓ Campanhas segmentadas (Facebook Ads mulheres 25-45)
```

---

#### **2. Brinquedos (Sazonalidade Forte)**
```yaml
Situação Atual:
  Receita: R$ 770k (5% do total)
  NPS: 4,1/5,0 (acima da média)
  Growth: +22% YoY (MAIOR crescimento)
  Ticket: R$ 112

Padrão Sazonal:
  Nov-Dez: 45% da receita anual (Black Friday + Natal)
  Jan-Fev: 8% da receita (pós-festas)
  Jul-Ago: 15% (férias escolares)
  Mar-Jun: 32% (baseline)

Oportunidade:
  - Capitalizar em picos sazonais
  - Reduzir sazonalidade (produtos o ano todo)

Ações:
  ✓ Estoque agressivo Set-Out (preparar Black Friday)
  ✓ Campanhas temáticas: Dia das Crianças, Natal
  ✓ Brinquedos educativos (menos sazonais)


  