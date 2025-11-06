# 🔄 ETL Pipeline - Olist E-Commerce

Pipeline de extração, transformação e carga (ETL) dos dados do e-commerce brasileiro para Google BigQuery.

---

## 📋 Índice

1. [Visão Geral](#visao-geral)
2. [Arquitetura](#arquitetura)
3. [Scripts Disponíveis](#scripts)
4. [Como Executar](#execucao)
5. [Configuração](#configuracao)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral {#visao-geral}

O pipeline ETL realiza:

1. **Extract:** Leitura de CSVs do Kaggle (`data/raw/`)
2. **Transform:** Limpeza, validação e enriquecimento
3. **Load:** Carga no Google BigQuery

**Tecnologias:**
- Python 3.11+
- pandas
- google-cloud-bigquery
- Docker (opcional)

---

## 🏗️ Arquitetura {#arquitetura}
```
python/etl/
├── load_to_bigquery.py      # Script principal ETL
├── data_validation.py        # Validação de qualidade
├── transform_data.py         # Transformações (opcional)
├── config/
│   └── bigquery_schema.json  # Schema das tabelas
└── utils/
    ├── __init__.py
    ├── bigquery_client.py    # Cliente BigQuery
    └── validators.py         # Validadores customizados
```

### **Fluxo de Dados:**
```
CSV Files (data/raw/)
    ↓
[Extract] → pd.read_csv()
    ↓
[Transform] → Limpeza + Validação
    ↓
[Load] → BigQuery.load_table_from_dataframe()
    ↓
BigQuery Tables (olist_ecommerce dataset)
```

---

## 📜 Scripts Disponíveis {#scripts}

### **1. load_to_bigquery.py**

**Descrição:** Carrega todos os CSVs para o BigQuery

**Uso:**
```bash
python python/etl/load_to_bigquery.py
```

**Parâmetros:**
```bash
# Com argumentos opcionais
python python/etl/load_to_bigquery.py \
  --project-id your-project \
  --dataset-id olist_ecommerce \
  --data-dir data/raw/
```

**Output:**
```
✓ Conectado ao BigQuery: your-project.olist_ecommerce
✓ Carregando olist_orders_dataset.csv...
  → 99,441 registros carregados
✓ Carregando olist_customers_dataset.csv...
  → 99,441 registros carregados
...
✓ ETL concluído: 8 tabelas carregadas em 45s
```

---

### **2. data_validation.py**

**Descrição:** Valida integridade e qualidade dos dados

**Uso:**
```bash
python python/etl/data_validation.py
```

**Validações:**
- ✅ Integridade referencial (FKs)
- ✅ Valores nulos críticos
- ✅ Outliers (preços, datas)
- ✅ Duplicatas
- ✅ Consistência temporal

**Output:**
```
🔍 VALIDAÇÃO DE DADOS - RELATÓRIO
=====================================

✓ orders: 99,441 registros
  → 0 duplicatas
  → 0 valores nulos críticos
  
⚠ order_items: 112,650 registros
  → 15 preços = 0 (0.01%)
  → Sugestão: Revisar preços zerados

✓ customers: 99,441 registros
  → Integridade OK

❌ FALHA: geolocation
  → 5,432 zip_codes inválidos (0.5%)
  
=====================================
Score de Qualidade: 92/100
```

---

### **3. transform_data.py** (Opcional)

**Descrição:** Transformações avançadas pré-carga

**Uso:**
```bash
python python/etl/transform_data.py --table orders
```

**Transformações:**
- Normalização de datas
- Cálculo de métricas derivadas
- Enriquecimento geográfico
- Tratamento de outliers

---

## ▶️ Como Executar {#execucao}

### **Método 1: Local (Python direto)**
```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar credenciais
export GOOGLE_APPLICATION_CREDENTIALS="path/to/gcp-key.json"
export GCP_PROJECT_ID="your-project"
export GCP_DATASET_ID="olist_ecommerce"

# 3. Executar ETL
python python/etl/load_to_bigquery.py

# 4. Validar dados
python python/etl/data_validation.py
```

---

### **Método 2: Docker (Recomendado)**
```bash
# 1. Build
docker-compose build etl

# 2. Executar ETL
docker-compose run etl python python/etl/load_to_bigquery.py

# 3. Validar
docker-compose run etl python python/etl/data_validation.py
```

---

### **Método 3: Automático (docker-compose up)**
```bash
# Executar pipeline completo
docker-compose up etl

# Com logs detalhados
docker-compose up --verbose etl
```

---

## ⚙️ Configuração {#configuracao}

### **Variáveis de Ambiente (.env)**
```bash
# Google Cloud
GCP_PROJECT_ID=your-gcp-project
GCP_DATASET_ID=olist_ecommerce
GOOGLE_APPLICATION_CREDENTIALS=./keys/gcp-key.json

# Configurações ETL
DATA_DIR=data/raw
BATCH_SIZE=10000
WRITE_DISPOSITION=WRITE_TRUNCATE  # ou WRITE_APPEND
```

---

### **Schema BigQuery (config/bigquery_schema.json)**
```json
{
  "orders": [
    {"name": "order_id", "type": "STRING", "mode": "REQUIRED"},
    {"name": "customer_id", "type": "STRING", "mode": "REQUIRED"},
    {"name": "order_status", "type": "STRING", "mode": "NULLABLE"},
    {"name": "order_purchase_timestamp", "type": "TIMESTAMP", "mode": "NULLABLE"},
    {"name": "order_delivered_customer_date", "type": "TIMESTAMP", "mode": "NULLABLE"}
  ],
  "customers": [
    {"name": "customer_id", "type": "STRING", "mode": "REQUIRED"},
    {"name": "customer_unique_id", "type": "STRING", "mode": "REQUIRED"},
    {"name": "customer_zip_code_prefix", "type": "STRING", "mode": "NULLABLE"},
    {"name": "customer_city", "type": "STRING", "mode": "NULLABLE"},
    {"name": "customer_state", "type": "STRING", "mode": "NULLABLE"}
  ]
}
```

---

## 🔧 Troubleshooting {#troubleshooting}

### **Erro: "Credentials not found"**
```bash
# Verificar credenciais
echo $GOOGLE_APPLICATION_CREDENTIALS

# Re-configurar
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
```

---

### **Erro: "Permission denied: bigquery.tables.create"**

**Solução:** Garantir permissões no IAM:
- `BigQuery Data Editor`
- `BigQuery Job User`
```bash
# Verificar permissões
gcloud projects get-iam-policy $GCP_PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:YOUR_EMAIL"
```

---

### **Erro: "Dataset not found"**
```bash
# Criar dataset manualmente
bq mk --dataset $GCP_PROJECT_ID:olist_ecommerce

# Ou pelo script
python -c "from google.cloud import bigquery; \
client = bigquery.Client(); \
client.create_dataset('olist_ecommerce', exists_ok=True)"
```

---

### **Erro: "CSV file not found"**
```bash
# Verificar arquivos
ls -lh data/raw/*.csv

# Re-download
kaggle datasets download olistbr/brazilian-ecommerce -p data/raw/ --unzip
```

---

### **Performance Lenta**

**Otimizações:**
```python
# 1. Aumentar batch size
BATCH_SIZE = 50000  # default: 10000

# 2. Usar parquet ao invés de CSV
df.to_parquet('data/processed/orders.parquet')

# 3. Paralelizar cargas
from concurrent.futures import ThreadPoolExecutor
```

---

## 📊 Monitoramento

### **Logs**
```bash
# Logs em tempo real
tail -f logs/etl.log

# Erros apenas
grep "ERROR" logs/etl.log
```

---

### **Métricas de Execução**
```python
# Registrar no BigQuery
INSERT INTO etl_logs (timestamp, table_name, rows_loaded, duration_seconds)
VALUES (CURRENT_TIMESTAMP(), 'orders', 99441, 12.5)
```

---

## 🚀 Próximos Passos

Após ETL bem-sucedido:

1. **Validar dados:** `python python/etl/data_validation.py`
2. **Executar queries SQL:** `sql/01_setup/`
3. **Rodar análises:** `notebooks/`
4. **Criar dashboards:** Looker Studio

---

## 📚 Referências

- [BigQuery Python Client](https://cloud.google.com/python/docs/reference/bigquery/latest)
- [pandas Documentation](https://pandas.pydata.org/docs/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

**✅ ETL Configurado?** Prossiga para: [Análises SQL](../../sql/README.md)