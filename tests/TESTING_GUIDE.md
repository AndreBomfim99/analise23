# 🧪 Tests - Olist E-Commerce Analysis

Documentação completa da estratégia de testes, validações de qualidade de dados e testes de integridade do pipeline ETL.

---

## 📋 Índice

1. [Visão Geral](#visao-geral)
2. [Estratégia de Testes](#estrategia)
3. [Tipos de Testes](#tipos-testes)
4. [Estrutura de Testes](#estrutura)
5. [Como Executar](#como-executar)
6. [Cobertura de Testes](#cobertura)
7. [CI/CD Integration](#cicd)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral {#visao-geral}

### **Objetivo dos Testes**

Garantir a **qualidade, consistência e confiabilidade** dos dados e análises ao longo de todo o pipeline:

```
Raw Data → ETL → BigQuery → Analytics → Dashboards
    ↓        ↓       ↓          ↓           ↓
  Tests   Tests   Tests     Tests      Tests
```

### **Princípios de Qualidade**

1. **Completude:** Dados ausentes são identificados
2. **Consistência:** Relações entre tabelas são válidas
3. **Acurácia:** Valores estão dentro de ranges esperados
4. **Integridade:** Chaves primárias e estrangeiras respeitadas
5. **Atualidade:** Dados recentes disponíveis

---

## 🎯 Estratégia de Testes {#estrategia}

### **Pirâmide de Testes (Adaptada para Data)**

```
           /\
          /  \  E2E Tests
         /    \  (Dashboard validation)
        /------\
       /        \  Integration Tests
      /          \  (ETL pipeline)
     /------------\
    /              \  Unit Tests
   /                \  (Data quality)
  /------------------\
```

### **Níveis de Teste**

| Nível | Foco | Frequência | Ferramenta |
|-------|------|------------|------------|
| **Unit Tests** | Qualidade de dados individual | Cada carga | pytest |
| **Integration Tests** | Pipeline ETL completo | Deploy | pytest + BigQuery |
| **Schema Tests** | Estrutura de tabelas | Deploy | SQL |
| **Business Logic Tests** | Regras de negócio | Semanal | SQL + Python |
| **E2E Tests** | Dashboards funcionais | Manual | Looker Studio |

---

## 🧪 Tipos de Testes {#tipos-testes}

### **1. Testes de Qualidade de Dados**

#### **1.1 Testes de Completude**

Verificar dados ausentes (nulls):

```python
# tests/test_data_quality.py

def test_no_null_in_critical_columns():
    """Colunas críticas não devem ter valores nulos"""
    
    query = """
    SELECT 
      COUNT(*) as total_nulls
    FROM `olist_ecommerce.orders`
    WHERE order_id IS NULL 
       OR customer_id IS NULL
       OR order_status IS NULL
    """
    
    result = client.query(query).to_dataframe()
    assert result['total_nulls'].iloc[0] == 0, "Null values found in critical columns"
```

#### **1.2 Testes de Unicidade**

Verificar chaves primárias:

```python
def test_order_id_is_unique():
    """Order ID deve ser único"""
    
    query = """
    SELECT 
      COUNT(*) as total,
      COUNT(DISTINCT order_id) as unique_ids
    FROM `olist_ecommerce.orders`
    """
    
    result = client.query(query).to_dataframe()
    assert result['total'].iloc[0] == result['unique_ids'].iloc[0], \
           "Duplicate order_ids found"
```

#### **1.3 Testes de Integridade Referencial**

Verificar foreign keys:

```python
def test_foreign_key_integrity():
    """Todos os customer_ids em orders devem existir em customers"""
    
    query = """
    SELECT COUNT(*) as orphan_records
    FROM `olist_ecommerce.orders` o
    LEFT JOIN `olist_ecommerce.customers` c 
      ON o.customer_id = c.customer_id
    WHERE c.customer_id IS NULL
    """
    
    result = client.query(query).to_dataframe()
    assert result['orphan_records'].iloc[0] == 0, \
           "Orders with invalid customer_ids found"
```

#### **1.4 Testes de Range**

Verificar valores dentro de limites esperados:

```python
def test_price_in_valid_range():
    """Preços devem estar entre R$ 0,01 e R$ 10.000"""
    
    query = """
    SELECT 
      MIN(price) as min_price,
      MAX(price) as max_price
    FROM `olist_ecommerce.order_items`
    """
    
    result = client.query(query).to_dataframe()
    assert result['min_price'].iloc[0] > 0, "Price cannot be zero or negative"
    assert result['max_price'].iloc[0] < 10000, "Price too high (outlier?)"
```

#### **1.5 Testes de Consistência Temporal**

Verificar sequência de datas:

```python
def test_order_dates_consistency():
    """Data de entrega deve ser após data de compra"""
    
    query = """
    SELECT COUNT(*) as inconsistent_dates
    FROM `olist_ecommerce.orders`
    WHERE order_delivered_customer_date < order_purchase_timestamp
    """
    
    result = client.query(query).to_dataframe()
    assert result['inconsistent_dates'].iloc[0] == 0, \
           "Delivery date before purchase date found"
```

---

### **2. Testes de ETL**

#### **2.1 Teste de Contagem de Registros**

```python
def test_etl_record_count():
    """Número de registros carregados deve ser igual ao CSV"""
    
    # Contar linhas no CSV
    df_csv = pd.read_csv('data/raw/olist_orders_dataset.csv')
    expected_count = len(df_csv)
    
    # Contar linhas no BigQuery
    query = "SELECT COUNT(*) as total FROM `olist_ecommerce.orders`"
    result = client.query(query).to_dataframe()
    actual_count = result['total'].iloc[0]
    
    assert actual_count == expected_count, \
           f"Expected {expected_count}, got {actual_count}"
```

#### **2.2 Teste de Schema**

```python
def test_table_schema():
    """Schema da tabela deve corresponder ao esperado"""
    
    table = client.get_table('olist_ecommerce.orders')
    
    expected_schema = {
        'order_id': 'STRING',
        'customer_id': 'STRING',
        'order_status': 'STRING',
        'order_purchase_timestamp': 'TIMESTAMP',
        'order_delivered_customer_date': 'TIMESTAMP'
    }
    
    for field in table.schema:
        if field.name in expected_schema:
            assert field.field_type == expected_schema[field.name], \
                   f"Field {field.name} has wrong type"
```

#### **2.3 Teste de Transformações**

```python
def test_rfm_segmentation_logic():
    """Segmentação RFM deve seguir regras de negócio"""
    
    query = """
    SELECT 
      customer_segment,
      AVG(r_score) as avg_r,
      AVG(f_score) as avg_f,
      AVG(m_score) as avg_m
    FROM `olist_ecommerce.rfm_segmentation`
    WHERE customer_segment = 'Champions'
    GROUP BY customer_segment
    """
    
    result = client.query(query).to_dataframe()
    
    # Champions devem ter scores altos
    assert result['avg_r'].iloc[0] >= 4, "Champions should have high recency score"
    assert result['avg_f'].iloc[0] >= 4, "Champions should have high frequency score"
    assert result['avg_m'].iloc[0] >= 4, "Champions should have high monetary score"
```

---

### **3. Testes de Análises**

#### **3.1 Teste de Cohort Retention**

```python
def test_cohort_retention_logic():
    """Retenção M0 deve ser 100%"""
    
    query = """
    SELECT 
      cohort_month,
      retention_rate
    FROM `olist_ecommerce.cohort_retention`
    WHERE months_since_first_purchase = 0
    """
    
    result = client.query(query).to_dataframe()
    
    # M0 sempre 100%
    assert (result['retention_rate'] == 100.0).all(), \
           "M0 retention should always be 100%"
```

#### **3.2 Teste de LTV**

```python
def test_ltv_calculation():
    """LTV não pode ser negativo"""
    
    query = """
    SELECT 
      MIN(avg_ltv) as min_ltv
    FROM `olist_ecommerce.ltv_by_state`
    """
    
    result = client.query(query).to_dataframe()
    assert result['min_ltv'].iloc[0] >= 0, "LTV cannot be negative"
```

---

### **4. Testes de Performance**

#### **4.1 Teste de Tempo de Query**

```python
def test_query_performance():
    """Queries críticas devem executar em menos de 30s"""
    
    import time
    
    query = """
    SELECT * FROM `olist_ecommerce.rfm_segmentation`
    """
    
    start = time.time()
    result = client.query(query).to_dataframe()
    elapsed = time.time() - start
    
    assert elapsed < 30, f"Query took {elapsed}s, expected < 30s"
```

---

## 📁 Estrutura de Testes {#estrutura}

```
tests/
│
├── __init__.py                    # Package initialization
│
├── test_data_quality.py           # Testes de qualidade de dados
│   ├── test_no_nulls()
│   ├── test_unique_keys()
│   ├── test_foreign_keys()
│   ├── test_value_ranges()
│   └── test_date_consistency()
│
├── test_etl.py                    # Testes do pipeline ETL
│   ├── test_extract_csv()
│   ├── test_transform_data()
│   ├── test_load_to_bigquery()
│   ├── test_record_counts()
│   └── test_schema_validation()
│
├── test_analytics.py              # Testes de análises
│   ├── test_rfm_segmentation()
│   ├── test_cohort_retention()
│   ├── test_ltv_calculation()
│   └── test_category_performance()
│
├── test_performance.py            # Testes de performance
│   ├── test_query_speed()
│   └── test_dashboard_load_time()
│
├── conftest.py                    # Fixtures pytest
│   ├── bigquery_client()
│   ├── sample_data()
│   └── test_database()
│
├── fixtures/                      # Dados de teste
│   ├── sample_orders.csv
│   ├── sample_customers.csv
│   └── expected_results.json
│
└── README.md                      # Este arquivo
```

---

## 🚀 Como Executar {#como-executar}

### **Pré-requisitos**

```bash
# Instalar dependências de teste
pip install pytest pytest-cov google-cloud-bigquery pandas

# Configurar variáveis de ambiente
export GOOGLE_APPLICATION_CREDENTIALS="./keys/gcp-key.json"
export GCP_PROJECT_ID="seu-projeto"
```

---

### **Executar Todos os Testes**

```bash
# Rodar todos os testes
pytest tests/

# Com verbose
pytest tests/ -v

# Com cobertura
pytest tests/ --cov=python --cov-report=html
```

---

### **Executar Testes Específicos**

```bash
# Apenas testes de qualidade de dados
pytest tests/test_data_quality.py

# Apenas testes de ETL
pytest tests/test_etl.py

# Teste específico
pytest tests/test_data_quality.py::test_no_null_in_critical_columns

# Com output detalhado
pytest tests/test_etl.py -v -s
```

---

### **Executar por Marcadores (Tags)**

```bash
# Apenas testes rápidos
pytest -m "not slow"

# Apenas testes críticos
pytest -m "critical"

# Apenas testes de integração
pytest -m "integration"
```

**Definir marcadores no código:**
```python
import pytest

@pytest.mark.critical
def test_order_id_is_unique():
    # ...

@pytest.mark.slow
def test_full_pipeline():
    # ...
```

---

## 📊 Cobertura de Testes {#cobertura}

### **Métricas de Cobertura**

```bash
# Gerar relatório de cobertura
pytest --cov=python --cov-report=html --cov-report=term

# Abrir relatório HTML
open htmlcov/index.html  # Mac/Linux
start htmlcov/index.html  # Windows
```

### **Meta de Cobertura**

| Componente | Meta | Atual | Status |
|------------|------|-------|--------|
| ETL Scripts | 80%+ | TBD | ⚪ |
| Analytics Scripts | 70%+ | TBD | ⚪ |
| Utils/Helpers | 90%+ | TBD | ⚪ |
| Data Quality | 100% | TBD | ⚪ |

---

## 🔄 CI/CD Integration {#cicd}

### **GitHub Actions (Exemplo)**

Criar arquivo: `.github/workflows/tests.yml`

```yaml
name: Data Quality Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      env:
        GOOGLE_APPLICATION_CREDENTIALS: ${{ secrets.GCP_KEY }}
      run: |
        pytest tests/ --cov=python --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
      with:
        file: ./coverage.xml
```

---

## 🛠️ Troubleshooting {#troubleshooting}

### **Problema: "Authentication Failed"**

```bash
# Solução: Verificar credenciais GCP
export GOOGLE_APPLICATION_CREDENTIALS="./keys/gcp-key.json"

# Ou autenticar via gcloud
gcloud auth application-default login
```

---

### **Problema: "Table Not Found"**

```bash
# Solução: Verificar se tabelas existem
bq ls olist_ecommerce

# Se não existir, rodar ETL primeiro
python python/etl/load_to_bigquery.py
```

---

### **Problema: "Tests Too Slow"**

```bash
# Solução: Rodar apenas testes rápidos
pytest -m "not slow"

# Ou usar dados de amostra
pytest --use-sample-data
```

---

### **Problema: "Import Error"**

```bash
# Solução: Adicionar projeto ao PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Ou instalar projeto em modo dev
pip install -e .
```

---

## 📝 Boas Práticas

### **1. Nomes Descritivos**

❌ **Ruim:**
```python
def test_1():
    assert True
```

✅ **Bom:**
```python
def test_order_id_is_unique_across_all_orders():
    """Verifica que não há order_ids duplicados na tabela orders"""
    # ...
```

---

### **2. Mensagens de Erro Claras**

❌ **Ruim:**
```python
assert result == expected
```

✅ **Bom:**
```python
assert result == expected, \
       f"Expected {expected} orders, but got {result}. " \
       f"Check if ETL loaded all records correctly."
```

---

### **3. Fixtures Reutilizáveis**

```python
# conftest.py

@pytest.fixture
def bigquery_client():
    """Cliente BigQuery configurado"""
    return bigquery.Client()

@pytest.fixture
def sample_orders():
    """DataFrame com pedidos de exemplo"""
    return pd.DataFrame({
        'order_id': ['1', '2', '3'],
        'customer_id': ['c1', 'c2', 'c3'],
        'order_status': ['delivered', 'delivered', 'canceled']
    })
```

---

### **4. Testes Independentes**

Cada teste deve ser **independente** e **idempotente**:

```python
def test_example():
    # Setup
    data = load_test_data()
    
    # Execute
    result = process(data)
    
    # Assert
    assert result is not None
    
    # Cleanup (se necessário)
    cleanup_test_data()
```

---

## 🎯 Roadmap de Testes

### **Fase 1: Fundação (Atual)**
- [x] Testes de qualidade de dados básicos
- [ ] Testes de ETL completos
- [ ] Cobertura > 50%

### **Fase 2: Expansão**
- [ ] Testes de análises (RFM, Cohort, LTV)
- [ ] Testes de performance
- [ ] CI/CD pipeline
- [ ] Cobertura > 70%

### **Fase 3: Maturidade**
- [ ] Testes E2E automatizados
- [ ] Monitoramento contínuo de qualidade
- [ ] Data profiling automático
- [ ] Cobertura > 80%

---

## 📚 Referências

### **Frameworks de Teste**

- **pytest:** https://docs.pytest.org/
- **Great Expectations:** https://greatexpectations.io/ (futuro)
- **dbt tests:** https://docs.getdbt.com/docs/build/tests

### **Qualidade de Dados**

- **Data Quality Dimensions:**
  - Completeness, Consistency, Accuracy, Validity, Uniqueness, Timeliness

### **Artigos Recomendados**

1. "Testing Data Pipelines" - Thoughtworks
2. "Data Quality at Scale" - Netflix Tech Blog
3. "Testing ML Systems" - Google Research

---

## ✅ Checklist de Qualidade

Antes de fazer deploy, verificar:

- [ ] Todos os testes passando
- [ ] Cobertura > 70%
- [ ] Sem dados sensíveis em testes
- [ ] Documentação atualizada
- [ ] Performance aceitável (< 30s por teste)
- [ ] CI/CD configurado
- [ ] Logs de teste revisados

---

**Última atualização:** Novembro 2024  
**Versão:** 1.0  
**Autor:** Andre Bomfim  
**Contato:** [GitHub](https://github.com/AndreBomfim99/analise23)