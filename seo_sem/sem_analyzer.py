"""SEM Analysis Engine - Search Engine Marketing analysis capabilities."""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class SEMAnalyzer:
    """
    SEM (Search Engine Marketing) analysis:
    - Google Ads keyword research
    - Ad copy analysis
    - Landing page optimization
    - Conversion tracking
    - Campaign performance analysis
    - Competitor ad analysis
    - Bid management insights
    - Quality score analysis
    - Ad extension optimization
    - A/B testing recommendations
    """

    def __init__(self, db: Session):
        self.db = db
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)

    async def keyword_research(
        self,
        seed_keywords: List[str],
        location: Optional[str] = None,
        investigation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """SEM keyword research with metrics."""
        logger.info(f"Performing SEM keyword research for {len(seed_keywords)} seed keywords")

        research_results = {
            "seed_keywords": seed_keywords,
            "location": location,
            "keyword_suggestions": [],
            "total_keywords_found": 0,
            "estimated_total_cost": 0.0
        }

        for seed in seed_keywords:
            suggestions = await self._get_keyword_suggestions(seed, location)
            research_results["keyword_suggestions"].extend(suggestions)

        research_results["total_keywords_found"] = len(research_results["keyword_suggestions"])

        # Calculate estimated total cost
        for keyword_data in research_results["keyword_suggestions"]:
            cpc = keyword_data.get("cpc", 0)
            search_volume = keyword_data.get("search_volume", 0)
            research_results["estimated_total_cost"] += cpc * search_volume * 0.01  # Rough estimate

        # Sort by opportunity score
        research_results["keyword_suggestions"] = sorted(
            research_results["keyword_suggestions"],
            key=lambda x: x.get("opportunity_score", 0),
            reverse=True
        )

        return research_results

    async def _get_keyword_suggestions(
        self,
        seed_keyword: str,
        location: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get keyword suggestions for a seed keyword."""
        # In production, integrate with Google Ads API, SEMrush, etc.
        # For now, return simulated data

        suggestions = []

        # Simulated keyword variations
        variations = [
            seed_keyword,
            f"{seed_keyword} online",
            f"{seed_keyword} near me",
            f"best {seed_keyword}",
            f"{seed_keyword} reviews",
            f"{seed_keyword} price",
            f"buy {seed_keyword}",
            f"{seed_keyword} services"
        ]

        for variation in variations:
            keyword_data = {
                "keyword": variation,
                "search_volume": self._simulate_search_volume(),
                "cpc": self._simulate_cpc(),
                "competition": self._simulate_competition(),
                "competition_index": self._simulate_competition_index(),
                "ad_impression_share": self._simulate_impression_share(),
                "opportunity_score": 0.0
            }

            # Calculate opportunity score
            keyword_data["opportunity_score"] = self._calculate_opportunity_score(keyword_data)

            suggestions.append(keyword_data)

        return suggestions

    def _simulate_search_volume(self) -> int:
        """Simulate search volume (placeholder)."""
        import random
        return random.randint(100, 10000)

    def _simulate_cpc(self) -> float:
        """Simulate CPC (placeholder)."""
        import random
        return round(random.uniform(0.50, 15.00), 2)

    def _simulate_competition(self) -> str:
        """Simulate competition level (placeholder)."""
        import random
        return random.choice(["low", "medium", "high"])

    def _simulate_competition_index(self) -> float:
        """Simulate competition index 0-100 (placeholder)."""
        import random
        return round(random.uniform(0, 100), 2)

    def _simulate_impression_share(self) -> float:
        """Simulate impression share (placeholder)."""
        import random
        return round(random.uniform(10, 90), 2)

    def _calculate_opportunity_score(self, keyword_data: Dict[str, Any]) -> float:
        """Calculate opportunity score for a keyword."""
        # Higher search volume is better
        volume_score = min(keyword_data["search_volume"] / 1000, 100)

        # Lower CPC is better for budget
        cpc_score = max(100 - (keyword_data["cpc"] * 5), 0)

        # Lower competition is better
        competition_score = 100 - keyword_data["competition_index"]

        # Weighted average
        opportunity_score = (
            volume_score * 0.4 +
            cpc_score * 0.3 +
            competition_score * 0.3
        )

        return round(opportunity_score, 2)

    async def ad_copy_analysis(
        self,
        ad_copies: List[Dict[str, str]],
        investigation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Analyze ad copy effectiveness."""
        logger.info(f"Analyzing {len(ad_copies)} ad copies")

        analysis_results = {
            "total_ads_analyzed": len(ad_copies),
            "ad_analyses": [],
            "best_performing_elements": {},
            "recommendations": []
        }

        for ad_copy in ad_copies:
            ad_analysis = self._analyze_single_ad(ad_copy)
            analysis_results["ad_analyses"].append(ad_analysis)

        # Identify best performing elements
        analysis_results["best_performing_elements"] = self._identify_best_elements(
            analysis_results["ad_analyses"]
        )

        # Generate recommendations
        analysis_results["recommendations"] = self._generate_ad_recommendations(
            analysis_results["ad_analyses"]
        )

        return analysis_results

    def _analyze_single_ad(self, ad_copy: Dict[str, str]) -> Dict[str, Any]:
        """Analyze a single ad copy."""
        headline = ad_copy.get("headline", "")
        description = ad_copy.get("description", "")
        display_url = ad_copy.get("display_url", "")

        analysis = {
            "ad_copy": ad_copy,
            "headline_length": len(headline),
            "description_length": len(description),
            "has_call_to_action": self._has_call_to_action(description),
            "has_numbers": self._has_numbers(headline + description),
            "has_emotional_words": self._has_emotional_words(headline + description),
            "quality_score": 0.0,
            "issues": [],
            "strengths": []
        }

        # Check headline length
        if analysis["headline_length"] > 30:
            analysis["issues"].append("Headline may be truncated (>30 chars)")
        elif analysis["headline_length"] < 15:
            analysis["issues"].append("Headline too short (<15 chars)")
        else:
            analysis["strengths"].append("Headline length optimal")

        # Check description length
        if analysis["description_length"] > 90:
            analysis["issues"].append("Description may be truncated (>90 chars)")
        elif analysis["description_length"] < 40:
            analysis["issues"].append("Description too short (<40 chars)")
        else:
            analysis["strengths"].append("Description length optimal")

        # Check for CTA
        if analysis["has_call_to_action"]:
            analysis["strengths"].append("Includes call-to-action")
        else:
            analysis["issues"].append("Missing clear call-to-action")

        # Check for numbers
        if analysis["has_numbers"]:
            analysis["strengths"].append("Includes numbers/statistics")

        # Check for emotional words
        if analysis["has_emotional_words"]:
            analysis["strengths"].append("Uses emotional triggers")

        # Calculate quality score
        analysis["quality_score"] = self._calculate_ad_quality_score(analysis)

        return analysis

    def _has_call_to_action(self, text: str) -> bool:
        """Check if text has a call-to-action."""
        cta_words = [
            "buy", "shop", "order", "call", "contact", "learn", "discover",
            "get", "try", "start", "sign up", "subscribe", "download",
            "register", "book", "reserve", "request", "schedule"
        ]
        text_lower = text.lower()
        return any(cta in text_lower for cta in cta_words)

    def _has_numbers(self, text: str) -> bool:
        """Check if text contains numbers."""
        import re
        return bool(re.search(r'\d', text))

    def _has_emotional_words(self, text: str) -> bool:
        """Check if text contains emotional words."""
        emotional_words = [
            "amazing", "best", "exclusive", "limited", "guaranteed",
            "proven", "certified", "professional", "expert", "premium",
            "quality", "trusted", "official", "free", "save"
        ]
        text_lower = text.lower()
        return any(word in text_lower for word in emotional_words)

    def _calculate_ad_quality_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate ad quality score."""
        score = 70.0  # Base score

        # Headline length
        if 15 <= analysis["headline_length"] <= 30:
            score += 10
        else:
            score -= 5

        # Description length
        if 40 <= analysis["description_length"] <= 90:
            score += 10
        else:
            score -= 5

        # Has CTA
        if analysis["has_call_to_action"]:
            score += 10

        # Has numbers
        if analysis["has_numbers"]:
            score += 5

        # Has emotional words
        if analysis["has_emotional_words"]:
            score += 5

        return max(0.0, min(100.0, score))

    def _identify_best_elements(
        self,
        ad_analyses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Identify best performing elements across ads."""
        best_elements = {
            "highest_quality_score": 0.0,
            "most_common_strengths": [],
            "most_common_issues": []
        }

        if not ad_analyses:
            return best_elements

        # Find highest quality score
        best_elements["highest_quality_score"] = max(
            a["quality_score"] for a in ad_analyses
        )

        # Count strengths
        strength_counts = {}
        for analysis in ad_analyses:
            for strength in analysis["strengths"]:
                strength_counts[strength] = strength_counts.get(strength, 0) + 1

        best_elements["most_common_strengths"] = sorted(
            strength_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]

        # Count issues
        issue_counts = {}
        for analysis in ad_analyses:
            for issue in analysis["issues"]:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1

        best_elements["most_common_issues"] = sorted(
            issue_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]

        return best_elements

    def _generate_ad_recommendations(
        self,
        ad_analyses: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate ad recommendations."""
        recommendations = []

        # Check for common issues
        cta_missing_count = sum(
            1 for a in ad_analyses if not a["has_call_to_action"]
        )
        if cta_missing_count > len(ad_analyses) * 0.5:
            recommendations.append("Add clear calls-to-action to more ads")

        numbers_missing_count = sum(
            1 for a in ad_analyses if not a["has_numbers"]
        )
        if numbers_missing_count > len(ad_analyses) * 0.5:
            recommendations.append("Include numbers or statistics in ad copy")

        emotional_missing_count = sum(
            1 for a in ad_analyses if not a["has_emotional_words"]
        )
        if emotional_missing_count > len(ad_analyses) * 0.5:
            recommendations.append("Use more emotional trigger words")

        # Average quality score
        avg_quality = sum(a["quality_score"] for a in ad_analyses) / len(ad_analyses)
        if avg_quality < 70:
            recommendations.append("Overall ad quality needs improvement - focus on best practices")

        return recommendations

    async def landing_page_analysis(
        self,
        url: str,
        investigation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Landing page optimization analysis."""
        logger.info(f"Analyzing landing page: {url}")

        try:
            response = await self.client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            analysis = {
                "url": url,
                "status_code": response.status_code,
                "load_time": response.elapsed.total_seconds(),
                "has_headline": bool(soup.find('h1')),
                "has_form": bool(soup.find('form')),
                "has_cta_button": self._has_cta_button(soup),
                "mobile_responsive": self._check_mobile_responsive(soup),
                "optimization_score": 0.0,
                "issues": [],
                "recommendations": []
            }

            # Generate issues and recommendations
            if not analysis["has_headline"]:
                analysis["issues"].append("Missing clear headline (H1)")
                analysis["recommendations"].append("Add a compelling headline that matches ad copy")

            if not analysis["has_form"]:
                analysis["issues"].append("No form found for lead capture")
                analysis["recommendations"].append("Add a lead capture form")

            if not analysis["has_cta_button"]:
                analysis["issues"].append("No clear call-to-action button")
                analysis["recommendations"].append("Add prominent CTA button")

            if not analysis["mobile_responsive"]:
                analysis["issues"].append("May not be mobile responsive")
                analysis["recommendations"].append("Ensure mobile responsiveness")

            if analysis["load_time"] > 3.0:
                analysis["issues"].append("Page load time too slow")
                analysis["recommendations"].append("Optimize page load time (target <3 seconds)")

            # Calculate optimization score
            analysis["optimization_score"] = self._calculate_landing_page_score(analysis)

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing landing page: {str(e)}")
            return {
                "url": url,
                "error": str(e),
                "optimization_score": 0.0
            }

    def _has_cta_button(self, soup: BeautifulSoup) -> bool:
        """Check if page has a CTA button."""
        buttons = soup.find_all(['button', 'a'], class_=lambda x: x and 'btn' in x.lower() if x else False)
        return len(buttons) > 0

    def _check_mobile_responsive(self, soup: BeautifulSoup) -> bool:
        """Check if page appears mobile responsive."""
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        return viewport is not None

    def _calculate_landing_page_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate landing page optimization score."""
        score = 100.0

        if not analysis["has_headline"]:
            score -= 20
        if not analysis["has_form"]:
            score -= 20
        if not analysis["has_cta_button"]:
            score -= 20
        if not analysis["mobile_responsive"]:
            score -= 20
        if analysis["load_time"] > 3.0:
            score -= 10

        return max(0.0, min(100.0, score))

    async def competitor_ads(
        self,
        keywords: List[str],
        investigation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Analyze competitor advertisements."""
        logger.info(f"Analyzing competitor ads for {len(keywords)} keywords")

        # In production, integrate with ad intelligence APIs
        competitor_results = {
            "keywords_analyzed": len(keywords),
            "competitor_ads_found": 0,
            "competitors": [],
            "common_ad_strategies": []
        }

        return competitor_results

    async def campaign_insights(
        self,
        campaign_data: Dict[str, Any],
        investigation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Campaign performance insights."""
        logger.info("Analyzing campaign performance")

        insights = {
            "campaign_id": campaign_data.get("campaign_id"),
            "impressions": campaign_data.get("impressions", 0),
            "clicks": campaign_data.get("clicks", 0),
            "conversions": campaign_data.get("conversions", 0),
            "cost": campaign_data.get("cost", 0.0),
            "ctr": 0.0,
            "conversion_rate": 0.0,
            "cpa": 0.0,
            "roas": 0.0,
            "quality_score_avg": campaign_data.get("quality_score_avg", 0.0),
            "recommendations": []
        }

        # Calculate metrics
        if insights["impressions"] > 0:
            insights["ctr"] = (insights["clicks"] / insights["impressions"]) * 100

        if insights["clicks"] > 0:
            insights["conversion_rate"] = (insights["conversions"] / insights["clicks"]) * 100

        if insights["conversions"] > 0:
            insights["cpa"] = insights["cost"] / insights["conversions"]

        revenue = campaign_data.get("revenue", 0.0)
        if insights["cost"] > 0:
            insights["roas"] = revenue / insights["cost"]

        # Generate recommendations
        if insights["ctr"] < 2.0:
            insights["recommendations"].append("CTR below 2% - improve ad copy and targeting")

        if insights["conversion_rate"] < 5.0:
            insights["recommendations"].append("Conversion rate below 5% - optimize landing pages")

        if insights["quality_score_avg"] < 7.0:
            insights["recommendations"].append("Quality score below 7 - improve ad relevance")

        if insights["roas"] < 4.0:
            insights["recommendations"].append("ROAS below 4x - review targeting and bidding strategy")

        return insights

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
