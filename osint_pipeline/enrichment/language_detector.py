"""
Language detection for text content
"""
from typing import Any, Dict, List, Optional
from datetime import datetime


class LanguageDetector:
    """Detect language of text content"""

    def __init__(self):
        """Initialize language detector"""
        pass

    def enrich(self, data: Dict[str, Any], fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Enrich data with language detection

        Args:
            data: Input data
            fields: Specific fields to analyze

        Returns:
            Enriched data with language information
        """
        # Extract text from data
        text = self._extract_text(data, fields)

        if not text:
            return {
                'language': None,
                'timestamp': datetime.utcnow().isoformat()
            }

        # Detect language
        result = self.detect(text)

        return result

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze text for language

        Args:
            text: Input text

        Returns:
            Language detection results
        """
        return self.detect(text)

    def detect(self, text: str) -> Dict[str, Any]:
        """
        Detect language of text

        Args:
            text: Input text

        Returns:
            Detection results with language code and confidence
        """
        try:
            from langdetect import detect, detect_langs

            # Detect language
            language = detect(text)

            # Get probabilities for all detected languages
            languages = detect_langs(text)

            results = []
            for lang in languages:
                results.append({
                    'language': lang.lang,
                    'probability': round(lang.prob, 3)
                })

            return {
                'language': language,
                'languages': results,
                'timestamp': datetime.utcnow().isoformat()
            }

        except ImportError:
            # langdetect not installed, use simple fallback
            return self._detect_simple(text)
        except Exception as e:
            return {
                'language': None,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def _detect_simple(self, text: str) -> Dict[str, Any]:
        """
        Simple language detection based on character sets

        Args:
            text: Input text

        Returns:
            Detection results
        """
        # Very basic detection based on character ranges
        char_counts = {
            'latin': 0,
            'cyrillic': 0,
            'arabic': 0,
            'chinese': 0,
            'japanese': 0,
            'korean': 0
        }

        for char in text:
            code = ord(char)

            # Latin characters (basic)
            if (0x0041 <= code <= 0x005A) or (0x0061 <= code <= 0x007A):
                char_counts['latin'] += 1

            # Cyrillic
            elif 0x0400 <= code <= 0x04FF:
                char_counts['cyrillic'] += 1

            # Arabic
            elif 0x0600 <= code <= 0x06FF:
                char_counts['arabic'] += 1

            # Chinese (CJK Unified Ideographs)
            elif 0x4E00 <= code <= 0x9FFF:
                char_counts['chinese'] += 1

            # Japanese Hiragana/Katakana
            elif (0x3040 <= code <= 0x309F) or (0x30A0 <= code <= 0x30FF):
                char_counts['japanese'] += 1

            # Korean Hangul
            elif 0xAC00 <= code <= 0xD7AF:
                char_counts['korean'] += 1

        # Determine most likely language
        max_script = max(char_counts, key=char_counts.get)

        # Map script to language code
        script_to_lang = {
            'latin': 'en',
            'cyrillic': 'ru',
            'arabic': 'ar',
            'chinese': 'zh',
            'japanese': 'ja',
            'korean': 'ko'
        }

        language = script_to_lang.get(max_script, 'unknown')

        return {
            'language': language,
            'script': max_script,
            'method': 'simple',
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

    def detect_multiple(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Detect language for multiple texts

        Args:
            texts: List of text strings

        Returns:
            List of detection results
        """
        return [self.detect(text) for text in texts]

    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported language codes

        Returns:
            List of ISO 639-1 language codes
        """
        # Common ISO 639-1 language codes
        return [
            'en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko',
            'ar', 'hi', 'tr', 'nl', 'pl', 'sv', 'da', 'fi', 'no', 'cs',
            'el', 'he', 'id', 'ms', 'th', 'vi', 'uk', 'ro', 'hu', 'bg'
        ]

    def is_language(self, text: str, expected_language: str, threshold: float = 0.7) -> bool:
        """
        Check if text is in expected language

        Args:
            text: Input text
            expected_language: Expected language code
            threshold: Minimum confidence threshold

        Returns:
            True if text matches expected language
        """
        result = self.detect(text)

        if result.get('language') == expected_language:
            # Check confidence if available
            if 'languages' in result:
                for lang in result['languages']:
                    if lang['language'] == expected_language:
                        return lang['probability'] >= threshold

            return True

        return False
