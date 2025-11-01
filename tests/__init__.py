"""
Tests Package - Olist E-Commerce Analysis
------------------------------------------
Configurações e fixtures compartilhadas para todos os testes.

Autor: Andre Bomfim
Data: Outubro 2025
"""

import os
import sys
from pathlib import Path

import pytest
import pandas as pd
import numpy as np
from google.cloud import bigquery
from dotenv import load_dotenv

# Adicionar o diretório raiz ao path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Carregar variáveis de ambiente
load_dotenv()


# ============================================
# FIXTURES GLOBAIS - CONFIGURAÇÃO
# ============================================

@pytest.fixture(scope="session")
def project_id():
    """Fixture: GCP Project ID"""
    return os.getenv('GCP_PROJECT_ID', 'ecommerce-analysis-andre')


@pytest.fixture(scope="session")
def dataset_id():
    """Fixture: BigQuery Dataset ID"""
    return os.getenv('GCP_DATASET_ID', 'olist_ecommerce')


@pytest.fixture(scope="session")
def data_raw_path():
    """Fixture: Caminho para dados raw"""
    path = Path(os.getenv('DATA_RAW_PATH', './data/raw'))
    return path


@pytest.fixture(scope="session")
def data_processed_path():
    """Fixture: Caminho para dados processados"""
    path = Path(os.getenv('DATA_PROCESSED_PATH', './data/processed'))
    path.mkdir(parents=True, exist_ok=True)
    return path


@pytest.fixture(scope="session")
def sql_path():
    """Fixture: Caminho para arquivos SQL"""
    path = Path(os.getenv('SQL_PATH', './sql'))
    return path


@pytest.fixture(scope="session")
def bigquery_client(project_id):
    """Fixture: Cliente BigQuery"""
    try:
        client = bigquery.Client(project=project_id)
        # Testar conexão
        client.query("SELECT 1").result()
        return client
    except Exception as e:
        pytest.skip(f"BigQuery client não disponível: {e}")


# ============================================
# FIXTURES - SAMPLE DATA
# ============================================

@pytest.fixture(scope="session")
def sample_customers_df():
    """Fixture: DataFrame de exemplo de customers"""
    return pd.DataFrame({
        'customer_id': ['c1', 'c2', 'c3', 'c4', 'c5'],
        'customer_unique_id': ['u1', 'u2', 'u3', 'u4', 'u5'],
        'customer_zip_code_prefix': ['01310', '02010', '03030', '04040', '05050'],
        'customer_city': ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Curitiba', 'Porto Alegre'],
        'customer_state': ['SP', 'RJ', 'MG', 'PR', 'RS']
    })


@pytest.fixture(scope="session")
def sample_orders_df():
    """Fixture: DataFrame de exemplo de orders"""
    return pd.DataFrame({
        'order_id': ['o1', 'o2', 'o3', 'o4', 'o5'],
        'customer_id': ['c1', 'c2', 'c3', 'c4', 'c5'],
        'order_status': ['delivered', 'delivered', 'canceled', 'delivered', 'delivered'],
        'order_purchase_timestamp': pd.to_datetime([
            '2018-01-01 10:00:00',
            '2018-01-05 14:30:00',
            '2018-01-10 09:15:00',
            '2018-01-15 16:45:00',
            '2018-01-20 11:20:00'
        ]),
        'order_delivered_customer_date': pd.to_datetime([
            '2018-01-10',
            '2018-01-12',
            None,
            '2018-01-22',
            '2018-01-27'
        ]),
        'order_estimated_delivery_date': pd.to_datetime([
            '2018-01-15',
            '2018-01-15',
            '2018-01-17',
            '2018-01-25',
            '2018-01-30'
        ])
    })


@pytest.fixture(scope="session")
def sample_order_items_df():
    """Fixture: DataFrame de exemplo de order_items"""
    return pd.DataFrame({
        'order_id': ['o1', 'o1', 'o2', 'o3', 'o4'],
        'order_item_id': [1, 2, 1, 1, 1],
        'product_id': ['p1', 'p2', 'p3', 'p1', 'p4'],
        'seller_id': ['s1', 's2', 's1', 's3', 's1'],
        'price': [100.0, 50.0, 200.0, 100.0, 150.0],
        'freight_value': [10.0, 5.0, 20.0, 15.0, 12.0]
    })


@pytest.fixture(scope="session")
def sample_products_df():
    """Fixture: DataFrame de exemplo de products"""
    return pd.DataFrame({
        'product_id': ['p1', 'p2', 'p3', 'p4'],
        'product_category_name': ['moveis_decoracao', 'eletronicos', 'beleza_saude', 'esporte_lazer'],
        'product_name_lenght': [50, 45, 40, 55],
        'product_weight_g': [5000, 2000, 500, 3000],
        'product_length_cm': [100, 50, 20, 80],
        'product_height_cm': [80, 30, 15, 60],
        'product_width_cm': [60, 40, 10, 50]
    })


@pytest.fixture(scope="session")
def sample_payments_df():
    """Fixture: DataFrame de exemplo de payments"""
    return pd.DataFrame({
        'order_id': ['o1', 'o1', 'o2', 'o4'],
        'payment_sequential': [1, 2, 1, 1],
        'payment_type': ['credit_card', 'credit_card', 'boleto', 'debit_card'],
        'payment_installments': [3, 2, 1, 1],
        'payment_value': [100.0, 60.0, 220.0, 162.0]
    })


@pytest.fixture(scope="session")
def sample_reviews_df():
    """Fixture: DataFrame de exemplo de reviews"""
    return pd.DataFrame({
        'review_id': ['r1', 'r2', 'r3', 'r4'],
        'order_id': ['o1', 'o2', 'o4', 'o5'],
        'review_score': [5, 4, 3, 5],
        'review_comment_title': ['Ótimo!', 'Bom', 'Regular', 'Excelente'],
        'review_comment_message': ['Produto ótimo', 'Gostei', 'Ok', 'Perfeito'],
        'review_creation_date': pd.to_datetime([
            '2018-01-15',
            '2018-01-18',
            '2018-01-28',
            '2018-02-02'
        ])
    })


@pytest.fixture(scope="session")
def sample_rfm_df():
    """Fixture: DataFrame de exemplo para RFM"""
    return pd.DataFrame({
        'customer_unique_id': ['u1', 'u2', 'u3', 'u4', 'u5', 'u6'],
        'customer_state': ['SP', 'RJ', 'MG', 'SP', 'RS', 'BA'],
        'recency': [10, 30, 90, 180, 365, 500],
        'frequency': [5, 3, 2, 1, 1, 1],
        'monetary': [1000.0, 500.0, 200.0, 100.0, 50.0, 30.0],
        'avg_order_value': [200.0, 166.67, 100.0, 100.0, 50.0, 30.0],
        'last_purchase_date': pd.to_datetime([
            '2018-09-20',
            '2018-09-01',
            '2018-07-02',
            '2018-04-03',
            '2017-10-01',
            '2017-05-15'
        ]),
        'first_purchase_date': pd.to_datetime([
            '2018-01-01',
            '2018-02-01',
            '2018-05-01',
            '2018-04-03',
            '2017-10-01',
            '2017-05-15'
        ])
    })


# ============================================
# HELPER FUNCTIONS - ASSERTIONS
# ============================================

def assert_dataframe_not_empty(df: pd.DataFrame, name: str = "DataFrame"):
    """
    Helper: Verifica se DataFrame não está vazio
    
    Args:
        df: DataFrame a verificar
        name: Nome para mensagem de erro
    """
    assert df is not None, f"{name} é None"
    assert isinstance(df, pd.DataFrame), f"{name} não é um DataFrame"
    assert len(df) > 0, f"{name} está vazio"


def assert_columns_exist(df: pd.DataFrame, columns: list, name: str = "DataFrame"):
    """
    Helper: Verifica se colunas existem no DataFrame
    
    Args:
        df: DataFrame a verificar
        columns: Lista de colunas esperadas
        name: Nome para mensagem de erro
    """
    missing_cols = set(columns) - set(df.columns)
    assert not missing_cols, f"{name} está faltando colunas: {missing_cols}"


def assert_no_nulls(df: pd.DataFrame, columns: list, name: str = "DataFrame"):
    """
    Helper: Verifica se não há valores nulos nas colunas especificadas
    
    Args:
        df: DataFrame a verificar
        columns: Lista de colunas para verificar
        name: Nome para mensagem de erro
    """
    for col in columns:
        null_count = df[col].isnull().sum()
        assert null_count == 0, f"{name}.{col} tem {null_count} valores nulos"


def assert_values_in_range(df: pd.DataFrame, column: str, min_val, max_val):
    """
    Helper: Verifica se valores estão dentro de um range
    
    Args:
        df: DataFrame a verificar
        column: Nome da coluna
        min_val: Valor mínimo
        max_val: Valor máximo
    """
    invalid_count = ((df[column] < min_val) | (df[column] > max_val)).sum()
    assert invalid_count == 0, (
        f"{column} tem {invalid_count} valores fora do range [{min_val}, {max_val}]"
    )


def assert_unique_values(df: pd.DataFrame, column: str, name: str = "DataFrame"):
    """
    Helper: Verifica se todos os valores são únicos
    
    Args:
        df: DataFrame a verificar
        column: Nome da coluna
        name: Nome para mensagem de erro
    """
    duplicates = df[column].duplicated().sum()
    assert duplicates == 0, f"{name}.{column} tem {duplicates} valores duplicados"


def assert_positive_values(df: pd.DataFrame, columns: list, strict: bool = True):
    """
    Helper: Verifica se valores são positivos
    
    Args:
        df: DataFrame a verificar
        columns: Lista de colunas para verificar
        strict: Se True, usa > 0; se False, usa >= 0
    """
    for col in columns:
        if strict:
            invalid = (df[col] <= 0).sum()
            msg = f"{col} tem {invalid} valores <= 0"
        else:
            invalid = (df[col] < 0).sum()
            msg = f"{col} tem {invalid} valores < 0"
        
        assert invalid == 0, msg


def assert_date_order(df: pd.DataFrame, date_col1: str, date_col2: str, 
                     allow_equal: bool = True):
    """
    Helper: Verifica se date_col1 <= date_col2 (ou < se allow_equal=False)
    
    Args:
        df: DataFrame a verificar
        date_col1: Coluna de data inicial
        date_col2: Coluna de data final
        allow_equal: Se True, permite datas iguais
    """
    # Filtrar apenas linhas sem nulls
    valid_rows = df[[date_col1, date_col2]].notna().all(axis=1)
    df_valid = df[valid_rows]
    
    if allow_equal:
        invalid = (df_valid[date_col1] > df_valid[date_col2]).sum()
        msg = f"{invalid} linhas onde {date_col1} > {date_col2}"
    else:
        invalid = (df_valid[date_col1] >= df_valid[date_col2]).sum()
        msg = f"{invalid} linhas onde {date_col1} >= {date_col2}"
    
    assert invalid == 0, msg


# ============================================
# HELPER FUNCTIONS - DATA GENERATION
# ============================================

def create_test_csv(path: Path, df: pd.DataFrame):
    """
    Helper: Cria arquivo CSV de teste
    
    Args:
        path: Caminho do arquivo
        df: DataFrame a salvar
        
    Returns:
        Path do arquivo criado
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path


def generate_random_customers(n: int = 100) -> pd.DataFrame:
    """
    Helper: Gera DataFrame aleatório de customers
    
    Args:
        n: Número de clientes
        
    Returns:
        DataFrame de customers
    """
    states = ['SP', 'RJ', 'MG', 'RS', 'PR', 'BA', 'CE', 'PE']
    
    return pd.DataFrame({
        'customer_id': [f'c{i}' for i in range(n)],
        'customer_unique_id': [f'u{i}' for i in range(n)],
        'customer_zip_code_prefix': [f'{np.random.randint(10000, 99999)}' for _ in range(n)],
        'customer_city': [f'City_{i}' for i in range(n)],
        'customer_state': np.random.choice(states, n)
    })


def generate_random_orders(n: int = 200, customer_ids: list = None) -> pd.DataFrame:
    """
    Helper: Gera DataFrame aleatório de orders
    
    Args:
        n: Número de pedidos
        customer_ids: Lista de customer_ids (gera se None)
        
    Returns:
        DataFrame de orders
    """
    if customer_ids is None:
        customer_ids = [f'c{i}' for i in range(100)]
    
    statuses = ['delivered', 'delivered', 'delivered', 'delivered', 'canceled', 'shipped']
    
    base_date = pd.Timestamp('2018-01-01')
    
    return pd.DataFrame({
        'order_id': [f'o{i}' for i in range(n)],
        'customer_id': np.random.choice(customer_ids, n),
        'order_status': np.random.choice(statuses, n),
        'order_purchase_timestamp': [
            base_date + pd.Timedelta(days=np.random.randint(0, 365)) 
            for _ in range(n)
        ]
    })


# ============================================
# CONFIGURATION
# ============================================

def pytest_configure(config):
    """Configuração customizada do pytest"""
    config.addinivalue_line(
        "markers", 
        "bigquery: marca testes que requerem conexão com BigQuery"
    )
    config.addinivalue_line(
        "markers", 
        "slow: marca testes lentos (> 5s)"
    )
    config.addinivalue_line(
        "markers",
        "integration: marca testes de integração"
    )
    config.addinivalue_line(
        "markers",
        "unit: marca testes unitários"
    )


# ============================================
# PYTEST HOOKS (OPCIONAL)
# ============================================

def pytest_collection_modifyitems(config, items):
    """
    Hook: Modifica items coletados
    Adiciona marker 'unit' automaticamente se não tiver bigquery/integration
    """
    for item in items:
        markers = [marker.name for marker in item.iter_markers()]
        
        # Se não tem bigquery nem integration, adiciona unit
        if 'bigquery' not in markers and 'integration' not in markers:
            item.add_marker(pytest.mark.unit)


def pytest_addoption(parser):
    """
    Hook: Adiciona opções customizadas ao pytest
    """
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="Executar testes de integração (requer BigQuery)"
    )


def pytest_runtest_setup(item):
    """
    Hook: Setup antes de cada teste
    Pula testes de integração se flag não estiver ativa
    """
    if 'integration' in [marker.name for marker in item.iter_markers()]:
        if not item.config.getoption("--run-integration"):
            pytest.skip("Testes de integração desabilitados. Use --run-integration")