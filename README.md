# 🛒 E-Commerce Olist: Advanced Analytics & Business Intelligence

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![BigQuery](https://img.shields.io/badge/Google-BigQuery-yellow.svg)](https://cloud.google.com/bigquery)
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Análise avançada de dados de e-commerce brasileiro utilizando SQL, Python, BigQuery e Looker Studio**

📊 [Ver Dashboards](dashboards/looker_studio_links.md) | 📑 [Executive Summary](EXECUTIVE_SUMMARY.md) | 🏗️ [Arquitetura](docs/architecture.md)

---

## 📋 Sobre o Projeto

Este projeto apresenta uma análise completa e profissional do dataset **Brazilian E-Commerce Public Dataset by Olist**, demonstrando habilidades avançadas em:

- **SQL Avançado**: CTEs complexas, Window Functions, análises temporais
- **Engenharia de Dados**: Pipeline de ETL com Docker e Google BigQuery
- **Business Analytics**: LTV, Cohort Analysis, RFM Segmentation, Forecasting
- **Visualização de Dados**: Dashboards interativos em Looker Studio
- **Best Practices**: Código documentado, testes, reprodutibilidade

### 🎯 Objetivo de Negócio

Responder perguntas estratégicas críticas para um e-commerce:
- Qual o **Lifetime Value (LTV)** dos clientes por região?
- Como está a **retenção de clientes** ao longo do tempo?
- Quais **segmentos de clientes** são mais valiosos?
- Qual a **performance por categoria** de produto?
- Onde estão as **oportunidades de crescimento**?

---

## 🗂️ Estrutura do Dataset

**Fonte**: [Kaggle - Olist Brazilian E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

O dataset contém **100k pedidos** de 2016 a 2018 feitos em múltiplos marketplaces no Brasil.

**Tabelas Principais**:
- `olist_orders_dataset` - Pedidos e status
- `olist_order_items_dataset` - Itens dos pedidos
- `olist_customers_dataset` - Dados dos clientes
- `olist_products_dataset` - Catálogo de produtos
- `olist_order_reviews_dataset` - Avaliações e reviews
- `olist_order_payments_dataset` - Dados de pagamento
- `olist_sellers_dataset` - Vendedores
- `olist_geolocation_dataset` - Geolocalização

---

## 🏗️ Arquitetura do Projeto

```
┌─────────────────┐
│  Kaggle Dataset │
│   (CSV Files)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Docker          │
│  + Python ETL   │ ◄─── Data Validation & Transformation
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Google BigQuery │ ◄─── Advanced SQL Analytics
│  Data Warehouse │      • LTV Calculation
└────────┬────────┘      • Cohort Analysis
         │               • RFM Segmentation
         │               • Time Series Analysis
         ▼
┌─────────────────┐
│ Looker Studio   │ ◄─── Interactive Dashboards
│   Dashboards    │
└─────────────────┘
```

---

## 🚀 Quick Start

### Pré-requisitos

- Docker & Docker Compose instalados
- Conta Google Cloud (free tier suficiente)
- Git
- Python 3.11+ (opcional, Docker já inclui)

### 1️⃣ Clone o Repositório

```bash
git clone https://github.com/seu-usuario/ecommerce-olist-analysis.git
cd ecommerce-olist-analysis
```

### 2️⃣ Download do Dataset

```bash
# Baixe o dataset do Kaggle e extraia em data/raw/
# https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
```

### 3️⃣ Configure Variáveis de Ambiente

```bash
# Copie o template
cp .env.example .env

# Edite .env com suas credenciais do Google Cloud
# GCP_PROJECT_ID=seu-projeto
# GCP_DATASET_ID=olist_ecommerce
# GOOGLE_APPLICATION_CREDENTIALS=./keys/gcp-key.json
```

### 4️⃣ Suba o Ambiente Docker

```bash
docker-compose up -d
```

### 5️⃣ Execute o Pipeline de ETL

```bash
# Carregar dados para BigQuery
docker exec -it ecommerce-python python python/etl/load_to_bigquery.py

# Validar qualidade dos dados
docker exec -it ecommerce-python python python/etl/data_validation.py
```

### 6️⃣ Acesse os Notebooks

```bash
# Jupyter Lab estará disponível em:
http://localhost:8888
```

---

## 📊 Análises Realizadas

### 1. **Customer Lifetime Value (LTV) por Estado**
- Cálculo de LTV médio, mediano e por percentil
- Análise geográfica de clientes mais valiosos
- Identificação de estados com maior potencial

**Arquivo**: [`sql/03_analytics/ltv_analysis.sql`](sql/03_analytics/ltv_analysis.sql)

### 2. **Cohort Retention Analysis**
- Análise de retenção mês a mês
- Identificação de padrões de churn
- Segmentação por canal de aquisição

**Arquivo**: [`sql/03_analytics/cohort_retention.sql`](sql/03_analytics/cohort_retention.sql)

### 3. **RFM Segmentation (Recência, Frequência, Valor)**
- Segmentação automática de clientes
- Identificação de "Champions", "At Risk", "Hibernating"
- Recomendações de estratégias por segmento

**Arquivo**: [`python/analytics/rfm_segmentation.py`](python/analytics/rfm_segmentation.py)

### 4. **Product Category Performance**
- Análise de receita por categoria
- Ticket médio e margem por produto
- Sazonalidade de vendas

**Arquivo**: [`sql/03_analytics/category_performance.sql`](sql/03_analytics/category_performance.sql)

### 5. **Delivery & Logistics Analysis**
- Análise de SLA de entrega
- Correlação entre prazo e NPS
- Identificação de gargalos logísticos

**Arquivo**: [`notebooks/05_delivery_analysis.ipynb`](notebooks/05_delivery_analysis.ipynb)

---

## 🎨 Dashboards Interativos

Todos os dashboards estão disponíveis publicamente no **Looker Studio**:

1. **📈 Executive Dashboard** - Visão geral do negócio
2. **👥 Customer Analytics** - LTV, Cohort, RFM
3. **📦 Product Performance** - Análise por categoria
4. **🚚 Logistics Overview** - Performance de entregas
5. **💰 Financial Deep Dive** - Análise de receita e margens

👉 [Acesse os Dashboards Aqui](dashboards/looker_studio_links.md)

---

## 🔍 Principais Insights de Negócio

### 💡 Top 5 Descobertas

1. **80% da receita vem de 20% dos clientes** (Princípio de Pareto confirmado)
   - LTV médio: R$ 154,00
   - Top 10% de clientes: LTV > R$ 500,00

2. **Retenção crítica no 2º mês**
   - Taxa de retenção M0→M1: 3.2%
   - Oportunidade: programa de fidelidade early-stage

3. **São Paulo concentra 42% do GMV**, mas tem menor LTV per capita
   - Oportunidade: aumentar ticket médio em SP

4. **Categorias "Beleza & Saúde" têm maior NPS** (4.2/5.0)
   - Mas representam apenas 5% da receita
   - Oportunidade: expansão de mix

5. **Atraso na entrega reduz NPS em 40%**
   - SLA crítico: 15 dias
   - Investir em logística = maior retenção

📄 **Leia mais**: [Executive Summary Completo](EXECUTIVE_SUMMARY.md)

---

## 🛠️ Stack Tecnológico

| Camada | Tecnologia | Uso |
|--------|-----------|-----|
| **Orquestração** | Docker Compose | Ambiente reprodutível |
| **Storage** | Google BigQuery | Data Warehouse |
| **Processing** | Python 3.11 | ETL & Analytics |
| **SQL Engine** | BigQuery SQL | Queries avançadas |
| **Notebooks** | Jupyter Lab | Análise exploratória |
| **Visualization** | Looker Studio | Dashboards interativos |
| **Version Control** | Git + GitHub | Código versionado |

### 📚 Bibliotecas Python

```
pandas >= 2.0.0
google-cloud-bigquery >= 3.10.0
sqlalchemy >= 2.0.0
matplotlib >= 3.7.0
seaborn >= 0.12.0
scikit-learn >= 1.3.0
jupyter >= 1.0.0
```

---

## 📖 Documentação Técnica

- **[Arquitetura Detalhada](docs/architecture.md)** - Pipeline completo
- **[Metodologia de Análise](docs/methodology.md)** - Abordagens técnicas
- **[Business Insights](docs/business_insights.md)** - Descobertas e recomendações
- **[SQL Reference](sql/README.md)** - Guia das queries

---

## 🧪 Testes e Qualidade

```bash
# Executar testes de qualidade de dados
docker exec -it ecommerce-python pytest tests/

# Validação de schema
python tests/test_data_quality.py
```

**Cobertura de Testes**:
- ✅ Validação de integridade referencial
- ✅ Detecção de outliers
- ✅ Verificação de missing values críticos
- ✅ Consistência temporal

---

## 📈 Próximos Passos / Roadmap

- [ ] Implementar modelo de Churn Prediction (ML)
- [ ] Adicionar análise de NPS por categoria
- [ ] Dashboard de Real-Time com Streaming
- [ ] Análise de sentimento dos reviews (NLP)
- [ ] Forecast de demanda por categoria

---

## 🤝 Contribuições

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 👤 Autor

**André Bomfim**

- GitHub: [@AndreBomfim99](https://github.com/AndreBomfim99)
- LinkedIn: [Seu LinkedIn]
- Email: seu.email@example.com

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 🙏 Agradecimentos

- **Olist** por disponibilizar o dataset
- **Kaggle** pela plataforma
- **Google Cloud** pelo BigQuery free tier
- Comunidade open-source

---

## 📚 Referências

- [Kaggle Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
- [Google BigQuery Docs](https://cloud.google.com/bigquery/docs)
- [Looker Studio](https://lookerstudio.google.com/)

---

<div align="center">
  
**⭐ Se este projeto foi útil, considere dar uma estrela!**

Made with ❤️ and ☕ in Brasil

</div>