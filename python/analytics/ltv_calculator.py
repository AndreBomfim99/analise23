"""
LTV Calculator - Olist E-Commerce
----------------------------------
Cálculo de Customer Lifetime Value com múltiplas metodologias:
- Historical LTV (real)
- Predictive LTV (projeção)
- Cohort-based LTV
- Segmentação por geografia, categoria, etc.

Autor: Andre Bomfim
Data: Outubro 2025
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from google.cloud import bigquery
import matplotlib.pyplot as plt
import seaborn as sns
from loguru import logger


class LTVCalculator:
    """Classe para cálculo de Customer Lifetime Value"""
    
    def __init__(self, project_id: str, dataset_id: str):
        """
        Inicializa o calculador de LTV
        
        Args:
            project_id: ID do projeto GCP
            dataset_id: ID do dataset BigQuery
        """
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.client = bigquery.Client(project=project_id)
        self.customer_ltv = None
        
        logger.info("LTV Calculator inicializado")
    
    def calculate_historical_ltv(self) -> pd.DataFrame:
        """
        Calcula LTV histórico (real) de cada cliente
        
        Returns:
            DataFrame com LTV por cliente
        """
        logger.info("Calculando LTV histórico...")
        
        query = f"""
        WITH customer_orders AS (
            SELECT 
                c.customer_unique_id,
                c.customer_state,
                c.customer_city,
                o.order_id,
                o.order_purchase_timestamp,
                p.payment_value,
                r.review_score
                
            FROM `{self.project_id}.{self.dataset_id}.orders` o
            INNER JOIN `{self.project_id}.{self.dataset_id}.customers` c 
                ON o.customer_id = c.customer_id
            INNER JOIN `{self.project_id}.{self.dataset_id}.payments` p 
                ON o.order_id = p.order_id
            LEFT JOIN `{self.project_id}.{self.dataset_id}.reviews` r 
                ON o.order_id = r.order_id
            WHERE o.order_status = 'delivered'
        )
        
        SELECT 
            customer_unique_id,
            customer_state,
            customer_city,
            
            -- LTV Metrics
            COUNT(DISTINCT order_id) AS total_orders,
            SUM(payment_value) AS lifetime_value,
            AVG(payment_value) AS avg_order_value,
            MIN(payment_value) AS min_order_value,
            MAX(payment_value) AS max_order_value,
            STDDEV(payment_value) AS stddev_order_value,
            
            -- Temporal metrics
            MIN(order_purchase_timestamp) AS first_order_date,
            MAX(order_purchase_timestamp) AS last_order_date,
            DATE_DIFF(
                MAX(order_purchase_timestamp), 
                MIN(order_purchase_timestamp), 
                DAY
            ) AS customer_lifetime_days,
            
            -- Frequency
            DATE_DIFF(CURRENT_DATE(), DATE(MAX(order_purchase_timestamp)), DAY) AS recency_days,
            
            -- Satisfaction
            AVG(review_score) AS avg_review_score
            
        FROM customer_orders
        GROUP BY customer_unique_id, customer_state, customer_city
        """
        
        df = self.client.query(query).to_dataframe()
        
        logger.success(f"✓ LTV calculado para {len(df):,} clientes")
        
        self.customer_ltv = df
        return df
    
    def calculate_predictive_ltv(self, time_horizon_days: int = 365) -> pd.DataFrame:
        """
        Calcula LTV preditivo (projeção futura)
        Usa método simples: (valor_médio_pedido × frequência_projetada)
        
        Args:
            time_horizon_days: Horizonte de previsão em dias
            
        Returns:
            DataFrame com LTV preditivo
        """
        logger.info(f"Calculando LTV preditivo ({time_horizon_days} dias)...")
        
        if self.customer_ltv is None:
            self.calculate_historical_ltv()
        
        df = self.customer_ltv.copy()
        
        # Filtrar clientes com histórico mínimo (30 dias)
        df = df[df['customer_lifetime_days'] >= 30].copy()
        
        # Calcular taxa de pedidos por dia
        df['orders_per_day'] = df['total_orders'] / df['customer_lifetime_days'].replace(0, 1)
        
        # Projetar pedidos futuros
        df['predicted_future_orders'] = df['orders_per_day'] * time_horizon_days
        
        # Calcular LTV preditivo
        df['predicted_ltv'] = (
            df['lifetime_value'] +  # LTV atual
            (df['predicted_future_orders'] * df['avg_order_value'])  # Projeção futura
        )
        
        # Adicionar intervalo de confiança (simples)
        df['predicted_ltv_lower'] = df['predicted_ltv'] * 0.7  # -30%
        df['predicted_ltv_upper'] = df['predicted_ltv'] * 1.3  # +30%
        
        # Classificar confiança
        df['prediction_confidence'] = pd.cut(
            df['total_orders'],
            bins=[0, 1, 3, 5, float('inf')],
            labels=['Low', 'Medium', 'High', 'Very High']
        )
        
        logger.success(f"✓ LTV preditivo calculado para {len(df):,} clientes")
        
        return df[['customer_unique_id', 'customer_state', 'lifetime_value', 
                   'predicted_ltv', 'predicted_ltv_lower', 'predicted_ltv_upper',
                   'prediction_confidence']]
    
    def calculate_ltv_by_segment(self, segment_by: str = 'customer_state') -> pd.DataFrame:
        """
        Calcula LTV agregado por segmento
        
        Args:
            segment_by: Coluna para segmentação (customer_state, customer_city, etc)
            
        Returns:
            DataFrame com LTV por segmento
        """
        logger.info(f"Calculando LTV por segmento: {segment_by}...")
        
        if self.customer_ltv is None:
            self.calculate_historical_ltv()
        
        # Agregar por segmento
        ltv_by_segment = self.customer_ltv.groupby(segment_by).agg({
            'customer_unique_id': 'count',
            'lifetime_value': ['sum', 'mean', 'median', 
                              lambda x: x.quantile(0.25),
                              lambda x: x.quantile(0.75),
                              lambda x: x.quantile(0.90)],
            'total_orders': 'mean',
            'avg_order_value': 'mean',
            'avg_review_score': 'mean'
        }).reset_index()
        
        # Flatten columns
        ltv_by_segment.columns = [
            segment_by, 'customers', 'total_revenue', 'avg_ltv', 'median_ltv',
            'p25_ltv', 'p75_ltv', 'p90_ltv', 'avg_orders', 'avg_aov', 'avg_nps'
        ]
        
        # Calcular share
        ltv_by_segment['revenue_share_pct'] = (
            ltv_by_segment['total_revenue'] / ltv_by_segment['total_revenue'].sum() * 100
        )
        
        # Ranking
        ltv_by_segment = ltv_by_segment.sort_values('avg_ltv', ascending=False)
        ltv_by_segment['ltv_rank'] = range(1, len(ltv_by_segment) + 1)
        
        # Arredondar
        numeric_cols = ['total_revenue', 'avg_ltv', 'median_ltv', 'p25_ltv', 
                       'p75_ltv', 'p90_ltv', 'avg_aov', 'avg_nps', 'revenue_share_pct']
        for col in numeric_cols:
            ltv_by_segment[col] = ltv_by_segment[col].round(2)
        
        ltv_by_segment['avg_orders'] = ltv_by_segment['avg_orders'].round(1)
        
        logger.success(f"✓ LTV calculado para {len(ltv_by_segment)} segmentos")
        
        return ltv_by_segment
    
    def calculate_cohort_ltv(self) -> pd.DataFrame:
        """
        Calcula LTV por cohort (mês de primeira compra)
        
        Returns:
            DataFrame com LTV por cohort
        """
        logger.info("Calculando LTV por cohort...")
        
        query = f"""
        WITH customer_cohort AS (
            SELECT 
                c.customer_unique_id,
                DATE_TRUNC(MIN(o.order_purchase_timestamp), MONTH) AS cohort_month,
                SUM(p.payment_value) AS lifetime_value,
                COUNT(DISTINCT o.order_id) AS total_orders,
                AVG(p.payment_value) AS avg_order_value
                
            FROM `{self.project_id}.{self.dataset_id}.orders` o
            INNER JOIN `{self.project_id}.{self.dataset_id}.customers` c 
                ON o.customer_id = c.customer_id
            INNER JOIN `{self.project_id}.{self.dataset_id}.payments` p 
                ON o.order_id = p.order_id
            WHERE o.order_status = 'delivered'
            GROUP BY c.customer_unique_id
        )
        
        SELECT 
            cohort_month,
            COUNT(customer_unique_id) AS cohort_size,
            SUM(lifetime_value) AS total_revenue,
            AVG(lifetime_value) AS avg_ltv,
            APPROX_QUANTILES(lifetime_value, 4)[OFFSET(2)] AS median_ltv,
            AVG(total_orders) AS avg_orders_per_customer,
            AVG(avg_order_value) AS avg_aov
            
        FROM customer_cohort
        GROUP BY cohort_month
        ORDER BY cohort_month
        """
        
        df = self.client.query(query).to_dataframe()
        
        # Formatar
        df['cohort_month'] = pd.to_datetime(df['cohort_month'])
        df['cohort_year_month'] = df['cohort_month'].dt.strftime('%Y-%m')
        
        # Calcular growth vs cohort anterior
        df['ltv_vs_prev_cohort'] = df['avg_ltv'].pct_change() * 100
        
        # Arredondar
        for col in ['total_revenue', 'avg_ltv', 'median_ltv', 'avg_aov']:
            df[col] = df[col].round(2)
        
        df['avg_orders_per_customer'] = df['avg_orders_per_customer'].round(1)
        df['ltv_vs_prev_cohort'] = df['ltv_vs_prev_cohort'].round(2)
        
        logger.success(f"✓ LTV calculado para {len(df)} cohorts")
        
        return df
    
    def identify_high_value_customers(self, top_pct: float = 10) -> pd.DataFrame:
        """
        Identifica clientes de alto valor (top X%)
        
        Args:
            top_pct: Percentual top de clientes (default: 10%)
            
        Returns:
            DataFrame com clientes VIP
        """
        logger.info(f"Identificando top {top_pct}% clientes...")
        
        if self.customer_ltv is None:
            self.calculate_historical_ltv()
        
        # Calcular threshold
        threshold = self.customer_ltv['lifetime_value'].quantile(1 - top_pct/100)
        
        # Filtrar top clientes
        vip_customers = self.customer_ltv[
            self.customer_ltv['lifetime_value'] >= threshold
        ].copy()
        
        # Adicionar percentil
        vip_customers['ltv_percentile'] = (
            vip_customers['lifetime_value'].rank(pct=True) * 100
        ).round(2)
        
        # Classificar tier
        vip_customers['vip_tier'] = pd.cut(
            vip_customers['lifetime_value'],
            bins=[threshold, threshold*2, threshold*5, float('inf')],
            labels=['Gold', 'Platinum', 'Diamond']
        )
        
        # Ordenar
        vip_customers = vip_customers.sort_values('lifetime_value', ascending=False)
        
        logger.success(f"✓ {len(vip_customers):,} clientes VIP identificados")
        logger.info(f"LTV mínimo: R$ {threshold:.2f}")
        logger.info(f"LTV médio VIP: R$ {vip_customers['lifetime_value'].mean():.2f}")
        
        return vip_customers
    
    def calculate_pareto_analysis(self) -> Tuple[pd.DataFrame, Dict]:
        """
        Análise de Pareto (80/20) para LTV
        
        Returns:
            Tuple (DataFrame com clientes, Dict com métricas)
        """
        logger.info("Calculando análise de Pareto...")
        
        if self.customer_ltv is None:
            self.calculate_historical_ltv()
        
        df = self.customer_ltv.sort_values('lifetime_value', ascending=False).copy()
        
        # Calcular acumulados
        df['cumulative_revenue'] = df['lifetime_value'].cumsum()
        df['cumulative_customers'] = range(1, len(df) + 1)
        
        total_revenue = df['lifetime_value'].sum()
        total_customers = len(df)
        
        # Calcular percentuais
        df['cumulative_revenue_pct'] = df['cumulative_revenue'] / total_revenue * 100
        df['cumulative_customers_pct'] = df['cumulative_customers'] / total_customers * 100
        
        # Identificar pontos chave
        pareto_80 = df[df['cumulative_revenue_pct'] <= 80].iloc[-1]
        pareto_50 = df[df['cumulative_revenue_pct'] <= 50].iloc[-1]
        
        metrics = {
            'total_customers': total_customers,
            'total_revenue': total_revenue,
            'top_20_pct_customers': int(pareto_80['cumulative_customers']),
            'top_20_pct_revenue_share': pareto_80['cumulative_revenue_pct'],
            'top_50_revenue_customers': int(pareto_50['cumulative_customers']),
            'top_50_revenue_customers_pct': pareto_50['cumulative_customers_pct']
        }
        
        logger.success("✓ Análise de Pareto concluída")
        logger.info(f"Top 20% clientes = {metrics['top_20_pct_revenue_share']:.1f}% da receita")
        logger.info(f"Top 50% receita = {metrics['top_50_revenue_customers_pct']:.1f}% dos clientes")
        
        return df, metrics
    
    def plot_ltv_distribution(self, figsize: Tuple[int, int] = (12, 5),
                             save_path: Optional[str] = None):
        """
        Plota distribuição de LTV
        
        Args:
            figsize: Tamanho da figura
            save_path: Caminho para salvar
        """
        if self.customer_ltv is None:
            self.calculate_historical_ltv()
        
        fig, axes = plt.subplots(1, 2, figsize=figsize)
        
        # Histogram
        axes[0].hist(self.customer_ltv['lifetime_value'], bins=50, 
                    edgecolor='black', alpha=0.7)
        axes[0].axvline(self.customer_ltv['lifetime_value'].mean(), 
                       color='red', linestyle='--', linewidth=2, 
                       label=f"Média: R$ {self.customer_ltv['lifetime_value'].mean():.2f}")
        axes[0].axvline(self.customer_ltv['lifetime_value'].median(), 
                       color='green', linestyle='--', linewidth=2,
                       label=f"Mediana: R$ {self.customer_ltv['lifetime_value'].median():.2f}")
        axes[0].set_xlabel('Lifetime Value (R$)')
        axes[0].set_ylabel('Frequência')
        axes[0].set_title('Distribuição de LTV')
        axes[0].legend()
        axes[0].grid(alpha=0.3)
        
        # Box plot
        axes[1].boxplot(self.customer_ltv['lifetime_value'], vert=True)
        axes[1].set_ylabel('Lifetime Value (R$)')
        axes[1].set_title('Box Plot - LTV')
        axes[1].grid(alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.success(f"✓ Gráfico salvo: {save_path}")
        
        plt.show()
    
    def plot_ltv_by_segment(self, segment_by: str = 'customer_state',
                           top_n: int = 10,
                           figsize: Tuple[int, int] = (12, 6),
                           save_path: Optional[str] = None):
        """
        Plota LTV por segmento
        
        Args:
            segment_by: Coluna de segmentação
            top_n: Top N segmentos
            figsize: Tamanho da figura
            save_path: Caminho para salvar
        """
        ltv_segment = self.calculate_ltv_by_segment(segment_by)
        ltv_segment = ltv_segment.head(top_n)
        
        fig, axes = plt.subplots(1, 2, figsize=figsize)
        
        # Bar plot - Avg LTV
        axes[0].barh(ltv_segment[segment_by], ltv_segment['avg_ltv'])
        axes[0].set_xlabel('Average LTV (R$)')
        axes[0].set_title(f'Top {top_n} - Average LTV by {segment_by}')
        axes[0].grid(axis='x', alpha=0.3)
        
        # Bar plot - Total Revenue
        axes[1].barh(ltv_segment[segment_by], ltv_segment['total_revenue'])
        axes[1].set_xlabel('Total Revenue (R$)')
        axes[1].set_title(f'Top {top_n} - Total Revenue by {segment_by}')
        axes[1].grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.success(f"✓ Gráfico salvo: {save_path}")
        
        plt.show()
    
    def plot_pareto_curve(self, figsize: Tuple[int, int] = (10, 6),
                         save_path: Optional[str] = None):
        """
        Plota curva de Pareto
        
        Args:
            figsize: Tamanho
            save_path: Caminho para salvar
        """
        pareto_df, metrics = self.calculate_pareto_analysis()
        
        plt.figure(figsize=figsize)
        
        plt.plot(pareto_df['cumulative_customers_pct'], 
                pareto_df['cumulative_revenue_pct'],
                linewidth=2.5, color='#2E86AB')
        
        # Linha de referência (igualdade perfeita)
        plt.plot([0, 100], [0, 100], 'r--', linewidth=1.5, 
                label='Perfect Equality', alpha=0.7)
        
        # Marcar 80/20
        plt.axhline(80, color='green', linestyle=':', alpha=0.7)
        plt.axvline(metrics['top_50_revenue_customers_pct'], 
                   color='orange', linestyle=':', alpha=0.7)
        
        plt.xlabel('Cumulative % of Customers')
        plt.ylabel('Cumulative % of Revenue')
        plt.title('Pareto Analysis - Customer LTV Concentration')
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.success(f"✓ Curva de Pareto salva: {save_path}")
        
        plt.show()
    
    def export_results(self, output_dir: str = 'data/processed'):
        """
        Exporta todos os resultados
        
        Args:
            output_dir: Diretório de saída
        """
        from pathlib import Path
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # LTV histórico
        if self.customer_ltv is not None:
            file = output_path / f'ltv_historical_{timestamp}.csv'
            self.customer_ltv.to_csv(file, index=False)
            logger.success(f"✓ LTV histórico: {file}")
        
        # LTV por estado
        ltv_state = self.calculate_ltv_by_segment('customer_state')
        file = output_path / f'ltv_by_state_{timestamp}.csv'
        ltv_state.to_csv(file, index=False)
        logger.success(f"✓ LTV por estado: {file}")
        
        # LTV por cohort
        ltv_cohort = self.calculate_cohort_ltv()
        file = output_path / f'ltv_by_cohort_{timestamp}.csv'
        ltv_cohort.to_csv(file, index=False)
        logger.success(f"✓ LTV por cohort: {file}")
        
        # Clientes VIP
        vip = self.identify_high_value_customers(top_pct=10)
        file = output_path / f'vip_customers_{timestamp}.csv'
        vip.to_csv(file, index=False)
        logger.success(f"✓ Clientes VIP: {file}")


def main():
    """Função principal"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    project_id = os.getenv('GCP_PROJECT_ID')
    dataset_id = os.getenv('GCP_DATASET_ID', 'olist_ecommerce')
    
    # Executar análise
    calculator = LTVCalculator(project_id, dataset_id)
    
    # LTV histórico
    ltv = calculator.calculate_historical_ltv()
    print(f"\nLTV Médio: R$ {ltv['lifetime_value'].mean():.2f}")
    print(f"LTV Mediano: R$ {ltv['lifetime_value'].median():.2f}")
    
    # Visualizações
    calculator.plot_ltv_distribution(save_path='docs/images/ltv_distribution.png')
    calculator.plot_pareto_curve(save_path='docs/images/ltv_pareto.png')
    
    # Export
    calculator.export_results()


if __name__ == "__main__":
    main()