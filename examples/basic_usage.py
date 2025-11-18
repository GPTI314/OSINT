"""
Basic Usage Examples for OSINT Toolkit
"""

from osint import (
    DomainIntelligence,
    IPIntelligence,
    EmailIntelligence,
    PhoneIntelligence,
    SocialMediaIntelligence,
    ImageIntelligence
)
from osint.core import Config
import json


def example_domain_intelligence():
    """Example: Domain Intelligence Gathering"""
    print("\n=== Domain Intelligence Example ===")

    config = Config()
    domain_intel = DomainIntelligence(config.get_all())

    # Collect comprehensive domain intelligence
    result = domain_intel.collect('example.com')

    print(json.dumps(result, indent=2))

    # Collect specific data only
    result = domain_intel.collect(
        'example.com',
        include_whois=True,
        include_dns=True,
        include_subdomains=False,  # Skip subdomain enumeration
        include_ssl=True,
        include_technology=False,
        include_historical=False,
        include_threat_intel=False
    )

    print(f"WHOIS Data: {result['data'].get('whois', {})}")
    print(f"DNS Records: {result['data'].get('dns', {})}")


def example_ip_intelligence():
    """Example: IP Intelligence Gathering"""
    print("\n=== IP Intelligence Example ===")

    config = Config()
    ip_intel = IPIntelligence(config.get_all())

    # Basic IP intelligence
    result = ip_intel.collect('8.8.8.8')

    print(json.dumps(result, indent=2))

    # Include port scanning (use with caution)
    result = ip_intel.collect(
        '8.8.8.8',
        include_ports=True,
        port_range='80,443,8080'
    )

    print(f"Open Ports: {result['data'].get('ports', {})}")


def example_email_intelligence():
    """Example: Email Intelligence Gathering"""
    print("\n=== Email Intelligence Example ===")

    config = Config()
    email_intel = EmailIntelligence(config.get_all())

    # Collect email intelligence
    result = email_intel.collect('test@example.com')

    print(json.dumps(result, indent=2))

    # Check for breaches and verification only
    result = email_intel.collect(
        'test@example.com',
        include_breaches=True,
        include_verification=True,
        include_social=False,
        include_passwords=False
    )

    print(f"Breach Data: {result['data'].get('breaches', {})}")
    print(f"Verification: {result['data'].get('verification', {})}")


def example_phone_intelligence():
    """Example: Phone Intelligence Gathering"""
    print("\n=== Phone Intelligence Example ===")

    config = Config()
    phone_intel = PhoneIntelligence(config.get_all())

    # Collect phone intelligence
    result = phone_intel.collect('+1234567890')

    print(json.dumps(result, indent=2))

    print(f"Carrier: {result['data'].get('carrier', {})}")
    print(f"Geolocation: {result['data'].get('geolocation', {})}")
    print(f"Line Type: {result['data'].get('line_type', {})}")


def example_social_media_intelligence():
    """Example: Social Media Intelligence Gathering"""
    print("\n=== Social Media Intelligence Example ===")

    config = Config()
    social_intel = SocialMediaIntelligence(config.get_all())

    # Collect from specific platform
    result = social_intel.collect(
        'username',
        platforms=['twitter'],
        include_posts=True,
        include_connections=True,
        max_posts=50
    )

    print(json.dumps(result, indent=2))

    # Discover profiles across all platforms
    result = social_intel.discover_profiles('username', 'username')

    print(f"Discovered Profiles: {result}")


def example_image_intelligence():
    """Example: Image Intelligence Gathering"""
    print("\n=== Image Intelligence Example ===")

    config = Config()
    image_intel = ImageIntelligence(config.get_all())

    # Analyze local image
    result = image_intel.collect(
        '/path/to/image.jpg',
        include_metadata=True,
        include_ocr=True,
        include_face_detection=True
    )

    print(json.dumps(result, indent=2))

    # Analyze image from URL
    result = image_intel.collect(
        'https://example.com/image.jpg',
        include_reverse_search=True,
        include_metadata=True
    )

    print(f"Metadata: {result['data'].get('metadata', {})}")
    print(f"Reverse Search: {result['data'].get('reverse_search', {})}")


def example_combined_investigation():
    """Example: Combined Investigation"""
    print("\n=== Combined Investigation Example ===")

    config = Config()

    # Investigate a domain comprehensively
    domain = 'example.com'

    # 1. Domain intelligence
    domain_intel = DomainIntelligence(config.get_all())
    domain_result = domain_intel.collect(domain)

    # 2. Get IPs from domain
    dns_records = domain_result['data'].get('dns', {})
    ips = dns_records.get('A', [])

    # 3. Investigate each IP
    ip_intel = IPIntelligence(config.get_all())
    ip_results = []
    for ip in ips[:3]:  # Limit to first 3 IPs
        ip_result = ip_intel.collect(ip)
        ip_results.append(ip_result)

    # 4. Check emails associated with domain
    email_intel = EmailIntelligence(config.get_all())
    whois_data = domain_result['data'].get('whois', {})
    emails = whois_data.get('emails', [])

    email_results = []
    for email in emails[:3]:  # Limit to first 3 emails
        email_result = email_intel.collect(email)
        email_results.append(email_result)

    # Compile comprehensive report
    investigation_report = {
        'target': domain,
        'domain_intelligence': domain_result,
        'ip_intelligence': ip_results,
        'email_intelligence': email_results
    }

    print(json.dumps(investigation_report, indent=2))


if __name__ == '__main__':
    # Run examples
    print("OSINT Toolkit - Usage Examples")
    print("=" * 50)

    # Note: Uncomment the examples you want to run
    # example_domain_intelligence()
    # example_ip_intelligence()
    # example_email_intelligence()
    # example_phone_intelligence()
    # example_social_media_intelligence()
    # example_image_intelligence()
    # example_combined_investigation()

    print("\nNote: Configure API keys in .env file for full functionality")
    print("See .env.example for required API keys")
