"""
Text data extractor with NLP, regex, and pattern matching
"""
from typing import Any, Dict, List, Optional, Tuple
import re
from datetime import datetime
from collections import Counter


class TextExtractor:
    """Extract structured data from unstructured text"""

    def __init__(self):
        """Initialize text extractor"""
        self.patterns = self._initialize_patterns()

    def _initialize_patterns(self) -> Dict[str, str]:
        """Initialize common regex patterns"""
        return {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'url': r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            'phone_us': r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b',
            'phone_intl': r'\+?[1-9]\d{1,14}',
            'ip_address': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
            'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'date_iso': r'\b\d{4}-\d{2}-\d{2}\b',
            'date_us': r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',
            'time': r'\b\d{1,2}:\d{2}(?::\d{2})?\s?(?:AM|PM|am|pm)?\b',
            'hashtag': r'#\w+',
            'mention': r'@\w+',
            'bitcoin_address': r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b',
            'mac_address': r'\b(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})\b'
        }

    def extract(self, source: str, **kwargs) -> Dict[str, Any]:
        """
        Extract data from text

        Args:
            source: Text string
            **kwargs: Additional extraction options

        Returns:
            Extracted data dictionary
        """
        extracted_data = {
            'source_type': 'text',
            'extracted_at': datetime.utcnow().isoformat(),
            'text': source,
            'length': len(source),
            'patterns': self.extract_patterns(source),
            'statistics': self.extract_statistics(source),
            'entities': self.extract_entities(source),
            'custom_data': {}
        }

        # Apply custom patterns if provided
        if 'custom_patterns' in kwargs:
            extracted_data['custom_data']['patterns'] = self.extract_custom_patterns(
                source, kwargs['custom_patterns']
            )

        # Extract sentences if requested
        if kwargs.get('extract_sentences', False):
            extracted_data['sentences'] = self.extract_sentences(source)

        # Extract words if requested
        if kwargs.get('extract_words', False):
            extracted_data['words'] = self.extract_words(source)

        return extracted_data

    def extract_patterns(self, text: str) -> Dict[str, List[str]]:
        """
        Extract common patterns from text

        Args:
            text: Input text

        Returns:
            Dictionary of extracted patterns
        """
        results = {}

        for pattern_name, pattern in self.patterns.items():
            matches = re.findall(pattern, text)

            # Handle tuple results (e.g., from grouped patterns)
            if matches and isinstance(matches[0], tuple):
                matches = ['-'.join(match) if isinstance(match, tuple) else match for match in matches]

            if matches:
                results[pattern_name] = list(set(matches))  # Remove duplicates

        return results

    def extract_custom_patterns(self, text: str, patterns: Dict[str, str]) -> Dict[str, List[str]]:
        """
        Extract data using custom regex patterns

        Args:
            text: Input text
            patterns: Dictionary mapping names to regex patterns

        Returns:
            Dictionary of extracted data
        """
        results = {}

        for name, pattern in patterns.items():
            try:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    results[name] = matches
            except Exception as e:
                results[name] = f"Error: {str(e)}"

        return results

    def extract_statistics(self, text: str) -> Dict[str, Any]:
        """
        Extract text statistics

        Args:
            text: Input text

        Returns:
            Statistics dictionary
        """
        words = re.findall(r'\b\w+\b', text.lower())
        sentences = self.extract_sentences(text)
        lines = text.split('\n')

        return {
            'character_count': len(text),
            'word_count': len(words),
            'unique_word_count': len(set(words)),
            'sentence_count': len(sentences),
            'line_count': len(lines),
            'average_word_length': sum(len(word) for word in words) / len(words) if words else 0,
            'average_sentence_length': len(words) / len(sentences) if sentences else 0
        }

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities using pattern matching

        Args:
            text: Input text

        Returns:
            Dictionary of entities
        """
        entities = {
            'emails': [],
            'urls': [],
            'phones': [],
            'ips': [],
            'hashtags': [],
            'mentions': []
        }

        # Extract using predefined patterns
        patterns_data = self.extract_patterns(text)

        if 'email' in patterns_data:
            entities['emails'] = patterns_data['email']

        if 'url' in patterns_data:
            entities['urls'] = patterns_data['url']

        if 'phone_us' in patterns_data or 'phone_intl' in patterns_data:
            entities['phones'] = patterns_data.get('phone_us', []) + patterns_data.get('phone_intl', [])

        if 'ip_address' in patterns_data:
            entities['ips'] = patterns_data['ip_address']

        if 'hashtag' in patterns_data:
            entities['hashtags'] = patterns_data['hashtag']

        if 'mention' in patterns_data:
            entities['mentions'] = patterns_data['mention']

        # Extract capitalized words (potential proper nouns)
        capitalized = re.findall(r'\b[A-Z][a-z]+\b', text)
        entities['capitalized_words'] = list(set(capitalized))

        return entities

    def extract_sentences(self, text: str) -> List[str]:
        """
        Extract sentences from text

        Args:
            text: Input text

        Returns:
            List of sentences
        """
        # Simple sentence splitting (can be improved with NLP libraries)
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]

    def extract_words(self, text: str) -> List[str]:
        """
        Extract words from text

        Args:
            text: Input text

        Returns:
            List of words
        """
        words = re.findall(r'\b\w+\b', text.lower())
        return words

    def extract_ngrams(self, text: str, n: int = 2) -> List[Tuple[str, ...]]:
        """
        Extract n-grams from text

        Args:
            text: Input text
            n: N-gram size

        Returns:
            List of n-grams
        """
        words = self.extract_words(text)
        ngrams = []

        for i in range(len(words) - n + 1):
            ngrams.append(tuple(words[i:i+n]))

        return ngrams

    def extract_word_frequency(self, text: str, top_n: int = 20) -> List[Tuple[str, int]]:
        """
        Extract word frequency

        Args:
            text: Input text
            top_n: Number of top words to return

        Returns:
            List of (word, frequency) tuples
        """
        words = self.extract_words(text)

        # Filter out common stop words (basic list)
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that',
            'these', 'those', 'it', 'its', 'i', 'you', 'he', 'she', 'we', 'they'
        }

        filtered_words = [word for word in words if word not in stop_words]
        word_counts = Counter(filtered_words)

        return word_counts.most_common(top_n)

    def extract_quoted_text(self, text: str) -> List[str]:
        """
        Extract quoted text

        Args:
            text: Input text

        Returns:
            List of quoted strings
        """
        # Match both single and double quotes
        quotes = re.findall(r'"([^"]+)"|\'([^\']+)\'', text)

        # Flatten the tuple results
        return [q[0] or q[1] for q in quotes]

    def extract_code_blocks(self, text: str) -> List[str]:
        """
        Extract code blocks (markdown-style)

        Args:
            text: Input text

        Returns:
            List of code blocks
        """
        # Match code blocks with triple backticks
        code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', text, re.DOTALL)

        # Also match inline code
        inline_code = re.findall(r'`([^`]+)`', text)

        return {
            'blocks': code_blocks,
            'inline': inline_code
        }

    def clean_text(self, text: str, remove_urls: bool = True, remove_emails: bool = True,
                   remove_numbers: bool = False, lowercase: bool = False) -> str:
        """
        Clean and normalize text

        Args:
            text: Input text
            remove_urls: Remove URLs
            remove_emails: Remove email addresses
            remove_numbers: Remove numbers
            lowercase: Convert to lowercase

        Returns:
            Cleaned text
        """
        cleaned = text

        if remove_urls:
            cleaned = re.sub(self.patterns['url'], '', cleaned)

        if remove_emails:
            cleaned = re.sub(self.patterns['email'], '', cleaned)

        if remove_numbers:
            cleaned = re.sub(r'\d+', '', cleaned)

        if lowercase:
            cleaned = cleaned.lower()

        # Clean up whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)

        return cleaned.strip()
