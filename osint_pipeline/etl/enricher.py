"""
Data enrichment orchestrator
"""
from typing import Any, Dict, List, Optional
from datetime import datetime


class DataEnricher:
    """Orchestrates data enrichment operations"""

    def __init__(self):
        self.enrichers = []
        self.metadata = {}

    def register_enricher(self, enricher: Any, name: str):
        """
        Register an enricher module

        Args:
            enricher: Enricher instance
            name: Name of the enricher
        """
        self.enrichers.append({
            'name': name,
            'enricher': enricher,
            'enabled': True
        })

    def enable_enricher(self, name: str):
        """Enable specific enricher"""
        for enricher in self.enrichers:
            if enricher['name'] == name:
                enricher['enabled'] = True

    def disable_enricher(self, name: str):
        """Disable specific enricher"""
        for enricher in self.enrichers:
            if enricher['name'] == name:
                enricher['enabled'] = False

    def enrich(self, data: Dict[str, Any], fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Enrich data using registered enrichers

        Args:
            data: Data to enrich
            fields: Specific fields to enrich (None = all)

        Returns:
            Enriched data dictionary
        """
        enriched_data = data.copy()
        enriched_data['enrichment'] = {
            'timestamp': datetime.utcnow().isoformat(),
            'results': {}
        }

        for enricher_info in self.enrichers:
            if not enricher_info['enabled']:
                continue

            enricher = enricher_info['enricher']
            name = enricher_info['name']

            try:
                # Call enricher's enrich method
                if hasattr(enricher, 'enrich'):
                    result = enricher.enrich(data, fields)
                    enriched_data['enrichment']['results'][name] = result
                elif hasattr(enricher, 'analyze'):
                    result = enricher.analyze(data.get('text', ''))
                    enriched_data['enrichment']['results'][name] = result
                else:
                    enriched_data['enrichment']['results'][name] = {
                        'error': 'No suitable method found'
                    }
            except Exception as e:
                enriched_data['enrichment']['results'][name] = {
                    'error': str(e)
                }

        return enriched_data

    def enrich_batch(self, data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich multiple data items

        Args:
            data_list: List of data dictionaries to enrich

        Returns:
            List of enriched data dictionaries
        """
        return [self.enrich(data) for data in data_list]

    def get_enrichment_context(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get enrichment context and metadata

        Args:
            data: Data with enrichment

        Returns:
            Context dictionary
        """
        if 'enrichment' not in data:
            return {}

        enrichment = data['enrichment']
        results = enrichment.get('results', {})

        context = {
            'timestamp': enrichment.get('timestamp'),
            'enrichers_applied': list(results.keys()),
            'success_count': sum(1 for r in results.values() if 'error' not in r),
            'error_count': sum(1 for r in results.values() if 'error' in r)
        }

        return context
