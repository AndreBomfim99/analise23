# 📊 Dados - Brazilian E-Commerce (Olist)

Este diretório contém os dados brutos utilizados no projeto de análise do e-commerce brasileiro.

---

## 🗂️ Estrutura de Diretórios
```
data/
├── raw/                    # Dados brutos originais (CSV)
│   ├── olist_customers_dataset.csv
│   ├── olist_geolocation_dataset.csv
│   ├── olist_order_items_dataset.csv
│   ├── olist_order_payments_dataset.csv
│   ├── olist_order_reviews_dataset.csv
│   ├── olist_orders_dataset.csv
│   ├── olist_products_dataset.csv
│   ├── olist_sellers_dataset.csv
│   └── product_category_name_translation.csv
└── processed/              # Dados processados (gerados pelo ETL)
```

---

## 📥 Como Obter os Dados

### **Opção 1: Download Manual (Kaggle)**

1. Acesse: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
2. Clique em **"Download"** (necessário login no Kaggle)
3. Extraia o arquivo `archive.zip`
4. Mova todos os arquivos `.csv` para `data/raw/`

### **Opção 2: Kaggle API (Recomendado)**
```bash
# 1. Instalar Kaggle CLI
pip install kaggle

# 2. Configurar credenciais
# Baixe kaggle.json em: https://www.kaggle.com/settings
# Mova para: ~/.kaggle/kaggle.json (Linux/Mac) ou C:\Users\<user>\.kaggle\kaggle.json (Windows)

# 3. Download automático
kaggle datasets download -d olistbr/brazilian-ecommerce -p data/raw/ --unzip
```

### **Opção 3: Script Python Automatizado**
```python
import kaggle
import os

# Autenticar (requer kaggle.json configurado)
kaggle.api.authenticate()

# Download dataset
kaggle.api.dataset_download_files(
    'olistbr/brazilian-ecommerce',
    path='data/raw/',
    unzip=True
)

print("✓ Dataset baixado com sucesso!")
```

---

## 📋 Descrição dos Arquivos

| Arquivo | Descrição | Registros | Tamanho |
|---------|-----------|-----------|---------|
| **olist_orders_dataset.csv** | Pedidos principais | ~100k | ~5 MB |
| **olist_order_items_dataset.csv** | Itens dos pedidos | ~112k | ~15 MB |
| **olist_customers_dataset.csv** | Dados dos clientes | ~99k | ~5 MB |
| **olist_sellers_dataset.csv** | Vendedores | ~3k | ~200 KB |
| **olist_products_dataset.csv** | Catálogo de produtos | ~32k | ~2 MB |
| **olist_order_payments_dataset.csv** | Pagamentos | ~103k | ~5 MB |
| **olist_order_reviews_dataset.csv** | Avaliações | ~99k | ~35 MB |
| **olist_geolocation_dataset.csv** | Geolocalização | ~1M | ~50 MB |
| **product_category_name_translation.csv** | Tradução categorias | 71 | ~2 KB |

**Total:** ~117 MB (comprimido: ~35 MB)

---

## 🔒 Integridade dos Dados

Após o download, valide a integridade:
```bash
# Verificar arquivos presentes
ls -lh data/raw/*.csv

# Contar registros (Linux/Mac)
wc -l data/raw/*.csv

# Verificar primeiras linhas
head data/raw/olist_orders_dataset.csv
```

**Checksums esperados (MD5):**
```
olist_orders_dataset.csv: a1b2c3d4e5f6...
olist_customers_dataset.csv: f6e5d4c3b2a1...
# ... (adicionar checksums reais se necessário)
```

---

## 🚨 Importante

- **NÃO commitar dados brutos** no Git (`.gitignore` já configurado)
- Dados processados vão para `processed/` (gerados pelo ETL)
- Dados sensíveis (se houver) devem ser anonimizados
- Dataset original: © Olist (uso educacional/pesquisa)

---

## 📊 Schema das Tabelas

### **Relacionamentos:**
```
orders (order_id) ──┬──→ order_items (order_id)
                    ├──→ order_payments (order_id)
                    ├──→ order_reviews (order_id)
                    └──→ customers (customer_id)

order_items (product_id) ──→ products (product_id)
order_items (seller_id) ──→ sellers (seller_id)

customers (customer_zip_code) ──→ geolocation (zip_code)
sellers (seller_zip_code) ──→ geolocation (zip_code)
```

### **Principais Colunas:**

**orders:**
- `order_id` (PK)
- `customer_id` (FK)
- `order_status`
- `order_purchase_timestamp`
- `order_delivered_customer_date`
- `order_estimated_delivery_date`

**order_items:**
- `order_id` (FK)
- `product_id` (FK)
- `seller_id` (FK)
- `price`
- `freight_value`

**customers:**
- `customer_id` (PK)
- `customer_unique_id`
- `customer_zip_code`
- `customer_city`
- `customer_state`

---

## 🔧 Próximos Passos

Após baixar os dados:

1. **Validar integridade:** `python scripts/validate_data.py`
2. **Executar ETL:** `docker-compose up etl`
3. **Carregar no BigQuery:** `python python/etl/load_to_bigquery.py`
4. **Iniciar análises:** Abrir notebooks em `notebooks/`

---

## 📚 Referências

- **Fonte Original:** [Kaggle - Olist Brazilian E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
- **Documentação Olist:** [Olist Store](https://olist.com/)
- **Paper Acadêmico:** [E-Commerce Analysis Paper](https://arxiv.org/...)

---

## ❓ Problemas Comuns

**Erro: "Dataset not found"**
- Verifique credenciais Kaggle (`kaggle.json`)
- Confirme permissões do dataset

**Erro: "Permission denied"**
- Ajuste permissões: `chmod 600 ~/.kaggle/kaggle.json`

**Arquivos corrompidos:**
- Re-download: `kaggle datasets download ... --force`

---

**✅ Dados prontos?** Prossiga para: [Configuração do Ambiente](../README.md#setup)