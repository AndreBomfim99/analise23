"""
RFM Segmentation - Recency, Frequency, Monetary Analysis
---------------------------------------------------------
Segmentação avançada de clientes usando análise RFM
com machine learning para clustering automático.

Autor: Andre Bomfim
Data: Outubro 2025
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from google.cloud import bigquery
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple, Dict
from loguru import logger


class RFMAnalyzer:
    """Classe para análise RFM de clientes"""
    
    def __init__(self, project_id: str, dataset_id: str):
        """
        Inicializa o analisador RFM
        
        Args:
            project_id: ID do projeto GCP
            dataset_id: ID do dataset BigQuery
        """
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.client = bigquery.Client(project=project_id)
        self.rfm_data = None
        
        logger.info("RFM Analyzer inicializado")
    
    def extract_rfm_data(self, reference_date: str = None) -> pd.DataFrame:
        """
        Extrai dados para cálculo RFM do BigQuery
        
        Args:
            reference_date: Data de referência (formato YYYY-MM-DD)
                           Se None, usa a data máxima do dataset
        
        Returns:
            DataFrame com dados RFM
        """
        logger.info("Extraindo dados para RFM...")
        
        # Se não fornecida, buscar data máxima
        if reference_date is None:
            query_max_date = f"""
            SELECT MAX(order_purchase_timestamp) as max_date
            FROM `{self.project_id}.{self.dataset_id}.orders`
            WHERE order_status = 'delivered'
            """
            max_date = self.client.query(query_max_date).to_dataframe()
            reference_date = max_date['max_date'].iloc[0]
        
        logger.info(f"Data de referência: {reference_date}")
        
        # Query principal para RFM
        query = f"""
        WITH customer_orders AS (
            SELECT 
                c.customer_unique_id,
                c.customer_state,
                o.order_id,
                o.order_purchase_timestamp,
                p.payment_value,
                
                -- Recência: dias desde a última compra
                DATE_DIFF(
                    DATE('{reference_date}'),
                    DATE(o.order_purchase_timestamp),
                    DAY
                ) AS days_since_purchase

            FROM `{self.project_id}.{self.dataset_id}.orders` o
            INNER JOIN `{self.project_id}.{self.dataset_id}.customers` c 
                ON o.customer_id = c.customer_id
            INNER JOIN `{self.project_id}.{self.dataset_id}.payments` p 
                ON o.order_id = p.order_id
            WHERE o.order_status = 'delivered'
                AND o.order_purchase_timestamp <= '{reference_date}'
        )

        SELECT 
            customer_unique_id,
            customer_state,
            
            -- Recency: dias desde a última compra
            MIN(days_since_purchase) AS recency,
            
            -- Frequency: número de compras
            COUNT(DISTINCT order_id) AS frequency,
            
            -- Monetary: valor total gasto
            SUM(payment_value) AS monetary,
            
            -- Métricas adicionais
            AVG(payment_value) AS avg_order_value,
            MAX(order_purchase_timestamp) AS last_purchase_date,
            MIN(order_purchase_timestamp) AS first_purchase_date

        FROM customer_orders
        GROUP BY customer_unique_id, customer_state
        """
        
        df = self.client.query(query).to_dataframe()
        
        logger.success(f"✓ {len(df):,} clientes extraídos")
        
        self.rfm_data = df
        return df
    
    def calculate_rfm_scores(self, df: pd.DataFrame, n_quantiles: int = 5) -> pd.DataFrame:
        """
        Calcula scores RFM (1-5) usando quantis
        
        Args:
            df: DataFrame com dados RFM
            n_quantiles: Número de quantis (default: 5 para 1-5)
        
        Returns:
            DataFrame com scores RFM adicionados
        """
        logger.info(f"Calculando scores RFM ({n_quantiles} quantis)...")
        
        df = df.copy()
        
        # Recency: menor é melhor (inverter)
        df['R_score'] = pd.qcut(
            df['recency'], 
            q=n_quantiles, 
            labels=range(n_quantiles, 0, -1),
            duplicates='drop'
        )
        
        # Frequency: maior é melhor
        df['F_score'] = pd.qcut(
            df['frequency'], 
            q=n_quantiles, 
            labels=range(1, n_quantiles + 1),
            duplicates='drop'
        )
        
        # Monetary: maior é melhor
        df['M_score'] = pd.qcut(
            df['monetary'], 
            q=n_quantiles, 
            labels=range(1, n_quantiles + 1),
            duplicates='drop'
        )
        
        # Converter para int
        df['R_score'] = df['R_score'].astype(int)
        df['F_score'] = df['F_score'].astype(int)
        df['M_score'] = df['M_score'].astype(int)
        
        # RFM Score combinado (string)
        df['RFM_score'] = (
            df['R_score'].astype(str) + 
            df['F_score'].astype(str) + 
            df['M_score'].astype(str)
        )
        
        # RFM Score numérico (média ponderada)
        df['RFM_score_numeric'] = (
            df['R_score'] * 0.4 +  # Recency mais importante
            df['F_score'] * 0.3 + 
            df['M_score'] * 0.3
        )
        
        logger.success("✓ Scores RFM calculados")
        
        return df
    
    def segment_customers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Segmenta clientes em categorias de negócio
        
        Args:
            df: DataFrame com scores RFM
        
        Returns:
            DataFrame com segmentos adicionados
        """
        logger.info("Segmentando clientes...")
        
        df = df.copy()
        
        # Segmentação baseada em regras de negócio
        def assign_segment(row):
            r, f, m = row['R_score'], row['F_score'], row['M_score']
            
            # Champions: Melhores clientes
            if r >= 4 and f >= 4 and m >= 4:
                return 'Champions'
            
            # Loyal: Compram frequentemente
            elif f >= 4:
                return 'Loyal Customers'
            
            # Potential Loyalist: Clientes recentes com potencial
            elif r >= 4 and f >= 2 and m >= 2:
                return 'Potential Loyalist'
            
            # New Customers: Clientes novos
            elif r >= 4 and f == 1:
                return 'New Customers'
            
            # Promising: Compradores recentes, baixa frequência
            elif r >= 3 and f == 1 and m >= 2:
                return 'Promising'
            
            # Need Attention: Clientes em risco
            elif r >= 2 and f >= 2 and m >= 2:
                return 'Need Attention'
            
            # About to Sleep: Risco de churn
            elif r >= 2 and f <= 2 and m <= 2:
                return 'About To Sleep'
            
            # At Risk: Alto risco de perda
            elif r <= 2 and f >= 3 and m >= 3:
                return 'At Risk'
            
            # Cannot Lose Them: Clientes valiosos inativos
            elif r <= 2 and f >= 4 and m >= 4:
                return 'Cannot Lose Them'
            
            # Hibernating: Inativos há muito tempo
            elif r <= 2 and f <= 2 and m <= 2:
                return 'Hibernating'
            
            # Lost: Perdidos
            elif r == 1:
                return 'Lost'
            
            else:
                return 'Others'
        
        df['segment'] = df.apply(assign_segment, axis=1)
        
        # Adicionar prioridade de ação
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
        
        logger.success("✓ Clientes segmentados")
        
        return df
    
    def generate_segment_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Gera sumário estatístico por segmento
        
        Args:
            df: DataFrame com segmentação
        
        Returns:
            DataFrame com sumário
        """
        logger.info("Gerando sumário por segmento...")
        
        summary = df.groupby('segment').agg({
            'customer_unique_id': 'count',
            'monetary': ['sum', 'mean', 'median'],
            'frequency': ['mean', 'median'],
            'recency': ['mean', 'median'],
            'avg_order_value': 'mean',
            'RFM_score_numeric': 'mean'
        }).round(2)
        
        # Flatten columns
        summary.columns = [
            'customers', 
            'total_revenue', 'avg_revenue', 'median_revenue',
            'avg_frequency', 'median_frequency',
            'avg_recency', 'median_recency',
            'avg_aov', 'avg_rfm_score'
        ]
        
        # Calcular percentuais
        summary['customer_pct'] = (
            summary['customers'] / summary['customers'].sum() * 100
        ).round(2)
        
        summary['revenue_pct'] = (
            summary['total_revenue'] / summary['total_revenue'].sum() * 100
        ).round(2)
        
        # Ordenar por prioridade
        priority_order = [
            'Champions', 'Loyal Customers', 'Cannot Lose Them', 'At Risk',
            'Potential Loyalist', 'Need Attention', 'Promising', 
            'New Customers', 'About To Sleep', 'Hibernating', 'Lost', 'Others'
        ]
        
        summary = summary.reindex([s for s in priority_order if s in summary.index])
        
        logger.success("✓ Sumário gerado")
        
        return summary
    
    def recommend_actions(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Gera recomendações de ação por segmento
        
        Args:
            df: DataFrame com segmentação
        
        Returns:
            Dict com recomendações
        """
        recommendations = {
            'Champions': "🏆 Recompense! Programa VIP, early access, benefícios exclusivos",
            'Loyal Customers': "⭐ Upsell e cross-sell produtos premium. Peça reviews/referrals",
            'Cannot Lose Them': "🚨 URGENTE! Oferta especial, contato direto, recupere antes que seja tarde",
            'At Risk': "⚠️ Campanha win-back agressiva. Cupom 20%, pesquisa de satisfação",
            'Potential Loyalist': "📈 Nurturing com email marketing. Ofereça programa de fidelidade",
            'Need Attention': "🔔 Reative com ofertas limitadas. Lembre que sentem falta",
            'Promising': "🌟 Incentive segunda compra. Cupom 15% com prazo curto",
            'New Customers': "👋 Onboarding especial. Email sequência de boas-vindas",
            'About To Sleep': "😴 Alerta! Email re-engajamento. Novidades e ofertas",
            'Hibernating': "💤 Campanha de reativação massiva. Cupom agressivo ou não investir",
            'Lost': "❌ Custo alto para recuperar. Considere não investir recursos",
            'Others': "📊 Analisar caso a caso. Possível segmentação adicional"
        }
        
        return recommendations
    
    def plot_rfm_distribution(self, df: pd.DataFrame, save_path: str = None):
        """
        Plota distribuições RFM
        
        Args:
            df: DataFrame com RFM
            save_path: Caminho para salvar imagem
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Distribuição de segmentos
        segment_counts = df['segment'].value_counts()
        axes[0, 0].barh(segment_counts.index, segment_counts.values)
        axes[0, 0].set_xlabel('Número de Clientes')
        axes[0, 0].set_title('Distribuição por Segmento')
        
        # 2. Recency vs Frequency
        scatter = axes[0, 1].scatter(
            df['recency'], df['frequency'], 
            c=df['monetary'], cmap='viridis', alpha=0.5
        )
        axes[0, 1].set_xlabel('Recency (dias)')
        axes[0, 1].set_ylabel('Frequency (pedidos)')
        axes[0, 1].set_title('Recency vs Frequency (cor = Monetary)')
        plt.colorbar(scatter, ax=axes[0, 1])
        
        # 3. RFM Score distribution
        axes[1, 0].hist(df['RFM_score_numeric'], bins=30, edgecolor='black')
        axes[1, 0].set_xlabel('RFM Score Numérico')
        axes[1, 0].set_ylabel('Frequência')
        axes[1, 0].set_title('Distribuição de RFM Score')
        
        # 4. Revenue por segmento
        revenue_by_segment = df.groupby('segment')['monetary'].sum().sort_values()
        axes[1, 1].barh(revenue_by_segment.index, revenue_by_segment.values)
        axes[1, 1].set_xlabel('Receita Total (R$)')
        axes[1, 1].set_title('Receita por Segmento')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Gráfico salvo em: {save_path}")
        
        plt.show()
    
    def run_full_analysis(self, reference_date: str = None, 
                         save_results: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Executa análise RFM completa
        
        Args:
            reference_date: Data de referência
            save_results: Se True, salva resultados em CSV
        
        Returns:
            Tuple (rfm_data, summary)
        """
        logger.info("=" * 60)
        logger.info("INICIANDO ANÁLISE RFM COMPLETA")
        logger.info("=" * 60)
        
        # 1. Extrair dados
        df = self.extract_rfm_data(reference_date)
        
        # 2. Calcular scores
        df = self.calculate_rfm_scores(df)
        
        # 3. Segmentar
        df = self.segment_customers(df)
        
        # 4. Gerar sumário
        summary = self.generate_segment_summary(df)
        
        # 5. Recomendações
        recommendations = self.recommend_actions(df)
        
        # 6. Exibir resultados
        logger.info("\n" + "=" * 60)
        logger.info("SUMÁRIO POR SEGMENTO")
        logger.info("=" * 60)
        print(summary[['customers', 'customer_pct', 'revenue_pct', 'avg_revenue']])
        
        logger.info("\n" + "=" * 60)
        logger.info("RECOMENDAÇÕES DE AÇÃO")
        logger.info("=" * 60)
        for segment, action in recommendations.items():
            if segment in df['segment'].values:
                logger.info(f"{segment}: {action}")
        
        # 7. Salvar resultados
        if save_results:
            df.to_csv('data/processed/rfm_customers.csv', index=False)
            summary.to_csv('data/processed/rfm_summary.csv')
            logger.success("✓ Resultados salvos em data/processed/")
        
        logger.success("\n✓ Análise RFM concluída!")
        
        return df, summary


def main():
    """Função principal"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    project_id = os.getenv('GCP_PROJECT_ID')
    dataset_id = os.getenv('GCP_DATASET_ID', 'olist_ecommerce')
    
    # Executar análise
    analyzer = RFMAnalyzer(project_id, dataset_id)
    rfm_data, summary = analyzer.run_full_analysis()
    
    # Plot (opcional)
    # analyzer.plot_rfm_distribution(rfm_data, save_path='docs/images/rfm_analysis.png')


if __name__ == "__main__":
    main()