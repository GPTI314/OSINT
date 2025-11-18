"""
Configuration Settings
Centralized configuration management using Pydantic
"""

from typing import Optional, List, Dict
from pathlib import Path
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings
from loguru import logger


class ProxyConfig(BaseModel):
    """Proxy configuration"""
    enabled: bool = False
    proxies: List[str] = Field(default_factory=list)
    rotation: bool = True
    test_url: str = "http://httpbin.org/ip"
    max_failures: int = 3


class UserAgentConfig(BaseModel):
    """User-Agent configuration"""
    rotation: bool = True
    browser_type: str = "random"  # chrome, firefox, safari, edge, random
    device_type: str = "desktop"  # desktop, mobile, tablet
    custom_user_agents: List[str] = Field(default_factory=list)


class RateLimitConfig(BaseModel):
    """Rate limiting configuration"""
    enabled: bool = True
    requests_per_second: float = 1.0
    burst_size: Optional[int] = None
    adaptive: bool = False
    domain_specific: Dict[str, float] = Field(default_factory=dict)


class CaptchaConfig(BaseModel):
    """CAPTCHA solving configuration"""
    enabled: bool = False
    service: str = "2captcha"  # 2captcha, anticaptcha
    api_key: Optional[str] = None
    timeout: int = 120


class ScraperConfig(BaseModel):
    """Base scraper configuration"""
    timeout: int = 30
    max_retries: int = 3
    retry_backoff_factor: float = 2.0
    verify_ssl: bool = True
    headers: Dict[str, str] = Field(default_factory=dict)
    cookies: Dict[str, str] = Field(default_factory=dict)


class HTMLScraperConfig(ScraperConfig):
    """HTML scraper configuration"""
    parser: str = "lxml"  # lxml, html.parser, html5lib


class JSScraperConfig(ScraperConfig):
    """JavaScript scraper configuration"""
    browser_type: str = "chromium"  # chromium, firefox, webkit
    headless: bool = True
    viewport_width: int = 1920
    viewport_height: int = 1080
    ignore_https_errors: bool = False
    default_wait_time: int = 2


class APIScraperConfig(ScraperConfig):
    """API scraper configuration"""
    base_url: Optional[str] = None
    auth_type: Optional[str] = None  # basic, bearer, api_key
    api_key: Optional[str] = None
    api_key_header: str = "X-API-Key"
    bearer_token: Optional[str] = None


class FileDownloaderConfig(ScraperConfig):
    """File downloader configuration"""
    download_dir: str = "./downloads"
    chunk_size: int = 8192
    verify_mime_type: bool = True
    show_progress: bool = True


class ImageScraperConfig(FileDownloaderConfig):
    """Image scraper configuration"""
    download_dir: str = "./images"
    auto_convert: bool = False
    target_format: str = "PNG"


class LoggingConfig(BaseModel):
    """Logging configuration"""
    level: str = "INFO"
    format: str = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    colorize: bool = True
    rotation: str = "10 MB"
    retention: str = "1 week"
    log_file: Optional[str] = None


class Settings(BaseSettings):
    """
    Main configuration settings.
    Can be loaded from environment variables or .env file.
    """

    # General settings
    project_name: str = "OSINT Toolkit"
    debug: bool = False

    # Component configurations
    proxy: ProxyConfig = Field(default_factory=ProxyConfig)
    user_agent: UserAgentConfig = Field(default_factory=UserAgentConfig)
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    captcha: CaptchaConfig = Field(default_factory=CaptchaConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    # Scraper configurations
    html_scraper: HTMLScraperConfig = Field(default_factory=HTMLScraperConfig)
    js_scraper: JSScraperConfig = Field(default_factory=JSScraperConfig)
    api_scraper: APIScraperConfig = Field(default_factory=APIScraperConfig)
    file_downloader: FileDownloaderConfig = Field(default_factory=FileDownloaderConfig)
    image_scraper: ImageScraperConfig = Field(default_factory=ImageScraperConfig)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"
        case_sensitive = False

    def configure_logging(self):
        """Configure loguru logging"""
        logger.remove()  # Remove default handler

        # Add console handler
        logger.add(
            sink=lambda msg: print(msg, end=""),
            format=self.logging.format,
            level=self.logging.level,
            colorize=self.logging.colorize
        )

        # Add file handler if specified
        if self.logging.log_file:
            logger.add(
                self.logging.log_file,
                format=self.logging.format,
                level=self.logging.level,
                rotation=self.logging.rotation,
                retention=self.logging.retention
            )

        logger.info(f"Logging configured (level={self.logging.level})")


class ConfigManager:
    """
    Configuration manager for loading and saving settings
    """

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize config manager.

        Args:
            config_file: Path to configuration file (YAML or JSON)
        """
        self.config_file = config_file
        self.settings: Optional[Settings] = None

    def load(self) -> Settings:
        """
        Load configuration.

        Returns:
            Settings object
        """
        if self.config_file and Path(self.config_file).exists():
            return self.load_from_file(self.config_file)
        else:
            # Load from environment variables
            self.settings = Settings()
            logger.info("Loaded configuration from environment variables")
            return self.settings

    def load_from_file(self, filepath: str) -> Settings:
        """
        Load configuration from file.

        Args:
            filepath: Path to config file (YAML or JSON)

        Returns:
            Settings object
        """
        path = Path(filepath)

        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {filepath}")

        import yaml
        import json

        # Load based on file extension
        if path.suffix in ['.yaml', '.yml']:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
        elif path.suffix == '.json':
            with open(path, 'r') as f:
                data = json.load(f)
        else:
            raise ValueError(f"Unsupported config file format: {path.suffix}")

        self.settings = Settings(**data)
        logger.info(f"Loaded configuration from {filepath}")
        return self.settings

    def save_to_file(self, filepath: str, settings: Optional[Settings] = None):
        """
        Save configuration to file.

        Args:
            filepath: Path to save config file
            settings: Settings object (uses current if not provided)
        """
        settings = settings or self.settings
        if not settings:
            raise ValueError("No settings to save")

        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        import yaml
        import json

        # Convert to dict
        data = settings.model_dump()

        # Save based on file extension
        if path.suffix in ['.yaml', '.yml']:
            with open(path, 'w') as f:
                yaml.safe_dump(data, f, default_flow_style=False, indent=2)
        elif path.suffix == '.json':
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
        else:
            raise ValueError(f"Unsupported config file format: {path.suffix}")

        logger.info(f"Saved configuration to {filepath}")

    def create_example_config(self, filepath: str = "config.example.yaml"):
        """
        Create an example configuration file with defaults.

        Args:
            filepath: Path to save example config
        """
        example_settings = Settings()
        self.save_to_file(filepath, example_settings)
        logger.info(f"Created example configuration: {filepath}")


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get global settings instance.

    Returns:
        Settings object
    """
    global _settings
    if _settings is None:
        _settings = Settings()
        _settings.configure_logging()
    return _settings


def load_settings(config_file: Optional[str] = None) -> Settings:
    """
    Load and set global settings.

    Args:
        config_file: Optional path to config file

    Returns:
        Settings object
    """
    global _settings
    manager = ConfigManager(config_file)
    _settings = manager.load()
    _settings.configure_logging()
    return _settings
