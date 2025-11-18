"""
Command Line Interface for OSINT Toolkit
"""

import argparse
import json
import sys
from typing import Optional

from .core.config import Config
from .modules.domain import DomainIntelligence
from .modules.ip import IPIntelligence
from .modules.email import EmailIntelligence
from .modules.phone import PhoneIntelligence
from .modules.social import SocialMediaIntelligence
from .modules.image import ImageIntelligence


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='OSINT Toolkit - Open Source Intelligence Gathering',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  osint domain example.com
  osint ip 8.8.8.8 --include-ports
  osint email user@example.com
  osint phone +1234567890
  osint social twitter username
  osint image /path/to/image.jpg --include-ocr

For more information, visit: https://github.com/yourusername/OSINT
        """
    )

    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--output', '-o', help='Output file for results (JSON)')
    parser.add_argument('--pretty', action='store_true', help='Pretty print JSON output')

    subparsers = parser.add_subparsers(dest='module', help='Intelligence module to use')

    # Domain Intelligence
    domain_parser = subparsers.add_parser('domain', help='Domain intelligence gathering')
    domain_parser.add_argument('target', help='Domain name to investigate')
    domain_parser.add_argument('--no-whois', action='store_true', help='Exclude WHOIS data')
    domain_parser.add_argument('--no-dns', action='store_true', help='Exclude DNS records')
    domain_parser.add_argument('--no-subdomains', action='store_true', help='Exclude subdomain enumeration')
    domain_parser.add_argument('--no-ssl', action='store_true', help='Exclude SSL certificate data')
    domain_parser.add_argument('--no-technology', action='store_true', help='Exclude technology detection')
    domain_parser.add_argument('--no-historical', action='store_true', help='Exclude historical data')
    domain_parser.add_argument('--no-threat', action='store_true', help='Exclude threat intelligence')

    # IP Intelligence
    ip_parser = subparsers.add_parser('ip', help='IP address intelligence gathering')
    ip_parser.add_argument('target', help='IP address to investigate')
    ip_parser.add_argument('--include-ports', action='store_true', help='Include port scanning')
    ip_parser.add_argument('--include-services', action='store_true', help='Include service detection')
    ip_parser.add_argument('--port-range', default='1-1000', help='Port range to scan (default: 1-1000)')

    # Email Intelligence
    email_parser = subparsers.add_parser('email', help='Email intelligence gathering')
    email_parser.add_argument('target', help='Email address to investigate')
    email_parser.add_argument('--include-passwords', action='store_true', help='Include password leak checking')
    email_parser.add_argument('--no-breaches', action='store_true', help='Exclude breach data')
    email_parser.add_argument('--no-social', action='store_true', help='Exclude social profiles')

    # Phone Intelligence
    phone_parser = subparsers.add_parser('phone', help='Phone number intelligence gathering')
    phone_parser.add_argument('target', help='Phone number to investigate')

    # Social Media Intelligence
    social_parser = subparsers.add_parser('social', help='Social media intelligence gathering')
    social_parser.add_argument('platform', choices=['twitter', 'reddit', 'linkedin', 'instagram', 'facebook', 'tiktok', 'all'],
                               help='Social media platform')
    social_parser.add_argument('username', help='Username to investigate')
    social_parser.add_argument('--max-posts', type=int, default=100, help='Maximum posts to collect (default: 100)')
    social_parser.add_argument('--no-posts', action='store_true', help='Exclude post collection')
    social_parser.add_argument('--no-connections', action='store_true', help='Exclude connection analysis')
    social_parser.add_argument('--no-activity', action='store_true', help='Exclude activity tracking')

    # Image Intelligence
    image_parser = subparsers.add_parser('image', help='Image intelligence gathering')
    image_parser.add_argument('target', help='Image path or URL')
    image_parser.add_argument('--include-objects', action='store_true', help='Include object detection')
    image_parser.add_argument('--include-forensics', action='store_true', help='Include forensics analysis')
    image_parser.add_argument('--no-reverse', action='store_true', help='Exclude reverse image search')
    image_parser.add_argument('--no-metadata', action='store_true', help='Exclude metadata extraction')
    image_parser.add_argument('--no-ocr', action='store_true', help='Exclude OCR text extraction')
    image_parser.add_argument('--no-faces', action='store_true', help='Exclude face detection')

    args = parser.parse_args()

    if not args.module:
        parser.print_help()
        sys.exit(1)

    # Load configuration
    config = Config(args.config) if args.config else Config()

    # Execute module
    try:
        result = execute_module(args, config)

        # Output results
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2 if args.pretty else None)
            print(f"Results saved to {args.output}")
        else:
            print(json.dumps(result, indent=2 if args.pretty else None))

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


def execute_module(args, config: Config) -> dict:
    """
    Execute the specified module

    Args:
        args: Command line arguments
        config: Configuration object

    Returns:
        Module execution results
    """
    if args.module == 'domain':
        module = DomainIntelligence(config.get_all())
        return module.collect(
            args.target,
            include_whois=not args.no_whois,
            include_dns=not args.no_dns,
            include_subdomains=not args.no_subdomains,
            include_ssl=not args.no_ssl,
            include_technology=not args.no_technology,
            include_historical=not args.no_historical,
            include_threat_intel=not args.no_threat
        )

    elif args.module == 'ip':
        module = IPIntelligence(config.get_all())
        return module.collect(
            args.target,
            include_ports=args.include_ports,
            include_services=args.include_services,
            port_range=args.port_range
        )

    elif args.module == 'email':
        module = EmailIntelligence(config.get_all())
        return module.collect(
            args.target,
            include_breaches=not args.no_breaches,
            include_social=not args.no_social,
            include_passwords=args.include_passwords
        )

    elif args.module == 'phone':
        module = PhoneIntelligence(config.get_all())
        return module.collect(args.target)

    elif args.module == 'social':
        module = SocialMediaIntelligence(config.get_all())
        platforms = ['twitter', 'reddit', 'linkedin', 'instagram', 'facebook', 'tiktok'] if args.platform == 'all' else [args.platform]
        return module.collect(
            args.username,
            platforms=platforms,
            include_posts=not args.no_posts,
            include_connections=not args.no_connections,
            include_activity=not args.no_activity,
            max_posts=args.max_posts
        )

    elif args.module == 'image':
        module = ImageIntelligence(config.get_all())
        return module.collect(
            args.target,
            include_reverse_search=not args.no_reverse,
            include_metadata=not args.no_metadata,
            include_ocr=not args.no_ocr,
            include_face_detection=not args.no_faces,
            include_object_detection=args.include_objects,
            include_forensics=args.include_forensics
        )

    else:
        raise ValueError(f"Unknown module: {args.module}")


if __name__ == '__main__':
    main()
