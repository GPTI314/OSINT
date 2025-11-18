"""
Matchmaking Algorithm

Multi-factor scoring algorithm for lead-to-service matching.
"""

from typing import Dict, List, Optional, Any, Tuple
import re


class MatchingAlgorithm:
    """
    Multi-factor matchmaking algorithm.

    Scoring factors (total: 100 points):
    - Geographic match: 0-25 points
    - Industry match: 0-20 points
    - Need match: 0-25 points
    - Profile match: 0-15 points
    - Behavioral match: 0-15 points
    """

    DEFAULT_WEIGHTS = {
        'geographic': 0.25,
        'industry': 0.20,
        'need': 0.25,
        'profile': 0.15,
        'behavioral': 0.15,
    }

    def calculate_match_score(
        self,
        lead: Dict[str, Any],
        service: Dict[str, Any],
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive match score.

        Args:
            lead: Lead data
            service: Service data
            weights: Custom scoring weights

        Returns:
            Match data with scores and reasons
        """
        weights = weights or self.DEFAULT_WEIGHTS

        # Calculate individual scores
        geographic_score = self.geographic_match(
            lead.get('city'),
            lead.get('state'),
            lead.get('country'),
            service.get('target_locations', [])
        )

        industry_score = self.industry_match(
            lead.get('industry'),
            service.get('target_industries', [])
        )

        need_score = self.need_match(
            lead.get('needs_identified', []),
            lead.get('lead_category'),
            service.get('service_type'),
            service.get('service_category')
        )

        profile_score = self.profile_match(
            lead.get('lead_type'),
            lead.get('company_size'),
            lead.get('revenue_range'),
            service.get('target_audience'),
            service.get('target_company_sizes', []),
            service.get('requirements', {})
        )

        behavioral_score = self.behavioral_match(
            lead.get('signal_strength', 0),
            lead.get('intent_score', 0),
            lead.get('signals_detected', [])
        )

        # Calculate weighted total
        match_score = (
            geographic_score * weights['geographic'] +
            industry_score * weights['industry'] +
            need_score * weights['need'] +
            profile_score * weights['profile'] +
            behavioral_score * weights['behavioral']
        )

        # Determine confidence level
        confidence_level = self._determine_confidence(
            match_score,
            [geographic_score, industry_score, need_score, profile_score, behavioral_score]
        )

        # Generate match reasons
        reasons = self._generate_match_reasons(
            geographic_score, industry_score, need_score,
            profile_score, behavioral_score, lead, service
        )

        # Determine priority
        priority = self._determine_priority(match_score, lead.get('intent_score', 0))

        return {
            'match_score': round(match_score, 2),
            'geographic_score': round(geographic_score, 2),
            'industry_score': round(industry_score, 2),
            'need_score': round(need_score, 2),
            'profile_score': round(profile_score, 2),
            'behavioral_score': round(behavioral_score, 2),
            'confidence_level': confidence_level,
            'reasons': reasons,
            'priority': priority,
        }

    def geographic_match(
        self,
        lead_city: Optional[str],
        lead_state: Optional[str],
        lead_country: Optional[str],
        service_locations: List[str]
    ) -> float:
        """
        Calculate geographic match score (0-100).

        Args:
            lead_city: Lead city
            lead_state: Lead state
            lead_country: Lead country
            service_locations: Service target locations

        Returns:
            Geographic score (0-100)
        """
        if not service_locations:
            return 100  # Service available everywhere

        # Normalize locations
        service_locations = [loc.lower().strip() for loc in service_locations]

        # Check for nationwide/global
        if any(loc in ['nationwide', 'national', 'global', 'all'] for loc in service_locations):
            return 100

        # Check exact matches
        if lead_city and any(lead_city.lower() in loc for loc in service_locations):
            return 100

        if lead_state and any(lead_state.lower() in loc for loc in service_locations):
            return 85

        if lead_country and any(lead_country.lower() in loc for loc in service_locations):
            return 70

        # Partial matches
        if lead_state:
            state_abbrev = self._get_state_abbreviation(lead_state)
            if any(state_abbrev.lower() in loc for loc in service_locations):
                return 85

        return 0  # No geographic match

    def industry_match(
        self,
        lead_industry: Optional[str],
        service_industries: List[str]
    ) -> float:
        """
        Calculate industry match score (0-100).

        Args:
            lead_industry: Lead industry
            service_industries: Service target industries

        Returns:
            Industry score (0-100)
        """
        if not service_industries:
            return 100  # Service targets all industries

        if not lead_industry:
            return 50  # Unknown industry, moderate score

        # Normalize
        lead_industry = lead_industry.lower().strip()
        service_industries = [ind.lower().strip() for ind in service_industries]

        # Check for "all" industries
        if any(ind in ['all', 'any', 'various'] for ind in service_industries):
            return 100

        # Exact match
        if lead_industry in service_industries:
            return 100

        # Partial match
        for service_ind in service_industries:
            if service_ind in lead_industry or lead_industry in service_ind:
                return 80

        # Industry category match (e.g., "retail" matches "retail store")
        for service_ind in service_industries:
            if self._industries_related(lead_industry, service_ind):
                return 60

        return 30  # No match, but still possible

    def need_match(
        self,
        lead_needs: List[str],
        lead_category: Optional[str],
        service_type: Optional[str],
        service_category: Optional[str]
    ) -> float:
        """
        Calculate need match score (0-100).

        Args:
            lead_needs: Lead's identified needs
            lead_category: Lead category
            service_type: Service type
            service_category: Service category

        Returns:
            Need score (0-100)
        """
        score = 0

        # Direct need match
        if lead_needs and service_type:
            service_type_lower = service_type.lower()
            for need in lead_needs:
                need_lower = need.lower()
                if service_type_lower in need_lower or need_lower in service_type_lower:
                    score = max(score, 100)
                elif self._needs_related(need_lower, service_type_lower):
                    score = max(score, 80)

        # Category match
        if lead_category and service_category:
            if lead_category.lower() == service_category.lower():
                score = max(score, 90)
            elif self._categories_related(lead_category, service_category):
                score = max(score, 70)

        # Type match
        if lead_category and service_type:
            if lead_category.lower() == service_type.lower():
                score = max(score, 85)

        return score if score > 0 else 40  # Minimum score for potential match

    def profile_match(
        self,
        lead_type: Optional[str],
        lead_company_size: Optional[str],
        lead_revenue_range: Optional[str],
        service_audience: Optional[str],
        service_company_sizes: List[str],
        service_requirements: Dict[str, Any]
    ) -> float:
        """
        Calculate profile match score (0-100).

        Args:
            lead_type: Lead type (consumer/business)
            lead_company_size: Company size
            lead_revenue_range: Revenue range
            service_audience: Target audience
            service_company_sizes: Target company sizes
            service_requirements: Service requirements

        Returns:
            Profile score (0-100)
        """
        score = 100

        # Audience match
        if service_audience and lead_type:
            if service_audience.lower() == 'both':
                score = min(score, 100)
            elif service_audience.lower() == lead_type.lower():
                score = min(score, 100)
            else:
                score = min(score, 30)  # Mismatch

        # Company size match
        if service_company_sizes and lead_company_size:
            company_sizes_lower = [cs.lower() for cs in service_company_sizes]
            if lead_company_size.lower() in company_sizes_lower:
                score = min(score, 100)
            else:
                score = min(score, 60)  # Size mismatch

        # Revenue match (if service has min/max requirements)
        if service_requirements.get('min_revenue') and lead_revenue_range:
            # Simplified revenue check (in production, parse range properly)
            score = min(score, 80)

        return score

    def behavioral_match(
        self,
        signal_strength: int,
        intent_score: int,
        signals: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate behavioral match score (0-100).

        Args:
            signal_strength: Overall signal strength
            intent_score: Intent score
            signals: Detected signals

        Returns:
            Behavioral score (0-100)
        """
        # Weight signal strength and intent
        base_score = (signal_strength * 0.6) + (intent_score * 0.4)

        # Bonus for multiple signals
        if isinstance(signals, list) and len(signals) > 0:
            signal_bonus = min(20, len(signals) * 3)
            base_score = min(100, base_score + signal_bonus)

        return base_score

    def _determine_confidence(
        self,
        match_score: float,
        component_scores: List[float]
    ) -> str:
        """Determine confidence level based on scores."""
        if match_score >= 80:
            # Check if all components are decent
            if all(score >= 50 for score in component_scores):
                return 'high'
            return 'medium'
        elif match_score >= 60:
            return 'medium'
        else:
            return 'low'

    def _generate_match_reasons(
        self,
        geo_score: float,
        ind_score: float,
        need_score: float,
        prof_score: float,
        behav_score: float,
        lead: Dict[str, Any],
        service: Dict[str, Any]
    ) -> List[str]:
        """Generate human-readable match reasons."""
        reasons = []

        if geo_score >= 85:
            reasons.append(f"Strong geographic match: {lead.get('city', '')}, {lead.get('state', '')}")
        elif geo_score >= 70:
            reasons.append("Moderate geographic match")

        if ind_score >= 80:
            reasons.append(f"Industry match: {lead.get('industry', '')}")

        if need_score >= 80:
            reasons.append(f"Strong need match: {lead.get('lead_category', '')}")

        if prof_score >= 80:
            reasons.append("Good profile fit")

        if behav_score >= 70:
            reasons.append(f"High intent signals (score: {lead.get('intent_score', 0)})")

        if not reasons:
            reasons.append("Potential match based on general criteria")

        return reasons

    def _determine_priority(self, match_score: float, intent_score: int) -> str:
        """Determine match priority."""
        if match_score >= 80 and intent_score >= 70:
            return 'urgent'
        elif match_score >= 70:
            return 'high'
        elif match_score >= 50:
            return 'medium'
        else:
            return 'low'

    def _get_state_abbreviation(self, state: str) -> str:
        """Get state abbreviation (simplified)."""
        # In production, use a complete state mapping
        state_map = {
            'california': 'CA', 'new york': 'NY', 'texas': 'TX',
            'florida': 'FL', 'illinois': 'IL', 'pennsylvania': 'PA',
            # Add more states...
        }
        return state_map.get(state.lower(), state[:2].upper())

    def _industries_related(self, industry1: str, industry2: str) -> bool:
        """Check if industries are related."""
        # Simplified industry relationship check
        related_groups = [
            {'retail', 'e-commerce', 'store', 'shop'},
            {'technology', 'software', 'it', 'tech', 'saas'},
            {'healthcare', 'medical', 'hospital', 'clinic'},
            {'finance', 'banking', 'financial services'},
            {'manufacturing', 'production', 'factory'},
            {'food', 'restaurant', 'hospitality', 'dining'},
        ]

        for group in related_groups:
            if any(term in industry1 for term in group) and any(term in industry2 for term in group):
                return True

        return False

    def _needs_related(self, need: str, service_type: str) -> bool:
        """Check if need is related to service type."""
        relations = {
            'loan': ['financing', 'capital', 'funding', 'credit'],
            'consulting': ['advice', 'strategy', 'improvement', 'optimization'],
            'financial_service': ['accounting', 'tax', 'planning', 'advisory'],
        }

        for key, related in relations.items():
            if key in service_type and any(term in need for term in related):
                return True

        return False

    def _categories_related(self, category1: str, category2: str) -> bool:
        """Check if categories are related."""
        category_map = {
            'loan': ['financing', 'lending', 'credit'],
            'consulting': ['advisory', 'strategy', 'coaching'],
        }

        cat1_lower = category1.lower()
        cat2_lower = category2.lower()

        for key, related in category_map.items():
            if (key in cat1_lower and any(r in cat2_lower for r in related)) or \
               (key in cat2_lower and any(r in cat1_lower for r in related)):
                return True

        return False
