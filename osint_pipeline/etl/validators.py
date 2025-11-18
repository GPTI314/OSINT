"""
Data validation components
"""
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
import re


class ValidationRule:
    """Base validation rule class"""

    def __init__(self, name: str, validator: Callable[[Any], bool], error_message: str):
        self.name = name
        self.validator = validator
        self.error_message = error_message

    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        """
        Validate a value against the rule

        Args:
            value: Value to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            is_valid = self.validator(value)
            return (is_valid, None if is_valid else self.error_message)
        except Exception as e:
            return (False, f"Validation error: {str(e)}")


class DataValidator:
    """Data validation with quality checks"""

    def __init__(self):
        self.rules: Dict[str, List[ValidationRule]] = {}
        self.errors: List[Dict[str, Any]] = []

    def add_rule(self, field: str, rule: ValidationRule):
        """
        Add validation rule for a field

        Args:
            field: Field name
            rule: ValidationRule instance
        """
        if field not in self.rules:
            self.rules[field] = []
        self.rules[field].append(rule)

    def add_required_field(self, field: str):
        """
        Add required field validation

        Args:
            field: Field name that is required
        """
        rule = ValidationRule(
            name=f"{field}_required",
            validator=lambda x: x is not None and x != "",
            error_message=f"Field '{field}' is required"
        )
        self.add_rule(field, rule)

    def add_type_check(self, field: str, expected_type: type):
        """
        Add type checking validation

        Args:
            field: Field name
            expected_type: Expected Python type
        """
        rule = ValidationRule(
            name=f"{field}_type",
            validator=lambda x: isinstance(x, expected_type),
            error_message=f"Field '{field}' must be of type {expected_type.__name__}"
        )
        self.add_rule(field, rule)

    def add_regex_pattern(self, field: str, pattern: str, description: str = ""):
        """
        Add regex pattern validation

        Args:
            field: Field name
            pattern: Regex pattern
            description: Description of the pattern
        """
        rule = ValidationRule(
            name=f"{field}_pattern",
            validator=lambda x: bool(re.match(pattern, str(x))),
            error_message=f"Field '{field}' does not match pattern {description or pattern}"
        )
        self.add_rule(field, rule)

    def add_range_check(self, field: str, min_val: Optional[float] = None, max_val: Optional[float] = None):
        """
        Add range validation for numeric fields

        Args:
            field: Field name
            min_val: Minimum value (inclusive)
            max_val: Maximum value (inclusive)
        """
        def range_validator(x):
            if not isinstance(x, (int, float)):
                return False
            if min_val is not None and x < min_val:
                return False
            if max_val is not None and x > max_val:
                return False
            return True

        rule = ValidationRule(
            name=f"{field}_range",
            validator=range_validator,
            error_message=f"Field '{field}' must be between {min_val} and {max_val}"
        )
        self.add_rule(field, rule)

    def validate(self, data: Dict[str, Any]) -> tuple[bool, List[Dict[str, Any]]]:
        """
        Validate data against all rules

        Args:
            data: Data dictionary to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        self.errors = []
        is_valid = True

        for field, rules in self.rules.items():
            value = data.get(field)

            for rule in rules:
                valid, error_msg = rule.validate(value)
                if not valid:
                    is_valid = False
                    self.errors.append({
                        'field': field,
                        'rule': rule.name,
                        'message': error_msg,
                        'timestamp': datetime.utcnow().isoformat()
                    })

        return (is_valid, self.errors)

    def get_errors(self) -> List[Dict[str, Any]]:
        """
        Get validation errors

        Returns:
            List of error dictionaries
        """
        return self.errors

    def clear_errors(self):
        """Clear all validation errors"""
        self.errors = []

    def quality_check(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform quality checks on data

        Args:
            data: Data to check

        Returns:
            Quality report dictionary
        """
        report = {
            'completeness': self._check_completeness(data),
            'consistency': self._check_consistency(data),
            'validity': self._check_validity(data),
            'timestamp': datetime.utcnow().isoformat()
        }
        return report

    def _check_completeness(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check data completeness"""
        total_fields = len(self.rules)
        filled_fields = sum(1 for field in self.rules.keys() if data.get(field))
        return {
            'score': filled_fields / total_fields if total_fields > 0 else 1.0,
            'total_fields': total_fields,
            'filled_fields': filled_fields
        }

    def _check_consistency(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check data consistency"""
        # Basic consistency check - could be extended
        return {
            'score': 1.0,
            'issues': []
        }

    def _check_validity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check data validity"""
        is_valid, errors = self.validate(data)
        return {
            'score': 1.0 if is_valid else 0.0,
            'valid': is_valid,
            'errors': errors
        }
