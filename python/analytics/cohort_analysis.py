"""
Cohort Retention Analysis - Olist E-Commerce
---------------------------------------------
Análise de retenção de clientes por cohort (mês de primeira compra).
Calcula taxas de retenção, churn, e visualizações.

Autor: Andre Bomfim
Data: Outubro 2025
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional, Tuple, Dict
from google.cloud import bigquery
import matplotlib.pyplot as plt
import seaborn as sns
from loguru import logger


class CohortAnalyzer:
    """Classe para análise de cohort de clientes"""
    
    def __init__(self, project_id: str, dataset_id: str):
        """
        Inicializa o analisador de cohort
        
        Args:
            project_id: ID do projeto GCP
            dataset_id: ID do dataset BigQuery
        """
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.client = bigquery.Client(project=project_id)
        self.cohort_data = None
        self.retention_matrix = None
        
        logger.info("Cohort Analyzer inicializado")
    
    def extract_cohort_data(self, start_date: Optional[str] = None, 
                           end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Extrai dados de cohort do BigQuery
        
        Args:
            start_date: Data inicial (formato YYYY-MM-DD)
            end_date: Data final (formato YYYY-MM-DD)
            
        Returns:
            DataFrame com dados de cohort
        """
        logger.info("Extraindo dados de cohort do BigQuery...")
        
        date_filter = ""
        if start_date:
            date_filter += f"AND o.order_purchase_timestamp >= '{start_date}' "
        if end_date:
            date_filter += f"AND o.order_purchase_timestamp <= '{end_date}' "
        
        query = f"""
        WITH first_purchase AS (
            SELECT 
                c.customer_unique_id,
                MIN(o.order_purchase_timestamp) AS first_purchase_date,
                DATE_TRUNC(MIN(o.order_purchase_timestamp), MONTH) AS cohort_month
            FROM `{self.project_id}.{self.dataset_id}.orders` o
            INNER JOIN `{self.project_id}.{self.dataset_id}.customers` c 
                ON o.customer_id = c.customer_id
            WHERE o.order_status = 'delivered'
                {date_filter}
            GROUP BY c.customer_unique_id
        ),
        
        all_purchases AS (
            SELECT 
                c.customer_unique_id,
                o.order_purchase_timestamp,
                DATE_TRUNC(o.order_purchase_timestamp, MONTH) AS purchase_month,
                fp.cohort_month,
                p.payment_value
            FROM `{self.project_id}.{self.dataset_id}.orders` o
            INNER JOIN `{self.project_id}.{self.dataset_id}.customers` c 
                ON o.customer_id = c.customer_id
            INNER JOIN first_purchase fp 
                ON c.customer_unique_id = fp.customer_unique_id
            INNER JOIN `{self.project_id}.{self.dataset_id}.payments` p 
                ON o.order_id = p.order_id
            WHERE o.order_status = 'delivered'
        )
        
        SELECT 
            customer_unique_id,
            cohort_month,
            purchase_month,
            payment_value,
            DATE_DIFF(purchase_month, cohort_month, MONTH) AS months_since_first_purchase
        FROM all_purchases
        ORDER BY cohort_month, customer_unique_id, purchase_month
        """
        
        df = self.client.query(query).to_dataframe()
        
        logger.success(f"✓ {len(df):,} registros extraídos")
        logger.info(f"Cohorts: {df['cohort_month'].min()} a {df['cohort_month'].max()}")
        
        self.cohort_data = df
        return df
    
    def calculate_retention_matrix(self, max_months: int = 12) -> pd.DataFrame:
        """
        Calcula matriz de retenção
        
        Args:
            max_months: Número máximo de meses a analisar
            
        Returns:
            DataFrame com matriz de retenção (cohort × mês)
        """
        logger.info("Calculando matriz de retenção...")
        
        if self.cohort_data is None:
            raise ValueError("Execute extract_cohort_data() primeiro")
        
        # Filtrar apenas até max_months
        df = self.cohort_data[
            self.cohort_data['months_since_first_purchase'] <= max_months
        ].copy()
        
        # Contar usuários ativos por cohort e mês
        retention_counts = df.groupby([
            'cohort_month', 
            'months_since_first_purchase'
        ])['customer_unique_id'].nunique().reset_index()
        
        retention_counts.columns = ['cohort_month', 'period', 'active_users']
        
        # Tamanho de cada cohort (M0)
        cohort_sizes = df[df['months_since_first_purchase'] == 0].groupby(
            'cohort_month'
        )['customer_unique_id'].nunique().reset_index()
        cohort_sizes.columns = ['cohort_month', 'cohort_size']
        
        # Merge para calcular taxa de retenção
        retention_data = retention_counts.merge(cohort_sizes, on='cohort_month')
        retention_data['retention_rate'] = (
            retention_data['active_users'] / retention_data['cohort_size'] * 100
        )
        
        # Pivot para matriz
        retention_matrix = retention_data.pivot(
            index='cohort_month',
            columns='period',
            values='retention_rate'
        ).fillna(0)
        
        # Formatar index
        retention_matrix.index = retention_matrix.index.strftime('%Y-%m')
        retention_matrix.columns = [f'M{int(col)}' for col in retention_matrix.columns]
        
        logger.success(f"✓ Matriz calculada: {retention_matrix.shape}")
        
        self.retention_matrix = retention_matrix
        return retention_matrix
    
    def calculate_churn_matrix(self, max_months: int = 12) -> pd.DataFrame:
        """
        Calcula matriz de churn (complemento da retenção)
        
        Args:
            max_months: Número máximo de meses
            
        Returns:
            DataFrame com matriz de churn
        """
        if self.retention_matrix is None:
            self.calculate_retention_matrix(max_months)
        
        churn_matrix = 100 - self.retention_matrix
        
        logger.success("✓ Matriz de churn calculada")
        
        return churn_matrix
    
    def calculate_cohort_metrics(self) -> pd.DataFrame:
        """
        Calcula métricas agregadas por cohort
        
        Returns:
            DataFrame com métricas por cohort
        """
        logger.info("Calculando métricas agregadas...")
        
        if self.cohort_data is None:
            raise ValueError("Execute extract_cohort_data() primeiro")
        
        # Agrupar por cohort
        cohort_metrics = self.cohort_data.groupby('cohort_month').agg({
            'customer_unique_id': 'nunique',
            'payment_value': ['sum', 'mean'],
            'months_since_first_purchase': 'max'
        }).reset_index()
        
        cohort_metrics.columns = [
            'cohort_month', 
            'cohort_size', 
            'total_revenue', 
            'avg_revenue_per_order',
            'max_months_tracked'
        ]
        
        # LTV por cohort
        ltv_by_cohort = self.cohort_data.groupby([
            'cohort_month', 
            'customer_unique_id'
        ])['payment_value'].sum().reset_index()
        
        ltv_summary = ltv_by_cohort.groupby('cohort_month')['payment_value'].agg([
            'mean', 
            'median', 
            ('p25', lambda x: x.quantile(0.25)),
            ('p75', lambda x: x.quantile(0.75))
        ]).reset_index()
        
        ltv_summary.columns = [
            'cohort_month', 
            'avg_ltv', 
            'median_ltv', 
            'p25_ltv', 
            'p75_ltv'
        ]
        
        # Merge
        cohort_metrics = cohort_metrics.merge(ltv_summary, on='cohort_month')
        
        # Adicionar taxa de retenção M1 e M3
        if self.retention_matrix is not None:
            retention_m1 = self.retention_matrix['M1'].reset_index()
            retention_m1.columns = ['cohort_str', 'm1_retention']
            retention_m1['cohort_month'] = pd.to_datetime(retention_m1['cohort_str'])
            
            retention_m3 = self.retention_matrix['M3'].reset_index()
            retention_m3.columns = ['cohort_str', 'm3_retention']
            retention_m3['cohort_month'] = pd.to_datetime(retention_m3['cohort_str'])
            
            cohort_metrics = cohort_metrics.merge(
                retention_m1[['cohort_month', 'm1_retention']], 
                on='cohort_month', 
                how='left'
            )
            cohort_metrics = cohort_metrics.merge(
                retention_m3[['cohort_month', 'm3_retention']], 
                on='cohort_month', 
                how='left'
            )
        
        # Formatar
        cohort_metrics['cohort_month'] = cohort_metrics['cohort_month'].dt.strftime('%Y-%m')
        
        for col in ['total_revenue', 'avg_revenue_per_order', 'avg_ltv', 'median_ltv', 'p25_ltv', 'p75_ltv']:
            if col in cohort_metrics.columns:
                cohort_metrics[col] = cohort_metrics[col].round(2)
        
        logger.success(f"✓ Métricas calculadas para {len(cohort_metrics)} cohorts")
        
        return cohort_metrics
    
    def plot_retention_heatmap(self, figsize: Tuple[int, int] = (14, 10), 
                               save_path: Optional[str] = None):
        """
        Plota heatmap de retenção
        
        Args:
            figsize: Tamanho da figura
            save_path: Caminho para salvar imagem
        """
        if self.retention_matrix is None:
            raise ValueError("Execute calculate_retention_matrix() primeiro")
        
        plt.figure(figsize=figsize)
        
        # Criar heatmap
        sns.heatmap(
            self.retention_matrix,
            annot=True,
            fmt='.1f',
            cmap='RdYlGn',
            center=50,
            vmin=0,
            vmax=100,
            cbar_kws={'label': 'Retention Rate (%)'},
            linewidths=0.5
        )
        
        plt.title('Cohort Retention Analysis - Olist E-Commerce', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Meses desde Primeira Compra', fontsize=12, fontweight='bold')
        plt.ylabel('Cohort (Mês de Primeira Compra)', fontsize=12, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.success(f"✓ Heatmap salvo em: {save_path}")
        
        plt.show()
    
    def plot_retention_curves(self, top_n: int = 5, 
                             figsize: Tuple[int, int] = (12, 6),
                             save_path: Optional[str] = None):
        """
        Plota curvas de retenção dos N maiores cohorts
        
        Args:
            top_n: Número de cohorts a plotar
            figsize: Tamanho da figura
            save_path: Caminho para salvar
        """
        if self.retention_matrix is None:
            raise ValueError("Execute calculate_retention_matrix() primeiro")
        
        # Selecionar top N cohorts por tamanho
        cohort_sizes = self.cohort_data[
            self.cohort_data['months_since_first_purchase'] == 0
        ].groupby('cohort_month')['customer_unique_id'].nunique().sort_values(ascending=False)
        
        top_cohorts = cohort_sizes.head(top_n).index.strftime('%Y-%m').tolist()
        
        # Plot
        plt.figure(figsize=figsize)
        
        for cohort in top_cohorts:
            if cohort in self.retention_matrix.index:
                plt.plot(
                    self.retention_matrix.columns,
                    self.retention_matrix.loc[cohort],
                    marker='o',
                    label=cohort,
                    linewidth=2
                )
        
        plt.title('Retention Curves by Cohort', fontsize=14, fontweight='bold')
        plt.xlabel('Months Since First Purchase', fontsize=12)
        plt.ylabel('Retention Rate (%)', fontsize=12)
        plt.legend(title='Cohort', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.success(f"✓ Curvas salvas em: {save_path}")
        
        plt.show()
    
    def plot_average_retention_curve(self, figsize: Tuple[int, int] = (10, 6),
                                     save_path: Optional[str] = None):
        """
        Plota curva média de retenção com intervalo de confiança
        
        Args:
            figsize: Tamanho da figura
            save_path: Caminho para salvar
        """
        if self.retention_matrix is None:
            raise ValueError("Execute calculate_retention_matrix() primeiro")
        
        # Calcular estatísticas
        avg_retention = self.retention_matrix.mean()
        std_retention = self.retention_matrix.std()
        
        # Plot
        plt.figure(figsize=figsize)
        
        x = range(len(avg_retention))
        
        plt.plot(x, avg_retention, marker='o', linewidth=2.5, 
                label='Average Retention', color='#2E86AB')
        plt.fill_between(
            x,
            avg_retention - std_retention,
            avg_retention + std_retention,
            alpha=0.3,
            color='#2E86AB',
            label='±1 Std Dev'
        )
        
        plt.title('Average Retention Curve - All Cohorts', 
                 fontsize=14, fontweight='bold')
        plt.xlabel('Months Since First Purchase', fontsize=12)
        plt.ylabel('Retention Rate (%)', fontsize=12)
        plt.xticks(x, avg_retention.index, rotation=0)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.success(f"✓ Curva média salva em: {save_path}")
        
        plt.show()
    
    def export_results(self, output_dir: str = 'data/processed'):
        """
        Exporta resultados para CSV
        
        Args:
            output_dir: Diretório de saída
        """
        from pathlib import Path
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Exportar matriz de retenção
        if self.retention_matrix is not None:
            retention_file = output_path / f'cohort_retention_matrix_{timestamp}.csv'
            self.retention_matrix.to_csv(retention_file)
            logger.success(f"✓ Matriz salva: {retention_file}")
        
        # Exportar métricas
        cohort_metrics = self.calculate_cohort_metrics()
        metrics_file = output_path / f'cohort_metrics_{timestamp}.csv'
        cohort_metrics.to_csv(metrics_file, index=False)
        logger.success(f"✓ Métricas salvas: {metrics_file}")
        
        # Exportar dados brutos
        if self.cohort_data is not None:
            raw_file = output_path / f'cohort_raw_data_{timestamp}.csv'
            self.cohort_data.to_csv(raw_file, index=False)
            logger.success(f"✓ Dados brutos salvos: {raw_file}")
    
    def run_full_analysis(self, start_date: Optional[str] = None,
                         end_date: Optional[str] = None,
                         max_months: int = 12,
                         plot: bool = True,
                         export: bool = True) -> Dict:
        """
        Executa análise completa de cohort
        
        Args:
            start_date: Data inicial
            end_date: Data final
            max_months: Meses máximos
            plot: Se True, gera visualizações
            export: Se True, exporta resultados
            
        Returns:
            Dict com todos os resultados
        """
        logger.info("=" * 60)
        logger.info("INICIANDO ANÁLISE COMPLETA DE COHORT")
        logger.info("=" * 60)
        
        # 1. Extrair dados
        cohort_data = self.extract_cohort_data(start_date, end_date)
        
        # 2. Calcular retenção
        retention_matrix = self.calculate_retention_matrix(max_months)
        
        # 3. Calcular métricas
        cohort_metrics = self.calculate_cohort_metrics()
        
        # 4. Visualizações
        if plot:
            logger.info("\nGerando visualizações...")
            self.plot_retention_heatmap(
                save_path='docs/images/cohort_retention_heatmap.png'
            )
            self.plot_average_retention_curve(
                save_path='docs/images/cohort_avg_retention.png'
            )
            self.plot_retention_curves(
                save_path='docs/images/cohort_retention_curves.png'
            )
        
        # 5. Exportar
        if export:
            logger.info("\nExportando resultados...")
            self.export_results()
        
        # 6. Sumário
        logger.info("\n" + "=" * 60)
        logger.info("SUMÁRIO DA ANÁLISE")
        logger.info("=" * 60)
        logger.info(f"Total de cohorts: {len(cohort_metrics)}")
        logger.info(f"Período: {cohort_data['cohort_month'].min()} a {cohort_data['cohort_month'].max()}")
        logger.info(f"\nRetenção M1 média: {retention_matrix['M1'].mean():.2f}%")
        logger.info(f"Retenção M3 média: {retention_matrix['M3'].mean():.2f}%")
        logger.info(f"Retenção M6 média: {retention_matrix['M6'].mean():.2f}%")
        
        logger.success("\n✓ Análise de cohort concluída!")
        
        return {
            'cohort_data': cohort_data,
            'retention_matrix': retention_matrix,
            'cohort_metrics': cohort_metrics
        }


def main():
    """Função principal"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    project_id = os.getenv('GCP_PROJECT_ID')
    dataset_id = os.getenv('GCP_DATASET_ID', 'olist_ecommerce')
    
    # Executar análise
    analyzer = CohortAnalyzer(project_id, dataset_id)
    results = analyzer.run_full_analysis()


if __name__ == "__main__":
    main()