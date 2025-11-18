"""
Phone Intelligence Module

Provides comprehensive phone number intelligence gathering including:
- Carrier information
- Geolocation
- Line type detection
- Social profile discovery
- Phone number verification
"""

import requests
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
from typing import Dict, Any, List, Optional

from ..core.base import BaseModule
from ..core.utils import parse_phone_number


class PhoneIntelligence(BaseModule):
    """Phone Intelligence gathering module"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.numverify_api_key = self.config.get('numverify_api_key')
        self.twilio_account_sid = self.config.get('twilio_account_sid')
        self.twilio_auth_token = self.config.get('twilio_auth_token')

    def collect(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Collect comprehensive phone intelligence

        Args:
            target: Phone number to investigate
            **kwargs: Additional options
                - include_carrier: Include carrier information (default: True)
                - include_geolocation: Include geolocation (default: True)
                - include_line_type: Include line type detection (default: True)
                - include_social: Include social profile discovery (default: True)
                - include_verification: Include verification (default: True)

        Returns:
            Dictionary with comprehensive phone intelligence
        """
        try:
            # Parse phone number
            parsed = parse_phone_number(target)
            if not parsed.get('valid', False):
                return self._create_result(
                    target=target,
                    data={},
                    success=False,
                    error="Invalid phone number"
                )

            data = {
                'parsed': parsed
            }

            if kwargs.get('include_carrier', True):
                data['carrier'] = self.get_carrier_info(target)

            if kwargs.get('include_geolocation', True):
                data['geolocation'] = self.get_geolocation(target)

            if kwargs.get('include_line_type', True):
                data['line_type'] = self.get_line_type(target)

            if kwargs.get('include_social', True):
                data['social_profiles'] = self.discover_social_profiles(target)

            if kwargs.get('include_verification', True):
                data['verification'] = self.verify_phone(target)

            return self._create_result(target=target, data=data)

        except Exception as e:
            return self._handle_error(target, e)

    def get_carrier_info(self, phone: str) -> Dict[str, Any]:
        """
        Get carrier information for phone number

        Args:
            phone: Phone number

        Returns:
            Carrier information
        """
        carrier_info = {}

        # phonenumbers library
        try:
            parsed = phonenumbers.parse(phone, None)
            carrier_name = carrier.name_for_number(parsed, 'en')

            carrier_info['phonenumbers'] = {
                'carrier': carrier_name,
                'country_code': parsed.country_code,
                'national_number': parsed.national_number
            }

        except Exception as e:
            self.logger.warning(f"phonenumbers carrier lookup failed: {str(e)}")
            carrier_info['phonenumbers'] = {'error': str(e)}

        # NumVerify API
        if self.numverify_api_key:
            try:
                params = {
                    'access_key': self.numverify_api_key,
                    'number': phone,
                    'format': 1
                }
                url = "http://apilayer.net/api/validate"
                response = requests.get(url, params=params, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    if data.get('valid'):
                        carrier_info['numverify'] = {
                            'carrier': data.get('carrier'),
                            'line_type': data.get('line_type'),
                            'country_code': data.get('country_code'),
                            'country_name': data.get('country_name'),
                            'location': data.get('location')
                        }
                    else:
                        carrier_info['numverify'] = {'error': 'Invalid phone number'}

            except Exception as e:
                self.logger.warning(f"NumVerify lookup failed: {str(e)}")
                carrier_info['numverify'] = {'error': str(e)}

        # Twilio Lookup API
        if self.twilio_account_sid and self.twilio_auth_token:
            try:
                from twilio.rest import Client
                client = Client(self.twilio_account_sid, self.twilio_auth_token)

                phone_number = client.lookups.v2.phone_numbers(phone).fetch()

                carrier_info['twilio'] = {
                    'phone_number': phone_number.phone_number,
                    'country_code': phone_number.country_code,
                    'national_format': phone_number.national_format,
                    'valid': phone_number.valid
                }

            except Exception as e:
                self.logger.warning(f"Twilio lookup failed: {str(e)}")
                carrier_info['twilio'] = {'error': str(e)}

        return carrier_info

    def get_geolocation(self, phone: str) -> Dict[str, Any]:
        """
        Get geolocation for phone number

        Args:
            phone: Phone number

        Returns:
            Geolocation data
        """
        geolocation = {}

        try:
            parsed = phonenumbers.parse(phone, None)

            # Get country
            country = geocoder.country_name_for_number(parsed, 'en')

            # Get description (region/city)
            description = geocoder.description_for_number(parsed, 'en')

            # Get timezone
            timezones = timezone.time_zones_for_number(parsed)

            geolocation['phonenumbers'] = {
                'country': country,
                'region': description,
                'timezones': list(timezones),
                'country_code': parsed.country_code
            }

        except Exception as e:
            self.logger.warning(f"Geolocation lookup failed: {str(e)}")
            geolocation['phonenumbers'] = {'error': str(e)}

        return geolocation

    def get_line_type(self, phone: str) -> Dict[str, Any]:
        """
        Detect line type (mobile, landline, VoIP)

        Args:
            phone: Phone number

        Returns:
            Line type information
        """
        line_type = {}

        try:
            parsed = phonenumbers.parse(phone, None)
            number_type = phonenumbers.number_type(parsed)

            type_mapping = {
                phonenumbers.PhoneNumberType.FIXED_LINE: 'Landline',
                phonenumbers.PhoneNumberType.MOBILE: 'Mobile',
                phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: 'Fixed Line or Mobile',
                phonenumbers.PhoneNumberType.TOLL_FREE: 'Toll Free',
                phonenumbers.PhoneNumberType.PREMIUM_RATE: 'Premium Rate',
                phonenumbers.PhoneNumberType.SHARED_COST: 'Shared Cost',
                phonenumbers.PhoneNumberType.VOIP: 'VoIP',
                phonenumbers.PhoneNumberType.PERSONAL_NUMBER: 'Personal Number',
                phonenumbers.PhoneNumberType.PAGER: 'Pager',
                phonenumbers.PhoneNumberType.UAN: 'UAN',
                phonenumbers.PhoneNumberType.VOICEMAIL: 'Voicemail',
                phonenumbers.PhoneNumberType.UNKNOWN: 'Unknown'
            }

            line_type['type'] = type_mapping.get(number_type, 'Unknown')
            line_type['type_code'] = number_type
            line_type['is_mobile'] = number_type == phonenumbers.PhoneNumberType.MOBILE
            line_type['is_landline'] = number_type == phonenumbers.PhoneNumberType.FIXED_LINE
            line_type['is_voip'] = number_type == phonenumbers.PhoneNumberType.VOIP

        except Exception as e:
            self.logger.warning(f"Line type detection failed: {str(e)}")
            line_type['error'] = str(e)

        return line_type

    def discover_social_profiles(self, phone: str) -> Dict[str, Any]:
        """
        Discover social media profiles associated with phone number

        Args:
            phone: Phone number

        Returns:
            Social profile discovery results
        """
        profiles = {}

        # Format phone number for searching
        try:
            parsed = phonenumbers.parse(phone, None)
            e164_format = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            international_format = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            national_format = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)

            profiles['search_formats'] = {
                'e164': e164_format,
                'international': international_format,
                'national': national_format
            }

            # Social media search URLs
            profiles['search_urls'] = {
                'facebook': f"https://www.facebook.com/search/top/?q={e164_format}",
                'linkedin': f"https://www.linkedin.com/search/results/all/?keywords={e164_format}",
                'twitter': f"https://twitter.com/search?q={e164_format}",
                'instagram': f"https://www.instagram.com/explore/tags/{e164_format.replace('+', '')}/",
            }

            # Note: Actual profile discovery would require scraping or API access
            profiles['note'] = "Social profile discovery requires manual verification or API access to social platforms"

        except Exception as e:
            self.logger.warning(f"Social profile discovery failed: {str(e)}")
            profiles['error'] = str(e)

        return profiles

    def verify_phone(self, phone: str) -> Dict[str, Any]:
        """
        Verify phone number validity

        Args:
            phone: Phone number

        Returns:
            Verification results
        """
        verification = {}

        try:
            parsed = phonenumbers.parse(phone, None)

            verification['is_valid'] = phonenumbers.is_valid_number(parsed)
            verification['is_possible'] = phonenumbers.is_possible_number(parsed)
            verification['formatted'] = {
                'e164': phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164),
                'international': phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
                'national': phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL),
                'rfc3966': phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.RFC3966)
            }

            # Additional validation
            verification['country_code'] = parsed.country_code
            verification['national_number'] = parsed.national_number

            # Check if number could be valid in specific region
            region_code = phonenumbers.region_code_for_number(parsed)
            verification['region_code'] = region_code

            if region_code:
                verification['valid_for_region'] = phonenumbers.is_valid_number_for_region(
                    parsed, region_code
                )

        except phonenumbers.NumberParseException as e:
            verification['is_valid'] = False
            verification['error'] = str(e)
            verification['error_type'] = type(e).__name__

        except Exception as e:
            verification['is_valid'] = False
            verification['error'] = str(e)

        return verification
