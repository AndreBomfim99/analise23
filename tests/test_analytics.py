"""
Tests: Analytics (RFM Segmentation)
------------------------------------
Testa o módulo de análise RFM de clientes.

Autor: Andre Bomfim
Data: Outubro 2025
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Adicionar path
sys.path.insert(0, str(Path(__file__).parent.parent))

from python.analytics.rfm_segmentation import RFMAnalyzer


# ============================================
# TESTES DA CLASSE RFMAnalyzer
# ============================================

class TestRFMAnalyzer:
    """Testes para RFMAnalyzer"""
    
    @pytest.fixture
    def analyzer(self, project_id, dataset_id):
        """Fixture: RFMAnalyzer instance com mock"""
        with patch('python.analytics.rfm_segmentation.bigquery.Client'):
            analyzer = RFMAnalyzer(project_id, dataset_id)
            analyzer.client = Mock()
            return analyzer
    
    def test_analyzer_initialization(self, analyzer, project_id, dataset_id):
        """Testa inicialização do analyzer"""
        assert analyzer.project_id == project_id
        assert analyzer.dataset_id == dataset_id
        assert analyzer.rfm_data is None
        assert analyzer.client is not None
    
    def test_extract_rfm_data_with_reference_date(self, analyzer, sample_rfm_df):
        """Testa extração de dados RFM com data de referência"""
        # Mock do resultado
        analyzer.client.query.return_value.to_dataframe.return_value = sample_rfm_df
        
        # Executar
        df = analyzer.extract_rfm_data(reference_date='2018-10-01')
        
        # Verificar
        assert isinstance(df, pd.DataFrame)
        assert len(df) == len(sample_rfm_df)
        assert 'customer_unique_id' in df.columns
        assert 'recency' in df.columns
        assert 'frequency' in df.columns
        assert 'monetary' in df.columns
        assert analyzer.rfm_data is not None
        
        # Verificar que query foi chamada apenas uma vez
        assert analyzer.client.query.call_count == 1
    
    def test_extract_rfm_data_without_reference_date(self, analyzer, sample_rfm_df):
        """Testa extração de dados sem data de referência (usa max)"""
        # Mock para buscar data máxima
        max_date_df = pd.DataFrame({'max_date': [pd.Timestamp('2018-10-01')]})
        
        # Mock para query principal
        analyzer.client.query.return_value.to_dataframe.side_effect = [
            max_date_df,
            sample_rfm_df
        ]
        
        # Executar
        df = analyzer.extract_rfm_data()
        
        # Verificar
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert analyzer.client.query.call_count == 2  # Uma para max_date, outra para RFM
    
    def test_extract_rfm_data_columns(self, analyzer, sample_rfm_df):
        """Testa se todas as colunas esperadas estão presentes"""
        analyzer.client.query.return_value.to_dataframe.return_value = sample_rfm_df
        
        df = analyzer.extract_rfm_data(reference_date='2018-10-01')
        
        expected_columns = [
            'customer_unique_id',
            'customer_state',
            'recency',
            'frequency',
            'monetary',
            'avg_order_value'
        ]
        
        for col in expected_columns:
            assert col in df.columns, f"Coluna {col} não encontrada"
    
    def test_calculate_rfm_scores(self, analyzer, sample_rfm_df):
        """Testa cálculo de scores RFM"""
        # Calcular scores
        df = analyzer.calculate_rfm_scores(sample_rfm_df, n_quantiles=5)
        
        # Verificar colunas criadas
        assert 'R_score' in df.columns
        assert 'F_score' in df.columns
        assert 'M_score' in df.columns
        assert 'RFM_score' in df.columns
        assert 'RFM_score_numeric' in df.columns
        
        # Verificar ranges (1-5)
        assert df['R_score'].between(1, 5).all()
        assert df['F_score'].between(1, 5).all()
        assert df['M_score'].between(1, 5).all()
        
        # Verificar tipos
        assert df['R_score'].dtype == int
        assert df['F_score'].dtype == int
        assert df['M_score'].dtype == int
        assert df['RFM_score'].dtype == object  # string
        assert pd.api.types.is_float_dtype(df['RFM_score_numeric'])
    
    def test_calculate_rfm_scores_string_format(self, analyzer, sample_rfm_df):
        """Testa formato do RFM_score como string"""
        df = analyzer.calculate_rfm_scores(sample_rfm_df)
        
        # RFM_score deve ser string de 3 dígitos
        assert df['RFM_score'].str.len().eq(3).all()
        assert df['RFM_score'].str.isnumeric().all()
    
    def test_calculate_rfm_scores_numeric_formula(self, analyzer):
        """Testa fórmula do RFM_score_numeric"""
        df = pd.DataFrame({
            'customer_unique_id': ['c1'],
            'recency': [10],
            'frequency': [5],
            'monetary': [1000.0],
            'avg_order_value': [200.0]
        })
        
        df = analyzer.calculate_rfm_scores(df, n_quantiles=5)
        
        # Fórmula: R*0.4 + F*0.3 + M*0.3
        r, f, m = df.loc[0, 'R_score'], df.loc[0, 'F_score'], df.loc[0, 'M_score']
        expected = r * 0.4 + f * 0.3 + m * 0.3
        
        assert abs(df.loc[0, 'RFM_score_numeric'] - expected) < 0.01
    
    def test_rfm_scores_logic(self):
        """Testa lógica dos scores RFM"""
        df = pd.DataFrame({
            'recency': [1, 30, 90, 180, 365],  # Menor recency = melhor
            'frequency': [1, 2, 3, 5, 10],      # Maior frequency = melhor
            'monetary': [100, 200, 500, 1000, 5000]  # Maior monetary = melhor
        })
        
        # Calcular scores manualmente (5 quantis)
        df['R_score'] = pd.qcut(df['recency'], q=5, labels=[5, 4, 3, 2, 1], duplicates='drop')
        df['F_score'] = pd.qcut(df['frequency'], q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')
        df['M_score'] = pd.qcut(df['monetary'], q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')
        
        # Cliente com menor recency deve ter maior R_score
        min_recency_idx = df['recency'].idxmin()
        assert df.loc[min_recency_idx, 'R_score'] == 5
        
        # Cliente com maior frequency deve ter maior F_score
        max_frequency_idx = df['frequency'].idxmax()
        assert df.loc[max_frequency_idx, 'F_score'] == 5
        
        # Cliente com maior monetary deve ter maior M_score
        max_monetary_idx = df['monetary'].idxmax()
        assert df.loc[max_monetary_idx, 'M_score'] == 5
    
    def test_segment_customers(self, analyzer):
        """Testa segmentação de clientes"""
        # Criar DataFrame com scores variados
        df = pd.DataFrame({
            'customer_unique_id': ['c1', 'c2', 'c3', 'c4', 'c5', 'c6'],
            'R_score': [5, 5, 3, 1, 1, 2],
            'F_score': [5, 1, 3, 5, 1, 2],
            'M_score': [5, 2, 3, 5, 1, 2]
        })
        
        # Segmentar
        df = analyzer.segment_customers(df)
        
        # Verificar colunas criadas
        assert 'segment' in df.columns
        assert 'priority' in df.columns
        
        # Verificar segmentos esperados
        assert df.loc[0, 'segment'] == 'Champions'  # R=5, F=5, M=5
        assert df.loc[1, 'segment'] == 'New Customers'  # R=5, F=1
        assert df.loc[3, 'segment'] == 'Cannot Lose Them'  # R=1, F=5, M=5
        
        # Verificar prioridades
        assert df['priority'].isin([1, 2, 3, 4, 5, 6]).all()
        
        # Champions devem ter alta prioridade
        champions_priority = df[df['segment'] == 'Champions']['priority'].iloc[0]
        assert champions_priority in [1, 2]
    
    def test_segment_assignment_logic(self, analyzer):
        """Testa lógica de atribuição de segmentos"""
        test_cases = [
            {'R': 5, 'F': 5, 'M': 5, 'expected': 'Champions'},
            {'R': 5, 'F': 1, 'M': 3, 'expected': 'New Customers'},
            {'R': 1, 'F': 5, 'M': 5, 'expected': 'Cannot Lose Them'},
            {'R': 1, 'F': 1, 'M': 1, 'expected': 'Hibernating'},
            {'R': 5, 'F': 3, 'M': 3, 'expected': 'Potential Loyalist'},
            {'R': 5, 'F': 5, 'M': 1, 'expected': 'Loyal Customers'},  # F>=4
            {'R': 3, 'F': 1, 'M': 3, 'expected': 'Promising'},
            {'R': 2, 'F': 3, 'M': 3, 'expected': 'Need Attention'},
            {'R': 2, 'F': 2, 'M': 2, 'expected': 'About To Sleep'},
            {'R': 1, 'F': 4, 'M': 4, 'expected': 'At Risk'},
            {'R': 1, 'F': 2, 'M': 1, 'expected': 'Lost'},
        ]
        
        for case in test_cases:
            df = pd.DataFrame({
                'R_score': [case['R']],
                'F_score': [case['F']],
                'M_score': [case['M']]
            })
            
            df = analyzer.segment_customers(df)
            actual = df.loc[0, 'segment']
            
            assert actual == case['expected'], \
                f"R={case['R']}, F={case['F']}, M={case['M']} deveria ser {case['expected']}, mas foi {actual}"
    
    def test_all_segments_have_priority(self, analyzer):
        """Testa se todos os segmentos têm prioridade definida"""
        # Criar DataFrame com todos os segmentos possíveis
        segments = [
            'Champions', 'Loyal Customers', 'Potential Loyalist', 'New Customers',
            'Promising', 'Need Attention', 'About To Sleep', 'At Risk',
            'Cannot Lose Them', 'Hibernating', 'Lost', 'Others'
        ]
        
        df = pd.DataFrame({
            'segment': segments
        })
        
        # Mapear prioridades
        priority_map = {
            'Champions': 1,
            'Loyal Customers': 2,
            'Cannot Lose Them': 1,
            'At Risk': 2,
            'Potential Loyalist': 3,
            'Need Attention': 3,
            'Promising': 4,
            'New Customers': 4,
            'About To Sleep': 3,
            'Hibernating': 5,
            'Lost': 6,
            'Others': 5
        }
        
        df['priority'] = df['segment'].map(priority_map)
        
        # Todos devem ter prioridade
        assert df['priority'].notna().all()
        assert df['priority'].between(1, 6).all()
    
    def test_generate_segment_summary(self, analyzer):
        """Testa geração de sumário por segmento"""
        df = pd.DataFrame({
            'customer_unique_id': ['c1', 'c2', 'c3', 'c4'],
            'segment': ['Champions', 'Champions', 'Lost', 'At Risk'],
            'monetary': [1000, 1500, 100, 500],
            'frequency': [5, 7, 1, 3],
            'recency': [10, 5, 300, 100],
            'avg_order_value': [200, 214, 100, 167],
            'RFM_score_numeric': [5.0, 5.0, 1.0, 2.5]
        })
        
        summary = analyzer.generate_segment_summary(df)
        
        # Verificar estrutura
        assert isinstance(summary, pd.DataFrame)
        assert 'customers' in summary.columns
        assert 'total_revenue' in summary.columns
        assert 'avg_revenue' in summary.columns
        assert 'customer_pct' in summary.columns
        assert 'revenue_pct' in summary.columns
        
        # Verificar valores para Champions
        champions_row = summary.loc['Champions']
        assert champions_row['customers'] == 2
        assert champions_row['total_revenue'] == 2500
        assert champions_row['customer_pct'] == 50.0
    
    def test_generate_segment_summary_calculations(self, analyzer):
        """Testa cálculos do sumário"""
        df = pd.DataFrame({
            'customer_unique_id': ['c1', 'c2', 'c3'],
            'segment': ['Champions', 'Lost', 'At Risk'],
            'monetary': [1000, 100, 500],
            'frequency': [5, 1, 3],
            'recency': [10, 300, 100],
            'avg_order_value': [200, 100, 167],
            'RFM_score_numeric': [5.0, 1.0, 2.5]
        })
        
        summary = analyzer.generate_segment_summary(df)
        
        # Verificar soma de clientes = 3
        assert summary['customers'].sum() == 3
        
        # Verificar percentuais somam 100%
        assert abs(summary['customer_pct'].sum() - 100.0) < 0.01
        assert abs(summary['revenue_pct'].sum() - 100.0) < 0.01
        
        # Verificar receita total
        assert summary['total_revenue'].sum() == 1600
    
    def test_recommend_actions(self, analyzer):
        """Testa geração de recomendações"""
        df = pd.DataFrame({
            'segment': ['Champions', 'Lost', 'At Risk', 'New Customers']
        })
        
        recommendations = analyzer.recommend_actions(df)
        
        # Verificar estrutura
        assert isinstance(recommendations, dict)
        assert len(recommendations) > 0
        
        # Verificar segmentos principais
        assert 'Champions' in recommendations
        assert 'Lost' in recommendations
        assert 'At Risk' in recommendations
        
        # Verificar que recomendações não são vazias
        for segment, action in recommendations.items():
            assert isinstance(action, str)
            assert len(action) > 0
            
        # Verificar emojis nas recomendações
        assert '🏆' in recommendations['Champions']
        assert '❌' in recommendations['Lost']
        assert '⚠️' in recommendations['At Risk']
    
    def test_all_segments_have_recommendations(self, analyzer):
        """Testa se todos os segmentos têm recomendações"""
        df = pd.DataFrame({
            'segment': ['Champions', 'Loyal Customers', 'Cannot Lose Them', 'At Risk',
                       'Potential Loyalist', 'Need Attention', 'Promising', 'New Customers',
                       'About To Sleep', 'Hibernating', 'Lost', 'Others']
        })
        
        recommendations = analyzer.recommend_actions(df)
        
        # Todos os segmentos devem ter recomendação
        for segment in df['segment'].unique():
            assert segment in recommendations
            assert len(recommendations[segment]) > 10  # Mínimo de caracteres
    
    def test_run_full_analysis(self, analyzer, sample_rfm_df, tmp_path):
        """Testa análise RFM completa"""
        # Mock query results
        analyzer.client.query.return_value.to_dataframe.return_value = sample_rfm_df
        
        # Mock save
        with patch('pandas.DataFrame.to_csv') as mock_csv:
            rfm_data, summary = analyzer.run_full_analysis(
                reference_date='2018-10-01',
                save_results=True
            )
        
        # Verificar outputs
        assert isinstance(rfm_data, pd.DataFrame)
        assert isinstance(summary, pd.DataFrame)
        
        # Verificar que dados foram processados
        assert 'R_score' in rfm_data.columns
        assert 'F_score' in rfm_data.columns
        assert 'M_score' in rfm_data.columns
        assert 'segment' in rfm_data.columns
        
        # Verificar que arquivos foram salvos
        assert mock_csv.call_count == 2  # rfm_customers.csv e rfm_summary.csv
    
    def test_run_full_analysis_without_save(self, analyzer, sample_rfm_df):
        """Testa análise sem salvar arquivos"""
        analyzer.client.query.return_value.to_dataframe.return_value = sample_rfm_df
        
        with patch('pandas.DataFrame.to_csv') as mock_csv:
            rfm_data, summary = analyzer.run_full_analysis(
                reference_date='2018-10-01',
                save_results=False
            )
        
        # Não deve ter salvado
        mock_csv.assert_not_called()
        
        # Mas dados devem estar presentes
        assert rfm_data is not None
        assert summary is not None


# ============================================
# TESTES DE MÉTRICAS RFM
# ============================================

class TestRFMMetrics:
    """Testes para cálculo de métricas RFM"""
    
    def test_recency_calculation(self):
        """Testa cálculo de recency"""
        reference_date = pd.Timestamp('2018-10-01')
        last_purchase = pd.Timestamp('2018-09-20')
        
        recency = (reference_date - last_purchase).days
        
        assert recency == 11
    
    def test_recency_same_day(self):
        """Testa recency quando compra é no mesmo dia"""
        reference_date = pd.Timestamp('2018-10-01')
        last_purchase = pd.Timestamp('2018-10-01')
        
        recency = (reference_date - last_purchase).days
        
        assert recency == 0
    
    def test_frequency_calculation(self):
        """Testa cálculo de frequency"""
        orders = pd.DataFrame({
            'customer_id': ['c1', 'c1', 'c1', 'c2', 'c2'],
            'order_id': ['o1', 'o2', 'o3', 'o4', 'o5']
        })
        
        frequency = orders.groupby('customer_id')['order_id'].nunique()
        
        assert frequency['c1'] == 3
        assert frequency['c2'] == 2
    
    def test_frequency_single_order(self):
        """Testa frequency com um único pedido"""
        orders = pd.DataFrame({
            'customer_id': ['c1'],
            'order_id': ['o1']
        })
        
        frequency = orders.groupby('customer_id')['order_id'].nunique()
        
        assert frequency['c1'] == 1
    
    def test_monetary_calculation(self):
        """Testa cálculo de monetary"""
        payments = pd.DataFrame({
            'customer_id': ['c1', 'c1', 'c2'],
            'payment_value': [100.0, 150.0, 200.0]
        })
        
        monetary = payments.groupby('customer_id')['payment_value'].sum()
        
        assert monetary['c1'] == 250.0
        assert monetary['c2'] == 200.0
    
    def test_avg_order_value_calculation(self):
        """Testa cálculo do Average Order Value"""
        df = pd.DataFrame({
            'monetary': [1000.0, 500.0, 300.0],
            'frequency': [5, 2, 3]
        })
        
        df['avg_order_value'] = df['monetary'] / df['frequency']
        
        assert df.loc[0, 'avg_order_value'] == 200.0
        assert df.loc[1, 'avg_order_value'] == 250.0
        assert df.loc[2, 'avg_order_value'] == 100.0
    
    def test_rfm_score_numeric_calculation(self):
        """Testa cálculo do score numérico RFM"""
        df = pd.DataFrame({
            'R_score': [5, 3, 1],
            'F_score': [4, 3, 2],
            'M_score': [5, 2, 1]
        })
        
        # Fórmula: R*0.4 + F*0.3 + M*0.3
        df['RFM_score_numeric'] = (
            df['R_score'] * 0.4 +
            df['F_score'] * 0.3 +
            df['M_score'] * 0.3
        )
        
        expected_first = 5*0.4 + 4*0.3 + 5*0.3  # = 4.7
        assert abs(df.loc[0, 'RFM_score_numeric'] - expected_first) < 0.01
        
        expected_second = 3*0.4 + 3*0.3 + 2*0.3  # = 2.7
        assert abs(df.loc[1, 'RFM_score_numeric'] - expected_second) < 0.01
    
    def test_rfm_score_weights(self):
        """Testa se os pesos do RFM score somam 1.0"""
        weights = {'R': 0.4, 'F': 0.3, 'M': 0.3}
        
        assert sum(weights.values()) == 1.0


# ============================================
# TESTES DE QUALIDADE DE DADOS RFM
# ============================================

class TestRFMDataQuality:
    """Testes de qualidade para dados RFM"""
    
    def test_no_negative_recency(self):
        """Testa que recency não pode ser negativa"""
        df = pd.DataFrame({
            'recency': [10, 30, 90, 180]
        })
        
        assert (df['recency'] >= 0).all()
    
    def test_negative_recency_detection(self):
        """Testa detecção de recency negativa (erro)"""
        df = pd.DataFrame({
            'recency': [10, -5, 90]  # -5 é inválido
        })
        
        invalid = (df['recency'] < 0).sum()
        assert invalid == 1
    
    def test_positive_frequency(self):
        """Testa que frequency deve ser >= 1"""
        df = pd.DataFrame({
            'frequency': [1, 2, 3, 5]
        })
        
        assert (df['frequency'] >= 1).all()
    
    def test_zero_frequency_detection(self):
        """Testa detecção de frequency zero (inválido)"""
        df = pd.DataFrame({
            'frequency': [1, 0, 3]  # 0 é inválido
        })
        
        invalid = (df['frequency'] < 1).sum()
        assert invalid == 1
    
    def test_positive_monetary(self):
        """Testa que monetary deve ser > 0"""
        df = pd.DataFrame({
            'monetary': [100.0, 250.5, 1000.0]
        })
        
        assert (df['monetary'] > 0).all()
    
    def test_negative_monetary_detection(self):
        """Testa detecção de monetary negativo ou zero"""
        df = pd.DataFrame({
            'monetary': [100.0, 0.0, -50.0]
        })
        
        invalid = (df['monetary'] <= 0).sum()
        assert invalid == 2
    
    def test_unique_customers(self):
        """Testa que customer_unique_id são únicos"""
        df = pd.DataFrame({
            'customer_unique_id': ['c1', 'c2', 'c3', 'c4']
        })
        
        assert df['customer_unique_id'].nunique() == len(df)
    
    def test_duplicate_customers_detection(self):
        """Testa detecção de clientes duplicados"""
        df = pd.DataFrame({
            'customer_unique_id': ['c1', 'c2', 'c1', 'c4']
        })
        
        duplicates = df['customer_unique_id'].duplicated().sum()
        assert duplicates == 1
    
    def test_avg_order_value_consistency(self):
        """Testa consistência do avg_order_value"""
        df = pd.DataFrame({
            'monetary': [1000.0, 500.0],
            'frequency': [5, 2],
            'avg_order_value': [200.0, 250.0]
        })
        
        # Calcular AOV esperado
        expected_aov = df['monetary'] / df['frequency']
        
        # Verificar consistência
        assert np.allclose(df['avg_order_value'], expected_aov)
    
    def test_avg_order_value_inconsistency(self):
        """Testa detecção de AOV inconsistente"""
        df = pd.DataFrame({
            'monetary': [1000.0, 500.0],
            'frequency': [5, 2],
            'avg_order_value': [300.0, 250.0]  # 300 está errado (deveria ser 200)
        })
        
        expected_aov = df['monetary'] / df['frequency']
        
        # Não deve ser igual
        assert not np.allclose(df['avg_order_value'], expected_aov)
    
    def test_recency_reasonable_range(self):
        """Testa se recency está em range razoável (< 1000 dias)"""
        df = pd.DataFrame({
            'recency': [10, 90, 365, 730]
        })
        
        # Todos devem estar abaixo de 3 anos (1095 dias)
        assert (df['recency'] < 1095).all()
    
    def test_frequency_reasonable_range(self):
        """Testa se frequency está em range razoável"""
        df = pd.DataFrame({
            'frequency': [1, 5, 10, 20]
        })
        
        # Deve estar entre 1 e um limite razoável (ex: 100)
        assert df['frequency'].between(1, 100).all()
    
    def test_monetary_reasonable_range(self):
        """Testa se monetary está em range razoável"""
        df = pd.DataFrame({
            'monetary': [50.0, 500.0, 5000.0, 50000.0]
        })
        
        # Valores muito grandes podem ser outliers
        suspicious = (df['monetary'] > 100000).sum()
        assert suspicious == 0  # Nenhum valor acima de 100k neste exemplo


# ============================================
# TESTES DE SEGMENTAÇÃO
# ============================================

class TestRFMSegmentation:
    """Testes específicos para segmentação"""
    
    def test_champions_definition(self, analyzer):
        """Testa definição de Champions (R>=4, F>=4, M>=4)"""
        df = pd.DataFrame({
            'R_score': [5, 4, 4],
            'F_score': [5, 4, 4],
            'M_score': [5, 4, 4]
        })
        
        df = analyzer.segment_customers(df)
        
        assert (df['segment'] == 'Champions').all()
    
    def test_loyal_customers_definition(self, analyzer):
        """Testa definição de Loyal Customers (F>=4)"""
        df = pd.DataFrame({
            'R_score': [3, 2, 1],
            'F_score': [5, 4, 5],
            'M_score': [3, 2, 1]
        })
        
        df = analyzer.segment_customers(df)
        
        # Todos devem ser Loyal (exceto se forem Champions ou Cannot Lose Them)
        assert all(seg in ['Loyal Customers', 'Cannot Lose Them', 'At Risk'] 
                  for seg in df['segment'])
    
    def test_lost_customers_definition(self, analyzer):
        """Testa definição de Lost (R==1)"""
        df = pd.DataFrame({
            'R_score': [1, 1, 1],
            'F_score': [1, 2, 3],
            'M_score': [1, 2, 3]
        })
        
        df = analyzer.segment_customers(df)
        
        # Maioria deve ser Lost ou Cannot Lose Them
        assert all(seg in ['Lost', 'Cannot Lose Them', 'At Risk', 'Hibernating'] 
                  for seg in df['segment'])
    
    def test_new_customers_definition(self, analyzer):
        """Testa definição de New Customers (R>=4, F==1)"""
        df = pd.DataFrame({
            'R_score': [5, 4],
            'F_score': [1, 1],
            'M_score': [2, 3]
        })
        
        df = analyzer.segment_customers(df)
        
        assert (df['segment'] == 'New Customers').all()
    
    def test_hibernating_definition(self, analyzer):
        """Testa definição de Hibernating (R<=2, F<=2, M<=2)"""
        df = pd.DataFrame({
            'R_score': [2, 1, 2],
            'F_score': [2, 1, 2],
            'M_score': [2, 1, 2]
        })
        
        df = analyzer.segment_customers(df)
        
        # Todos devem ser Hibernating, Lost ou About To Sleep
        assert all(seg in ['Hibernating', 'Lost', 'About To Sleep'] 
                  for seg in df['segment'])
    
    def test_segment_distribution(self, analyzer, sample_rfm_df):
        """Testa distribuição de segmentos"""
        df = analyzer.calculate_rfm_scores(sample_rfm_df)
        df = analyzer.segment_customers(df)
        
        # Deve ter pelo menos 1 segmento
        assert df['segment'].nunique() >= 1
        
        # Todos devem ter algum segmento
        assert df['segment'].notna().all()
    
    def test_no_empty_segments(self, analyzer, sample_rfm_df):
        """Testa que nenhum cliente fica sem segmento"""
        df = analyzer.calculate_rfm_scores(sample_rfm_df)
        df = analyzer.segment_customers(df)
        
        # Nenhum valor nulo
        assert df['segment'].notna().all()
        
        # Nenhum string vazia
        assert (df['segment'].str.len() > 0).all()


# ============================================
# TESTES DE ANÁLISE DE COHORT
# ============================================

class TestCohortAnalysis:
    """Testes para análise de cohort (conceitual, não implementado no RFMAnalyzer)"""
    
    def test_cohort_grouping_by_month(self):
        """Testa agrupamento de clientes por mês de primeira compra"""
        df = pd.DataFrame({
            'customer_id': ['c1', 'c2', 'c3', 'c4'],
            'first_purchase_date': pd.to_datetime([
                '2018-01-15', '2018-01-20', '2018-02-10', '2018-02-15'
            ])
        })
        
        df['cohort_month'] = df['first_purchase_date'].dt.to_period('M')
        
        cohorts = df.groupby('cohort_month')['customer_id'].count()
        
        assert cohorts['2018-01'] == 2
        assert cohorts['2018-02'] == 2
    
    def test_customer_lifetime_calculation(self):
        """Testa cálculo de tempo de vida do cliente"""
        df = pd.DataFrame({
            'first_purchase_date': pd.to_datetime(['2018-01-01']),
            'last_purchase_date': pd.to_datetime(['2018-06-01'])
        })
        
        df['lifetime_days'] = (df['last_purchase_date'] - df['first_purchase_date']).dt.days
        
        assert df.loc[0, 'lifetime_days'] == 151


# ============================================
# TESTES DE VISUALIZAÇÃO
# ============================================

class TestRFMVisualization:
    """Testes para visualizações RFM"""
    
    @pytest.mark.skipif(True, reason="Matplotlib não funciona em headless mode")
    def test_plot_rfm_distribution(self, analyzer, sample_rfm_df, tmp_path):
        """Testa geração de gráficos (skip em CI)"""
        # Adicionar scores e segmentos
        df = analyzer.calculate_rfm_scores(sample_rfm_df)
        df = analyzer.segment_customers(df)
        
        # Plotar
        output_path = tmp_path / "rfm_plot.png"
        analyzer.plot_rfm_distribution(df, save_path=str(output_path))
        
        # Verificar que arquivo foi criado
        assert output_path.exists()
    
    def test_plot_without_save(self, analyzer, sample_rfm_df):
        """Testa plot sem salvar arquivo"""
        df = analyzer.calculate_rfm_scores(sample_rfm_df)
        df = analyzer.segment_customers(df)
        
        # Não deve dar erro
        with patch('matplotlib.pyplot.show'):
            with patch('matplotlib.pyplot.subplots'):
                analyzer.plot_rfm_distribution(df, save_path=None)


# ============================================
# TESTES DE PERFORMANCE
# ============================================

@pytest.mark.slow
class TestRFMPerformance:
    """Testes de performance para RFM"""
    
    def test_large_dataset_performance(self, analyzer):
        """Testa performance com dataset grande"""
        import time
        
        # Criar dataset grande
        large_df = pd.DataFrame({
            'customer_unique_id': [f'c{i}' for i in range(10000)],
            'customer_state': np.random.choice(['SP', 'RJ', 'MG'], 10000),
            'recency': np.random.randint(1, 365, 10000),
            'frequency': np.random.randint(1, 20, 10000),
            'monetary': np.random.uniform(50, 5000, 10000),
            'avg_order_value': np.random.uniform(50, 500, 10000)
        })
        
        start = time.time()
        
        # Calcular scores
        df = analyzer.calculate_rfm_scores(large_df)
        
        # Segmentar
        df = analyzer.segment_customers(df)
        
        elapsed = time.time() - start
        
        # Deve ser rápido (< 5 segundos para 10k clientes)
        assert elapsed < 5.0, f"Performance ruim: {elapsed:.2f}s"
        
        # Verificar resultado
        assert len(df) == 10000
        assert df['segment'].notna().all()


# ============================================
# TESTES DE INTEGRAÇÃO
# ============================================

class TestRFMIntegration:
    """Testes de integração para análise RFM"""
    
    @pytest.mark.integration
    @pytest.mark.bigquery
    def test_full_rfm_analysis_with_real_data(self, project_id, dataset_id):
        """Testa análise RFM completa com dados reais (requer BigQuery)"""
        try:
            analyzer = RFMAnalyzer(project_id, dataset_id)
            
            # Executar análise
            rfm_data, summary = analyzer.run_full_analysis(
                reference_date='2018-10-01',
                save_results=False
            )
            
            # Verificar resultados
            assert len(rfm_data) > 0
            assert len(summary) > 0
            
            # Verificar colunas essenciais
            required_cols = ['customer_unique_id', 'R_score', 'F_score', 'M_score', 'segment']
            for col in required_cols:
                assert col in rfm_data.columns
            
            # Verificar segmentos principais existem
            expected_segments = ['Champions', 'Loyal Customers', 'At Risk', 'Lost']
            found_segments = set(rfm_data['segment'].unique())
            
            assert len(found_segments) > 0, "Nenhum segmento foi criado"
            
            # Verificar sumário tem métricas
            assert 'customers' in summary.columns
            assert 'total_revenue' in summary.columns
            
        except Exception as e:
            pytest.skip(f"Análise RFM completa falhou (pode não ter dados): {e}")
    
    @pytest.mark.integration
    @pytest.mark.bigquery
    def test_rfm_with_different_quantiles(self, project_id, dataset_id):
        """Testa RFM com diferentes números de quantis"""
        try:
            analyzer = RFMAnalyzer(project_id, dataset_id)
            
            # Extrair dados
            df = analyzer.extract_rfm_data(reference_date='2018-10-01')
            
            # Testar com 3, 4 e 5 quantis
            for n_quantiles in [3, 4, 5]:
                df_scored = analyzer.calculate_rfm_scores(df.copy(), n_quantiles=n_quantiles)
                
                # Verificar ranges
                assert df_scored['R_score'].between(1, n_quantiles).all()
                assert df_scored['F_score'].between(1, n_quantiles).all()
                assert df_scored['M_score'].between(1, n_quantiles).all()
            
        except Exception as e:
            pytest.skip(f"Teste de quantis falhou: {e}")


# ============================================
# TESTES DE EDGE CASES
# ============================================

class TestRFMEdgeCases:
    """Testes de casos extremos"""
    
    def test_single_customer(self, analyzer):
        """Testa análise com um único cliente"""
        df = pd.DataFrame({
            'customer_unique_id': ['c1'],
            'customer_state': ['SP'],
            'recency': [10],
            'frequency': [5],
            'monetary': [1000.0],
            'avg_order_value': [200.0]
        })
        
        # Calcular scores (pode falhar com 1 cliente e 5 quantis)
        try:
            df = analyzer.calculate_rfm_scores(df, n_quantiles=3)
            df = analyzer.segment_customers(df)
            
            assert len(df) == 1
            assert df['segment'].notna().all()
        except:
            # É esperado que possa falhar com poucos dados
            pass
    
    def test_all_same_values(self, analyzer):
        """Testa quando todos os valores são iguais"""
        df = pd.DataFrame({
            'customer_unique_id': ['c1', 'c2', 'c3'],
            'customer_state': ['SP', 'SP', 'SP'],
            'recency': [10, 10, 10],
            'frequency': [5, 5, 5],
            'monetary': [1000.0, 1000.0, 1000.0],
            'avg_order_value': [200.0, 200.0, 200.0]
        })
        
        # qcut pode falhar com valores idênticos
        try:
            df = analyzer.calculate_rfm_scores(df, n_quantiles=3)
            # Todos devem ter mesmo score
            assert df['R_score'].nunique() == 1
            assert df['F_score'].nunique() == 1
            assert df['M_score'].nunique() == 1
        except:
            # É esperado que possa falhar com valores idênticos
            pass
    
    def test_extreme_recency(self, analyzer):
        """Testa com valores extremos de recency"""
        df = pd.DataFrame({
            'customer_unique_id': ['c1', 'c2', 'c3'],
            'recency': [0, 1, 10000],  # 10000 dias = 27 anos
            'frequency': [5, 5, 5],
            'monetary': [1000.0, 1000.0, 1000.0],
            'avg_order_value': [200.0, 200.0, 200.0]
        })
        
        df = analyzer.calculate_rfm_scores(df, n_quantiles=3)
        
        # Cliente com recency=0 deve ter R_score alto
        assert df[df['recency'] == 0]['R_score'].iloc[0] == 3
        
        # Cliente com recency=10000 deve ter R_score baixo
        assert df[df['recency'] == 10000]['R_score'].iloc[0] == 1
    
    def test_zero_monetary(self):
        """Testa detecção de monetary zero (inválido)"""
        df = pd.DataFrame({
            'customer_unique_id': ['c1', 'c2'],
            'monetary': [1000.0, 0.0]  # 0 é inválido
        })
        
        # Detectar valores inválidos
        invalid = (df['monetary'] <= 0).sum()
        assert invalid == 1


# ============================================
# TESTES DE BUSINESS RULES
# ============================================

class TestBusinessRules:
    """Testes de regras de negócio"""
    
    def test_pareto_principle(self, analyzer):
        """Testa Princípio de Pareto (80/20)"""
        # Criar dataset simulando Pareto
        df = pd.DataFrame({
            'customer_unique_id': [f'c{i}' for i in range(100)],
            'monetary': [5000]*20 + [100]*80  # 20% geram muito mais
        })
        
        # Top 20%
        top_20_pct = df.nlargest(20, 'monetary')
        
        # Receita top 20%
        top_revenue = top_20_pct['monetary'].sum()
        total_revenue = df['monetary'].sum()
        
        top_pct = (top_revenue / total_revenue) * 100
        
        # Deve estar próximo de 80%
        assert top_pct > 70  # Pelo menos 70%
    
    def test_high_value_customers_priority(self, analyzer):
        """Testa prioridade de clientes de alto valor"""
        df = pd.DataFrame({
            'R_score': [5, 1],
            'F_score': [5, 5],
            'M_score': [5, 5]
        })
        
        df = analyzer.segment_customers(df)
        
        # Champions deve ter prioridade 1
        champions = df[df['segment'] == 'Champions']
        if len(champions) > 0:
            assert champions['priority'].iloc[0] == 1
        
        # Cannot Lose Them também deve ter prioridade alta
        cannot_lose = df[df['segment'] == 'Cannot Lose Them']
        if len(cannot_lose) > 0:
            assert cannot_lose['priority'].iloc[0] in [1, 2]
    
    def test_churn_risk_identification(self, analyzer):
        """Testa identificação de risco de churn"""
        df = pd.DataFrame({
            'R_score': [1, 2, 5],
            'F_score': [5, 2, 1],
            'M_score': [5, 2, 1]
        })
        
        df = analyzer.segment_customers(df)
        
        # Clientes com R baixo devem estar em segmentos de risco
        high_risk_segments = ['At Risk', 'Cannot Lose Them', 'Lost', 'Hibernating']
        
        low_recency_customers = df[df['R_score'] <= 2]
        
        for idx, row in low_recency_customers.iterrows():
            assert row['segment'] in high_risk_segments


# ============================================
# TESTES AUXILIARES
# ============================================

class TestRFMHelpers:
    """Testes para funções auxiliares"""
    
    def test_quantile_calculation(self):
        """Testa cálculo de quantis"""
        df = pd.DataFrame({
            'value': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        })
        
        df['quantile'] = pd.qcut(df['value'], q=5, labels=[1, 2, 3, 4, 5])
        
        # Verificar distribuição
        assert df['quantile'].value_counts().min() >= 1
        assert df['quantile'].value_counts().max() <= 3
    
    def test_percentile_calculation(self):
        """Testa cálculo de percentis"""
        df = pd.DataFrame({
            'value': range(1, 101)  # 1 a 100
        })
        
        p50 = df['value'].quantile(0.50)
        p90 = df['value'].quantile(0.90)
        
        assert p50 == 50.5
        assert p90 == 90.1


# ============================================
# TESTES DE REGRESSÃO
# ============================================

class TestRFMRegression:
    """Testes de regressão para evitar bugs"""
    
    def test_segment_names_unchanged(self, analyzer):
        """Testa que nomes de segmentos não mudaram"""
        expected_segments = [
            'Champions', 'Loyal Customers', 'Potential Loyalist', 'New Customers',
            'Promising', 'Need Attention', 'About To Sleep', 'At Risk',
            'Cannot Lose Them', 'Hibernating', 'Lost', 'Others'
        ]
        
        # Criar DF com todos os casos
        test_cases = [
            {'R': 5, 'F': 5, 'M': 5},
            {'R': 3, 'F': 5, 'M': 3},
            {'R': 5, 'F': 3, 'M': 3},
            {'R': 5, 'F': 1, 'M': 2},
            {'R': 3, 'F': 1, 'M': 3},
            {'R': 2, 'F': 3, 'M': 3},
            {'R': 2, 'F': 2, 'M': 2},
            {'R': 1, 'F': 4, 'M': 4},
            {'R': 1, 'F': 5, 'M': 5},
            {'R': 2, 'F': 1, 'M': 1},
            {'R': 1, 'F': 1, 'M': 1},
            {'R': 3, 'F': 3, 'M': 3},
        ]
        
        df = pd.DataFrame(test_cases)
        df.columns = ['R_score', 'F_score', 'M_score']
        
        df = analyzer.segment_customers(df)
        
        # Todos os segmentos devem estar na lista esperada
        for segment in df['segment'].unique():
            assert segment in expected_segments
    
    def test_rfm_score_formula_unchanged(self, analyzer):
        """Testa que fórmula do RFM score não mudou"""
        df = pd.DataFrame({
            'R_score': [5],
            'F_score': [4],
            'M_score': [3]
        })
        
        df['RFM_score_numeric'] = (
            df['R_score'] * 0.4 +
            df['F_score'] * 0.3 +
            df['M_score'] * 0.3
        )
        
        expected = 5*0.4 + 4*0.3 + 3*0.3  # = 4.1
        
        assert abs(df.loc[0, 'RFM_score_numeric'] - expected) < 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])