"""
Configuration management
"""
import os
import yaml
from typing import Any, Dict, Optional


_config: Optional[Dict[str, Any]] = None


def load_config(config_path: str = 'config.yaml') -> Dict[str, Any]:
    """
    Load configuration from YAML file

    Args:
        config_path: Path to configuration file

    Returns:
        Configuration dictionary
    """
    global _config

    if not os.path.exists(config_path):
        _config = get_default_config()
        return _config

    with open(config_path, 'r') as f:
        _config = yaml.safe_load(f)

    return _config


def get_config() -> Dict[str, Any]:
    """
    Get current configuration

    Returns:
        Configuration dictionary
    """
    global _config

    if _config is None:
        _config = get_default_config()

    return _config


def get_default_config() -> Dict[str, Any]:
    """
    Get default configuration

    Returns:
        Default configuration dictionary
    """
    return {
        'etl': {
            'batch_size': 100,
            'max_retries': 3,
            'timeout': 30
        },
        'extractors': {
            'html': {
                'parser': 'lxml',
                'timeout': 10
            },
            'pdf': {
                'extract_images': False,
                'extract_tables': True
            },
            'image': {
                'ocr_lang': 'eng',
                'max_size': 10485760  # 10MB
            }
        },
        'enrichment': {
            'entity_recognition': {
                'model': 'en_core_web_sm',
                'confidence_threshold': 0.7
            },
            'sentiment': {
                'model': 'textblob'
            },
            'topics': {
                'num_topics': 10,
                'num_words': 10
            }
        },
        'storage': {
            'default_backend': 'file',
            'file': {
                'output_dir': './output'
            },
            'sql': {
                'connection_string': 'sqlite:///osint_data.db'
            },
            'mongo': {
                'host': 'localhost',
                'port': 27017,
                'database': 'osint'
            }
        }
    }
