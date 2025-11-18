"""
OSINT Data Processing Pipeline

A comprehensive toolkit for processing OSINT data with ETL capabilities,
multiple extractors, and advanced enrichment features.
"""

__version__ = "1.0.0"

from .etl.pipeline import ETLPipeline
from .etl.processor import DataProcessor

__all__ = ['ETLPipeline', 'DataProcessor']
