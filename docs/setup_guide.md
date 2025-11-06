# 🚀 Setup Guide - Olist E-Commerce Analysis

Guia completo passo a passo para configurar e executar o projeto de análise de dados da Olist.

---

## 📋 Índice

1. [Pré-requisitos](#pre-requisitos)
2. [Estrutura do Projeto](#estrutura)
3. [Setup Passo a Passo](#setup)
4. [Configuração do BigQuery](#bigquery)
5. [Download dos Dados](#download-dados)
6. [ETL - Carga de Dados](#etl)
7. [Execução das Análises](#analises)
8. [Criação dos Dashboards](#dashboards)
9. [Troubleshooting](#troubleshooting)
10. [Próximos Passos](#proximos-passos)

---

## ✅ Pré-requisitos {#pre-requisitos}

### **1. Software Necessário**

```bash
# Sistema Operacional
- Windows 10/11, macOS, ou Linux (Ubuntu 20.04+)

# Ferramentas essenciais
- Git (versão 2.30+)
- Python 3.9 ou superior
- pip (gerenciador de pacotes Python)
- Conta Google Cloud Platform (GCP)
- Conta Kaggle (para download dos dados)

# Opcional (mas recomendado)
- Docker Desktop 4.0+
- VS Code ou PyCharm
- DBeaver ou BigQuery Studio
```

### **2. Verificar Instalações**

```bash
# Verificar versões instaladas
python --version        # Deve ser 3.9+
pip --version          
git --version
docker --version       # Opcional

# Verificar se Python está no PATH
which python           # Linux/Mac
where python           # Windows
```

### **3. Conhecimentos Necessários**

```yaml
Essencial:
  - Linha de comando básica (bash/cmd)
  - Git básico (clone, pull, push)
  - Python básico
  - SQL básico

Desejável:
  - Google Cloud Platform
  - Docker
  - BigQuery
  - Análise de dados
```

---

## 📁 Estrutura do Projeto {#estrutura}

```
ecommerce-olist-analysis/
│
├── data/
│   ├── raw/              # CSVs do Kaggle (você baixa)
│   └── processed/        # CSVs processados (gerado)
│
├── sql/
│   ├── 01_schema/        # Scripts criação tabelas
│   └── 03_analytics/     # Queries de análise
│
├── python/
│   ├── etl/              # Scripts ETL
│   └── analytics/        # Scripts análise
│
├── notebooks/            # Jupyter notebooks
├── dashboards/           # Screenshots dashboards
├── docs/                 # Documentação
├── keys/                 # Chaves GCP (não versionar!)
│
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🔧 Setup Passo a Passo {#setup}

### **PASSO 1: Clonar o Repositório**

```bash
# Clone o projeto do GitHub
git clone https://github.com/AndreBomfim99/analise23.git
cd analise23

# Verificar estrutura
ls -la  # Linux/Mac
dir     # Windows
```

---

### **PASSO 2: Criar Ambiente Virtual Python**

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Linux/Mac:
source venv/bin/activate

# Windows (CMD):
venv\Scripts\activate.bat

# Windows (PowerShell):
venv\Scripts\Activate.ps1

# Verificar ativação (deve aparecer (venv) no prompt)
which python  # Deve apontar para venv/bin/python
```

---

### **PASSO 3: Instalar Dependências**

```bash
# Atualizar pip
pip install --upgrade pip

# Instalar todas as dependências
pip install -r requirements.txt

# Verificar instalação
pip list | grep google-cloud  # Deve mostrar google-cloud-bigquery
pip list | grep pandas        # Deve mostrar pandas
```

**Dependências principais instaladas:**
```
google-cloud-bigquery>=3.11.0
pandas>=2.0.0
numpy>=1.24.0
python-dotenv>=1.0.0
kaggle>=1.5.16
jupyter>=1.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

---

### **PASSO 4: Configurar Variáveis de Ambiente**

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar arquivo .env
nano .env   # Linux/Mac
notepad .env  # Windows
```

**Conteúdo do `.env`:**
```bash
# Google Cloud Platform
GCP_PROJECT_ID=seu-projeto-gcp
GCP_DATASET_ID=olist_ecommerce
GCP_LOCATION=US  # ou southamerica-east1 (São Paulo)

# Credenciais BigQuery
GOOGLE_APPLICATION_CREDENTIALS=./keys/gcp-key.json

# Kaggle (opcional - para download automatizado)
KAGGLE_USERNAME=seu_usuario_kaggle
KAGGLE_KEY=sua_chave_api_kaggle

# Configurações ETL
DATA_RAW_PATH=./data/raw
DATA_PROCESSED_PATH=./data/processed
LOG_LEVEL=INFO
```

---

## 🌩️ Configuração do BigQuery {#bigquery}

### **PASSO 5: Criar Projeto no Google Cloud**

#### **5.1 - Acessar Google Cloud Console**
```
1. Acesse: https://console.cloud.google.com
2. Faça login com sua conta Google
3. Aceite os termos de serviço
```

#### **5.2 - Criar Novo Projeto**
```
1. Clique no seletor de projetos (topo da página)
2. Clique em "Novo Projeto"
3. Nome do projeto: olist-ecommerce-analysis
4. ID do projeto: olist-ecommerce-XXXX (anote este ID!)
5. Clique em "Criar"
6. Aguarde 30-60 segundos
```

#### **5.3 - Ativar BigQuery API**
```
1. Menu (☰) → APIs e Serviços → Biblioteca
2. Buscar: "BigQuery API"
3. Clicar em "BigQuery API"
4. Clicar em "Ativar"
5. Aguardar confirmação
```

#### **5.4 - Ativar Billing (Cobrança)**
```
⚠️ IMPORTANTE: BigQuery tem camada gratuita generosa!

Free Tier mensal:
- 1 TB de processamento de queries (suficiente!)
- 10 GB de armazenamento (nosso projeto usa ~500MB)
- Grátis para sempre, não expira

1. Menu → Faturamento
2. Vincular conta de faturamento
3. Adicionar cartão de crédito (não será cobrado no free tier)
4. Confirmar

Dica: Configure alertas de orçamento em $5 para segurança
```

---

### **PASSO 6: Criar Service Account e Baixar Chave**

#### **6.1 - Criar Service Account**
```
1. Menu (☰) → IAM e Admin → Contas de Serviço
2. Clique em "+ Criar Conta de Serviço"
3. Preencher:
   - Nome: bigquery-olist-etl
   - ID: bigquery-olist-etl (auto-preenchido)
   - Descrição: Service account para ETL Olist
4. Clique em "Criar e Continuar"
```

#### **6.2 - Atribuir Permissões**
```
1. Na seção "Conceder acesso"
2. Adicionar papéis:
   - BigQuery Admin
   - BigQuery Data Editor
   - BigQuery Job User
3. Clique em "Continuar"
4. Clique em "Concluir"
```

#### **6.3 - Baixar Chave JSON**
```
1. Na lista de contas de serviço, clique na conta criada
2. Aba "Chaves"
3. Clique em "Adicionar Chave" → "Criar Nova Chave"
4. Selecione "JSON"
5. Clique em "Criar"
6. Arquivo será baixado automaticamente (gcp-key.json)
```

#### **6.4 - Mover Chave para o Projeto**
```bash
# Criar pasta keys (se não existir)
mkdir -p keys

# Mover arquivo baixado para a pasta
mv ~/Downloads/olist-ecommerce-*.json ./keys/gcp-key.json

# Linux/Mac: Proteger arquivo (apenas dono pode ler)
chmod 600 ./keys/gcp-key.json

# Verificar
ls -la keys/
```

⚠️ **IMPORTANTE:** Nunca commite este arquivo no Git! Ele já está no `.gitignore`.

---

### **PASSO 7: Criar Dataset no BigQuery**

#### **Opção A: Via Console (Interface Gráfica)**
```
1. Acesse: https://console.cloud.google.com/bigquery
2. No Explorer (lateral esquerda), clique no seu projeto
3. Clique nos três pontos (⋮) → "Criar conjunto de dados"
4. Preencher:
   - ID do conjunto de dados: olist_ecommerce
   - Local: us (ou southamerica-east1)
   - Expiração de tabela padrão: Nunca
5. Clique em "Criar conjunto de dados"
```

#### **Opção B: Via CLI (Linha de Comando)**
```bash
# Autenticar
gcloud auth login

# Definir projeto
gcloud config set project olist-ecommerce-XXXX

# Criar dataset
bq mk --location=US --dataset olist_ecommerce

# Verificar
bq ls
```

---

## 📥 Download dos Dados {#download-dados}

### **PASSO 8: Baixar Dados do Kaggle**

#### **Opção A: Download Manual (Recomendado para iniciantes)**

```
1. Acesse: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
2. Clique em "Download" (botão azul)
3. Extrair arquivo brazilian-ecommerce.zip
4. Copiar todos os CSVs para ./data/raw/
```

**Arquivos necessários:**
```
data/raw/
├── olist_customers_dataset.csv
├── olist_orders_dataset.csv
├── olist_order_items_dataset.csv
├── olist_products_dataset.csv
├── olist_sellers_dataset.csv
├── olist_order_payments_dataset.csv
├── olist_order_reviews_dataset.csv
├── product_category_name_translation.csv
└── olist_geolocation_dataset.csv (opcional)
```

#### **Opção B: Download via Kaggle API (Avançado)**

```bash
# 1. Instalar Kaggle CLI (já foi instalado no requirements.txt)
pip install kaggle

# 2. Obter API Key do Kaggle
#    - Acesse: https://www.kaggle.com/settings
#    - Seção "API" → "Create New API Token"
#    - Baixa arquivo kaggle.json

# 3. Configurar credenciais
mkdir -p ~/.kaggle
mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json  # Linux/Mac

# 4. Download automático
kaggle datasets download -d olistbr/brazilian-ecommerce

# 5. Extrair
unzip brazilian-ecommerce.zip -d ./data/raw/

# 6. Limpar
rm brazilian-ecommerce.zip
```

#### **Verificar Download**
```bash
# Listar arquivos
ls -lh data/raw/

# Verificar tamanhos (aproximados)
# olist_customers_dataset.csv         ~8 MB
# olist_orders_dataset.csv            ~12 MB
# olist_order_items_dataset.csv       ~18 MB
# olist_products_dataset.csv          ~2 MB
# olist_sellers_dataset.csv           ~300 KB
# olist_order_payments_dataset.csv    ~5 MB
# olist_order_reviews_dataset.csv     ~35 MB
# product_category_name_translation.csv ~2 KB
```

---

## 🔄 ETL - Carga de Dados {#etl}

### **PASSO 9: Criar Tabelas no BigQuery**

```bash
# 1. Executar script de criação de schema
# Via BigQuery Console:
# - Abra: sql/01_schema/create_tables_bigquery.sql
# - Copie todo o conteúdo
# - Cole no BigQuery Editor
# - Clique em "Executar"

# Ou via CLI:
bq query --use_legacy_sql=false < sql/01_schema/create_tables_bigquery.sql
```

**Tabelas criadas:**
```
olist_ecommerce.customers
olist_ecommerce.sellers
olist_ecommerce.products
olist_ecommerce.orders
olist_ecommerce.order_items
olist_ecommerce.order_payments
olist_ecommerce.order_reviews
olist_ecommerce.product_category_translation
```

---

### **PASSO 10: Executar ETL Python**

```bash
# Verificar variáveis de ambiente
cat .env  # Deve ter GCP_PROJECT_ID e GOOGLE_APPLICATION_CREDENTIALS

# Executar script de carga
python python/etl/load_to_bigquery.py

# Logs esperados:
# [INFO] Iniciando carga de dados para BigQuery...
# [INFO] Carregando customers... ✓ 99,441 linhas
# [INFO] Carregando orders... ✓ 99,441 linhas
# [INFO] Carregando order_items... ✓ 112,650 linhas
# ...
# [SUCCESS] ETL concluído com sucesso!
```

**Monitorar progresso:**
```bash
# Em outro terminal, acompanhar logs
tail -f logs/etl_bigquery.log
```

**Tempo estimado:**
- Customers: ~30 segundos
- Orders: ~45 segundos
- Order Items: ~1 minuto
- Reviews: ~2 minutos
- **Total: ~5-7 minutos**

---

### **PASSO 11: Validar Dados Carregados**

```sql
-- No BigQuery Console, execute:

-- 1. Verificar contagem de registros
SELECT 
  'customers' as table_name, 
  COUNT(*) as row_count 
FROM `olist_ecommerce.customers`

UNION ALL

SELECT 
  'orders', 
  COUNT(*) 
FROM `olist_ecommerce.orders`

UNION ALL

SELECT 
  'order_items', 
  COUNT(*) 
FROM `olist_ecommerce.order_items`;

-- Resultado esperado:
-- customers: 99,441
-- orders: 99,441
-- order_items: 112,650


-- 2. Testar query simples
SELECT 
  customer_state,
  COUNT(*) as total_customers
FROM `olist_ecommerce.customers`
GROUP BY customer_state
ORDER BY total_customers DESC
LIMIT 10;

-- Deve retornar SP como estado com mais clientes
```

---

## 📊 Execução das Análises {#analises}

### **PASSO 12: Executar Queries de Análise**

#### **12.1 - Análise de LTV**
```sql
-- Abrir: sql/03_analytics/ltv_analysis.sql
-- Copiar e executar no BigQuery Console

-- Resultado: Salvar como tabela ou CSV
-- Tabela destino: olist_ecommerce.ltv_by_state
```

#### **12.2 - Análise de Cohort**
```sql
-- Abrir: sql/03_analytics/cohort_retention.sql
-- Executar no BigQuery

-- Resultado esperado: Taxa de retenção por mês
```

#### **12.3 - Segmentação RFM**
```sql
-- Abrir: sql/03_analytics/rfm_segmentation.sql
-- Executar no BigQuery

-- Salvar resultado em: data/processed/rfm_customers.csv
```

#### **12.4 - Performance de Categorias**
```sql
-- Abrir: sql/03_analytics/category_performance.sql
-- Executar no BigQuery
```

---

### **PASSO 13: Análises Python (Opcional)**

```bash
# Executar segmentação RFM em Python
python python/analytics/rfm_segmentation.py

# Saída esperada:
# - data/processed/rfm_customers.csv
# - data/processed/rfm_summary.csv
```

---

### **PASSO 14: Jupyter Notebooks (Opcional)**

```bash
# Iniciar Jupyter
jupyter notebook

# Ou Jupyter Lab (mais moderno)
jupyter lab

# Navegador abrirá automaticamente
# Abrir: notebooks/01_exploratory_analysis.ipynb
```

---

## 📈 Criação dos Dashboards {#dashboards}

### **PASSO 15: Criar Dashboards no Looker Studio**

#### **15.1 - Conectar BigQuery ao Looker Studio**
```
1. Acesse: https://lookerstudio.google.com
2. Clique em "Criar" → "Fonte de Dados"
3. Selecione "BigQuery"
4. Autorize acesso à sua conta Google
5. Selecione:
   - Projeto: olist-ecommerce-XXXX
   - Dataset: olist_ecommerce
6. Clique em "Conectar"
```

#### **15.2 - Criar Dashboard Executivo**
```
Métricas principais:
- GMV Total
- Total de Pedidos
- Ticket Médio
- NPS Médio
- Taxa de Retenção M1

Gráficos:
- Receita por mês (linha)
- Pedidos por estado (mapa)
- Top 10 categorias (barra)
- NPS por região (gauge)
```

#### **15.3 - Criar Dashboard de Clientes**
```
Métricas RFM:
- Distribuição de segmentos (pizza)
- LTV por segmento (barra)
- Cohort retention heatmap
- Churn rate por mês
```

#### **15.4 - Salvar e Compartilhar**
```
1. Clique em "Arquivo" → "Fazer download como PDF"
2. Salvar screenshot em: dashboards/screenshots/
3. Anotar URL do dashboard em: dashboards/looker_studio_links.md
```

---

## 🐛 Troubleshooting {#troubleshooting}

### **Problemas Comuns e Soluções**

#### **Erro: "Application Default Credentials not found"**
```bash
# Solução 1: Verificar caminho da chave no .env
cat .env | grep GOOGLE_APPLICATION_CREDENTIALS

# Solução 2: Definir variável manualmente
export GOOGLE_APPLICATION_CREDENTIALS="./keys/gcp-key.json"  # Linux/Mac
set GOOGLE_APPLICATION_CREDENTIALS=./keys/gcp-key.json        # Windows

# Solução 3: Autenticar via gcloud
gcloud auth application-default login
```

#### **Erro: "Permission denied: BigQuery"**
```
Solução:
1. Verificar papéis da Service Account
2. Menu → IAM e Admin → IAM
3. Encontrar bigquery-olist-etl
4. Editar → Adicionar papel "BigQuery Admin"
```

#### **Erro: "ModuleNotFoundError: No module named 'google'"**
```bash
# Reativar venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstalar dependências
pip install -r requirements.txt
```

#### **Erro: "FileNotFoundError: data/raw/olist_customers_dataset.csv"**
```bash
# Verificar se CSVs foram baixados
ls data/raw/

# Se vazio, baixar do Kaggle novamente (ver PASSO 8)
```

#### **Erro: BigQuery Quota Exceeded**
```
Problema: Ultrapassou 1TB de processamento mensal

Solução:
1. Otimizar queries (usar WHERE, LIMIT)
2. Evitar SELECT * em tabelas grandes
3. Usar cache do BigQuery (queries repetidas são grátis)
4. Aguardar próximo mês
```

#### **Erro: "Dataset not found"**
```sql
-- Verificar datasets existentes
SELECT 
  schema_name
FROM `olist_ecommerce.INFORMATION_SCHEMA.SCHEMATA`;

-- Se não existir, criar (ver PASSO 7)
```

---

### **Logs e Debug**

```bash
# Ver logs do ETL
cat logs/etl_bigquery.log

# Ver últimas 50 linhas
tail -n 50 logs/etl_bigquery.log

# Buscar erros
grep ERROR logs/etl_bigquery.log
```

---

## 🎯 Próximos Passos {#proximos-passos}

### **Após Setup Completo:**

#### **1. Exploração de Dados**
```bash
# Executar notebooks de análise
jupyter notebook notebooks/01_exploratory_analysis.ipynb
```

#### **2. Análises Avançadas**
```sql
-- Criar suas próprias queries em:
sql/03_analytics/custom_analysis.sql
```

#### **3. Automatizar ETL (Opcional)**
```bash
# Agendar execução diária via cron (Linux/Mac)
crontab -e

# Adicionar linha:
0 2 * * * cd /path/to/projeto && ./venv/bin/python python/etl/load_to_bigquery.py

# Ou usar Cloud Scheduler no GCP
```

#### **4. Deploy de Dashboards**
```
- Compartilhar dashboards Looker com stakeholders
- Configurar alertas de métricas críticas
- Agendar envio de relatórios por email
```

#### **5. Expandir Análises**
```
- Análise de sazonalidade
- Previsão de demanda
- Clusterização de clientes
- Recomendação de produtos
```

---

## 📚 Recursos Adicionais

### **Documentação:**
- [BigQuery Docs](https://cloud.google.com/bigquery/docs)
- [Pandas Docs](https://pandas.pydata.org/docs/)
- [Looker Studio Help](https://support.google.com/looker-studio)

### **Suporte:**
- GitHub Issues: [Abrir issue](https://github.com/AndreBomfim99/analise23/issues)
- Email: seu-email@example.com

---

## ✅ Checklist Final

Antes de considerar setup completo, verifique:

- [ ] Python 3.9+ instalado
- [ ] Ambiente virtual criado e ativado
- [ ] Dependências instaladas (`requirements.txt`)
- [ ] Arquivo `.env` configurado
- [ ] Projeto GCP criado
- [ ] BigQuery API ativada
- [ ] Service Account criada
- [ ] Chave JSON baixada (`keys/gcp-key.json`)
- [ ] Dataset BigQuery criado
- [ ] CSVs do Kaggle baixados (8 arquivos em `data/raw/`)
- [ ] Tabelas BigQuery criadas
- [ ] ETL executado com sucesso
- [ ] Dados validados no BigQuery
- [ ] Pelo menos 1 query de análise executada
- [ ] Dashboard básico criado no Looker

**Se todos os itens estão ✅, parabéns! Setup completo!** 🎉

---

## 🆘 Precisa de Ajuda?

Se encontrar problemas não cobertos neste guia:

1. Verifique a seção [Troubleshooting](#troubleshooting)
2. Consulte os logs em `logs/etl_bigquery.log`
3. Abra uma issue no GitHub com:
   - Descrição do erro
   - Mensagem de erro completa
   - Sistema operacional
   - Versões (Python, pip, etc.)

---

**Última atualização:** Novembro 2024  
**Versão:** 1.0  
**Autor:** Andre Bomfim