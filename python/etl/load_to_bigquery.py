"""
ETL Pipeline: Load Olist Data to Google BigQuery
-------------------------------------------------
Carrega todos os CSVs do dataset Olist para BigQuery
com validações e logging completo.

Autor: Andre Bomfim
Data: Outubro 2025
"""

import os
import sys
from pathlib import Path
from typing import Dict, List
import pandas as pd
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from loguru import logger
from tqdm import tqdm
import time

# Configuração de logging
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("logs/etl_bigquery.log", rotation="10 MB", level="DEBUG")


class OlistBigQueryETL:
    """Pipeline ETL para carregar dados Olist no BigQuery"""
    
    def __init__(self, project_id: str, dataset_id: str, data_path: str):
        """
        Inicializa o pipeline ETL
        
        Args:
            project_id: ID do projeto GCP
            dataset_id: ID do dataset BigQuery
            data_path: Caminho para os CSVs do Olist
        """
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.data_path = Path(data_path)
        self.client = bigquery.Client(project=project_id)
        
        # Mapeamento de arquivos CSV para tabelas BigQuery
        self.table_mapping = {
            'olist_customers_dataset.csv': 'customers',
            'olist_orders_dataset.csv': 'orders',
            'olist_order_items_dataset.csv': 'order_items',
            'olist_products_dataset.csv': 'products',
            'olist_sellers_dataset.csv': 'sellers',
            'olist_order_payments_dataset.csv': 'payments',
            'olist_order_reviews_dataset.csv': 'reviews',
            'product_category_name_translation.csv': 'product_category_translation',
            # 'olist_geolocation_dataset.csv': 'geolocation',  # Muito grande - opcional
        }
        
        # Schema definitions para cada tabela
        self.schemas = self._define_schemas()
        
        logger.info(f"ETL inicializado: {project_id}.{dataset_id}")
    
    def _define_schemas(self) -> Dict[str, List[bigquery.SchemaField]]:
        """Define schemas para todas as tabelas"""
        
        schemas = {
            'customers': [
                bigquery.SchemaField("customer_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("customer_unique_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("customer_zip_code_prefix", "STRING"),
                bigquery.SchemaField("customer_city", "STRING"),
                bigquery.SchemaField("customer_state", "STRING"),
            ],
            'orders': [
                bigquery.SchemaField("order_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("customer_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("order_status", "STRING"),
                bigquery.SchemaField("order_purchase_timestamp", "TIMESTAMP"),
                bigquery.SchemaField("order_approved_at", "TIMESTAMP"),
                bigquery.SchemaField("order_delivered_carrier_date", "TIMESTAMP"),
                bigquery.SchemaField("order_delivered_customer_date", "TIMESTAMP"),
                bigquery.SchemaField("order_estimated_delivery_date", "TIMESTAMP"),
            ],
            'order_items': [
                bigquery.SchemaField("order_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("order_item_id", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("product_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("seller_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("shipping_limit_date", "TIMESTAMP"),
                bigquery.SchemaField("price", "FLOAT"),
                bigquery.SchemaField("freight_value", "FLOAT"),
            ],
            'products': [
                bigquery.SchemaField("product_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("product_category_name", "STRING"),
                bigquery.SchemaField("product_name_lenght", "INTEGER"),
                bigquery.SchemaField("product_description_lenght", "INTEGER"),
                bigquery.SchemaField("product_photos_qty", "INTEGER"),
                bigquery.SchemaField("product_weight_g", "INTEGER"),
                bigquery.SchemaField("product_length_cm", "INTEGER"),
                bigquery.SchemaField("product_height_cm", "INTEGER"),
                bigquery.SchemaField("product_width_cm", "INTEGER"),
            ],
            'sellers': [
                bigquery.SchemaField("seller_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("seller_zip_code_prefix", "STRING"),
                bigquery.SchemaField("seller_city", "STRING"),
                bigquery.SchemaField("seller_state", "STRING"),
            ],
            'payments': [
                bigquery.SchemaField("order_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("payment_sequential", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("payment_type", "STRING"),
                bigquery.SchemaField("payment_installments", "INTEGER"),
                bigquery.SchemaField("payment_value", "FLOAT"),
            ],
            'reviews': [
                bigquery.SchemaField("review_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("order_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("review_score", "INTEGER"),
                bigquery.SchemaField("review_comment_title", "STRING"),
                bigquery.SchemaField("review_comment_message", "STRING"),
                bigquery.SchemaField("review_creation_date", "TIMESTAMP"),
                bigquery.SchemaField("review_answer_timestamp", "TIMESTAMP"),
            ],
            'product_category_translation': [
                bigquery.SchemaField("product_category_name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("product_category_name_english", "STRING", mode="REQUIRED"),
            ],
        }
        
        return schemas
    
    def create_dataset_if_not_exists(self):
        """Cria o dataset BigQuery se não existir"""
        
        dataset_ref = f"{self.project_id}.{self.dataset_id}"
        
        try:
            self.client.get_dataset(dataset_ref)
            logger.info(f"Dataset {dataset_ref} já existe")
        except NotFound:
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "US"
            dataset.description = "Olist E-Commerce Dataset - Analytics"
            
            self.client.create_dataset(dataset)
            logger.success(f"Dataset {dataset_ref} criado com sucesso")
    
    def load_csv_to_dataframe(self, csv_file: str) -> pd.DataFrame:
        """
        Carrega CSV para DataFrame com tratamento de erros
        
        Args:
            csv_file: Nome do arquivo CSV
            
        Returns:
            DataFrame com os dados
        """
        file_path = self.data_path / csv_file
        
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        logger.info(f"Carregando {csv_file}...")
        
        # Ler CSV com encoding UTF-8 (padrão Olist)
        df = pd.read_csv(file_path, encoding='utf-8')
        
        # Limpeza básica
        df.columns = df.columns.str.strip()
        
        # Converter timestamps
        timestamp_cols = [col for col in df.columns if 'timestamp' in col.lower() or 'date' in col.lower()]
        for col in timestamp_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        logger.info(f"✓ {len(df):,} linhas carregadas de {csv_file}")
        
        return df
    
    def load_table_to_bigquery(self, df: pd.DataFrame, table_name: str) -> None:
        """
        Carrega DataFrame para BigQuery
        
        Args:
            df: DataFrame com os dados
            table_name: Nome da tabela de destino
        """
        table_id = f"{self.project_id}.{self.dataset_id}.{table_name}"
        
        # Configuração do job
        job_config = bigquery.LoadJobConfig(
            schema=self.schemas.get(table_name),
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,  # Sobrescrever
            create_disposition=bigquery.CreateDisposition.CREATE_IF_NEEDED,
        )
        
        logger.info(f"Carregando para BigQuery: {table_id}")
        
        # Load job com progress bar
        job = self.client.load_table_from_dataframe(
            df, table_id, job_config=job_config
        )
        
        # Aguardar conclusão
        with tqdm(total=100, desc=f"Upload {table_name}", unit="%") as pbar:
            while not job.done():
                time.sleep(1)
                pbar.update(1)
            pbar.update(100 - pbar.n)
        
        # Verificar erros
        if job.errors:
            logger.error(f"Erros no job: {job.errors}")
            raise Exception(f"Job falhou: {job.errors}")
        
        logger.success(f"✓ {table_name}: {len(df):,} linhas carregadas")
    
    def validate_data_quality(self, table_name: str) -> Dict:
        """
        Valida qualidade dos dados carregados
        
        Args:
            table_name: Nome da tabela
            
        Returns:
            Dict com métricas de qualidade
        """
        table_id = f"{self.project_id}.{self.dataset_id}.{table_name}"
        
        query = f"""
        SELECT 
            COUNT(*) as total_rows,
            COUNT(DISTINCT *) as unique_rows,
            COUNTIF(*) - COUNT(*) as null_count
        FROM `{table_id}`
        """
        
        result = self.client.query(query).to_dataframe()
        
        quality_metrics = {
            'table': table_name,
            'total_rows': int(result['total_rows'].iloc[0]),
            'unique_rows': int(result['unique_rows'].iloc[0]),
            'duplicates': int(result['total_rows'].iloc[0] - result['unique_rows'].iloc[0]),
        }
        
        logger.info(f"Qualidade {table_name}: {quality_metrics['total_rows']:,} linhas")
        
        return quality_metrics
    
    def run_full_pipeline(self) -> None:
        """Executa o pipeline completo de ETL"""
        
        logger.info("=" * 60)
        logger.info("INICIANDO PIPELINE ETL - OLIST TO BIGQUERY")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        # 1. Criar dataset
        self.create_dataset_if_not_exists()
        
        # 2. Carregar cada tabela
        results = []
        
        for csv_file, table_name in self.table_mapping.items():
            try:
                logger.info(f"\n--- Processando {table_name} ---")
                
                # Carregar CSV
                df = self.load_csv_to_dataframe(csv_file)
                
                # Upload para BigQuery
                self.load_table_to_bigquery(df, table_name)
                
                # Validar qualidade
                quality = self.validate_data_quality(table_name)
                results.append(quality)
                
            except Exception as e:
                logger.error(f"Erro ao processar {table_name}: {str(e)}")
                continue
        
        # 3. Sumário final
        elapsed_time = time.time() - start_time
        
        logger.info("\n" + "=" * 60)
        logger.info("PIPELINE CONCLUÍDO")
        logger.info("=" * 60)
        logger.info(f"Tempo total: {elapsed_time:.2f} segundos")
        logger.info(f"Tabelas processadas: {len(results)}")
        
        total_rows = sum(r['total_rows'] for r in results)
        logger.info(f"Total de linhas carregadas: {total_rows:,}")
        
        logger.info("\nResumo por tabela:")
        for r in results:
            logger.info(f"  - {r['table']}: {r['total_rows']:,} linhas")
        
        logger.success("\n✓ ETL concluído com sucesso!")


def main():
    """Função principal"""
    
    # Carregar variáveis de ambiente
    from dotenv import load_dotenv
    load_dotenv()
    
    project_id = os.getenv('GCP_PROJECT_ID')
    dataset_id = os.getenv('GCP_DATASET_ID', 'olist_ecommerce')
    data_path = os.getenv('DATA_RAW_PATH', './data/raw')
    
    # Validar configuração
    if not project_id:
        logger.error("GCP_PROJECT_ID não definido no .env")
        sys.exit(1)
    
    if not Path(data_path).exists():
        logger.error(f"Diretório de dados não encontrado: {data_path}")
        sys.exit(1)
    
    # Executar ETL
    etl = OlistBigQueryETL(
        project_id=project_id,
        dataset_id=dataset_id,
        data_path=data_path
    )
    
    etl.run_full_pipeline()


if __name__ == "__main__":
    main()