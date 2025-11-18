"""
Keyword extraction from text
"""
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from collections import Counter
import re


class KeywordExtractor:
    """Extract important keywords from text"""

    def __init__(self, top_n: int = 20):
        """
        Initialize keyword extractor

        Args:
            top_n: Number of top keywords to extract
        """
        self.top_n = top_n

    def enrich(self, data: Dict[str, Any], fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Enrich data with keyword extraction

        Args:
            data: Input data
            fields: Specific fields to analyze

        Returns:
            Enriched data with keywords
        """
        # Extract text from data
        text = self._extract_text(data, fields)

        if not text:
            return {
                'keywords': [],
                'timestamp': datetime.utcnow().isoformat()
            }

        # Extract keywords
        keywords = self.extract(text)

        return keywords

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze text for keywords

        Args:
            text: Input text

        Returns:
            Keyword analysis results
        """
        return self.extract(text)

    def extract(self, text: str) -> Dict[str, Any]:
        """
        Extract keywords from text

        Args:
            text: Input text

        Returns:
            Keywords dictionary
        """
        # Try TF-IDF method first
        try:
            keywords_tfidf = self._extract_tfidf(text)
            return {
                'keywords': keywords_tfidf,
                'method': 'tfidf',
                'count': len(keywords_tfidf),
                'timestamp': datetime.utcnow().isoformat()
            }
        except ImportError:
            # Fall back to frequency-based method
            keywords_freq = self._extract_frequency(text)
            return {
                'keywords': keywords_freq,
                'method': 'frequency',
                'count': len(keywords_freq),
                'timestamp': datetime.utcnow().isoformat()
            }

    def _extract_tfidf(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract keywords using TF-IDF

        Args:
            text: Input text

        Returns:
            List of keyword dictionaries
        """
        from sklearn.feature_extraction.text import TfidfVectorizer

        # Split into sentences for TF-IDF
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) < 2:
            # Not enough sentences, use frequency method
            return self._extract_frequency(text)

        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            max_features=self.top_n,
            stop_words='english',
            ngram_range=(1, 2)  # Include unigrams and bigrams
        )

        # Fit and transform
        tfidf_matrix = vectorizer.fit_transform(sentences)
        feature_names = vectorizer.get_feature_names_out()

        # Get average TF-IDF scores
        avg_scores = tfidf_matrix.mean(axis=0).A1

        # Create keyword list
        keywords = []
        for idx, score in enumerate(avg_scores):
            keywords.append({
                'keyword': feature_names[idx],
                'score': round(score, 4)
            })

        # Sort by score
        keywords.sort(key=lambda x: x['score'], reverse=True)

        return keywords[:self.top_n]

    def _extract_frequency(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract keywords using word frequency

        Args:
            text: Input text

        Returns:
            List of keyword dictionaries
        """
        # Tokenize
        words = self._tokenize(text)

        # Remove stop words
        stop_words = self._get_stop_words()
        words = [w for w in words if w not in stop_words and len(w) > 2]

        # Count frequencies
        word_freq = Counter(words)

        # Get top keywords
        top_keywords = word_freq.most_common(self.top_n)

        keywords = []
        for word, count in top_keywords:
            keywords.append({
                'keyword': word,
                'frequency': count,
                'score': count  # Use frequency as score
            })

        return keywords

    def extract_phrases(self, text: str, max_phrase_length: int = 3) -> List[Dict[str, Any]]:
        """
        Extract key phrases (n-grams)

        Args:
            text: Input text
            max_phrase_length: Maximum length of phrases

        Returns:
            List of phrase dictionaries
        """
        phrases = []

        # Extract n-grams
        for n in range(2, max_phrase_length + 1):
            ngrams = self._extract_ngrams(text, n)
            phrases.extend(ngrams)

        # Sort by frequency
        phrases.sort(key=lambda x: x['frequency'], reverse=True)

        return phrases[:self.top_n]

    def _extract_ngrams(self, text: str, n: int) -> List[Dict[str, Any]]:
        """
        Extract n-grams from text

        Args:
            text: Input text
            n: N-gram size

        Returns:
            List of n-gram dictionaries
        """
        words = self._tokenize(text)
        stop_words = self._get_stop_words()

        # Filter stop words
        words = [w for w in words if w not in stop_words]

        # Create n-grams
        ngrams = []
        for i in range(len(words) - n + 1):
            ngram = ' '.join(words[i:i+n])
            ngrams.append(ngram)

        # Count frequencies
        ngram_freq = Counter(ngrams)

        # Convert to list of dictionaries
        results = []
        for ngram, count in ngram_freq.items():
            results.append({
                'phrase': ngram,
                'frequency': count,
                'length': n
            })

        return results

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words"""
        # Convert to lowercase and extract words
        words = re.findall(r'\b[a-z]+\b', text.lower())
        return words

    def _get_stop_words(self) -> set:
        """Get common English stop words"""
        return {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that',
            'these', 'those', 'it', 'its', 'i', 'you', 'he', 'she', 'we', 'they',
            'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'our', 'their'
        }

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

    def extract_named_entities_as_keywords(self, text: str) -> List[str]:
        """
        Extract named entities as keywords

        Args:
            text: Input text

        Returns:
            List of entity keywords
        """
        # Simple capitalized word extraction
        capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)

        # Remove duplicates and count
        entity_freq = Counter(capitalized)

        # Get top entities
        top_entities = [entity for entity, _ in entity_freq.most_common(self.top_n)]

        return top_entities
