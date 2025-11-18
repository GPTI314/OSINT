"""
Sentiment analysis for text data
"""
from typing import Any, Dict, List, Optional
from datetime import datetime


class SentimentAnalyzer:
    """Analyze sentiment of text using TextBlob"""

    def __init__(self, model: str = 'textblob'):
        """
        Initialize sentiment analyzer

        Args:
            model: Model to use for sentiment analysis
        """
        self.model = model

    def enrich(self, data: Dict[str, Any], fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Enrich data with sentiment analysis

        Args:
            data: Input data
            fields: Specific fields to analyze

        Returns:
            Enriched data with sentiment
        """
        # Extract text from data
        text = self._extract_text(data, fields)

        if not text:
            return {
                'sentiment': None,
                'timestamp': datetime.utcnow().isoformat()
            }

        # Analyze sentiment
        sentiment = self.analyze(text)

        return sentiment

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text

        Args:
            text: Input text

        Returns:
            Sentiment analysis results
        """
        try:
            from textblob import TextBlob

            blob = TextBlob(text)

            # Get polarity and subjectivity
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity

            # Determine sentiment category
            if polarity > 0.1:
                category = 'positive'
            elif polarity < -0.1:
                category = 'negative'
            else:
                category = 'neutral'

            return {
                'polarity': round(polarity, 3),
                'subjectivity': round(subjectivity, 3),
                'category': category,
                'model': self.model,
                'timestamp': datetime.utcnow().isoformat()
            }

        except ImportError:
            # TextBlob not installed, use simple fallback
            return self._analyze_simple(text)

    def _analyze_simple(self, text: str) -> Dict[str, Any]:
        """
        Simple sentiment analysis using keyword matching

        Args:
            text: Input text

        Returns:
            Sentiment results
        """
        # Simple positive and negative word lists
        positive_words = {
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'love', 'like', 'best', 'happy', 'glad', 'pleased', 'perfect',
            'beautiful', 'awesome', 'brilliant', 'superb', 'outstanding'
        }

        negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'poor', 'worst', 'hate',
            'dislike', 'disappointing', 'sad', 'angry', 'upset', 'ugly',
            'disgusting', 'pathetic', 'useless', 'waste', 'fail'
        }

        # Tokenize text
        words = text.lower().split()

        # Count positive and negative words
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)

        # Calculate polarity
        total = positive_count + negative_count
        if total > 0:
            polarity = (positive_count - negative_count) / total
        else:
            polarity = 0.0

        # Determine category
        if polarity > 0.1:
            category = 'positive'
        elif polarity < -0.1:
            category = 'negative'
        else:
            category = 'neutral'

        return {
            'polarity': round(polarity, 3),
            'subjectivity': 0.5,  # Default value
            'category': category,
            'positive_word_count': positive_count,
            'negative_word_count': negative_count,
            'model': 'simple',
            'timestamp': datetime.utcnow().isoformat()
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

    def analyze_sentences(self, text: str) -> List[Dict[str, Any]]:
        """
        Analyze sentiment of individual sentences

        Args:
            text: Input text

        Returns:
            List of sentence sentiment analyses
        """
        try:
            from textblob import TextBlob
            import re

            # Split into sentences
            sentences = re.split(r'[.!?]+', text)
            results = []

            for sentence in sentences:
                sentence = sentence.strip()
                if sentence:
                    blob = TextBlob(sentence)
                    results.append({
                        'sentence': sentence,
                        'polarity': round(blob.sentiment.polarity, 3),
                        'subjectivity': round(blob.sentiment.subjectivity, 3)
                    })

            return results

        except ImportError:
            return [{'error': 'TextBlob not installed'}]

    def get_emotion_scores(self, text: str) -> Dict[str, float]:
        """
        Get emotion scores for text (simple implementation)

        Args:
            text: Input text

        Returns:
            Dictionary of emotion scores
        """
        # Simple emotion keyword mapping
        emotions = {
            'joy': ['happy', 'joy', 'glad', 'delighted', 'cheerful', 'pleased'],
            'sadness': ['sad', 'unhappy', 'depressed', 'sorrowful', 'miserable'],
            'anger': ['angry', 'mad', 'furious', 'outraged', 'irritated'],
            'fear': ['afraid', 'scared', 'fearful', 'terrified', 'worried'],
            'surprise': ['surprised', 'amazed', 'astonished', 'shocked'],
            'disgust': ['disgusted', 'revolted', 'repulsed', 'nauseated']
        }

        words = text.lower().split()
        scores = {}

        for emotion, keywords in emotions.items():
            count = sum(1 for word in words if word in keywords)
            scores[emotion] = count / len(words) if words else 0.0

        return scores
