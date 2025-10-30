# 📊 Executive Summary: Olist E-Commerce Analytics

> **Análise Estratégica de 100k+ Pedidos | 2016-2018**  
> **Objetivo**: Identificar oportunidades de crescimento e otimização operacional

---

## 🎯 Contexto de Negócio

O Olist é uma plataforma de marketplace que conecta pequenos e médios varejistas a grandes canais de venda online. Este estudo analisa **99,441 pedidos** realizados entre **2016 e 2018**, totalizando **R$ 15.4 milhões em GMV**.

### KPIs Principais (Overview)

| Métrica | Valor | Benchmark |
|---------|-------|-----------|
| **GMV Total** | R$ 15.4M | - |
| **Ticket Médio** | R$ 154.00 | Mercado: R$ 180 |
| **LTV Médio** | R$ 154.00 | Target: R$ 200+ |
| **Taxa de Retenção M1** | 3.2% | Mercado: 8-12% |
| **NPS Médio** | 4.1/5.0 | Bom (>4.0) |
| **Clientes Únicos** | 96,096 | - |

---

## 💡 Top 10 Insights Estratégicos

### 1. 📍 **Concentração Geográfica Extrema**

**Achado**: São Paulo representa **42% do GMV total**, mas tem o **menor LTV per capita** (R$ 142).

**Análise**:
- SP tem alta volume, baixa fidelização
- Estados do Sul (RS, SC) têm LTV 18% maior
- Oportunidade: programas de fidelidade em SP

**Recomendação**:
```
✅ Implementar programa de cashback para SP
✅ Aumentar mix de produtos premium em SP
✅ Expandir operação em RS/SC (alta margem)
```

**Impacto Estimado**: +R$ 800k em LTV anual

---

### 2. 🔄 **Churn Crítico no 2º Mês**

**Achado**: Apenas **3.2% dos clientes** fazem uma segunda compra.

**Análise de Cohort (Primeiros 6 meses)**:
```
M0 → M1: 3.2%
M1 → M2: 12.8%
M2 → M3: 18.5%
```

✨ **Insight Oculto**: Clientes que passam do M1 têm 4x mais chance de virar recorrentes.

**Recomendação**:
```
✅ Email marketing agressivo em D+7 e D+15
✅ Cupom de 15% para segunda compra (ROI positivo)
✅ Remarketing focado em abandono de carrinho
```

**Impacto Estimado**: Aumentar retenção M0→M1 para 5% = +R$ 1.2M anual

---

### 3. 💎 **Segmentação RFM Revela Oportunidades**

**Distribuição de Clientes**:

| Segmento | % Clientes | % Receita | LTV Médio | Ação Recomendada |
|----------|------------|-----------|-----------|------------------|
| **Champions** | 8.2% | 38.4% | R$ 724 | Programa VIP exclusivo |
| **Loyal** | 12.1% | 28.6% | R$ 364 | Upsell de categorias premium |
| **Potential** | 15.3% | 18.2% | R$ 184 | Nurturing com conteúdo |
| **At Risk** | 18.4% | 10.8% | R$ 90 | Campanha de reativação |
| **Hibernating** | 46.0% | 4.0% | R$ 13 | Não investir (custo > retorno) |

**Recomendação**:
```
✅ Foco total em Champions + Loyal (67% da receita)
✅ Criar tier "Olist Black" para top 8%
✅ Win-back campaign para "At Risk" (ROI 3:1)
✅ Parar de enviar emails para "Hibernating" (economia)
```

**Impacto Estimado**: +R$ 2.1M em receita, -R$ 80k em custos de marketing

---

### 4. 📦 **Performance Desigual entre Categorias**

**Top 5 Categorias por Receita**:

1. **Beleza & Saúde** - R$ 1.8M (12%) | NPS: 4.3 ⭐ | Margem: Alta
2. **Relógios & Presentes** - R$ 1.6M (10%) | NPS: 4.1 | Margem: Média
3. **Cama, Mesa, Banho** - R$ 1.4M (9%) | NPS: 4.0 | Margem: Baixa
4. **Esporte & Lazer** - R$ 1.3M (8%) | NPS: 3.9 | Margem: Média
5. **Móveis & Decoração** - R$ 1.2M (8%) | NPS: 3.7 ⚠️ | Margem: Alta

**Insight**:
- **Beleza & Saúde** tem NPS mais alto, mas só 12% do mix
- **Móveis** tem margem alta, mas NPS baixo (logística)

**Recomendação**:
```
✅ Expandir catálogo de Beleza & Saúde (+30% SKUs)
✅ Melhorar logística de Móveis (parceria com frete dedicado)
✅ Cross-sell: Beleza → Relógios (complementares)
```

**Impacto Estimado**: +R$ 1.5M em GMV, +2 pontos no NPS

---

### 5. 🚚 **Logística é o Maior Driver de NPS**

**Correlação: Prazo de Entrega × NPS**

```
Entrega em até 10 dias:  NPS 4.5 ⭐⭐⭐⭐⭐
Entrega em 11-20 dias:   NPS 4.0 ⭐⭐⭐⭐
Entrega em 21+ dias:     NPS 2.7 ⭐⭐⭐ (crítico!)
```

**Achado**: 23% das entregas excedem 20 dias, gerando **68% das avaliações negativas**.

**Análise de Rota**:
- Rotas Norte/Nordeste: 45% de atraso
- Rotas Sul/Sudeste: 12% de atraso

**Recomendação**:
```
✅ Parcerias regionais para Norte/Nordeste
✅ SLA diferenciado por região (transparência)
✅ Compensação automática para atrasos >20 dias
```

**Impacto Estimado**: NPS de 4.1 → 4.5, redução de 40% em disputas

---

### 6. 💳 **Boleto Domina, mas Cartão Tem Maior LTV**

**Distribuição de Pagamento**:

| Método | % Pedidos | Ticket Médio | LTV 12M | Taxa Conversão |
|--------|-----------|--------------|---------|----------------|
| **Cartão de Crédito** | 76.8% | R$ 168 | R$ 189 | 94.2% |
| **Boleto** | 19.2% | R$ 98 | R$ 102 | 87.3% |
| **Débito** | 3.1% | R$ 112 | R$ 121 | 91.8% |
| **Voucher** | 0.9% | R$ 156 | R$ 178 | 95.1% |

**Insight**: Clientes de boleto têm **46% menos LTV**, mas representam 19% dos pedidos.

**Recomendação**:
```
✅ Incentivo de 5% desconto para trocar boleto → cartão
✅ Parcelamento agressivo (até 12x sem juros em categorias selecionadas)
✅ Programa de cashback exclusivo para cartão
```

**Impacto Estimado**: Migrar 30% dos clientes boleto = +R$ 450k LTV

---

### 7. 📈 **Sazonalidade Forte no Q4**

**Distribuição de GMV por Trimestre**:

```
Q1 2017: R$ 2.1M (14%)
Q2 2017: R$ 2.8M (18%)
Q3 2017: R$ 3.2M (21%)
Q4 2017: R$ 7.3M (47%) ← Black Friday + Natal
```

**Achado**: Q4 representa **quase metade da receita anual**.

**Recomendação**:
```
✅ Estoque estratégico 60 dias antes de Nov/Dez
✅ Campanhas de antecipação (Early Black Friday)
✅ Plano de contingência logístico para Q4
```

**Impacto Estimado**: Evitar stockout = +R$ 800k em Q4

---

### 8. ⭐ **Reviews Positivos = 3x Mais Vendas**

**Análise de Review Score**:

```
Produtos com 5 estrelas: 8.2x mais pedidos que média
Produtos com 4 estrelas: 3.1x mais pedidos
Produtos com <3 estrelas: 0.4x (praticamente mortos)
```

**Achado**: 12% dos SKUs têm review <3, mas ocupam espaço em estoque.

**Recomendação**:
```
✅ Deslistar produtos com <3 estrelas após 50 reviews
✅ Incentivo para review (cupom R$ 5 para próxima compra)
✅ Programa "Seller Excellence" (penaliza low NPS)
```

**Impacto Estimado**: +15% conversão, -R$ 200k em dead stock

---

### 9. 🎯 **80/20 Extremo: 5% dos Sellers = 60% GMV**

**Distribuição de Sellers**:

| Tier | % Sellers | % GMV | Ticket Médio |
|------|-----------|-------|--------------|
| **Top 5%** | 5% | 61.2% | R$ 284 |
| **Mid 25%** | 25% | 32.4% | R$ 142 |
| **Long Tail** | 70% | 6.4% | R$ 87 |

**Insight**: Dependência excessiva de poucos sellers = risco operacional.

**Recomendação**:
```
✅ Programa de aceleração para "Mid Tier"
✅ Account management dedicado para Top 5%
✅ Diversificar: trazer 50+ sellers Mid Tier
```

**Impacto Estimado**: Reduzir risco de concentração, +R$ 1M em GMV

---

### 10. 🔍 **Dados Ausentes em 8% dos Pedidos**

**Problemas de Qualidade de Dados**:

```
- 8.2% pedidos sem lat/long do cliente
- 3.1% pedidos sem categoria de produto
- 1.4% pedidos sem review (>90 dias)
```

**Impacto**: Impossível fazer análises precisas de geolocalização e performance de categoria.

**Recomendação**:
```
✅ Obrigar preenchimento de geolocalização no cadastro
✅ Validação de categoria no onboarding de seller
✅ Incentivo para review (auto-email D+7, D+15, D+30)
```

**Impacto Estimado**: Melhorar acurácia de análises em 40%

---

## 🎯 Priorização de Ações (Framework ICE)

| Ação | Impact | Confidence | Ease | Score | Prioridade |
|------|--------|-----------|------|-------|------------|
| Win-back "At Risk" | 9 | 8 | 9 | **8.7** | 🔥 P0 |
| Melhorar logística N/NE | 10 | 7 | 5 | **7.3** | 🔥 P0 |
| Programa fidelidade SP | 8 | 8 | 7 | **7.7** | 🔥 P0 |
| Expandir Beleza & Saúde | 7 | 9 | 8 | **8.0** | 🔥 P0 |
| Parcelamento 12x | 6 | 9 | 9 | **8.0** | 🚀 P1 |
| Programa review | 5 | 8 | 9 | **7.3** | 🚀 P1 |
| Tier "Olist Black" | 8 | 6 | 4 | **6.0** | 📋 P2 |
| Seller acceleration | 6 | 5 | 5 | **5.3** | 📋 P2 |

---

## 💰 Impacto Financeiro Estimado (12 meses)

```
Receita Incremental:
+ R$ 2.1M  (RFM + Segmentação)
+ R$ 1.5M  (Expansão Beleza & Saúde)
+ R$ 1.2M  (Aumento Retenção M1)
+ R$ 0.8M  (Otimização Q4)
+ R$ 1.0M  (Diversificação Sellers)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
= R$ 6.6M  Total Incremental

Redução de Custos:
- R$ 80k   (Otimização Marketing)
- R$ 200k  (Redução Dead Stock)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
= R$ 280k  Economia

IMPACTO TOTAL: R$ 6.88M (+44% vs baseline)
```

---

## 📊 Dashboards de Acompanhamento

Para monitorar a execução das ações, foram criados 5 dashboards no Looker Studio:

1. **Executive Dashboard** - KPIs principais
2. **Customer Health Score** - RFM + Cohort em tempo real
3. **Logistics Monitor** - SLA por rota
4. **Category Performance** - GMV + NPS por categoria
5. **Seller Dashboard** - Performance individual

👉 [Acesse os Dashboards](dashboards/looker_studio_links.md)

---

## 🚀 Roadmap de Execução (90 dias)

### Sprint 1 (Dias 1-30): Quick Wins
- [ ] Implementar campanha win-back "At Risk"
- [ ] Lançar parcelamento 12x em categorias selecionadas
- [ ] Criar programa de review com incentivo

### Sprint 2 (Dias 31-60): Melhorias Operacionais
- [ ] Parcerias logísticas Norte/Nordeste
- [ ] Expansão de 30% no catálogo Beleza & Saúde
- [ ] Sistema de compensação automática por atraso

### Sprint 3 (Dias 61-90): Estratégico
- [ ] Programa de fidelidade SP (piloto)
- [ ] Tier "Olist Black" para top 8%
- [ ] Seller acceleration program

---

## 📈 Métricas de Sucesso (OKRs Q1 2026)

**Objetivo 1**: Aumentar LTV dos clientes

- KR1: LTV médio de R$ 154 → R$ 185 (+20%)
- KR2: Taxa de retenção M1 de 3.2% → 5.0% (+56%)
- KR3: % clientes "Champions" de 8% → 12% (+50%)

**Objetivo 2**: Melhorar experiência do cliente

- KR1: NPS de 4.1 → 4.5 (+10%)
- KR2: % entregas <15 dias de 77% → 90% (+17%)
- KR3: Taxa de review de 58% → 75% (+29%)

**Objetivo 3**: Otimizar mix de produtos

- KR1: GMV Beleza & Saúde de 12% → 18% (+50%)
- KR2: Deslistar 100% SKUs com <3 estrelas
- KR3: Expandir top sellers de 5% → 10% do GMV

---

## 🔍 Metodologia Aplicada

Este estudo utilizou:

- **SQL Avançado**: Window Functions, CTEs recursivas, análises temporais
- **Python**: Análises estatísticas, segmentação RFM, modelagem
- **BigQuery**: Processamento de 100k+ linhas em escala
- **Looker Studio**: Visualização interativa e dashboards executivos
- **Statistical Analysis**: Testes de hipótese, correlações, análise de cohort

---

## 👤 Sobre o Analista

**Perfil**: Business Analyst com foco em estratégia data-driven para e-commerce e marketplaces.

**Competências Demonstradas**:
- ✅ SQL Avançado (Window Functions, CTEs complexas)
- ✅ Python para Analytics (pandas, scikit-learn)
- ✅ Cloud Data Warehouse (Google BigQuery)
- ✅ Business Intelligence (Looker Studio)
- ✅ Storytelling com Dados
- ✅ Pensamento Estratégico

---

## 📞 Contato

Para discussão detalhada dos insights ou oportunidades de colaboração:

- **GitHub**: [@AndreBomfim99](https://github.com/AndreBomfim99)
- **Email**: andre.bomfim99@gmail.com
- **LinkedIn**: https://www.linkedin.com/in/andre-bomfim/

---

**Última Atualização**: Outubro 2025  
**Versão**: 1.0