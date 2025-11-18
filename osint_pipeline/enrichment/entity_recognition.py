"""
Entity recognition for names, locations, and organizations
"""
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import re


class EntityRecognizer:
    """Named Entity Recognition using spaCy and pattern matching"""

    def __init__(self, model: str = 'en_core_web_sm', confidence_threshold: float = 0.7):
        """
        Initialize entity recognizer

        Args:
            model: spaCy model to use
            confidence_threshold: Minimum confidence for entity recognition
        """
        self.model_name = model
        self.confidence_threshold = confidence_threshold
        self.nlp = None
        self._load_model()

    def _load_model(self):
        """Load spaCy model"""
        try:
            import spacy
            try:
                self.nlp = spacy.load(self.model_name)
            except OSError:
                # Model not found, use pattern matching fallback
                self.nlp = None
        except ImportError:
            # spaCy not installed, use pattern matching fallback
            self.nlp = None

    def enrich(self, data: Dict[str, Any], fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Enrich data with entity recognition

        Args:
            data: Input data
            fields: Specific fields to analyze

        Returns:
            Enriched data with entities
        """
        # Extract text from data
        text = self._extract_text(data, fields)

        if not text:
            return {
                'entities': [],
                'entity_counts': {},
                'timestamp': datetime.utcnow().isoformat()
            }

        # Recognize entities
        entities = self.recognize_entities(text)

        return {
            'entities': entities,
            'entity_counts': self._count_entities(entities),
            'timestamp': datetime.utcnow().isoformat()
        }

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze text for entities

        Args:
            text: Input text

        Returns:
            Analysis results
        """
        entities = self.recognize_entities(text)

        return {
            'entities': entities,
            'entity_counts': self._count_entities(entities),
            'timestamp': datetime.utcnow().isoformat()
        }

    def recognize_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Recognize named entities in text

        Args:
            text: Input text

        Returns:
            List of entity dictionaries
        """
        if self.nlp:
            return self._recognize_with_spacy(text)
        else:
            return self._recognize_with_patterns(text)

    def _recognize_with_spacy(self, text: str) -> List[Dict[str, Any]]:
        """
        Recognize entities using spaCy

        Args:
            text: Input text

        Returns:
            List of entities
        """
        doc = self.nlp(text)
        entities = []

        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char,
                'confidence': 1.0  # spaCy doesn't provide confidence scores by default
            })

        return entities

    def _recognize_with_patterns(self, text: str) -> List[Dict[str, Any]]:
        """
        Recognize entities using pattern matching (fallback)

        Args:
            text: Input text

        Returns:
            List of entities
        """
        entities = []

        # Person names (capitalized words in sequence)
        person_pattern = r'\b([A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b'
        for match in re.finditer(person_pattern, text):
            entities.append({
                'text': match.group(1),
                'label': 'PERSON',
                'start': match.start(),
                'end': match.end(),
                'confidence': 0.6
            })

        # Organizations (words with Inc., Corp., LLC, etc.)
        org_pattern = r'\b([A-Z][A-Za-z\s&]+(?:Inc\.|Corp\.|LLC|Ltd\.|Company|Corporation))\b'
        for match in re.finditer(org_pattern, text):
            entities.append({
                'text': match.group(1),
                'label': 'ORG',
                'start': match.start(),
                'end': match.end(),
                'confidence': 0.7
            })

        # Locations (common location patterns)
        location_keywords = ['Street', 'Avenue', 'Road', 'Boulevard', 'City', 'State', 'Country']
        for keyword in location_keywords:
            pattern = rf'\b([A-Z][A-Za-z\s]+{keyword})\b'
            for match in re.finditer(pattern, text):
                entities.append({
                    'text': match.group(1),
                    'label': 'GPE',
                    'start': match.start(),
                    'end': match.end(),
                    'confidence': 0.6
                })

        # Dates
        date_pattern = r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})\b'
        for match in re.finditer(date_pattern, text, re.IGNORECASE):
            entities.append({
                'text': match.group(0),
                'label': 'DATE',
                'start': match.start(),
                'end': match.end(),
                'confidence': 0.8
            })

        # Money
        money_pattern = r'\$[\d,]+(?:\.\d{2})?|\b\d+\s*(?:dollars?|USD|EUR|GBP)\b'
        for match in re.finditer(money_pattern, text, re.IGNORECASE):
            entities.append({
                'text': match.group(0),
                'label': 'MONEY',
                'start': match.start(),
                'end': match.end(),
                'confidence': 0.8
            })

        # Filter by confidence threshold
        entities = [e for e in entities if e['confidence'] >= self.confidence_threshold]

        return entities

    def _extract_text(self, data: Dict[str, Any], fields: Optional[List[str]] = None) -> str:
        """Extract text from data dictionary"""
        texts = []

        if fields:
            for field in fields:
                if field in data and isinstance(data[field], str):
                    texts.append(data[field])
        else:
            # Extract all string fields
            for value in data.values():
                if isinstance(value, str):
                    texts.append(value)

        return ' '.join(texts)

    def _count_entities(self, entities: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count entities by type"""
        counts = {}

        for entity in entities:
            label = entity['label']
            counts[label] = counts.get(label, 0) + 1

        return counts

    def extract_persons(self, text: str) -> List[str]:
        """
        Extract person names from text

        Args:
            text: Input text

        Returns:
            List of person names
        """
        entities = self.recognize_entities(text)
        return [e['text'] for e in entities if e['label'] == 'PERSON']

    def extract_organizations(self, text: str) -> List[str]:
        """
        Extract organization names from text

        Args:
            text: Input text

        Returns:
            List of organization names
        """
        entities = self.recognize_entities(text)
        return [e['text'] for e in entities if e['label'] == 'ORG']

    def extract_locations(self, text: str) -> List[str]:
        """
        Extract location names from text

        Args:
            text: Input text

        Returns:
            List of location names
        """
        entities = self.recognize_entities(text)
        return [e['text'] for e in entities if e['label'] in ['GPE', 'LOC', 'FAC']]
