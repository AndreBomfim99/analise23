# python/etl/__init__.py
"""
ETL Package - Olist E-Commerce Analytics
-----------------------------------------
Módulo de ETL para ingestão de dados no BigQuery.
"""

__version__ = "1.0.0"
__author__ = "Andre Bomfim"

from .load_to_bigquery import OlistBigQueryETL

__all__ = [
    "OlistBigQueryETL",
]