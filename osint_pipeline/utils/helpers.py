"""
Helper utilities for data processing
"""
import re
from typing import Any, Dict, List, Optional
from datetime import datetime
import hashlib


def normalize_data(data: Any) -> Any:
    """
    Normalize data for consistent processing

    Args:
        data: Input data to normalize

    Returns:
        Normalized data
    """
    if isinstance(data, str):
        return data.strip().lower()
    elif isinstance(data, dict):
        return {k: normalize_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [normalize_data(item) for item in data]
    return data


def sanitize_text(text: str, remove_html: bool = True, remove_urls: bool = False) -> str:
    """
    Sanitize text by removing unwanted characters and patterns

    Args:
        text: Input text to sanitize
        remove_html: Whether to remove HTML tags
        remove_urls: Whether to remove URLs

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Remove HTML tags
    if remove_html:
        text = re.sub(r'<[^>]+>', '', text)

    # Remove URLs
    if remove_urls:
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def extract_urls(text: str) -> List[str]:
    """
    Extract all URLs from text

    Args:
        text: Input text containing URLs

    Returns:
        List of extracted URLs
    """
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(url_pattern, text)


def extract_emails(text: str) -> List[str]:
    """
    Extract email addresses from text

    Args:
        text: Input text containing emails

    Returns:
        List of extracted email addresses
    """
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, text)


def extract_phone_numbers(text: str) -> List[str]:
    """
    Extract phone numbers from text

    Args:
        text: Input text containing phone numbers

    Returns:
        List of extracted phone numbers
    """
    phone_pattern = r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b'
    matches = re.findall(phone_pattern, text)
    return ['-'.join(match) for match in matches]


def calculate_hash(data: str, algorithm: str = 'sha256') -> str:
    """
    Calculate hash of data

    Args:
        data: Input data to hash
        algorithm: Hash algorithm to use (md5, sha1, sha256)

    Returns:
        Hex digest of hash
    """
    if algorithm == 'md5':
        return hashlib.md5(data.encode()).hexdigest()
    elif algorithm == 'sha1':
        return hashlib.sha1(data.encode()).hexdigest()
    else:
        return hashlib.sha256(data.encode()).hexdigest()


def timestamp_now() -> str:
    """
    Get current timestamp in ISO format

    Returns:
        ISO formatted timestamp
    """
    return datetime.utcnow().isoformat()


def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """
    Parse timestamp string to datetime object

    Args:
        timestamp_str: Timestamp string

    Returns:
        Datetime object or None if parsing fails
    """
    try:
        return datetime.fromisoformat(timestamp_str)
    except (ValueError, TypeError):
        return None
