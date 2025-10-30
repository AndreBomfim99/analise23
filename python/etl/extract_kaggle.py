"""
Extract from Kaggle - Olist E-Commerce
---------------------------------------
Script para download automático do dataset Olist do Kaggle.
Usa Kaggle API para baixar e extrair os CSVs.

Autor: Andre Bomfim
Data: Outubro 2025
"""

import os
import sys
import zipfile
from pathlib import Path
from typing import Optional
import json
from loguru import logger

# Configuração de logging
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("logs/extract_kaggle.log", rotation="10 MB", level="DEBUG")


class KaggleExtractor:
    """Extrator de datasets do Kaggle"""
    
    def __init__(self, output_dir: str = "./data/raw"):
        """
        Inicializa o extrator
        
        Args:
            output_dir: Diretório de destino para os CSVs
        """
        self.output_dir = Path(output_dir)
        self.dataset_name = "olistbr/brazilian-ecommerce"
        
        # Criar diretório se não existir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Kaggle Extractor inicializado")
        logger.info(f"Output dir: {self.output_dir.absolute()}")
    
    def _check_kaggle_credentials(self) -> bool:
        """
        Verifica se credenciais Kaggle estão configuradas
        
        Returns:
            True se credenciais válidas, False caso contrário
        """
        # Método 1: Variáveis de ambiente
        if os.getenv('KAGGLE_USERNAME') and os.getenv('KAGGLE_KEY'):
            logger.success("✓ Credenciais Kaggle encontradas (variáveis de ambiente)")
            return True
        
        # Método 2: Arquivo kaggle.json
        kaggle_config_path = Path.home() / '.kaggle' / 'kaggle.json'
        if kaggle_config_path.exists():
            logger.success(f"✓ Credenciais Kaggle encontradas ({kaggle_config_path})")
            return True
        
        logger.error("❌ Credenciais Kaggle não encontradas!")
        logger.info("\nPara configurar:")
        logger.info("1. Acesse https://www.kaggle.com/settings/account")
        logger.info("2. Clique em 'Create New API Token'")
        logger.info("3. Salve kaggle.json em ~/.kaggle/")
        logger.info("   OU")
        logger.info("4. Configure variáveis de ambiente:")
        logger.info("   export KAGGLE_USERNAME=seu_username")
        logger.info("   export KAGGLE_KEY=sua_key")
        
        return False
    
    def _install_kaggle_package(self) -> bool:
        """
        Verifica se kaggle package está instalado
        
        Returns:
            True se instalado, False caso contrário
        """
        try:
            import kaggle
            logger.success("✓ Kaggle package instalado")
            return True
        except ImportError:
            logger.error("❌ Kaggle package não instalado")
            logger.info("\nPara instalar:")
            logger.info("pip install kaggle")
            return False
    
    def _check_existing_files(self) -> bool:
        """
        Verifica se os CSVs já existem
        
        Returns:
            True se todos os CSVs existem, False caso contrário
        """
        expected_files = [
            'olist_customers_dataset.csv',
            'olist_orders_dataset.csv',
            'olist_order_items_dataset.csv',
            'olist_products_dataset.csv',
            'olist_sellers_dataset.csv',
            'olist_order_payments_dataset.csv',
            'olist_order_reviews_dataset.csv',
            'product_category_name_translation.csv',
            'olist_geolocation_dataset.csv',
        ]
        
        existing = []
        missing = []
        
        for file in expected_files:
            file_path = self.output_dir / file
            if file_path.exists():
                existing.append(file)
            else:
                missing.append(file)
        
        if existing:
            logger.info(f"Arquivos existentes: {len(existing)}/{len(expected_files)}")
            for f in existing:
                logger.debug(f"  ✓ {f}")
        
        if missing:
            logger.info(f"Arquivos faltantes: {len(missing)}/{len(expected_files)}")
            for f in missing:
                logger.debug(f"  ✗ {f}")
        
        return len(missing) == 0
    
    def download_dataset(self, force: bool = False) -> bool:
        """
        Baixa o dataset do Kaggle
        
        Args:
            force: Se True, baixa mesmo se arquivos já existem
            
        Returns:
            True se sucesso, False caso contrário
        """
        logger.info("=" * 60)
        logger.info("DOWNLOAD DO DATASET OLIST - KAGGLE")
        logger.info("=" * 60)
        
        # Verificar se arquivos já existem
        if not force and self._check_existing_files():
            logger.warning("⚠️ Todos os arquivos já existem!")
            logger.info("Use force=True para baixar novamente")
            return True
        
        # Verificar pré-requisitos
        if not self._install_kaggle_package():
            return False
        
        if not self._check_kaggle_credentials():
            return False
        
        try:
            import kaggle
            
            logger.info(f"\nBaixando dataset: {self.dataset_name}")
            logger.info(f"Destino: {self.output_dir.absolute()}")
            
            # Download
            kaggle.api.dataset_download_files(
                self.dataset_name,
                path=str(self.output_dir),
                unzip=True,
                quiet=False
            )
            
            logger.success("\n✓ Download concluído!")
            
            # Verificar arquivos baixados
            csv_files = list(self.output_dir.glob("*.csv"))
            logger.info(f"\nArquivos CSV baixados: {len(csv_files)}")
            for csv in csv_files:
                size_mb = csv.stat().st_size / (1024 * 1024)
                logger.info(f"  ✓ {csv.name} ({size_mb:.2f} MB)")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao baixar dataset: {str(e)}")
            return False
    
    def extract_zip(self, zip_path: Optional[str] = None) -> bool:
        """
        Extrai arquivo ZIP do Kaggle (se necessário)
        
        Args:
            zip_path: Caminho do arquivo ZIP. Se None, procura no output_dir
            
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            # Procurar arquivo ZIP
            if zip_path is None:
                zip_files = list(self.output_dir.glob("*.zip"))
                if not zip_files:
                    logger.info("Nenhum arquivo ZIP encontrado para extrair")
                    return True
                zip_path = zip_files[0]
            else:
                zip_path = Path(zip_path)
            
            logger.info(f"Extraindo: {zip_path.name}")
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.output_dir)
            
            logger.success(f"✓ Arquivos extraídos para: {self.output_dir}")
            
            # Remover ZIP após extrair
            zip_path.unlink()
            logger.info(f"✓ Arquivo ZIP removido: {zip_path.name}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair ZIP: {str(e)}")
            return False
    
    def get_dataset_info(self) -> dict:
        """
        Obtém informações sobre o dataset
        
        Returns:
            Dict com informações do dataset
        """
        try:
            import kaggle
            
            # Buscar metadata do dataset
            datasets = kaggle.api.dataset_list(search=self.dataset_name)
            
            if datasets:
                dataset = datasets[0]
                info = {
                    "title": dataset.title,
                    "size": dataset.size,
                    "last_updated": dataset.lastUpdated,
                    "download_count": dataset.downloadCount,
                    "vote_count": dataset.voteCount,
                    "url": f"https://www.kaggle.com/datasets/{self.dataset_name}"
                }
                
                logger.info("\nInformações do Dataset:")
                logger.info(f"  Título: {info['title']}")
                logger.info(f"  Tamanho: {info['size']}")
                logger.info(f"  Última atualização: {info['last_updated']}")
                logger.info(f"  Downloads: {info['download_count']:,}")
                logger.info(f"  URL: {info['url']}")
                
                return info
            
        except Exception as e:
            logger.warning(f"Não foi possível obter info do dataset: {str(e)}")
        
        return {}
    
    def validate_downloaded_files(self) -> bool:
        """
        Valida se todos os arquivos esperados foram baixados
        
        Returns:
            True se todos os arquivos existem, False caso contrário
        """
        logger.info("\nValidando arquivos baixados...")
        
        expected_files = {
            'olist_customers_dataset.csv': 99441,  # Linhas esperadas (aproximado)
            'olist_orders_dataset.csv': 99441,
            'olist_order_items_dataset.csv': 112650,
            'olist_products_dataset.csv': 32951,
            'olist_sellers_dataset.csv': 3095,
            'olist_order_payments_dataset.csv': 103886,
            'olist_order_reviews_dataset.csv': 99224,
            'product_category_name_translation.csv': 71,
        }
        
        all_valid = True
        
        for filename, expected_rows in expected_files.items():
            file_path = self.output_dir / filename
            
            if not file_path.exists():
                logger.error(f"  ❌ Arquivo faltando: {filename}")
                all_valid = False
                continue
            
            try:
                import pandas as pd
                df = pd.read_csv(file_path)
                actual_rows = len(df)
                
                # Tolerância de 5% no número de linhas
                tolerance = expected_rows * 0.05
                if abs(actual_rows - expected_rows) <= tolerance:
                    logger.success(f"  ✓ {filename}: {actual_rows:,} linhas")
                else:
                    logger.warning(
                        f"  ⚠️ {filename}: {actual_rows:,} linhas "
                        f"(esperado ~{expected_rows:,})"
                    )
                
            except Exception as e:
                logger.error(f"  ❌ Erro ao validar {filename}: {str(e)}")
                all_valid = False
        
        if all_valid:
            logger.success("\n✅ Todos os arquivos validados com sucesso!")
        else:
            logger.error("\n❌ Alguns arquivos falharam na validação")
        
        return all_valid


def main():
    """Função principal"""
    
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Download do dataset Olist do Kaggle"
    )
    parser.add_argument(
        '--output-dir',
        default='./data/raw',
        help='Diretório de destino (default: ./data/raw)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Forçar download mesmo se arquivos existem'
    )
    parser.add_argument(
        '--info',
        action='store_true',
        help='Apenas mostrar informações do dataset'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Apenas validar arquivos existentes'
    )
    
    args = parser.parse_args()
    
    # Inicializar extrator
    extractor = KaggleExtractor(output_dir=args.output_dir)
    
    # Modo: apenas info
    if args.info:
        extractor.get_dataset_info()
        sys.exit(0)
    
    # Modo: apenas validar
    if args.validate:
        if extractor.validate_downloaded_files():
            sys.exit(0)
        else:
            sys.exit(1)
    
    # Modo: download
    success = extractor.download_dataset(force=args.force)
    
    if success:
        # Validar após download
        extractor.validate_downloaded_files()
        logger.success("\n🎉 Dataset Olist baixado e validado com sucesso!")
        sys.exit(0)
    else:
        logger.error("\n❌ Falha ao baixar dataset")
        sys.exit(1)


if __name__ == "__main__":
    main()