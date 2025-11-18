"""
Lead Signal Detection System

Detects signals indicating need for services (loans, consulting, etc.)
"""

import re
from typing import Dict, List, Any


class LeadSignalDetector:
    """
    Detect signals indicating need for various services.

    Signal types:
    - Loan need signals
    - Consulting need signals
    - Financial distress signals
    - Growth signals
    - Expansion signals
    """

    # Keyword patterns for different signal types
    LOAN_KEYWORDS = [
        r'\b(?:need|looking for|seeking|want)\s+(?:a\s+)?(?:business\s+)?loan\b',
        r'\b(?:small business|startup|working capital)\s+(?:loan|financing)\b',
        r'\b(?:equipment|inventory|expansion)\s+financing\b',
        r'\bcash flow\s+(?:problem|issue|challenge)\b',
        r'\bneed\s+(?:capital|funding|money)\b',
        r'\b(?:line of credit|credit line)\b',
        r'\bdebt consolidation\b',
        r'\brefinance\b',
        r'\b(?:bridge|gap)\s+financing\b',
    ]

    CONSULTING_KEYWORDS = [
        r'\bneed\s+(?:help|advice|guidance|consultant)\b',
        r'\blooking for\s+(?:consultant|consulting|advisor)\b',
        r'\bimprove\s+(?:operations|efficiency|processes)\b',
        r'\b(?:business|strategic|management)\s+consulting\b',
        r'\bdigital transformation\b',
        r'\bprocess improvement\b',
        r'\borganizational\s+(?:change|restructuring)\b',
        r'\bcost\s+reduction\b',
        r'\bperformance\s+optimization\b',
    ]

    FINANCIAL_DISTRESS_KEYWORDS = [
        r'\bcash flow\s+(?:problem|crisis|shortage)\b',
        r'\bstruggling\s+to\s+(?:pay|meet|cover)\b',
        r'\bmissing\s+payments\b',
        r'\b(?:behind|late)\s+on\s+(?:payments|bills|rent)\b',
        r'\bfinancial\s+(?:difficulty|hardship|trouble|crisis)\b',
        r'\bneed\s+money\s+(?:urgently|quickly|now|fast)\b',
        r'\bpayroll\s+(?:problem|issue|shortage)\b',
        r'\bcannot\s+(?:pay|afford)\b',
    ]

    GROWTH_KEYWORDS = [
        r'\b(?:hiring|recruiting|expanding team)\b',
        r'\bnew\s+(?:location|office|store|branch)\b',
        r'\b(?:expanding|growth|growing|scaling)\b',
        r'\bincreased\s+(?:revenue|sales|demand)\b',
        r'\bnew\s+(?:product|service)\s+launch\b',
        r'\bmarket\s+expansion\b',
        r'\bcapacity\s+expansion\b',
    ]

    EXPANSION_KEYWORDS = [
        r'\bopening\s+new\s+(?:location|office|store)\b',
        r'\bentering\s+new\s+market\b',
        r'\bacquisition\b',
        r'\bmerger\b',
        r'\bfranchise\s+expansion\b',
        r'\bgeographic\s+expansion\b',
        r'\bscale\s+(?:up|operations)\b',
    ]

    def detect_loan_signals(
        self,
        content: str,
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Detect loan need signals.

        Args:
            content: Text content to analyze
            metadata: Additional context

        Returns:
            List of detected signals
        """
        signals = []

        # Check for loan keywords
        for pattern in self.LOAN_KEYWORDS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                signals.append({
                    'type': 'loan_need',
                    'category': 'keyword',
                    'source': 'content_analysis',
                    'content': match,
                    'strength': self._calculate_keyword_strength(pattern, content),
                    'confidence': 80
                })

        # Check for loan-related behaviors
        if metadata.get('behavior'):
            behavior_signals = self._analyze_loan_behavior(metadata['behavior'])
            signals.extend(behavior_signals)

        return signals

    def detect_consulting_signals(
        self,
        content: str,
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Detect consulting need signals.

        Args:
            content: Text content to analyze
            metadata: Additional context

        Returns:
            List of detected signals
        """
        signals = []

        # Check for consulting keywords
        for pattern in self.CONSULTING_KEYWORDS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                signals.append({
                    'type': 'consulting_need',
                    'category': 'keyword',
                    'source': 'content_analysis',
                    'content': match,
                    'strength': self._calculate_keyword_strength(pattern, content),
                    'confidence': 75
                })

        # Check for problem indicators
        problem_signals = self._detect_problem_indicators(content)
        signals.extend(problem_signals)

        return signals

    def detect_financial_distress(self, content: str) -> List[Dict[str, Any]]:
        """Detect financial distress indicators."""
        signals = []

        for pattern in self.FINANCIAL_DISTRESS_KEYWORDS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                signals.append({
                    'type': 'financial_distress',
                    'category': 'keyword',
                    'source': 'content_analysis',
                    'content': match,
                    'strength': 90,  # High strength for distress signals
                    'confidence': 85
                })

        return signals

    def detect_growth_signals(self, content: str) -> List[Dict[str, Any]]:
        """Detect business growth indicators."""
        signals = []

        for pattern in self.GROWTH_KEYWORDS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                signals.append({
                    'type': 'growth',
                    'category': 'keyword',
                    'source': 'content_analysis',
                    'content': match,
                    'strength': 70,
                    'confidence': 75
                })

        return signals

    def detect_expansion_signals(self, content: str) -> List[Dict[str, Any]]:
        """Detect expansion/scale-up indicators."""
        signals = []

        for pattern in self.EXPANSION_KEYWORDS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                signals.append({
                    'type': 'expansion',
                    'category': 'keyword',
                    'source': 'content_analysis',
                    'content': match,
                    'strength': 80,
                    'confidence': 80
                })

        return signals

    def calculate_signal_strength(self, signals: List[Dict]) -> int:
        """
        Calculate overall signal strength from multiple signals.

        Args:
            signals: List of signals

        Returns:
            Overall strength (0-100)
        """
        if not signals:
            return 0

        # Calculate weighted average
        total_strength = sum(s.get('strength', 0) for s in signals)
        avg_strength = total_strength / len(signals)

        # Bonus for multiple signals
        if len(signals) > 1:
            bonus = min(20, len(signals) * 5)
            avg_strength = min(100, avg_strength + bonus)

        return int(avg_strength)

    def detect_all_signals(
        self,
        content: str,
        metadata: Optional[Dict] = None
    ) -> Dict[str, List[Dict]]:
        """
        Detect all types of signals in content.

        Args:
            content: Text content to analyze
            metadata: Additional context

        Returns:
            Dict of signal type -> list of signals
        """
        metadata = metadata or {}

        return {
            'loan_signals': self.detect_loan_signals(content, metadata),
            'consulting_signals': self.detect_consulting_signals(content, metadata),
            'financial_distress': self.detect_financial_distress(content),
            'growth_signals': self.detect_growth_signals(content),
            'expansion_signals': self.detect_expansion_signals(content)
        }

    def _calculate_keyword_strength(self, pattern: str, content: str) -> int:
        """Calculate strength based on keyword match and context."""
        # Base strength
        strength = 60

        # Check for urgency words
        urgency_words = ['urgent', 'immediately', 'asap', 'quickly', 'now', 'today']
        if any(word in content.lower() for word in urgency_words):
            strength += 15

        # Check for specific amounts (indicates serious intent)
        if re.search(r'\$\d+[,\d]*', content):
            strength += 10

        # Check for contact information (indicates readiness)
        if re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', content):
            strength += 10

        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content):
            strength += 10

        return min(100, strength)

    def _analyze_loan_behavior(self, behavior: Dict) -> List[Dict[str, Any]]:
        """Analyze behavior patterns for loan intent."""
        signals = []

        # Check for loan calculator usage
        if 'loan_calculator' in str(behavior).lower():
            signals.append({
                'type': 'loan_need',
                'category': 'behavior',
                'source': 'behavioral_analysis',
                'content': 'Used loan calculator',
                'strength': 85,
                'confidence': 90
            })

        # Check for application page visits
        if 'application' in str(behavior).lower():
            signals.append({
                'type': 'loan_need',
                'category': 'behavior',
                'source': 'behavioral_analysis',
                'content': 'Visited application page',
                'strength': 75,
                'confidence': 85
            })

        # Check for rates/pricing page visits
        if any(word in str(behavior).lower() for word in ['rate', 'pricing', 'cost']):
            signals.append({
                'type': 'loan_need',
                'category': 'behavior',
                'source': 'behavioral_analysis',
                'content': 'Checked rates/pricing',
                'strength': 70,
                'confidence': 80
            })

        return signals

    def _detect_problem_indicators(self, content: str) -> List[Dict[str, Any]]:
        """Detect problem statements indicating consulting needs."""
        signals = []

        problem_patterns = [
            r'\bproblem\s+with\s+\w+',
            r'\bchallenge\s+in\s+\w+',
            r'\bstruggling\s+with\s+\w+',
            r'\bdifficulty\s+\w+ing',
            r'\bnot\s+sure\s+how\s+to\s+\w+',
            r'\bneed\s+to\s+improve\s+\w+',
        ]

        for pattern in problem_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                signals.append({
                    'type': 'consulting_need',
                    'category': 'problem_indicator',
                    'source': 'content_analysis',
                    'content': match,
                    'strength': 65,
                    'confidence': 70
                })

        return signals


# Import for type checking
from typing import Optional
