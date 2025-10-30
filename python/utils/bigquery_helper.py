"""
BigQuery Helper - Olist E-Commerce
-----------------------------------
Funções utilitárias para facilitar interação com BigQuery.
Queries, exports, uploads, etc.

Autor: Andre Bomfim
Data: Outubro 2025
"""

import os
from typing import Optional, List, Dict, Union
from pathlib import Path
import pandas as pd
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from loguru import logger


class BigQueryHelper:
    """Classe helper para operações BigQuery"""
    
    def __init__(self, project_id: Optional[str] = None, 
                 dataset_id: Optional[str] = None,
                 credentials_path: Optional[str] = None):
        """
        Inicializa o helper
        
        Args:
            project_id: ID do projeto GCP
            dataset_id: ID do dataset BigQuery
            credentials_path: Caminho para arquivo de credenciais
        """
        # Configurar credenciais se fornecido
        if credentials_path:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        
        # Inicializar client
        self.project_id = project_id or os.getenv('GCP_PROJECT_ID')
        self.dataset_id = dataset_id or os.getenv('GCP_DATASET_ID')
        
        if not self.project_id:
            raise ValueError("project_id não fornecido. Configure GCP_PROJECT_ID no .env")
        
        self.client = bigquery.Client(project=self.project_id)
        
        logger.info(f"BigQuery Helper inicializado: {self.project_id}.{self.dataset_id}")
    
    def query_to_dataframe(self, query: str, 
                          use_cache: bool = True,
                          max_results: Optional[int] = None) -> pd.DataFrame:
        """
        Executa query e retorna DataFrame
        
        Args:
            query: Query SQL
            use_cache: Usar cache do BigQuery
            max_results: Limite de resultados
            
        Returns:
            DataFrame com resultados
        """
        job_config = bigquery.QueryJobConfig(use_query_cache=use_cache)
        
        try:
            logger.debug(f"Executando query...")
            
            query_job = self.client.query(query, job_config=job_config)
            df = query_job.to_dataframe(max_results=max_results)
            
            # Estatísticas da query
            total_bytes = query_job.total_bytes_processed
            total_mb = total_bytes / (1024 * 1024) if total_bytes else 0
            
            logger.success(
                f"✓ Query executada: {len(df):,} linhas, "
                f"{total_mb:.2f} MB processados"
            )
            
            return df
            
        except Exception as e:
            logger.error(f"Erro ao executar query: {str(e)}")
            raise
    
    def execute_query(self, query: str, 
                     wait_for_completion: bool = True) -> bigquery.QueryJob:
        """
        Executa query sem retornar resultados (para DDL, DML)
        
        Args:
            query: Query SQL
            wait_for_completion: Aguardar conclusão
            
        Returns:
            QueryJob
        """
        try:
            logger.debug("Executando query...")
            
            query_job = self.client.query(query)
            
            if wait_for_completion:
                query_job.result()  # Aguardar
                logger.success("✓ Query executada com sucesso")
            
            return query_job
            
        except Exception as e:
            logger.error(f"Erro ao executar query: {str(e)}")
            raise
    
    def table_exists(self, table_name: str, dataset_id: Optional[str] = None) -> bool:
        """
        Verifica se tabela existe
        
        Args:
            table_name: Nome da tabela
            dataset_id: ID do dataset (usa self.dataset_id se None)
            
        Returns:
            True se existe, False caso contrário
        """
        dataset_id = dataset_id or self.dataset_id
        table_ref = f"{self.project_id}.{dataset_id}.{table_name}"
        
        try:
            self.client.get_table(table_ref)
            return True
        except NotFound:
            return False
    
    def get_table_schema(self, table_name: str, 
                        dataset_id: Optional[str] = None) -> List[Dict]:
        """
        Obtém schema de uma tabela
        
        Args:
            table_name: Nome da tabela
            dataset_id: ID do dataset
            
        Returns:
            Lista de dicts com schema
        """
        dataset_id = dataset_id or self.dataset_id
        table_ref = f"{self.project_id}.{dataset_id}.{table_name}"
        
        try:
            table = self.client.get_table(table_ref)
            
            schema = []
            for field in table.schema:
                schema.append({
                    'name': field.name,
                    'type': field.field_type,
                    'mode': field.mode,
                    'description': field.description
                })
            
            return schema
            
        except NotFound:
            logger.error(f"Tabela não encontrada: {table_ref}")
            return []
    
    def get_table_info(self, table_name: str, 
                      dataset_id: Optional[str] = None) -> Dict:
        """
        Obtém informações detalhadas de uma tabela
        
        Args:
            table_name: Nome da tabela
            dataset_id: ID do dataset
            
        Returns:
            Dict com informações
        """
        dataset_id = dataset_id or self.dataset_id
        table_ref = f"{self.project_id}.{dataset_id}.{table_name}"
        
        try:
            table = self.client.get_table(table_ref)
            
            info = {
                'project': table.project,
                'dataset': table.dataset_id,
                'table': table.table_id,
                'full_id': table_ref,
                'created': table.created,
                'modified': table.modified,
                'num_rows': table.num_rows,
                'num_bytes': table.num_bytes,
                'size_mb': table.num_bytes / (1024 * 1024) if table.num_bytes else 0,
                'description': table.description,
                'partitioning': str(table.time_partitioning) if table.time_partitioning else None,
                'clustering': table.clustering_fields if table.clustering_fields else None
            }
            
            return info
            
        except NotFound:
            logger.error(f"Tabela não encontrada: {table_ref}")
            return {}
    
    def list_tables(self, dataset_id: Optional[str] = None) -> List[str]:
        """
        Lista todas as tabelas de um dataset
        
        Args:
            dataset_id: ID do dataset
            
        Returns:
            Lista de nomes de tabelas
        """
        dataset_id = dataset_id or self.dataset_id
        dataset_ref = f"{self.project_id}.{dataset_id}"
        
        try:
            tables = list(self.client.list_tables(dataset_ref))
            table_names = [table.table_id for table in tables]
            
            logger.info(f"Dataset {dataset_id}: {len(table_names)} tabelas")
            
            return table_names
            
        except NotFound:
            logger.error(f"Dataset não encontrado: {dataset_ref}")
            return []
    
    def count_rows(self, table_name: str, 
                  dataset_id: Optional[str] = None,
                  where_clause: Optional[str] = None) -> int:
        """
        Conta linhas de uma tabela
        
        Args:
            table_name: Nome da tabela
            dataset_id: ID do dataset
            where_clause: Cláusula WHERE (opcional)
            
        Returns:
            Número de linhas
        """
        dataset_id = dataset_id or self.dataset_id
        table_ref = f"{self.project_id}.{dataset_id}.{table_name}"
        
        query = f"SELECT COUNT(*) as count FROM `{table_ref}`"
        if where_clause:
            query += f" WHERE {where_clause}"
        
        df = self.query_to_dataframe(query)
        count = int(df['count'].iloc[0])
        
        logger.info(f"Tabela {table_name}: {count:,} linhas")
        
        return count
    
    def dataframe_to_bigquery(self, df: pd.DataFrame, 
                             table_name: str,
                             dataset_id: Optional[str] = None,
                             write_disposition: str = 'WRITE_TRUNCATE',
                             create_disposition: str = 'CREATE_IF_NEEDED') -> None:
        """
        Carrega DataFrame para BigQuery
        
        Args:
            df: DataFrame
            table_name: Nome da tabela de destino
            dataset_id: ID do dataset
            write_disposition: WRITE_TRUNCATE, WRITE_APPEND, WRITE_EMPTY
            create_disposition: CREATE_IF_NEEDED, CREATE_NEVER
        """
        dataset_id = dataset_id or self.dataset_id
        table_ref = f"{self.project_id}.{dataset_id}.{table_name}"
        
        job_config = bigquery.LoadJobConfig(
            write_disposition=write_disposition,
            create_disposition=create_disposition
        )
        
        try:
            logger.info(f"Carregando {len(df):,} linhas para {table_ref}...")
            
            job = self.client.load_table_from_dataframe(
                df, table_ref, job_config=job_config
            )
            job.result()  # Aguardar
            
            logger.success(f"✓ {len(df):,} linhas carregadas em {table_name}")
            
        except Exception as e:
            logger.error(f"Erro ao carregar dados: {str(e)}")
            raise
    
    def export_table_to_csv(self, table_name: str,
                           output_path: str,
                           dataset_id: Optional[str] = None,
                           max_rows: Optional[int] = None) -> str:
        """
        Exporta tabela para CSV
        
        Args:
            table_name: Nome da tabela
            output_path: Caminho do arquivo CSV
            dataset_id: ID do dataset
            max_rows: Limite de linhas
            
        Returns:
            Caminho do arquivo criado
        """
        dataset_id = dataset_id or self.dataset_id
        table_ref = f"{self.project_id}.{dataset_id}.{table_name}"
        
        query = f"SELECT * FROM `{table_ref}`"
        if max_rows:
            query += f" LIMIT {max_rows}"
        
        df = self.query_to_dataframe(query, max_results=max_rows)
        
        # Criar diretório se não existir
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        df.to_csv(output_path, index=False)
        
        logger.success(f"✓ {len(df):,} linhas exportadas para {output_path}")
        
        return output_path
    
    def run_sql_file(self, sql_file_path: str,
                    replace_vars: Optional[Dict[str, str]] = None) -> None:
        """
        Executa queries de um arquivo SQL
        
        Args:
            sql_file_path: Caminho do arquivo SQL
            replace_vars: Dict para substituir variáveis (ex: ${PROJECT_ID})
        """
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Substituir variáveis
        if replace_vars:
            for key, value in replace_vars.items():
                sql_content = sql_content.replace(f"${{{key}}}", value)
        
        # Substituir variáveis padrão
        sql_content = sql_content.replace("${GCP_PROJECT_ID}", self.project_id)
        sql_content = sql_content.replace("${GCP_DATASET_ID}", self.dataset_id)
        
        # Split por ; (queries múltiplas)
        queries = [q.strip() for q in sql_content.split(';') if q.strip()]
        
        logger.info(f"Executando {len(queries)} queries de {sql_file_path}...")
        
        for i, query in enumerate(queries, 1):
            # Pular comentários
            if query.startswith('--') or query.startswith('/*'):
                continue
            
            try:
                logger.debug(f"Query {i}/{len(queries)}...")
                self.execute_query(query)
            except Exception as e:
                logger.error(f"Erro na query {i}: {str(e)}")
                raise
        
        logger.success(f"✓ {len(queries)} queries executadas com sucesso")
    
    def get_query_cost_estimate(self, query: str) -> Dict[str, float]:
        """
        Estima custo de uma query (dry run)
        
        Args:
            query: Query SQL
            
        Returns:
            Dict com estimativa de bytes e custo
        """
        job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
        
        try:
            query_job = self.client.query(query, job_config=job_config)
            
            bytes_processed = query_job.total_bytes_processed
            mb_processed = bytes_processed / (1024 * 1024)
            gb_processed = bytes_processed / (1024 * 1024 * 1024)
            
            # BigQuery cobra $5 por TB processado
            cost_estimate = (bytes_processed / (1024**4)) * 5
            
            estimate = {
                'bytes': bytes_processed,
                'mb': round(mb_processed, 2),
                'gb': round(gb_processed, 4),
                'cost_usd': round(cost_estimate, 4)
            }
            
            logger.info(
                f"Estimativa: {estimate['gb']:.4f} GB, "
                f"~${estimate['cost_usd']:.4f}"
            )
            
            return estimate
            
        except Exception as e:
            logger.error(f"Erro ao estimar custo: {str(e)}")
            return {}
    
    def optimize_table(self, table_name: str,
                      dataset_id: Optional[str] = None) -> None:
        """
        Otimiza tabela (clustering, partitioning info)
        
        Args:
            table_name: Nome da tabela
            dataset_id: ID do dataset
        """
        info = self.get_table_info(table_name, dataset_id)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"ANÁLISE DE OTIMIZAÇÃO: {table_name}")
        logger.info(f"{'='*60}")
        logger.info(f"Linhas: {info.get('num_rows', 0):,}")
        logger.info(f"Tamanho: {info.get('size_mb', 0):.2f} MB")
        logger.info(f"Particionamento: {info.get('partitioning', 'Não configurado')}")
        logger.info(f"Clustering: {info.get('clustering', 'Não configurado')}")
        
        # Recomendações
        if info.get('num_rows', 0) > 1_000_000 and not info.get('partitioning'):
            logger.warning("⚠️ Recomendação: Adicionar particionamento por data")
        
        if info.get('num_rows', 0) > 100_000 and not info.get('clustering'):
            logger.warning("⚠️ Recomendação: Adicionar clustering em colunas frequentes")


def main():
    """Função de teste"""
    from dotenv import load_dotenv
    load_dotenv()
    
    helper = BigQueryHelper()
    
    # Listar tabelas
    tables = helper.list_tables()
    print(f"\nTabelas no dataset: {tables}")
    
    # Info de uma tabela
    if tables:
        info = helper.get_table_info(tables[0])
        print(f"\nInfo da tabela {tables[0]}:")
        for key, value in info.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()