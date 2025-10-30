"""
Configuration Management - Olist E-Commerce
--------------------------------------------
Gerenciamento centralizado de configurações do projeto.
Carrega variáveis de ambiente, valida configs, e fornece defaults.

Autor: Andre Bomfim
Data: Outubro 2025
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv
from loguru import logger


@dataclass
class GCPConfig:
    """Configurações do Google Cloud Platform"""
    project_id: str
    dataset_id: str
    region: str = "us-central1"
    credentials_path: Optional[str] = None
    
    def __post_init__(self):
        """Validação após inicialização"""
        if not self.project_id:
            raise ValueError("GCP_PROJECT_ID é obrigatório")
        if not self.dataset_id:
            raise ValueError("GCP_DATASET_ID é obrigatório")


@dataclass
class PathsConfig:
    """Configurações de caminhos do projeto"""
    data_raw: Path = field(default_factory=lambda: Path("./data/raw"))
    data_processed: Path = field(default_factory=lambda: Path("./data/processed"))
    sql_path: Path = field(default_factory=lambda: Path("./sql"))
    notebooks_path: Path = field(default_factory=lambda: Path("./notebooks"))
    logs_path: Path = field(default_factory=lambda: Path("./logs"))
    keys_path: Path = field(default_factory=lambda: Path("./keys"))
    
    def __post_init__(self):
        """Criar diretórios se não existirem"""
        for path in [self.data_raw, self.data_processed, self.logs_path]:
            path.mkdir(parents=True, exist_ok=True)


@dataclass
class DatabaseConfig:
    """Configurações de banco de dados local (PostgreSQL)"""
    host: str = "localhost"
    port: int = 5432
    database: str = "olist_ecommerce"
    user: str = "postgres"
    password: str = "postgres"
    
    @property
    def connection_string(self) -> str:
        """String de conexão PostgreSQL"""
        return (
            f"postgresql://{self.user}:{self.password}@"
            f"{self.host}:{self.port}/{self.database}"
        )


@dataclass
class LoggingConfig:
    """Configurações de logging"""
    level: str = "INFO"
    file: Optional[str] = None
    rotation: str = "10 MB"
    retention: str = "7 days"
    colorize: bool = True
    
    def __post_init__(self):
        """Validação"""
        valid_levels = ["DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]
        if self.level.upper() not in valid_levels:
            raise ValueError(f"Log level deve ser um de: {valid_levels}")
        self.level = self.level.upper()


@dataclass
class AnalyticsConfig:
    """Configurações para análises"""
    cohort_start_date: str = "2016-09-01"
    cohort_end_date: str = "2018-10-31"
    rfm_quantiles: int = 5
    ltv_time_horizon_days: int = 365
    max_cohort_months: int = 12
    
    def __post_init__(self):
        """Validação"""
        if self.rfm_quantiles < 3 or self.rfm_quantiles > 10:
            raise ValueError("rfm_quantiles deve estar entre 3 e 10")


@dataclass
class KaggleConfig:
    """Configurações da API Kaggle"""
    username: Optional[str] = None
    key: Optional[str] = None
    dataset_name: str = "olistbr/brazilian-ecommerce"
    
    @property
    def is_configured(self) -> bool:
        """Verifica se credenciais Kaggle estão configuradas"""
        # Variáveis de ambiente
        if self.username and self.key:
            return True
        # Arquivo kaggle.json
        kaggle_json = Path.home() / '.kaggle' / 'kaggle.json'
        return kaggle_json.exists()


@dataclass
class ProjectConfig:
    """Configuração completa do projeto"""
    gcp: GCPConfig
    paths: PathsConfig
    database: DatabaseConfig
    logging: LoggingConfig
    analytics: AnalyticsConfig
    kaggle: KaggleConfig
    
    # Metadata
    project_name: str = "Olist E-Commerce Analytics"
    version: str = "1.0.0"
    environment: str = "development"
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte config para dict"""
        return {
            'gcp': {
                'project_id': self.gcp.project_id,
                'dataset_id': self.gcp.dataset_id,
                'region': self.gcp.region,
            },
            'paths': {
                'data_raw': str(self.paths.data_raw),
                'data_processed': str(self.paths.data_processed),
                'sql_path': str(self.paths.sql_path),
            },
            'analytics': {
                'cohort_start_date': self.analytics.cohort_start_date,
                'cohort_end_date': self.analytics.cohort_end_date,
                'rfm_quantiles': self.analytics.rfm_quantiles,
            },
            'project': {
                'name': self.project_name,
                'version': self.version,
                'environment': self.environment,
            }
        }
    
    def print_config(self):
        """Imprime configuração atual"""
        print("\n" + "=" * 60)
        print(f"{self.project_name} v{self.version}")
        print("=" * 60)
        print(f"Ambiente: {self.environment}")
        print(f"\nGCP:")
        print(f"  Project: {self.gcp.project_id}")
        print(f"  Dataset: {self.gcp.dataset_id}")
        print(f"  Region: {self.gcp.region}")
        print(f"\nPaths:")
        print(f"  Data Raw: {self.paths.data_raw}")
        print(f"  Data Processed: {self.paths.data_processed}")
        print(f"  Logs: {self.paths.logs_path}")
        print(f"\nLogging:")
        print(f"  Level: {self.logging.level}")
        print(f"  File: {self.logging.file or 'Console only'}")
        print(f"\nAnalytics:")
        print(f"  Cohort Period: {self.analytics.cohort_start_date} - {self.analytics.cohort_end_date}")
        print(f"  RFM Quantiles: {self.analytics.rfm_quantiles}")
        print(f"\nKaggle:")
        print(f"  Configurado: {'✓' if self.kaggle.is_configured else '✗'}")
        print("=" * 60 + "\n")


def load_config(env_file: str = ".env", 
               validate: bool = True) -> ProjectConfig:
    """
    Carrega configuração completa do projeto
    
    Args:
        env_file: Caminho do arquivo .env
        validate: Se True, valida configurações obrigatórias
        
    Returns:
        ProjectConfig com todas as configurações
        
    Example:
        >>> from python.utils.config import load_config
        >>> config = load_config()
        >>> print(config.gcp.project_id)
    """
    
    # Carregar variáveis de ambiente
    load_dotenv(env_file)
    
    # GCP Config
    gcp_config = GCPConfig(
        project_id=os.getenv('GCP_PROJECT_ID', ''),
        dataset_id=os.getenv('GCP_DATASET_ID', 'olist_ecommerce'),
        region=os.getenv('GCP_REGION', 'us-central1'),
        credentials_path=os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    )
    
    # Paths Config
    paths_config = PathsConfig(
        data_raw=Path(os.getenv('DATA_RAW_PATH', './data/raw')),
        data_processed=Path(os.getenv('DATA_PROCESSED_PATH', './data/processed')),
        sql_path=Path(os.getenv('SQL_PATH', './sql')),
        notebooks_path=Path(os.getenv('NOTEBOOKS_PATH', './notebooks')),
        logs_path=Path('./logs'),
        keys_path=Path('./keys')
    )
    
    # Database Config (PostgreSQL local - opcional)
    database_config = DatabaseConfig(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=int(os.getenv('POSTGRES_PORT', '5432')),
        database=os.getenv('POSTGRES_DB', 'olist_ecommerce'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', 'postgres')
    )
    
    # Logging Config
    logging_config = LoggingConfig(
        level=os.getenv('LOG_LEVEL', 'INFO'),
        file=os.getenv('LOG_FILE'),
        rotation=os.getenv('LOG_ROTATION', '10 MB'),
        retention=os.getenv('LOG_RETENTION', '7 days'),
        colorize=os.getenv('LOG_COLORIZE', 'True').lower() == 'true'
    )
    
    # Analytics Config
    analytics_config = AnalyticsConfig(
        cohort_start_date=os.getenv('COHORT_START_DATE', '2016-09-01'),
        cohort_end_date=os.getenv('COHORT_END_DATE', '2018-10-31'),
        rfm_quantiles=int(os.getenv('RFM_QUANTILES', '5')),
        ltv_time_horizon_days=int(os.getenv('LTV_TIME_HORIZON_DAYS', '365')),
        max_cohort_months=int(os.getenv('MAX_COHORT_MONTHS', '12'))
    )
    
    # Kaggle Config
    kaggle_config = KaggleConfig(
        username=os.getenv('KAGGLE_USERNAME'),
        key=os.getenv('KAGGLE_KEY'),
        dataset_name=os.getenv('KAGGLE_DATASET', 'olistbr/brazilian-ecommerce')
    )
    
    # Project Config completo
    config = ProjectConfig(
        gcp=gcp_config,
        paths=paths_config,
        database=database_config,
        logging=logging_config,
        analytics=analytics_config,
        kaggle=kaggle_config,
        environment=os.getenv('ENVIRONMENT', 'development')
    )
    
    # Validação
    if validate:
        _validate_config(config)
    
    logger.info("Configuração carregada com sucesso")
    
    return config


def _validate_config(config: ProjectConfig):
    """
    Valida configurações críticas
    
    Args:
        config: ProjectConfig
        
    Raises:
        ValueError: Se configuração inválida
    """
    errors = []
    
    # GCP obrigatório
    if not config.gcp.project_id:
        errors.append("GCP_PROJECT_ID não configurado")
    
    # Credenciais GCP
    if config.gcp.credentials_path:
        creds_path = Path(config.gcp.credentials_path)
        if not creds_path.exists():
            errors.append(f"Arquivo de credenciais não encontrado: {creds_path}")
    
    # Paths críticos
    if not config.paths.data_raw.exists():
        logger.warning(f"Diretório data/raw não existe: {config.paths.data_raw}")
    
    if errors:
        error_msg = "\n".join(f"  - {e}" for e in errors)
        raise ValueError(f"Erros de configuração:\n{error_msg}")
    
    logger.success("✓ Configuração validada")


def get_config_value(key: str, default: Any = None) -> Any:
    """
    Obtém valor de configuração por chave
    
    Args:
        key: Chave da variável de ambiente
        default: Valor padrão se não encontrado
        
    Returns:
        Valor da configuração
    """
    return os.getenv(key, default)


def is_production() -> bool:
    """Verifica se está em produção"""
    return os.getenv('ENVIRONMENT', 'development').lower() == 'production'


def is_development() -> bool:
    """Verifica se está em desenvolvimento"""
    return os.getenv('ENVIRONMENT', 'development').lower() == 'development'


# Singleton - carregar config uma vez
_config_instance: Optional[ProjectConfig] = None


def get_config(reload: bool = False) -> ProjectConfig:
    """
    Obtém instância singleton de configuração
    
    Args:
        reload: Se True, recarrega configuração
        
    Returns:
        ProjectConfig
    """
    global _config_instance
    
    if _config_instance is None or reload:
        _config_instance = load_config()
    
    return _config_instance


if __name__ == "__main__":
    """Testes de configuração"""
    
    # Carregar config
    config = load_config(validate=False)
    
    # Imprimir
    config.print_config()
    
    # Testar métodos
    print("\nTestes:")
    print(f"Is Production? {is_production()}")
    print(f"Is Development? {is_development()}")
    print(f"Kaggle Configurado? {config.kaggle.is_configured}")
    
    # Dict
    print("\nConfig as dict:")
    import json
    print(json.dumps(config.to_dict(), indent=2))
    
    # Singleton
    config2 = get_config()
    print(f"\nSingleton funciona? {config is config2}")