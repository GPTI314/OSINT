"""
Phone number intelligence collector for validation and carrier lookup.
"""
from typing import Dict, Any
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
from datetime import datetime
import logging

from .base_collector import BaseCollector

logger = logging.getLogger(__name__)


class PhoneCollector(BaseCollector):
    """Collector for phone number intelligence gathering."""

    async def collect(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Collect intelligence on a phone number.

        Args:
            target: Phone number
            **kwargs: Additional parameters

        Returns:
            Dict containing phone intelligence
        """
        phone = target.strip()

        # Parse and validate phone number
        await self._parse_phone(phone, kwargs.get("default_region", "US"))

        return {
            "target": phone,
            "target_type": "phone",
            "results": self.results,
            "errors": self.errors,
            "summary": self.get_summary(),
            "collected_at": datetime.utcnow().isoformat()
        }

    async def _parse_phone(self, phone: str, default_region: str = "US"):
        """Parse and analyze phone number."""
        try:
            # Parse phone number
            parsed = phonenumbers.parse(phone, default_region)

            # Validate
            is_valid = phonenumbers.is_valid_number(parsed)
            is_possible = phonenumbers.is_possible_number(parsed)

            # Get carrier information
            carrier_name = carrier.name_for_number(parsed, "en")

            # Get geographic information
            location = geocoder.description_for_number(parsed, "en")

            # Get timezone
            tz = timezone.time_zones_for_number(parsed)

            # Get number type
            number_type = phonenumbers.number_type(parsed)
            type_name = {
                0: "FIXED_LINE",
                1: "MOBILE",
                2: "FIXED_LINE_OR_MOBILE",
                3: "TOLL_FREE",
                4: "PREMIUM_RATE",
                5: "SHARED_COST",
                6: "VOIP",
                7: "PERSONAL_NUMBER",
                8: "PAGER",
                9: "UAN",
                10: "VOICEMAIL",
                -1: "UNKNOWN"
            }.get(number_type, "UNKNOWN")

            phone_data = {
                "raw_input": phone,
                "formatted_e164": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164),
                "formatted_international": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
                "formatted_national": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL),
                "country_code": parsed.country_code,
                "national_number": parsed.national_number,
                "is_valid": is_valid,
                "is_possible": is_possible,
                "carrier": carrier_name if carrier_name else "Unknown",
                "location": location if location else "Unknown",
                "timezone": list(tz) if tz else [],
                "number_type": type_name
            }

            self.add_result("phone_analysis", phone_data, confidence=0.95)

        except phonenumbers.NumberParseException as e:
            self.add_error("phone_analysis", f"Invalid phone number: {str(e)}")
        except Exception as e:
            self.add_error("phone_analysis", str(e))
