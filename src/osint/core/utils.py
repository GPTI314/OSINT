"""
Utility functions for OSINT toolkit
"""

import re
import socket
import validators
from typing import Optional, List, Dict, Any
from datetime import datetime
import hashlib
import ipaddress


def is_valid_domain(domain: str) -> bool:
    """
    Check if a string is a valid domain

    Args:
        domain: Domain to validate

    Returns:
        True if valid domain, False otherwise
    """
    return validators.domain(domain) is True


def is_valid_ip(ip: str) -> bool:
    """
    Check if a string is a valid IP address

    Args:
        ip: IP address to validate

    Returns:
        True if valid IP, False otherwise
    """
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def is_valid_email(email: str) -> bool:
    """
    Check if a string is a valid email address

    Args:
        email: Email to validate

    Returns:
        True if valid email, False otherwise
    """
    return validators.email(email) is True


def is_valid_url(url: str) -> bool:
    """
    Check if a string is a valid URL

    Args:
        url: URL to validate

    Returns:
        True if valid URL, False otherwise
    """
    return validators.url(url) is True


def extract_domain_from_url(url: str) -> Optional[str]:
    """
    Extract domain from URL

    Args:
        url: URL to extract domain from

    Returns:
        Domain name or None
    """
    import tldextract

    extracted = tldextract.extract(url)
    if extracted.domain and extracted.suffix:
        return f"{extracted.domain}.{extracted.suffix}"
    return None


def resolve_domain(domain: str) -> List[str]:
    """
    Resolve domain to IP addresses

    Args:
        domain: Domain to resolve

    Returns:
        List of IP addresses
    """
    try:
        return [ip[4][0] for ip in socket.getaddrinfo(domain, None)]
    except socket.gaierror:
        return []


def reverse_dns(ip: str) -> Optional[str]:
    """
    Perform reverse DNS lookup

    Args:
        ip: IP address

    Returns:
        Hostname or None
    """
    try:
        return socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.gaierror):
        return None


def calculate_hash(data: str, algorithm: str = 'sha256') -> str:
    """
    Calculate hash of data

    Args:
        data: Data to hash
        algorithm: Hash algorithm (md5, sha1, sha256, etc.)

    Returns:
        Hash digest
    """
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(data.encode('utf-8'))
    return hash_obj.hexdigest()


def sanitize_input(input_str: str) -> str:
    """
    Sanitize user input

    Args:
        input_str: Input string

    Returns:
        Sanitized string
    """
    # Remove potentially dangerous characters
    return re.sub(r'[^\w\s\-\.\@\:]', '', input_str)


def parse_phone_number(phone: str) -> Dict[str, Any]:
    """
    Parse phone number

    Args:
        phone: Phone number

    Returns:
        Parsed phone number information
    """
    import phonenumbers

    try:
        parsed = phonenumbers.parse(phone, None)
        return {
            'valid': phonenumbers.is_valid_number(parsed),
            'country_code': parsed.country_code,
            'national_number': parsed.national_number,
            'e164': phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164),
            'international': phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            'national': phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL),
        }
    except phonenumbers.NumberParseException:
        return {'valid': False, 'error': 'Invalid phone number'}


def rate_limit(calls: int, period: int):
    """
    Decorator for rate limiting

    Args:
        calls: Number of calls allowed
        period: Time period in seconds
    """
    import time
    from functools import wraps

    def decorator(func):
        last_reset = [0.0]
        num_calls = [0]

        @wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            if current_time - last_reset[0] >= period:
                num_calls[0] = 0
                last_reset[0] = current_time

            if num_calls[0] >= calls:
                sleep_time = period - (current_time - last_reset[0])
                time.sleep(sleep_time)
                num_calls[0] = 0
                last_reset[0] = time.time()

            num_calls[0] += 1
            return func(*args, **kwargs)

        return wrapper
    return decorator


def format_timestamp(timestamp: Optional[datetime] = None) -> str:
    """
    Format timestamp to ISO format

    Args:
        timestamp: Datetime object or None for current time

    Returns:
        ISO formatted timestamp
    """
    if timestamp is None:
        timestamp = datetime.utcnow()
    return timestamp.isoformat()
