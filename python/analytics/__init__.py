# python/analytics/__init__.py
"""
Analytics Package - Olist E-Commerce Analytics
-----------------------------------------------
Módulo de análises avançadas (LTV, RFM, Cohort, etc).
"""

__version__ = "1.0.0"
__author__ = "Andre Bomfim"

from .rfm_segmentation import RFMAnalyzer

__all__ = [
    "RFMAnalyzer",
]