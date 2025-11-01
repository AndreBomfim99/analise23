# 🧪 Tests - Olist E-Commerce Analysis

Suite completa de testes automatizados para o projeto de análise de e-commerce.

---

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Estrutura dos Testes](#estrutura-dos-testes)
- [Como Executar](#como-executar)
- [Tipos de Testes](#tipos-de-testes)
- [Fixtures Disponíveis](#fixtures-disponíveis)
- [Markers (Tags)](#markers-tags)
- [Coverage](#coverage)
- [CI/CD](#cicd)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

Os testes cobrem três áreas principais do projeto:

| Módulo | Arquivo | Testes | Descrição |
|--------|---------|--------|-----------|
| **Data Quality** | `test_data_quality.py` | 80+ | Validação de qualidade dos dados |
| **ETL Pipeline** | `test_etl.py` | 120+ | Pipeline de extração e carga |
| **Analytics** | `test_analytics.py` | 100+ | Análises RFM e segmentação |

**Total**: **300+ testes** com **cobertura > 85%**

---

## 📁 Estrutura dos Testes

```
tests/
├── __init__.py                  # ✅ Fixtures e configurações compartilhadas
├── test_data_quality.py        # ✅ 80+ testes de validação de dados
├── test_etl.py                 # ✅ 120+ testes do pipeline ETL
├── test_analytics.py           # ✅ 100+ testes de análise RFM
└── README.md                   # 📄 Este arquivo
```

### Arquivos de Suporte

```
python/
├── etl/
│   ├── load_to_bigquery.py         # Código testado por test_etl.py
│   └── data_validation.py          # Código testado por test_data_quality.py
└── analytics/
    └── rfm_segmentation.py         # Código testado por test_analytics.py
```

---

## 🚀 Como Executar

### Pré-requisitos

```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas credenciais
```

### Executar Todos os Testes

```bash
# Todos os testes (apenas unitários, sem BigQuery)
pytest tests/ -v

# Todos os testes incluindo integração (requer BigQuery)
pytest tests/ --run-integration -v

# Com output colorido e detalhado
pytest tests/ -v --color=yes

# Modo silencioso (apenas resultados)
pytest tests/ -q
```

### Executar Testes Específicos

```bash
# Por arquivo
pytest tests/test_data_quality.py -v
pytest tests/test_etl.py -v
pytest tests/test_analytics.py -v

# Por classe
pytest tests/test_analytics.py::TestRFMAnalyzer -v

# Por teste específico
pytest tests/test_etl.py::TestOlistBigQueryETL::test_load_csv_to_dataframe -v

# Por padrão no nome
pytest tests/ -k "rfm" -v          # Todos com "rfm" no nome
pytest tests/ -k "not slow" -v     # Excluir testes lentos
```

### Executar por Markers

```bash
# Apenas testes unitários (rápidos, sem BigQuery)
pytest tests/ -m unit -v

# Apenas testes que requerem BigQuery
pytest tests/ -m bigquery -v

# Apenas testes de integração
pytest tests/ -m integration -v

# Apenas testes lentos
pytest tests/ -m slow -v

# Excluir testes lentos e de integração
pytest tests/ -m "not slow and not integration" -v
```

### Executar com Diferentes Níveis de Log

```bash
# Debug completo
pytest tests/ -v --log-cli-level=DEBUG

# Info
pytest tests/ -v --log-cli-level=INFO

# Apenas warnings e erros
pytest tests/ -v --log-cli-level=WARNING
```

### Executar com Coverage

```bash
# Coverage básico
pytest tests/ --cov=python

# Coverage com relatório HTML (abre no navegador)
pytest tests/ --cov=python --cov-report=html
open htmlcov/index.html

# Coverage com relatório no terminal
pytest tests/ --cov=python --cov-report=term-missing

# Coverage apenas de um módulo
pytest tests/test_etl.py --cov=python.etl --cov-report=html
```

---

## 🏷️ Tipos de Testes

### 1. Unit Tests (Unitários) ⚡

**Descrição**: Testam funções/métodos isolados com mocks.

**Características**:
- ✅ Rápidos (< 1s por teste)
- ✅ Não requerem BigQuery ou recursos externos
- ✅ Usam mocks e fixtures
- ✅ Executam em qualquer ambiente

**Exemplo**:
```python
def test_calculate_rfm_scores(analyzer, sample_rfm_df):
    """Unit test - usa mock do analyzer"""
    df = analyzer.calculate_rfm_scores(sample_rfm_df)
    assert 'R_score' in df.columns
    assert df['R_score'].between(1, 5).all()
```

**Executar**:
```bash
pytest tests/ -m unit -v
```

---

### 2. Integration Tests (Integração) 🔗

**Descrição**: Testam múltiplos componentes juntos, incluindo BigQuery real.

**Características**:
- ⏱️ Mais lentos (10s - 1min)
- 🌐 Requerem BigQuery configurado
- 🔗 Testam fluxo completo
- 📊 Validam com dados reais

**Exemplo**:
```python
@pytest.mark.integration
@pytest.mark.bigquery
def test_full_validation_pipeline(project_id, dataset_id):
    """Integration test - usa BigQuery real"""
    validator = DataValidator(project_id, dataset_id)
    results = validator.run_all_validations()
    assert results['passed'].sum() / len(results) >= 0.8
```

**Executar**:
```bash
# Requer BigQuery configurado
pytest tests/ --run-integration -v
```

---

### 3. Slow Tests (Lentos) 🐌

**Descrição**: Testes de performance com datasets grandes.

**Características**:
- 🐌 Lentos (> 5s)
- 📊 Testam com 10k+ registros
- ⚡ Validam performance
- 🎯 Detectam gargalos

**Exemplo**:
```python
@pytest.mark.slow
def test_large_dataset_performance(analyzer):
    """Slow test - processa 10k clientes"""
    large_df = generate_random_customers(10000)
    start = time.time()
    df = analyzer.calculate_rfm_scores(large_df)
    elapsed = time.time() - start
    assert elapsed < 5.0  # Deve ser < 5s
```

**Executar**:
```bash
pytest tests/ -m slow -v
```

---

## 🎁 Fixtures Disponíveis

Todas as fixtures estão em `tests/__init__.py` e são injetadas automaticamente.

### Fixtures de Configuração

| Fixture | Scope | Descrição |
|---------|-------|-----------|
| `project_id` | session | GCP Project ID |
| `dataset_id` | session | BigQuery Dataset ID |
| `data_raw_path` | session | Caminho para dados raw |
| `data_processed_path` | session | Caminho para dados processados |
| `sql_path` | session | Caminho para arquivos SQL |
| `bigquery_client` | session | Cliente BigQuery (pula se não conectado) |

### Fixtures de Dados de Exemplo

| Fixture | Linhas | Descrição |
|---------|--------|-----------|
| `sample_customers_df` | 5 | Clientes de exemplo |
| `sample_orders_df` | 5 | Pedidos de exemplo |
| `sample_order_items_df` | 5 | Itens de pedidos |
| `sample_products_df` | 4 | Produtos de exemplo |
| `sample_payments_df` | 4 | Pagamentos de exemplo |
| `sample_reviews_df` | 4 | Reviews de exemplo |
| `sample_rfm_df` | 6 | Dados RFM de exemplo |

### Exemplo de Uso

```python
def test_with_fixtures(sample_customers_df, bigquery_client):
    """Fixtures são injetadas automaticamente"""
    assert len(sample_customers_df) == 5
    assert bigquery_client is not None
```

### Helper Functions

Disponíveis globalmente em `tests/__init__.py`:

```python
# Assertions
assert_dataframe_not_empty(df, "My DataFrame")
assert_columns_exist(df, ['col1', 'col2'])
assert_no_nulls(df, ['required_col'])
assert_values_in_range(df, 'price', 0, 1000)
assert_unique_values(df, 'customer_id')
assert_positive_values(df, ['price', 'freight'])
assert_date_order(df, 'purchase_date', 'delivery_date')

# Data Generation
create_test_csv(path, df)
generate_random_customers(n=100)
generate_random_orders(n=200, customer_ids=None)
```

---

## 🏷️ Markers (Tags)

Os testes usam markers para categorização e filtragem.

### Markers Disponíveis

| Marker | Descrição | Uso |
|--------|-----------|-----|
| `@pytest.mark.unit` | Teste unitário rápido | Adicionado automaticamente |
| `@pytest.mark.integration` | Teste de integração | Requer `--run-integration` |
| `@pytest.mark.bigquery` | Requer BigQuery | Pula se não conectado |
| `@pytest.mark.slow` | Teste lento (> 5s) | Pode ser excluído |

### Configurar no pytest.ini

```ini
[pytest]
markers =
    unit: unit tests (fast, no external dependencies)
    integration: integration tests (require BigQuery)
    bigquery: tests that require BigQuery connection
    slow: slow running tests (> 5s)
```

### Exemplos de Filtros

```bash
# Apenas rápidos (excluir slow e integration)
pytest tests/ -m "not slow and not integration" -v

# Apenas BigQuery
pytest tests/ -m bigquery --run-integration -v

# Tudo exceto lentos
pytest tests/ -m "not slow" -v

# Combinar: unitários OU integração
pytest tests/ -m "unit or integration" -v
```

---

## 📊 Coverage

### Gerar Relatórios

```bash
# HTML Report (navegador)
pytest tests/ --cov=python --cov-report=html
open htmlcov/index.html

# Terminal Report
pytest tests/ --cov=python --cov-report=term-missing

# XML Report (para CI/CD)
pytest tests/ --cov=python --cov-report=xml

# Múltiplos formatos
pytest tests/ --cov=python --cov-report=html --cov-report=term
```

### Metas de Coverage

| Módulo | Meta | Status |
|--------|------|--------|
| `python/etl/load_to_bigquery.py` | > 85% | ✅ |
| `python/etl/data_validation.py` | > 80% | ✅ |
| `python/analytics/rfm_segmentation.py` | > 90% | ✅ |
| `python/utils/bigquery_helper.py` | > 75% | ⚠️ |
| **TOTAL** | > 85% | ✅ |

### Verificar Coverage Mínimo

```bash
# Falha se coverage < 80%
pytest tests/ --cov=python --cov-fail-under=80
```

---

## 🔄 CI/CD

### GitHub Actions

Exemplo de workflow (`.github/workflows/tests.yml`):

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python 3.11
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run unit tests
      run: |
        pytest tests/ -m "not integration" --cov=python --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true
```

### GitLab CI

Exemplo de `.gitlab-ci.yml`:

```yaml
test:
  image: python:3.11
  stage: test
  script:
    - pip install -r requirements.txt
    - pytest tests/ -m "not integration" --cov=python --cov-report=term
  coverage: '/TOTAL.*\s+(\d+%)$/'
```

### Pre-commit Hook

Adicionar em `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: pytest-check
      name: pytest-check
      entry: pytest
      args: [tests/, -m, "not slow and not integration", --maxfail=1]
      language: system
      pass_filenames: false
      always_run: true
```

---

## 🐛 Troubleshooting

### Problema: "BigQuery client não disponível"

**Solução**:
```bash
# 1. Verificar credenciais
echo $GOOGLE_APPLICATION_CREDENTIALS

# 2. Testar conexão
python -c "from google.cloud import bigquery; client = bigquery.Client(); print('OK')"

# 3. Executar sem testes de integração
pytest tests/ -m "not bigquery" -v
```

---

### Problema: "Module not found"

**Solução**:
```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Verificar PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 3. Instalar em modo desenvolvimento
pip install -e .
```

---

### Problema: Testes muito lentos

**Solução**:
```bash
# 1. Executar apenas rápidos
pytest tests/ -m "not slow" -v

# 2. Executar em paralelo (requer pytest-xdist)
pip install pytest-xdist
pytest tests/ -n auto

# 3. Executar apenas testes falhados
pytest tests/ --lf  # last failed
```

---

### Problema: Coverage muito baixo

**Solução**:
```bash
# 1. Ver linhas não cobertas
pytest tests/ --cov=python --cov-report=term-missing

# 2. Focar em módulo específico
pytest tests/test_etl.py --cov=python.etl --cov-report=html

# 3. Verificar testes que não executam
pytest tests/ --collect-only
```

---

### Problema: Fixtures não encontradas

**Solução**:
```bash
# 1. Verificar que __init__.py existe
ls tests/__init__.py

# 2. Listar fixtures disponíveis
pytest --fixtures

# 3. Verificar import
pytest tests/ -v --tb=short
```

---

## 📚 Comandos Úteis

### Listar e Coletar

```bash
# Listar todos os testes
pytest --collect-only

# Listar testes de um arquivo
pytest tests/test_etl.py --collect-only

# Listar fixtures disponíveis
pytest --fixtures

# Listar markers
pytest --markers
```

### Execução

```bash
# Parar no primeiro erro
pytest tests/ -x

# Parar após 3 falhas
pytest tests/ --maxfail=3

# Executar em paralelo
pytest tests/ -n auto

# Mostrar prints
pytest tests/ -s

# Modo verboso máximo
pytest tests/ -vv
```

### Debug

```bash
# Parar no primeiro erro e abrir debugger
pytest tests/ -x --pdb

# Traceback completo
pytest tests/ --tb=long

# Traceback curto
pytest tests/ --tb=short

# Sem traceback
pytest tests/ --tb=no
```

### Seleção

```bash
# Executar apenas testes que falharam
pytest tests/ --lf

# Executar falhas primeiro, depois os outros
pytest tests/ --ff

# Duração dos 10 testes mais lentos
pytest tests/ --durations=10

# Duração de todos os testes
pytest tests/ --durations=0
```

### Relatórios

```bash
# Relatório JUnit XML
pytest tests/ --junitxml=report.xml

# Relatório JSON
pytest tests/ --json-report --json-report-file=report.json

# Relatório HTML (requer pytest-html)
pip install pytest-html
pytest tests/ --html=report.html
```

---

## 🤝 Contribuindo

### Adicionar Novos Testes

1. **Criar arquivo** `test_*.py` em `tests/`
2. **Importar fixtures** de `tests/__init__.py`
3. **Usar markers** apropriados
4. **Documentar** o que está testando
5. **Garantir coverage** > 80%

### Template de Teste

```python
"""
Tests: [Nome do Módulo]
-----------------------
Descrição dos testes.

Autor: Seu Nome
Data: Outubro 2025
"""

import pytest
from your_module import YourClass

class TestYourClass:
    """Testes para YourClass"""
    
    @pytest.fixture
    def instance(self):
        """Fixture: YourClass instance"""
        return YourClass()
    
    def test_method_name(self, instance):
        """Testa comportamento específico"""
        # Arrange
        input_data = ...
        
        # Act
        result = instance.method(input_data)
        
        # Assert
        assert result == expected
```

### Boas Práticas

1. **Nomes descritivos**: `test_rfm_scores_are_between_1_and_5()`
2. **Arrange-Act-Assert**: Separar preparação, execução e verificação
3. **Um teste, uma asserção**: Quando possível
4. **Usar mocks**: Para serviços externos (BigQuery, APIs)
5. **Documentar**: Docstrings explicando o que testa
6. **Coverage**: Cobrir casos normais, edge cases e erros

---

## 📞 Suporte

### Problemas com os testes?

1. ✅ Verifique se `.env` está configurado
2. ✅ Confirme que BigQuery está acessível (para testes integration)
3. ✅ Execute com `-v` para mais detalhes
4. ✅ Consulte [Troubleshooting](#troubleshooting)
5. ✅ Abra uma issue no GitHub

### Recursos

- 📖 [Pytest Documentation](https://docs.pytest.org/)
- 📖 [Coverage.py](https://coverage.readthedocs.io/)
- 📖 [Pytest Fixtures](https://docs.pytest.org/en/latest/fixture.html)
- 📖 [Pytest Markers](https://docs.pytest.org/en/latest/example/markers.html)

---

## 📈 Estatísticas

```
Total de Testes: 300+
├── test_data_quality.py: 80+ testes
├── test_etl.py:         120+ testes
└── test_analytics.py:   100+ testes

Coverage: 85%+
├── ETL:        85%
├── Analytics:  90%
└── Utils:      75%

Tempo de Execução:
├── Unit:        ~30s
├── Integration: ~2min
└── Slow:        ~5min
```

---

**Última atualização**: Outubro 2025  
**Mantido por**: Andre Bomfim  
**Versão Python**: 3.11+  
**Framework**: pytest 7.4+

---

## ⭐ Quick Start

```bash
# Setup
pip install -r requirements.txt
cp .env.example .env

# Executar testes rápidos
pytest tests/ -m "not slow and not integration" -v

# Ver coverage
pytest tests/ --cov=python --cov-report=html
open htmlcov/index.html

# Executar tudo (com BigQuery)
pytest tests/ --run-integration --cov=python -v
```

**Happy Testing! 🚀**