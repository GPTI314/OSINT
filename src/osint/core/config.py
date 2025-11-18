"""
Configuration management for OSINT toolkit
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import yaml


class Config:
    """Configuration manager"""

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration

        Args:
            config_file: Path to YAML configuration file
        """
        load_dotenv()
        self.config_file = config_file
        self._config: Dict[str, Any] = {}

        if config_file and os.path.exists(config_file):
            self._load_from_file(config_file)

        self._load_from_env()

    def _load_from_file(self, config_file: str):
        """Load configuration from YAML file"""
        with open(config_file, 'r') as f:
            self._config = yaml.safe_load(f) or {}

    def _load_from_env(self):
        """Load API keys and sensitive data from environment variables"""
        env_mappings = {
            # Domain Intelligence
            'virustotal_api_key': 'VIRUSTOTAL_API_KEY',
            'shodan_api_key': 'SHODAN_API_KEY',
            'securitytrails_api_key': 'SECURITYTRAILS_API_KEY',

            # IP Intelligence
            'ipinfo_api_key': 'IPINFO_API_KEY',
            'abuseipdb_api_key': 'ABUSEIPDB_API_KEY',
            'censys_api_id': 'CENSYS_API_ID',
            'censys_api_secret': 'CENSYS_API_SECRET',

            # Email Intelligence
            'hibp_api_key': 'HIBP_API_KEY',
            'hunter_api_key': 'HUNTER_API_KEY',
            'dehashed_api_key': 'DEHASHED_API_KEY',
            'dehashed_username': 'DEHASHED_USERNAME',

            # Phone Intelligence
            'numverify_api_key': 'NUMVERIFY_API_KEY',
            'twilio_account_sid': 'TWILIO_ACCOUNT_SID',
            'twilio_auth_token': 'TWILIO_AUTH_TOKEN',

            # Social Media
            'twitter_api_key': 'TWITTER_API_KEY',
            'twitter_api_secret': 'TWITTER_API_SECRET',
            'twitter_access_token': 'TWITTER_ACCESS_TOKEN',
            'twitter_access_secret': 'TWITTER_ACCESS_SECRET',
            'twitter_bearer_token': 'TWITTER_BEARER_TOKEN',
            'linkedin_email': 'LINKEDIN_EMAIL',
            'linkedin_password': 'LINKEDIN_PASSWORD',
            'reddit_client_id': 'REDDIT_CLIENT_ID',
            'reddit_client_secret': 'REDDIT_CLIENT_SECRET',
            'reddit_user_agent': 'REDDIT_USER_AGENT',

            # Image Intelligence
            'google_api_key': 'GOOGLE_API_KEY',
            'google_cse_id': 'GOOGLE_CSE_ID',
            'yandex_api_key': 'YANDEX_API_KEY',
            'tineye_api_key': 'TINEYE_API_KEY',

            # MaxMind
            'maxmind_db_path': 'MAXMIND_DB_PATH',
        }

        for key, env_var in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                self._config[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        return self._config.get(key, default)

    def set(self, key: str, value: Any):
        """
        Set configuration value

        Args:
            key: Configuration key
            value: Configuration value
        """
        self._config[key] = value

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration"""
        return self._config.copy()
