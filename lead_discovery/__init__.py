"""
Lead Discovery & Matchmaking System

WARNING: This module is designed for authorized security testing and research purposes only.
Use only in controlled environments with proper authorization and consent.

Components:
- Cookie and identifier tracking
- Lead discovery and signal detection
- Matchmaking algorithm
- Geographic targeting
- Integration with OSINT profiler
"""

from .cookie_tracker import CookieTracker
from .identifier_manager import IdentifierManager
from .lead_discovery import LeadDiscoveryEngine
from .signal_detector import LeadSignalDetector
from .matchmaker import LeadMatchmaker
from .matching_algorithm import MatchingAlgorithm
from .geographic_targeting import GeographicTargeting
from .profiler_integration import ProfilerIntegration
from .alerts import LeadAlertSystem

__all__ = [
    'CookieTracker',
    'IdentifierManager',
    'LeadDiscoveryEngine',
    'LeadSignalDetector',
    'LeadMatchmaker',
    'MatchingAlgorithm',
    'GeographicTargeting',
    'ProfilerIntegration',
    'LeadAlertSystem',
]

__version__ = '1.0.0'
