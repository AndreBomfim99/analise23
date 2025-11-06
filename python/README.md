# 🐍 Python - Olist E-Commerce Analysis

Código Python para ETL, análises avançadas e automações do projeto.

---

## 📋 Estrutura
```
python/
├── etl/                    # Pipeline ETL
│   ├── load_to_bigquery.py
│   ├── data_validation.py
│   └── README.md
├── analytics/              # Scripts de análise
│   ├── rfm_segmentation.py
│   ├── cohort_analysis.py
│   └── README.md
├── utils/                  # Utilitários
│   ├── bigquery_client.py
│   └── helpers.py
└── tests/                  # Testes unitários
    ├── test_etl.py
    └── test_analytics.py
```

---

## 🎯 Componentes Principais

### **1. ETL Pipeline** (`etl/`)

Pipeline completo de extração, transformação e carga.

**Scripts:**
- `load_to_bigquery.py` - Carga de CSVs para BigQuery
- `data_validation.py` - Validação de qualidade
- `transform_data.py` - Transformações avançadas

**📖 Docs:** [python/etl/README.md](etl/README.md)

---

### **2. Analytics** (`analytics/`)

Scripts para análises programáticas e geração de insights.

**Scripts:**
- `rfm_segmentation.py` - Segmentação RFM
- `cohort_analysis.py` - Análise de retenção
- `category_performance.py` - Performance por categoria
- `delivery_analysis.py` - Análise de entregas
- `ltv_calculation.py` - Cálculo de LTV

**📖 Docs:** [python/analytics/README.md](analytics/README.md)

---

### **3. Utils** (`utils/`)

Funções auxiliares reutilizáveis.

**Módulos:**
- `bigquery_client.py` - Cliente BigQuery wrapper
- `helpers.py` - Funções gerais
- `validators.py` - Validadores customizados

---

### **4. Tests** (`tests/`)

Testes unitários e de integração.
```bash
# Rodar todos os testes
pytest python/tests/

# Com coverage
pytest --cov=python python/tests/
```

---

## ⚙️ Setup

### **1. Requisitos**
```bash
Python >= 3.11
pip >= 23.0
```

---

### **2. Instalação**
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt
```

---

### **3. Configuração**
```bash
# Copiar .env template
cp .env.example .env

# Editar variáveis
nano .env
```

**.env:**
```bash
GCP_PROJECT_ID=your-project
GCP_DATASET_ID=olist_ecommerce
GOOGLE_APPLICATION_CREDENTIALS=./keys/gcp-key.json
```

---

## ▶️ Uso Rápido

### **ETL Completo**
```bash
# Carregar dados
python python/etl/load_to_bigquery.py

# Validar
python python/etl/data_validation.py
```

---

### **Análises**
```bash
# Segmentação RFM
python python/analytics/rfm_segmentation.py

# Cohort Analysis
python python/analytics/cohort_analysis.py

# Todas análises
bash scripts/run_all_analytics.sh
```

---

## 🐳 Docker

### **Build**
```bash
docker build -t olist-python -f docker/Dockerfile.python .
```

---

### **Run (ETL)**
```bash
docker run --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/keys:/app/keys \
  --env-file .env \
  olist-python python python/etl/load_to_bigquery.py
```

---

### **Docker Compose**
```bash
# ETL
docker-compose run etl

# Analytics
docker-compose run analytics python python/analytics/rfm_segmentation.py
```

---

## 🧪 Testes

### **Estrutura de Testes**
```
python/tests/
├── test_etl.py              # Testes ETL
├── test_analytics.py        # Testes analytics
├── test_utils.py            # Testes utils
└── fixtures/                # Dados de teste
    └── sample_orders.csv
```

---

### **Executar Testes**
```bash
# Todos os testes
pytest

# Específico
pytest python/tests/test_etl.py

# Com coverage
pytest --cov=python --cov-report=html

# Verbose
pytest -v -s
```

---

### **Exemplo de Teste**
```python
# python/tests/test_etl.py
import pytest
from python.etl.load_to_bigquery import validate_csv

def test_validate_csv_success():
    """Testa validação de CSV válido"""
    result = validate_csv('tests/fixtures/sample_orders.csv')
    assert result['valid'] == True
    assert result['rows'] > 0

def test_validate_csv_missing_file():
    """Testa erro com arquivo inexistente"""
    with pytest.raises(FileNotFoundError):
        validate_csv('nonexistent.csv')
```

---

## 📦 Dependências

### **Core**
```txt
pandas>=2.0.0
numpy>=1.24.0
google-cloud-bigquery>=3.10.0
python-dotenv>=1.0.0
```

---

### **Analytics**
```txt
scipy>=1.10.0
scikit-learn>=1.3.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

---

### **Dev/Test**
```txt
pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.5.0
```

---

## 🔧 Desenvolvimento

### **Code Style**
```bash
# Formatar código
black python/

# Lint
flake8 python/

# Type checking
mypy python/
```

---

### **Pre-commit Hooks**
```bash
# Instalar
pip install pre-commit
pre-commit install

# Rodar manualmente
pre-commit run --all-files
```

**.pre-commit-config.yaml:**
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.0.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

---

## 📊 Performance

### **Profiling**
```bash
# Line profiler
pip install line_profiler
kernprof -l -v python/analytics/rfm_segmentation.py

# Memory profiler
pip install memory_profiler
python -m memory_profiler python/analytics/rfm_segmentation.py
```

---

### **Otimizações**
```python
# 1. Usar Dask para datasets grandes
import dask.dataframe as dd
df = dd.read_csv('data/raw/*.csv')

# 2. Paralelizar com multiprocessing
from multiprocessing import Pool
with Pool(4) as p:
    results = p.map(process_chunk, chunks)

# 3. Usar parquet ao invés de CSV
df.to_parquet('data/processed/orders.parquet', compression='snappy')
```

---

## 🚀 Deploy

### **Cloud Functions**
```bash
# Deploy analytics como Cloud Function
gcloud functions deploy rfm-segmentation \
  --runtime python311 \
  --trigger-http \
  --entry-point main \
  --source python/analytics/
```

---

### **Cloud Run**
```bash
# Build e deploy
gcloud run deploy olist-analytics \
  --source . \
  --platform managed \
  --region us-central1
```

---

## 📚 Recursos

- **Pandas:** https://pandas.pydata.org/docs/
- **BigQuery Python:** https://cloud.google.com/python/docs/reference/bigquery/latest
- **pytest:** https://docs.pytest.org/
- **Docker:** https://docs.docker.com/

---

## 🤝 Contribuindo

1. Fork o projeto
2. Criar branch (`git checkout -b feature/amazing`)
3. Adicionar testes
4. Commit (`git commit -m 'Add amazing feature'`)
5. Push (`git push origin feature/amazing`)
6. Pull Request

---

## ❓ FAQ

**Q: Erro "ModuleNotFoundError"?**
A: `pip install -r requirements.txt`

**Q: Testes falhando?**
A: Verificar credenciais GCP e `.env`

**Q: Performance lenta?**
A: Usar parquet, aumentar batch size, paralelizar

---

**✅ Python Setup Completo?** Veja: [Notebooks](../notebooks/README.md)