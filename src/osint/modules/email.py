"""
Email Intelligence Module

Provides comprehensive email intelligence gathering including:
- Breach data checking
- Social profile discovery
- Domain analysis
- Email verification
- Password leak checking
"""

import requests
import hashlib
import smtplib
import dns.resolver
from email_validator import validate_email, EmailNotValidError
from typing import Dict, Any, List, Optional
import re

from ..core.base import BaseModule
from ..core.utils import is_valid_email, is_valid_domain


class EmailIntelligence(BaseModule):
    """Email Intelligence gathering module"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.hibp_api_key = self.config.get('hibp_api_key')
        self.hunter_api_key = self.config.get('hunter_api_key')
        self.dehashed_api_key = self.config.get('dehashed_api_key')
        self.dehashed_username = self.config.get('dehashed_username')

    def collect(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Collect comprehensive email intelligence

        Args:
            target: Email address to investigate
            **kwargs: Additional options
                - include_breaches: Include breach data (default: True)
                - include_social: Include social profiles (default: True)
                - include_domain: Include domain analysis (default: True)
                - include_verification: Include email verification (default: True)
                - include_passwords: Include password leaks (default: False)

        Returns:
            Dictionary with comprehensive email intelligence
        """
        if not is_valid_email(target):
            return self._create_result(
                target=target,
                data={},
                success=False,
                error="Invalid email address"
            )

        try:
            data = {}

            if kwargs.get('include_breaches', True):
                data['breaches'] = self.check_breaches(target)

            if kwargs.get('include_social', True):
                data['social_profiles'] = self.discover_social_profiles(target)

            if kwargs.get('include_domain', True):
                domain = target.split('@')[1]
                data['domain_analysis'] = self.analyze_domain(domain)

            if kwargs.get('include_verification', True):
                data['verification'] = self.verify_email(target)

            if kwargs.get('include_passwords', False):
                data['password_leaks'] = self.check_password_leaks(target)

            return self._create_result(target=target, data=data)

        except Exception as e:
            return self._handle_error(target, e)

    def check_breaches(self, email: str) -> Dict[str, Any]:
        """
        Check if email appears in data breaches

        Args:
            email: Email address

        Returns:
            Breach data
        """
        breaches = {}

        # Have I Been Pwned
        if self.hibp_api_key:
            try:
                headers = {
                    'hibp-api-key': self.hibp_api_key,
                    'User-Agent': 'OSINT-Toolkit'
                }
                url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
                response = requests.get(url, headers=headers, timeout=10)

                if response.status_code == 200:
                    breach_data = response.json()
                    breaches['hibp'] = {
                        'found': True,
                        'breach_count': len(breach_data),
                        'breaches': [
                            {
                                'name': breach.get('Name'),
                                'title': breach.get('Title'),
                                'domain': breach.get('Domain'),
                                'breach_date': breach.get('BreachDate'),
                                'added_date': breach.get('AddedDate'),
                                'modified_date': breach.get('ModifiedDate'),
                                'pwn_count': breach.get('PwnCount'),
                                'description': breach.get('Description'),
                                'data_classes': breach.get('DataClasses', []),
                                'is_verified': breach.get('IsVerified'),
                                'is_sensitive': breach.get('IsSensitive')
                            }
                            for breach in breach_data
                        ]
                    }
                elif response.status_code == 404:
                    breaches['hibp'] = {
                        'found': False,
                        'breach_count': 0,
                        'breaches': []
                    }
                else:
                    breaches['hibp'] = {'error': f"Status code: {response.status_code}"}

            except Exception as e:
                self.logger.warning(f"HIBP lookup failed: {str(e)}")
                breaches['hibp'] = {'error': str(e)}

        # DeHashed
        if self.dehashed_api_key and self.dehashed_username:
            try:
                auth = (self.dehashed_username, self.dehashed_api_key)
                params = {'query': f'email:{email}'}
                url = "https://api.dehashed.com/search"
                response = requests.get(url, auth=auth, params=params, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    breaches['dehashed'] = {
                        'found': data.get('total', 0) > 0,
                        'total': data.get('total', 0),
                        'entries': data.get('entries', [])[:10]  # First 10 entries
                    }
            except Exception as e:
                self.logger.warning(f"DeHashed lookup failed: {str(e)}")
                breaches['dehashed'] = {'error': str(e)}

        return breaches

    def discover_social_profiles(self, email: str) -> Dict[str, Any]:
        """
        Discover social media profiles associated with email

        Args:
            email: Email address

        Returns:
            Social profile discovery results
        """
        profiles = {}

        # Hunter.io Email Finder
        if self.hunter_api_key:
            try:
                domain = email.split('@')[1]
                params = {
                    'domain': domain,
                    'api_key': self.hunter_api_key
                }
                url = "https://api.hunter.io/v2/domain-search"
                response = requests.get(url, params=params, timeout=10)

                if response.status_code == 200:
                    data = response.json().get('data', {})
                    emails = data.get('emails', [])

                    # Find matching email
                    for email_data in emails:
                        if email_data.get('value') == email:
                            profiles['hunter'] = {
                                'found': True,
                                'first_name': email_data.get('first_name'),
                                'last_name': email_data.get('last_name'),
                                'position': email_data.get('position'),
                                'department': email_data.get('department'),
                                'linkedin': email_data.get('linkedin'),
                                'twitter': email_data.get('twitter'),
                                'phone_number': email_data.get('phone_number'),
                                'confidence': email_data.get('confidence')
                            }
                            break
                    else:
                        profiles['hunter'] = {'found': False}

            except Exception as e:
                self.logger.warning(f"Hunter.io lookup failed: {str(e)}")
                profiles['hunter'] = {'error': str(e)}

        # Manual social media URL pattern checking
        username = email.split('@')[0]
        profiles['potential_usernames'] = [username]

        # Add variations
        if '.' in username:
            profiles['potential_usernames'].extend(username.split('.'))
        if '_' in username:
            profiles['potential_usernames'].extend(username.split('_'))

        # Common social media platforms
        profiles['social_urls'] = {
            'twitter': f"https://twitter.com/{username}",
            'linkedin': f"https://linkedin.com/in/{username}",
            'github': f"https://github.com/{username}",
            'instagram': f"https://instagram.com/{username}",
            'facebook': f"https://facebook.com/{username}",
            'reddit': f"https://reddit.com/user/{username}"
        }

        return profiles

    def analyze_domain(self, domain: str) -> Dict[str, Any]:
        """
        Analyze email domain

        Args:
            domain: Email domain

        Returns:
            Domain analysis results
        """
        analysis = {}

        # Check if disposable email
        analysis['is_disposable'] = self._is_disposable_email(domain)

        # Check if free email provider
        free_providers = [
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com',
            'icloud.com', 'mail.com', 'protonmail.com', 'zoho.com', 'yandex.com'
        ]
        analysis['is_free_provider'] = domain.lower() in free_providers

        # Get MX records
        try:
            answers = dns.resolver.resolve(domain, 'MX')
            analysis['mx_records'] = [
                {
                    'priority': rdata.preference,
                    'host': str(rdata.exchange)
                }
                for rdata in answers
            ]
            analysis['has_mx_records'] = True
        except:
            analysis['mx_records'] = []
            analysis['has_mx_records'] = False

        # Check SPF record
        try:
            answers = dns.resolver.resolve(domain, 'TXT')
            spf_records = [str(rdata) for rdata in answers if 'v=spf1' in str(rdata).lower()]
            analysis['spf_record'] = spf_records[0] if spf_records else None
            analysis['has_spf'] = len(spf_records) > 0
        except:
            analysis['spf_record'] = None
            analysis['has_spf'] = False

        # Check DMARC record
        try:
            dmarc_domain = f"_dmarc.{domain}"
            answers = dns.resolver.resolve(dmarc_domain, 'TXT')
            dmarc_records = [str(rdata) for rdata in answers]
            analysis['dmarc_record'] = dmarc_records[0] if dmarc_records else None
            analysis['has_dmarc'] = len(dmarc_records) > 0
        except:
            analysis['dmarc_record'] = None
            analysis['has_dmarc'] = False

        return analysis

    def verify_email(self, email: str) -> Dict[str, Any]:
        """
        Verify email address validity and deliverability

        Args:
            email: Email address

        Returns:
            Verification results
        """
        verification = {}

        # Syntax validation
        try:
            valid = validate_email(email, check_deliverability=False)
            verification['syntax_valid'] = True
            verification['normalized_email'] = valid.normalized
            verification['local_part'] = valid.local_part
            verification['domain'] = valid.domain
            verification['ascii_email'] = valid.ascii_email
        except EmailNotValidError as e:
            verification['syntax_valid'] = False
            verification['error'] = str(e)
            return verification

        # Domain validation
        domain = email.split('@')[1]
        verification['domain_exists'] = is_valid_domain(domain)

        # MX record check
        try:
            answers = dns.resolver.resolve(domain, 'MX')
            verification['mx_exists'] = len(answers) > 0
            verification['mx_servers'] = [str(rdata.exchange) for rdata in answers]
        except:
            verification['mx_exists'] = False
            verification['mx_servers'] = []

        # SMTP verification (basic check without actually sending)
        verification['smtp_check'] = self._smtp_verify(email)

        # Catch-all detection
        verification['is_catch_all'] = self._is_catch_all(domain)

        # Role-based email detection
        role_keywords = ['admin', 'info', 'support', 'sales', 'contact', 'noreply', 'no-reply']
        local_part = email.split('@')[0].lower()
        verification['is_role_based'] = any(keyword in local_part for keyword in role_keywords)

        return verification

    def check_password_leaks(self, email: str) -> Dict[str, Any]:
        """
        Check for password leaks associated with email

        Args:
            email: Email address

        Returns:
            Password leak information
        """
        leaks = {}

        # Have I Been Pwned Passwords
        if self.hibp_api_key:
            try:
                headers = {
                    'hibp-api-key': self.hibp_api_key,
                    'User-Agent': 'OSINT-Toolkit'
                }
                url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}?truncateResponse=false"
                response = requests.get(url, headers=headers, timeout=10)

                if response.status_code == 200:
                    breach_data = response.json()
                    passwords_exposed = []

                    for breach in breach_data:
                        data_classes = breach.get('DataClasses', [])
                        if 'Passwords' in data_classes:
                            passwords_exposed.append({
                                'breach': breach.get('Name'),
                                'date': breach.get('BreachDate'),
                                'data_classes': data_classes
                            })

                    leaks['hibp'] = {
                        'passwords_found': len(passwords_exposed) > 0,
                        'breach_count': len(passwords_exposed),
                        'breaches': passwords_exposed
                    }
                elif response.status_code == 404:
                    leaks['hibp'] = {
                        'passwords_found': False,
                        'breach_count': 0,
                        'breaches': []
                    }

            except Exception as e:
                self.logger.warning(f"HIBP password check failed: {str(e)}")
                leaks['hibp'] = {'error': str(e)}

        return leaks

    def _is_disposable_email(self, domain: str) -> bool:
        """
        Check if email domain is disposable

        Args:
            domain: Email domain

        Returns:
            True if disposable, False otherwise
        """
        # Common disposable email domains
        disposable_domains = [
            '10minutemail.com', 'guerrillamail.com', 'mailinator.com', 'temp-mail.org',
            'throwaway.email', 'tempmail.com', 'fakeinbox.com', 'trashmail.com'
        ]

        return domain.lower() in disposable_domains

    def _smtp_verify(self, email: str) -> Dict[str, Any]:
        """
        Perform SMTP verification

        Args:
            email: Email address

        Returns:
            SMTP verification results
        """
        domain = email.split('@')[1]

        try:
            # Get MX record
            answers = dns.resolver.resolve(domain, 'MX')
            mx_record = str(answers[0].exchange)

            # Connect to SMTP server
            server = smtplib.SMTP(timeout=10)
            server.set_debuglevel(0)
            server.connect(mx_record)
            server.helo()
            server.mail('verify@example.com')
            code, message = server.rcpt(email)
            server.quit()

            return {
                'verified': code == 250,
                'code': code,
                'message': message.decode() if isinstance(message, bytes) else str(message)
            }

        except Exception as e:
            return {
                'verified': False,
                'error': str(e)
            }

    def _is_catch_all(self, domain: str) -> bool:
        """
        Check if domain has catch-all email configured

        Args:
            domain: Email domain

        Returns:
            True if catch-all, False otherwise
        """
        try:
            # Test with a random email that likely doesn't exist
            test_email = f"random_nonexistent_{hashlib.md5(domain.encode()).hexdigest()[:8]}@{domain}"

            answers = dns.resolver.resolve(domain, 'MX')
            mx_record = str(answers[0].exchange)

            server = smtplib.SMTP(timeout=10)
            server.set_debuglevel(0)
            server.connect(mx_record)
            server.helo()
            server.mail('verify@example.com')
            code, message = server.rcpt(test_email)
            server.quit()

            # If random email is accepted, it's likely a catch-all
            return code == 250

        except:
            return False
