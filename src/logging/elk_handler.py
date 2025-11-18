"""
ELK Stack integration for centralized logging.
"""

import logging
import os
from logstash_async.handler import AsynchronousLogstashHandler
from logstash_async.formatter import LogstashFormatter
from elasticsearch import Elasticsearch
from typing import Optional


class ELKHandler:
    """Handler for sending logs to ELK Stack."""

    def __init__(
        self,
        host: str = None,
        port: int = None,
        elasticsearch_host: str = None,
        elasticsearch_port: int = None
    ):
        """
        Initialize ELK handler.

        Args:
            host: Logstash host
            port: Logstash port
            elasticsearch_host: Elasticsearch host
            elasticsearch_port: Elasticsearch port
        """
        self.logstash_host = host or os.getenv('LOGSTASH_HOST', 'localhost')
        self.logstash_port = int(port or os.getenv('LOGSTASH_PORT', '5000'))
        self.es_host = elasticsearch_host or os.getenv('ELASTICSEARCH_HOST', 'localhost')
        self.es_port = int(elasticsearch_port or os.getenv('ELASTICSEARCH_PORT', '9200'))

        self.es_client: Optional[Elasticsearch] = None
        self.logstash_handler: Optional[AsynchronousLogstashHandler] = None

    def get_logstash_handler(self) -> AsynchronousLogstashHandler:
        """
        Get Logstash handler for logging.

        Returns:
            AsynchronousLogstashHandler instance
        """
        if self.logstash_handler is None:
            self.logstash_handler = AsynchronousLogstashHandler(
                host=self.logstash_host,
                port=self.logstash_port,
                database_path='logstash.db',
                transport='logstash_async.transport.TcpTransport'
            )

            # Set formatter
            formatter = LogstashFormatter(
                message_type='osint-toolkit',
                extra_prefix='extra',
                extra={
                    'service': os.getenv('APP_NAME', 'osint-toolkit'),
                    'environment': os.getenv('APP_ENV', 'development')
                }
            )
            self.logstash_handler.setFormatter(formatter)

        return self.logstash_handler

    def get_elasticsearch_client(self) -> Elasticsearch:
        """
        Get Elasticsearch client.

        Returns:
            Elasticsearch client instance
        """
        if self.es_client is None:
            self.es_client = Elasticsearch(
                [{'host': self.es_host, 'port': self.es_port, 'scheme': 'http'}],
                verify_certs=False
            )

        return self.es_client

    def add_to_logger(self, logger: logging.Logger) -> None:
        """
        Add Logstash handler to a logger.

        Args:
            logger: Logger instance
        """
        handler = self.get_logstash_handler()
        logger.addHandler(handler)

    def search_logs(
        self,
        index: str = "osint-logs-*",
        query: dict = None,
        size: int = 100
    ) -> dict:
        """
        Search logs in Elasticsearch.

        Args:
            index: Index pattern to search
            query: Elasticsearch query DSL
            size: Number of results to return

        Returns:
            Search results
        """
        es = self.get_elasticsearch_client()

        if query is None:
            query = {"match_all": {}}

        try:
            response = es.search(
                index=index,
                query=query,
                size=size,
                sort=[{"@timestamp": {"order": "desc"}}]
            )
            return response
        except Exception as e:
            logging.error(f"Failed to search logs: {e}")
            return {}

    def get_error_logs(self, hours: int = 24, size: int = 100) -> dict:
        """
        Get error logs from the last N hours.

        Args:
            hours: Number of hours to look back
            size: Number of results to return

        Returns:
            Error logs
        """
        query = {
            "bool": {
                "must": [
                    {"terms": {"level": ["ERROR", "CRITICAL"]}},
                    {
                        "range": {
                            "@timestamp": {
                                "gte": f"now-{hours}h",
                                "lte": "now"
                            }
                        }
                    }
                ]
            }
        }

        return self.search_logs(query=query, size=size)

    def create_index_template(self) -> bool:
        """
        Create index template for OSINT logs.

        Returns:
            True if successful
        """
        es = self.get_elasticsearch_client()

        template = {
            "index_patterns": ["osint-logs-*"],
            "template": {
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 1,
                    "index.lifecycle.name": "osint-logs-policy",
                    "index.lifecycle.rollover_alias": "osint-logs"
                },
                "mappings": {
                    "properties": {
                        "@timestamp": {"type": "date"},
                        "level": {"type": "keyword"},
                        "message": {"type": "text"},
                        "logger_name": {"type": "keyword"},
                        "service": {"type": "keyword"},
                        "environment": {"type": "keyword"},
                        "extra": {"type": "object"}
                    }
                }
            }
        }

        try:
            es.indices.put_index_template(
                name="osint-logs-template",
                body=template
            )
            return True
        except Exception as e:
            logging.error(f"Failed to create index template: {e}")
            return False
