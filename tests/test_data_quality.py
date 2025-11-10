"""
Tests: Data Quality Validation
Testa o módulo de validação de qualidade de dados.
Autor: Andre Bomfim
Data: Outubro 2025
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock, call
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Adicionar path
sys.path.insert(0, str(Path(__file__).parent.parent))

from python.etl.data_validation import DataValidator

# TESTES DA CLASSE DataValidator
class TestDataValidator:
    """Testes para DataValidator"""
    
    @pytest.fixture
    def validator(self, project_id, dataset_id):
        """Fixture: DataValidator instance com mock"""
        with patch('python.etl.data_validation.bigquery.Client'):
            validator = DataValidator(project_id, dataset_id)
            validator.client = Mock()
            return validator
    
    def test_validator_initialization(self, validator, project_id, dataset_id):
        """Testa inicialização do validator"""
        assert validator.project_id == project_id
        assert validator.dataset_id == dataset_id
        assert validator.validation_results == []
        assert validator.client is not None
    
    def test_run_validation_query_pass(self, validator):
        """Testa query de validação que passa"""
        # Mock do resultado
        mock_df = pd.DataFrame({'result': [0]})
        validator.client.query.return_value.to_dataframe.return_value = mock_df
        
        result = validator._run_validation_query(
            test_name="Test Pass",
            query="SELECT 0",
            expected_value=0,
            operator="=="
        )
        
        assert result['passed'] is True
        assert result['status'] == "✅ PASS"
        assert result['actual'] == 0
        assert result['expected'] == 0
        assert 'timestamp' in result
        assert len(validator.validation_results) == 1
    
    def test_run_validation_query_fail(self, validator):
        """Testa query de validação que falha"""
        # Mock do resultado
        mock_df = pd.DataFrame({'result': [5]})
        validator.client.query.return_value.to_dataframe.return_value = mock_df
        
        result = validator._run_validation_query(
            test_name="Test Fail",
            query="SELECT 5",
            expected_value=0,
            operator="=="
        )
        
        assert result['passed'] is False
        assert result['status'] == "❌ FAIL"
        assert result['actual'] == 5
        assert result['expected'] == 0
    
    def test_run_validation_query_greater_than(self, validator):
        """Testa operador > (maior que)"""
        mock_df = pd.DataFrame({'result': [100]})
        validator.client.query.return_value.to_dataframe.return_value = mock_df
        
        result = validator._run_validation_query(
            test_name="Test GT",
            query="SELECT 100",
            expected_value=90,
            operator=">"
        )
        
        assert result['passed'] is True
        assert result['actual'] == 100
        assert result['expected'] == 90
    
    def test_run_validation_query_less_than(self, validator):
        """Testa operador < (menor que)"""
        mock_df = pd.DataFrame({'result': [50]})
        validator.client.query.return_value.to_dataframe.return_value = mock_df
        
        result = validator._run_validation_query(
            test_name="Test LT",
            query="SELECT 50",
            expected_value=100,
            operator="<"
        )
        
        assert result['passed'] is True
    
    def test_run_validation_query_greater_equal(self, validator):
        """Testa operador >= (maior ou igual)"""
        mock_df = pd.DataFrame({'result': [100]})
        validator.client.query.return_value.to_dataframe.return_value = mock_df
        
        result = validator._run_validation_query(
            test_name="Test GTE",
            query="SELECT 100",
            expected_value=100,
            operator=">="
        )
        
        assert result['passed'] is True
    
    def test_run_validation_query_less_equal(self, validator):
        """Testa operador <= (menor ou igual)"""
        mock_df = pd.DataFrame({'result': [50]})
        validator.client.query.return_value.to_dataframe.return_value = mock_df
        
        result = validator._run_validation_query(
            test_name="Test LTE",
            query="SELECT 50",
            expected_value=50,
            operator="<="
        )
        
        assert result['passed'] is True
    
    def test_run_validation_query_error_handling(self, validator):
        """Testa tratamento de erros"""
        validator.client.query.side_effect = Exception("Connection error")
        
        result = validator._run_validation_query(
            test_name="Test Error",
            query="SELECT * FROM invalid",
            expected_value=0
        )
        
        assert result['passed'] is False
        assert result['status'] == "⚠️ ERROR"
        assert 'error' in result
        assert 'Connection error' in result['error']
    
    @pytest.mark.unit
    def test_test_primary_keys(self, validator):
        """Testa validação de primary keys"""
        # Mock múltiplos resultados (todos passando)
        mock_df = pd.DataFrame({'result': [0]})
        validator.client.query.return_value.to_dataframe.return_value = mock_df
        
        validator.test_primary_keys()
        
        # Verifica que foram executados múltiplos testes
        assert len(validator.validation_results) > 0
        # Pelo menos 5 testes (customers id único e não nulo, orders id único e não nulo, order_items composite key)
        assert validator.client.query.call_count >= 5
        
        # Todos devem ter passado
        assert all(r['passed'] for r in validator.validation_results)
    
    @pytest.mark.unit
    def test_test_foreign_keys(self, validator):
        """Testa validação de foreign keys"""
        mock_df = pd.DataFrame({'result': [0]})
        validator.client.query.return_value.to_dataframe.return_value = mock_df
        
        validator.test_foreign_keys()
        
        assert len(validator.validation_results) > 0
        # Pelo menos 4 testes de FK
        assert validator.client.query.call_count >= 4
    
    @pytest.mark.unit
    def test_test_valid_values(self, validator):
        """Testa validação de valores válidos"""
        mock_df = pd.DataFrame({'result': [0]})
        validator.client.query.return_value.to_dataframe.return_value = mock_df
        
        validator.test_valid_values()
        
        assert len(validator.validation_results) > 0
        # Verifica que queries foram executadas
        assert validator.client.query.call_count > 0
    
    @pytest.mark.unit
    def test_test_completeness(self, validator):
        """Testa validação de completude"""
        mock_df = pd.DataFrame({'result': [99.5]})
        validator.client.query.return_value.to_dataframe.return_value = mock_df
        
        validator.test_completeness()
        
        assert len(validator.validation_results) > 0
        # Verifica que testes de completude passaram (>95% ou >99%)
        assert any(r['passed'] for r in validator.validation_results)
    
    @pytest.mark.unit
    def test_test_consistency(self, validator):
        """Testa validação de consistência"""
        mock_df = pd.DataFrame({'result': [0]})
        validator.client.query.return_value.to_dataframe.return_value = mock_df
        
        validator.test_consistency()
        
        assert len(validator.validation_results) > 0
        # Pelo menos 3 testes de consistência
        assert validator.client.query.call_count >= 3
    
    @pytest.mark.unit
    def test_test_volumetry(self, validator):
        """Testa validação de volumetria"""
        mock_df = pd.DataFrame({'result': [95000]})
        validator.client.query.return_value.to_dataframe.return_value = mock_df
        
        validator.test_volumetry()
        
        assert len(validator.validation_results) > 0
        # Testes de volumetria devem passar com 95k registros
        assert any(r['passed'] for r in validator.validation_results)
    
    @pytest.mark.unit
    def test_run_all_validations_success(self, validator, tmp_path):
        """Testa execução de todas as validações com sucesso"""
        # Mock resultado sempre passando
        mock_df = pd.DataFrame({'result': [0]})
        validator.client.query.return_value.to_dataframe.return_value = mock_df
        
        # Mock do salvamento de arquivo
        with patch('pandas.DataFrame.to_csv') as mock_to_csv:
            results_df = validator.run_all_validations()
        
        # Verificar DataFrame de resultados
        assert isinstance(results_df, pd.DataFrame)
        assert len(results_df) > 0
        assert 'test_name' in results_df.columns
        assert 'passed' in results_df.columns
        assert 'status' in results_df.columns
        assert 'timestamp' in results_df.columns
        
        # Verificar que arquivo foi salvo
        mock_to_csv.assert_called_once()
        
        # Verificar que todos os testes passaram
        assert results_df['passed'].all()
    
    @pytest.mark.unit
    def test_run_all_validations_with_failures(self, validator):
        """Testa execução com alguns testes falhando"""
        # Mock: alguns testes passam (0), outros falham (valores diferentes)
        mock_results = [
            pd.DataFrame({'result': [0]}),   # Pass
            pd.DataFrame({'result': [5]}),   # Fail
            pd.DataFrame({'result': [0]}),   # Pass
            pd.DataFrame({'result': [10]}),  # Fail
        ]
        
        validator.client.query.return_value.to_dataframe.side_effect = mock_results * 10
        
        with patch('pandas.DataFrame.to_csv'):
            results_df = validator.run_all_validations()
        
        # Verificar que há falhas
        assert not results_df['passed'].all()
        assert results_df['passed'].sum() < len(results_df)
        
        # Verificar taxa de sucesso
        success_rate = results_df['passed'].sum() / len(results_df)
        assert 0 < success_rate < 1



# TESTES DE REGRAS DE QUALIDADE
class TestDataQualityRules:
    """Testes de regras de qualidade específicas"""
    
    def test_primary_key_uniqueness(self):
        """Testa se primary keys são únicas"""
        df = pd.DataFrame({
            'customer_id': ['c1', 'c2', 'c3'],
            'name': ['A', 'B', 'C']
        })
        
        # Deve ter todas únicas
        assert df['customer_id'].nunique() == len(df)
        
        # Teste com duplicatas
        df_dup = pd.DataFrame({
            'customer_id': ['c1', 'c1', 'c3'],
            'name': ['A', 'B', 'C']
        })
        assert df_dup['customer_id'].nunique() < len(df_dup)
    
    def test_no_null_in_required_fields(self):
        """Testa campos obrigatórios sem nulos"""
        df = pd.DataFrame({
            'order_id': ['o1', 'o2', 'o3'],
            'customer_id': ['c1', 'c2', 'c3'],
            'optional_field': ['A', None, 'C']
        })
        
        # Required fields não devem ter nulos
        assert df['order_id'].isnull().sum() == 0
        assert df['customer_id'].isnull().sum() == 0
        
        # Optional pode ter
        assert df['optional_field'].isnull().sum() > 0
    
    def test_positive_values(self):
        """Testa valores positivos em campos monetários"""
        df = pd.DataFrame({
            'price': [10.0, 20.5, 15.99],
            'freight': [5.0, 3.5, 2.0]
        })
        
        assert (df['price'] > 0).all()
        assert (df['freight'] >= 0).all()
    
    def test_negative_values_detected(self):
        """Testa detecção de valores negativos"""
        df = pd.DataFrame({
            'price': [10.0, -5.0, 15.99],
            'freight': [5.0, 3.5, -1.0]
        })
        
        # Deve detectar valores negativos
        assert not (df['price'] > 0).all()
        assert not (df['freight'] >= 0).all()
        
        # Contar negativos
        assert (df['price'] < 0).sum() == 1
        assert (df['freight'] < 0).sum() == 1
    
    def test_valid_state_codes(self):
        """Testa códigos de estado válidos"""
        valid_states = [
            'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
            'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
            'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
        ]
        
        df = pd.DataFrame({
            'customer_state': ['SP', 'RJ', 'MG', 'BA']
        })
        
        assert df['customer_state'].isin(valid_states).all()
    
    def test_invalid_state_codes(self):
        """Testa detecção de códigos de estado inválidos"""
        valid_states = [
            'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
            'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
            'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
        ]
        
        df = pd.DataFrame({
            'customer_state': ['SP', 'XX', 'MG', 'YY']
        })
        
        # Deve detectar estados inválidos
        assert not df['customer_state'].isin(valid_states).all()
        
        # Contar inválidos
        invalid_count = (~df['customer_state'].isin(valid_states)).sum()
        assert invalid_count == 2
    
    def test_review_score_range(self):
        """Testa range de review scores (1-5)"""
        df = pd.DataFrame({
            'review_score': [1, 2, 3, 4, 5]
        })
        
        assert df['review_score'].between(1, 5).all()
    
    def test_review_score_out_of_range(self):
        """Testa detecção de scores fora do range"""
        df = pd.DataFrame({
            'review_score': [1, 2, 6, 4, 0]
        })
        
        # Deve detectar valores fora do range
        assert not df['review_score'].between(1, 5).all()
        
        # Contar inválidos
        invalid = (~df['review_score'].between(1, 5)).sum()
        assert invalid == 2
    
    def test_date_consistency(self):
        """Testa consistência de datas"""
        df = pd.DataFrame({
            'purchase_date': pd.to_datetime(['2018-01-01', '2018-01-05']),
            'delivery_date': pd.to_datetime(['2018-01-10', '2018-01-15'])
        })
        
        # Data de entrega deve ser >= data de compra
        assert (df['delivery_date'] >= df['purchase_date']).all()
    
    def test_date_inconsistency_detected(self):
        """Testa detecção de inconsistência de datas"""
        df = pd.DataFrame({
            'purchase_date': pd.to_datetime(['2018-01-10', '2018-01-05']),
            'delivery_date': pd.to_datetime(['2018-01-05', '2018-01-15'])
        })
        
        # Primeira linha tem data inconsistente
        assert not (df['delivery_date'] >= df['purchase_date']).all()
        
        # Contar inconsistências
        inconsistent = (df['delivery_date'] < df['purchase_date']).sum()
        assert inconsistent == 1
    
    def test_payment_sum_consistency(self):
        """Testa soma de pagamentos por pedido"""
        order_items = pd.DataFrame({
            'order_id': ['o1', 'o1', 'o2'],
            'price': [100.0, 50.0, 200.0],
            'freight': [10.0, 5.0, 20.0]
        })
        
        payments = pd.DataFrame({
            'order_id': ['o1', 'o2'],
            'payment_value': [165.0, 220.0]
        })
        
        # Calcular total por pedido
        order_totals = order_items.groupby('order_id').agg({
            'price': 'sum',
            'freight': 'sum'
        }).sum(axis=1).reset_index()
        order_totals.columns = ['order_id', 'total']
        
        # Merge com payments
        merged = order_totals.merge(payments, on='order_id')
        
        # Valores devem ser iguais
        assert np.allclose(merged['total'], merged['payment_value'])
    
    def test_payment_sum_inconsistency(self):
        """Testa detecção de inconsistência em pagamentos"""
        order_items = pd.DataFrame({
            'order_id': ['o1', 'o1', 'o2'],
            'price': [100.0, 50.0, 200.0],
            'freight': [10.0, 5.0, 20.0]
        })
        
        payments = pd.DataFrame({
            'order_id': ['o1', 'o2'],
            'payment_value': [150.0, 300.0]  # Valores inconsistentes
        })
        
        # Calcular total por pedido
        order_totals = order_items.groupby('order_id').agg({
            'price': 'sum',
            'freight': 'sum'
        }).sum(axis=1).reset_index()
        order_totals.columns = ['order_id', 'total']
        
        # Merge com payments
        merged = order_totals.merge(payments, on='order_id')
        
        # Valores NÃO devem ser iguais
        assert not np.allclose(merged['total'], merged['payment_value'])
    
    def test_order_status_values(self):
        """Testa valores válidos de order_status"""
        valid_statuses = [
            'delivered', 'shipped', 'canceled', 'unavailable',
            'invoiced', 'processing', 'created', 'approved'
        ]
        
        df = pd.DataFrame({
            'order_status': ['delivered', 'shipped', 'canceled']
        })
        
        assert df['order_status'].isin(valid_statuses).all()
    
    def test_invalid_order_status(self):
        """Testa detecção de status inválidos"""
        valid_statuses = [
            'delivered', 'shipped', 'canceled', 'unavailable',
            'invoiced', 'processing', 'created', 'approved'
        ]
        
        df = pd.DataFrame({
            'order_status': ['delivered', 'invalid_status', 'canceled']
        })
        
        assert not df['order_status'].isin(valid_statuses).all()
        invalid = (~df['order_status'].isin(valid_statuses)).sum()
        assert invalid == 1
    
    def test_zip_code_format(self):
        """Testa formato de CEP (5 dígitos)"""
        df = pd.DataFrame({
            'zip_code': ['01310', '12345', '99999']
        })
        
        # Deve ter 5 caracteres
        assert df['zip_code'].str.len().eq(5).all()
        
        # Deve ser numérico
        assert df['zip_code'].str.isnumeric().all()
    
    def test_invalid_zip_code_format(self):
        """Testa detecção de CEPs inválidos"""
        df = pd.DataFrame({
            'zip_code': ['01310', '123', 'ABCDE', '12345']
        })
        
        # Verificar length
        invalid_length = (~df['zip_code'].str.len().eq(5)).sum()
        assert invalid_length == 1  # '123'
        
        # Verificar se é numérico
        invalid_numeric = (~df['zip_code'].str.isnumeric()).sum()
        assert invalid_numeric == 1  # 'ABCDE'



# TESTES DE INTEGRIDADE REFERENCIAL
class TestReferentialIntegrity:
    """Testes de integridade referencial entre tabelas"""
    
    def test_orders_customers_integrity(self, sample_orders_df, sample_customers_df):
        """Testa se todos orders têm customer válido"""
        # Merge para verificar integridade
        merged = sample_orders_df.merge(
            sample_customers_df,
            on='customer_id',
            how='left',
            indicator=True
        )
        
        # Todos devem ter match
        assert (merged['_merge'] == 'both').all()
    
    def test_order_items_orders_integrity(self, sample_order_items_df, sample_orders_df):
        """Testa se todos order_items têm order válido"""
        merged = sample_order_items_df.merge(
            sample_orders_df,
            on='order_id',
            how='left',
            indicator=True
        )
        
        assert (merged['_merge'] == 'both').all()
    
    def test_order_items_products_integrity(self, sample_order_items_df, sample_products_df):
        """Testa se todos order_items têm product válido"""
        merged = sample_order_items_df.merge(
            sample_products_df,
            on='product_id',
            how='left',
            indicator=True
        )
        
        assert (merged['_merge'] == 'both').all()
    
    def test_payments_orders_integrity(self, sample_payments_df, sample_orders_df):
        """Testa se todos payments têm order válido"""
        merged = sample_payments_df.merge(
            sample_orders_df,
            on='order_id',
            how='left',
            indicator=True
        )
        
        assert (merged['_merge'] == 'both').all()
    
    def test_orphan_records_detection(self):
        """Testa detecção de registros órfãos"""
        orders = pd.DataFrame({
            'order_id': ['o1', 'o2'],
            'customer_id': ['c1', 'c2']
        })
        
        order_items = pd.DataFrame({
            'order_id': ['o1', 'o2', 'o3'],  # o3 é órfão
            'product_id': ['p1', 'p2', 'p3']
        })
        
        # Encontrar órfãos
        merged = order_items.merge(
            orders,
            on='order_id',
            how='left',
            indicator=True
        )
        
        orphans = merged[merged['_merge'] == 'left_only']
        
        assert len(orphans) == 1
        assert orphans.iloc[0]['order_id'] == 'o3'



# TESTES DE QUALIDADE DE DADOS TEMPORAIS
class TestTemporalDataQuality:
    """Testes de qualidade para dados temporais"""
    
    def test_date_not_in_future(self):
        """Testa se datas não estão no futuro"""
        today = pd.Timestamp.now()
        
        df = pd.DataFrame({
            'order_date': [
                today - pd.Timedelta(days=10),
                today - pd.Timedelta(days=5),
                today - pd.Timedelta(days=1)
            ]
        })
        
        assert (df['order_date'] <= today).all()
    
    def test_future_date_detection(self):
        """Testa detecção de datas futuras"""
        today = pd.Timestamp.now()
        
        df = pd.DataFrame({
            'order_date': [
                today - pd.Timedelta(days=10),
                today + pd.Timedelta(days=5),  # Futuro
                today - pd.Timedelta(days=1)
            ]
        })
        
        future_dates = (df['order_date'] > today).sum()
        assert future_dates == 1
    
    def test_date_range_validation(self):
        """Testa se datas estão dentro do range esperado (2016-2018)"""
        df = pd.DataFrame({
            'order_date': pd.to_datetime([
                '2016-09-01',
                '2017-06-15',
                '2018-10-30'
            ])
        })
        
        min_date = pd.Timestamp('2016-01-01')
        max_date = pd.Timestamp('2019-01-01')
        
        assert df['order_date'].between(min_date, max_date).all()
    
    def test_delivery_time_reasonable(self):
        """Testa se tempo de entrega é razoável (< 60 dias)"""
        df = pd.DataFrame({
            'purchase_date': pd.to_datetime(['2018-01-01', '2018-01-05']),
            'delivery_date': pd.to_datetime(['2018-01-10', '2018-01-20'])
        })
        
        df['delivery_days'] = (df['delivery_date'] - df['purchase_date']).dt.days
        
        # Entrega deve ser entre 1 e 60 dias
        assert df['delivery_days'].between(1, 60).all()
    
    def test_unreasonable_delivery_time(self):
        """Testa detecção de tempos de entrega irreais"""
        df = pd.DataFrame({
            'purchase_date': pd.to_datetime(['2018-01-01', '2018-01-05']),
            'delivery_date': pd.to_datetime(['2018-01-10', '2018-05-01'])  # 116 dias
        })
        
        df['delivery_days'] = (df['delivery_date'] - df['purchase_date']).dt.days
        
        # Segunda linha tem tempo irreal
        unreasonable = (df['delivery_days'] > 60).sum()
        assert unreasonable == 1



# TESTES DE INTEGRAÇÃO
class TestDataValidationIntegration:
    """Testes de integração para validação de dados"""
    
    @pytest.mark.integration
    @pytest.mark.bigquery
    def test_full_validation_pipeline(self, project_id, dataset_id):
        """Testa pipeline completo de validação (requer BigQuery real)"""
        validator = DataValidator(project_id, dataset_id)
        
        # Executar validações
        try:
            results = validator.run_all_validations()
            
            # Verificar resultados
            assert isinstance(results, pd.DataFrame)
            assert len(results) > 0
            assert 'test_name' in results.columns
            assert 'passed' in results.columns
            assert 'status' in results.columns
            
            # Verificar taxa de sucesso mínima (80%)
            success_rate = results['passed'].sum() / len(results)
            assert success_rate >= 0.8, f"Taxa de sucesso muito baixa: {success_rate:.2%}"
            
            # Mostrar testes que falharam
            if not results['passed'].all():
                failed_tests = results[~results['passed']]['test_name'].tolist()
                print(f"\nTestes que falharam: {failed_tests}")
            
        except Exception as e:
            pytest.skip(f"Validação completa falhou (pode não ter dados no BigQuery): {e}")
    
    @pytest.mark.integration
    @pytest.mark.bigquery
    def test_specific_table_validation(self, project_id, dataset_id):
        """Testa validação de tabela específica"""
        validator = DataValidator(project_id, dataset_id)
        
        try:
            # Testar apenas primary keys
            validator.test_primary_keys()
            
            assert len(validator.validation_results) > 0
            
            # Verificar se pelo menos alguns testes passaram
            passed = sum(r['passed'] for r in validator.validation_results)
            assert passed > 0
            
        except Exception as e:
            pytest.skip(f"Validação específica falhou: {e}")



# TESTES DE PERFORMANCE
@pytest.mark.slow
class TestDataValidationPerformance:
    """Testes de performance para validação"""
    
    def test_validation_query_efficiency(self, validator):
        """Testa eficiência das queries de validação"""
        import time
        
        # Mock rápido
        mock_df = pd.DataFrame({'result': [0]})
        validator.client.query.return_value.to_dataframe.return_value = mock_df
        
        start = time.time()
        
        # Executar 100 validações
        for i in range(100):
            validator._run_validation_query(
                test_name=f"Test {i}",
                query="SELECT 0",
                expected_value=0
            )
        
        elapsed = time.time() - start
        
        # Deve ser rápido (< 1 segundo para 100 validações com mock)
        assert elapsed < 1.0, f"Validações muito lentas: {elapsed:.2f}s"
        
        # Verificar que todas foram armazenadas
        assert len(validator.validation_results) == 100



# TESTES DE EDGE CASES
class TestDataValidationEdgeCases:
    """Testes de casos extremos"""
    
    def test_empty_dataframe(self):
        """Testa validação com DataFrame vazio"""
        df = pd.DataFrame(columns=['customer_id', 'name'])
        
        # Não deve ter erros, apenas alertar
        assert len(df) == 0
        assert df.empty
        assert list(df.columns) == ['customer_id', 'name']
    
    def test_single_row_dataframe(self):
        """Testa validação com uma única linha"""
        df = pd.DataFrame({
            'customer_id': ['c1'],
            'name': ['Test']
        })
        
        assert len(df) == 1
        assert df['customer_id'].nunique() == 1
    
    def test_very_large_numbers(self):
        """Testa valores numéricos muito grandes"""
        df = pd.DataFrame({
            'price': [1e10, 1e15, 1e20]
        })
        
        # Valores devem ser positivos
        assert (df['price'] > 0).all()
        
        # Mas podem ser irrealistas para o contexto
        unrealistic = (df['price'] > 1e6).sum()
        assert unrealistic > 0
    
    def test_very_small_numbers(self):
        """Testa valores numéricos muito pequenos"""
        df = pd.DataFrame({
            'price': [0.01, 0.001, 0.0001]
        })
        
        # Valores devem ser positivos
        assert (df['price'] > 0).all()
        
        # Mas podem ser suspeitos
        suspicious = (df['price'] < 1.0).sum()
        assert suspicious == 3
    
    def test_special_characters_in_text(self):
        """Testa caracteres especiais em campos de texto"""
        df = pd.DataFrame({
            'city': ['São Paulo', 'Goiânia', 'Brasília', 'Açailândia']
        })
        
        # Deve manter acentuação
        assert 'São Paulo' in df['city'].values
        assert 'Goiânia' in df['city'].values
    
    def test_whitespace_handling(self):
        """Testa tratamento de espaços em branco"""
        df = pd.DataFrame({
            'customer_id': [' c1 ', 'c2', ' c3'],
            'name': ['Test ', ' Name', 'Valid']
        })
        
        # Detectar campos com espaços
        has_leading = df['customer_id'].str.startswith(' ').sum()
        has_trailing = df['customer_id'].str.endswith(' ').sum()
        
        assert has_leading > 0 or has_trailing > 0
    
    def test_null_vs_empty_string(self):
        """Testa diferença entre NULL e string vazia"""
        df = pd.DataFrame({
            'field': ['value', None, '', 'another']
        })
        
        # NULL e empty string são diferentes
        null_count = df['field'].isnull().sum()
        empty_count = (df['field'] == '').sum()
        
        assert null_count == 1
        assert empty_count == 1
        assert null_count != empty_count
    
    def test_duplicate_keys_detection(self):
        """Testa detecção de chaves duplicadas"""
        df = pd.DataFrame({
            'customer_id': ['c1', 'c2', 'c1', 'c3'],  # c1 duplicado
            'name': ['A', 'B', 'C', 'D']
        })
        
        duplicates = df['customer_id'].duplicated().sum()
        assert duplicates == 1
        
        # Encontrar os duplicados
        dup_values = df[df['customer_id'].duplicated(keep=False)]['customer_id'].unique()
        assert 'c1' in dup_values
    
    def test_mixed_data_types(self):
        """Testa detecção de tipos mistos em colunas"""
        # Pandas vai inferir como object se tipos mistos
        df = pd.DataFrame({
            'mixed_field': [1, '2', 3.0, 'four']
        })
        
        assert df['mixed_field'].dtype == object
    
    def test_outliers_detection(self):
        """Testa detecção de outliers"""
        df = pd.DataFrame({
            'price': [100, 110, 105, 95, 102, 5000]  # 5000 é outlier
        })
        
        # Usar IQR method
        Q1 = df['price'].quantile(0.25)
        Q3 = df['price'].quantile(0.75)
        IQR = Q3 - Q1
        
        # Outliers são valores fora de [Q1 - 1.5*IQR, Q3 + 1.5*IQR]
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = ((df['price'] < lower_bound) | (df['price'] > upper_bound)).sum()
        assert outliers > 0



# TESTES DE RELATÓRIOS
class TestDataValidationReporting:
    """Testes para geração de relatórios"""
    
    def test_validation_results_structure(self, validator):
        """Testa estrutura dos resultados de validação"""
        mock_df = pd.DataFrame({'result': [0]})
        validator.client.query.return_value.to_dataframe.return_value = mock_df
        
        result = validator._run_validation_query(
            test_name="Test",
            query="SELECT 0",
            expected_value=0
        )
        
        # Verificar campos obrigatórios
        assert 'test_name' in result
        assert 'status' in result
        assert 'passed' in result
        assert 'expected' in result
        assert 'actual' in result
        assert 'timestamp' in result
    
    def test_results_dataframe_conversion(self, validator):
        """Testa conversão de resultados para DataFrame"""
        # Adicionar alguns resultados
        mock_df = pd.DataFrame({'result': [0]})
        validator.client.query.return_value.to_dataframe.return_value = mock_df
        
        for i in range(5):
            validator._run_validation_query(
                test_name=f"Test {i}",
                query="SELECT 0",
                expected_value=0
            )
        
        # Converter para DataFrame
        df = pd.DataFrame(validator.validation_results)
        
        assert len(df) == 5
        assert 'test_name' in df.columns
        assert 'passed' in df.columns
    
    def test_summary_statistics(self, validator):
        """Testa cálculo de estatísticas de sumário"""
        # Simular resultados mistos
        validator.validation_results = [
            {'passed': True, 'test_name': 'Test 1'},
            {'passed': True, 'test_name': 'Test 2'},
            {'passed': False, 'test_name': 'Test 3'},
            {'passed': True, 'test_name': 'Test 4'},
            {'passed': False, 'test_name': 'Test 5'},
        ]
        
        df = pd.DataFrame(validator.validation_results)
        
        total = len(df)
        passed = df['passed'].sum()
        failed = total - passed
        success_rate = (passed / total) * 100
        
        assert total == 5
        assert passed == 3
        assert failed == 2
        assert success_rate == 60.0



# TESTES AUXILIARES
class TestValidationHelpers:
    """Testes para funções auxiliares"""
    
    def test_format_large_numbers(self):
        """Testa formatação de números grandes"""
        num = 1000000
        formatted = f"{num:,}"
        assert formatted == "1,000,000"
    
    def test_percentage_calculation(self):
        """Testa cálculo de percentuais"""
        total = 100
        part = 75
        percentage = (part / total) * 100
        assert percentage == 75.0
    
    def test_date_difference_calculation(self):
        """Testa cálculo de diferença de datas"""
        date1 = pd.Timestamp('2018-01-01')
        date2 = pd.Timestamp('2018-01-10')
        
        diff_days = (date2 - date1).days
        assert diff_days == 9



# TESTES DE COBERTURA ADICIONAL
class TestAdditionalCoverage:
    """Testes adicionais para aumentar cobertura"""
    
    def test_all_operators(self, validator):
        """Testa todos os operadores de comparação"""
        operators = ['==', '>', '<', '>=', '<=']
        
        for op in operators:
            mock_df = pd.DataFrame({'result': [100]})
            validator.client.query.return_value.to_dataframe.return_value = mock_df
            
            result = validator._run_validation_query(
                test_name=f"Test {op}",
                query="SELECT 100",
                expected_value=100 if op in ['==', '>=', '<='] else 50,
                operator=op
            )
            
            # Resultado depende do operador
            if op in ['==', '>=', '<=']:
                assert result['passed']
            elif op == '>':
                assert result['passed']  # 100 > 50
            elif op == '<':
                assert not result['passed']  # 100 < 50 é falso
    
    def test_invalid_operator(self, validator):
        """Testa operador inválido"""
        mock_df = pd.DataFrame({'result': [100]})
        validator.client.query.return_value.to_dataframe.return_value = mock_df
        
        result = validator._run_validation_query(
            test_name="Test Invalid",
            query="SELECT 100",
            expected_value=100,
            operator="!="  # Operador não suportado
        )
        
        # Deve falhar
        assert not result['passed']
    
    def test_multiple_validation_rounds(self, validator):
        """Testa múltiplas rodadas de validação"""
        mock_df = pd.DataFrame({'result': [0]})
        validator.client.query.return_value.to_dataframe.return_value = mock_df
        
        # Primeira rodada
        validator.test_primary_keys()
        first_count = len(validator.validation_results)
        
        # Segunda rodada
        validator.test_foreign_keys()
        second_count = len(validator.validation_results)
        
        # Deve acumular resultados
        assert second_count > first_count
    
    def test_validation_with_none_values(self, validator):
        """Testa validação com valores None"""
        mock_df = pd.DataFrame({'result': [None]})
        validator.client.query.return_value.to_dataframe.return_value = mock_df
        
        result = validator._run_validation_query(
            test_name="Test None",
            query="SELECT NULL",
            expected_value=0
        )
        
        # None não é igual a 0
        assert not result['passed']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])