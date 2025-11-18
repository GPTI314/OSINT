"""
Topic modeling for content analysis
"""
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from collections import Counter
import re


class TopicModeler:
    """Extract topics from text using various methods"""

    def __init__(self, num_topics: int = 10, num_words: int = 10):
        """
        Initialize topic modeler

        Args:
            num_topics: Number of topics to extract
            num_words: Number of words per topic
        """
        self.num_topics = num_topics
        self.num_words = num_words

    def enrich(self, data: Dict[str, Any], fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Enrich data with topic modeling

        Args:
            data: Input data
            fields: Specific fields to analyze

        Returns:
            Enriched data with topics
        """
        # Extract text from data
        text = self._extract_text(data, fields)

        if not text:
            return {
                'topics': [],
                'timestamp': datetime.utcnow().isoformat()
            }

        # Extract topics
        topics = self.extract_topics(text)

        return topics

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze text for topics

        Args:
            text: Input text

        Returns:
            Topic analysis results
        """
        return self.extract_topics(text)

    def extract_topics(self, text: str) -> Dict[str, Any]:
        """
        Extract topics from text

        Args:
            text: Input text

        Returns:
            Topics dictionary
        """
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
            from sklearn.decomposition import LatentDirichletAllocation

            # Prepare text
            documents = self._split_into_documents(text)

            if len(documents) < 2:
                # Not enough documents, use simple keyword extraction
                return self._extract_topics_simple(text)

            # Create document-term matrix
            vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')
            doc_term_matrix = vectorizer.fit_transform(documents)

            # Perform LDA
            lda = LatentDirichletAllocation(
                n_components=min(self.num_topics, len(documents)),
                random_state=42
            )
            lda.fit(doc_term_matrix)

            # Extract topics
            topics = []
            feature_names = vectorizer.get_feature_names_out()

            for topic_idx, topic in enumerate(lda.components_):
                top_word_indices = topic.argsort()[-self.num_words:][::-1]
                top_words = [feature_names[i] for i in top_word_indices]
                weights = [topic[i] for i in top_word_indices]

                topics.append({
                    'topic_id': topic_idx,
                    'words': top_words,
                    'weights': [round(w, 4) for w in weights]
                })

            return {
                'topics': topics,
                'num_topics': len(topics),
                'method': 'lda',
                'timestamp': datetime.utcnow().isoformat()
            }

        except ImportError:
            # sklearn not available, use simple method
            return self._extract_topics_simple(text)
        except Exception as e:
            return {
                'topics': [],
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def _extract_topics_simple(self, text: str) -> Dict[str, Any]:
        """
        Simple topic extraction using word frequency

        Args:
            text: Input text

        Returns:
            Topics dictionary
        """
        # Tokenize and clean
        words = self._tokenize(text)

        # Remove stop words
        stop_words = self._get_stop_words()
        words = [w for w in words if w not in stop_words and len(w) > 2]

        # Count word frequency
        word_freq = Counter(words)

        # Get top words as "topics"
        top_words = word_freq.most_common(self.num_words)

        topics = [{
            'topic_id': 0,
            'words': [word for word, _ in top_words],
            'frequencies': [count for _, count in top_words]
        }]

        return {
            'topics': topics,
            'num_topics': 1,
            'method': 'frequency',
            'timestamp': datetime.utcnow().isoformat()
        }

    def _split_into_documents(self, text: str) -> List[str]:
        """Split text into documents (paragraphs or sentences)"""
        # Split by double newline (paragraphs)
        paragraphs = text.split('\n\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        if len(paragraphs) > 1:
            return paragraphs

        # Fallback to sentences
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]

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
            'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'our', 'their',
            'am', 'been', 'get', 'got', 'out', 'up', 'down', 'what', 'when',
            'where', 'who', 'which', 'how', 'all', 'each', 'every', 'some', 'any'
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

    def get_topic_summary(self, topics: List[Dict[str, Any]]) -> str:
        """
        Get human-readable summary of topics

        Args:
            topics: List of topic dictionaries

        Returns:
            Summary string
        """
        summaries = []

        for topic in topics:
            topic_id = topic.get('topic_id', 0)
            words = topic.get('words', [])
            top_words = ', '.join(words[:5])
            summaries.append(f"Topic {topic_id}: {top_words}")

        return '\n'.join(summaries)
