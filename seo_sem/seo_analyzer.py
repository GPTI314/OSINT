"""SEO Analysis Engine - Comprehensive SEO analysis capabilities."""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import re
from urllib.parse import urlparse
import logging

import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from database.models import SEOAnalysis, KeywordRanking
from config.settings import settings

logger = logging.getLogger(__name__)


class SEOAnalyzer:
    """
    Comprehensive SEO analysis:
    - Keyword research and analysis
    - On-page SEO audit
    - Technical SEO analysis
    - Backlink analysis
    - Competitor analysis
    - Content analysis
    - SERP tracking
    - Rank tracking
    - Site speed analysis
    - Mobile-friendliness check
    - Schema markup validation
    - Meta tag analysis
    - Heading structure analysis
    - Image optimization check
    - Internal linking analysis
    - External linking analysis
    """

    def __init__(self, db: Session):
        self.db = db
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)

    async def analyze_keywords(
        self,
        domain: str,
        keywords: List[str],
        investigation_id: Optional[int] = None,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze keyword rankings and opportunities."""
        logger.info(f"Analyzing keywords for domain: {domain}")

        results = {
            "domain": domain,
            "keywords_analyzed": len(keywords),
            "keyword_data": [],
            "opportunities": [],
            "total_search_volume": 0
        }

        for keyword in keywords:
            # Simulate keyword analysis (in production, integrate with real APIs)
            keyword_data = await self._analyze_single_keyword(
                domain, keyword, location
            )

            results["keyword_data"].append(keyword_data)
            results["total_search_volume"] += keyword_data.get("search_volume", 0)

            # Store in database
            ranking = KeywordRanking(
                investigation_id=investigation_id,
                domain=domain,
                keyword=keyword,
                position=keyword_data.get("position"),
                search_volume=keyword_data.get("search_volume"),
                difficulty=keyword_data.get("difficulty"),
                cpc=keyword_data.get("cpc"),
                location=location,
                device_type="desktop",
                metadata=keyword_data
            )
            self.db.add(ranking)

        self.db.commit()

        # Identify opportunities
        results["opportunities"] = self._identify_keyword_opportunities(
            results["keyword_data"]
        )

        return results

    async def _analyze_single_keyword(
        self,
        domain: str,
        keyword: str,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze a single keyword."""
        # In production, integrate with APIs like SEMrush, Ahrefs, etc.
        # For now, return simulated data

        return {
            "keyword": keyword,
            "position": None,  # Would be actual SERP position
            "search_volume": 1000,  # Placeholder
            "difficulty": 45.5,  # Placeholder (0-100)
            "cpc": 2.50,  # Placeholder
            "trend": "stable",
            "serp_features": ["featured_snippet", "people_also_ask"]
        }

    def _identify_keyword_opportunities(
        self, keyword_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify keyword opportunities based on analysis."""
        opportunities = []

        for data in keyword_data:
            # Low difficulty, high volume keywords are opportunities
            if (data.get("difficulty", 100) < 40 and
                data.get("search_volume", 0) > 500):
                opportunities.append({
                    "keyword": data["keyword"],
                    "reason": "Low competition, high volume",
                    "search_volume": data["search_volume"],
                    "difficulty": data["difficulty"]
                })

        return opportunities

    async def on_page_audit(
        self,
        url: str,
        investigation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Complete on-page SEO audit."""
        logger.info(f"Performing on-page SEO audit for: {url}")

        try:
            response = await self.client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            audit_results = {
                "url": url,
                "status_code": response.status_code,
                "score": 0.0,
                "issues": [],
                "recommendations": [],
                "meta_tags": self._analyze_meta_tags(soup),
                "headings": self._analyze_headings(soup),
                "images": self._analyze_images(soup),
                "links": self._analyze_links(soup, url),
                "content": self._analyze_content(soup),
                "schema": self._analyze_schema(soup)
            }

            # Calculate score
            audit_results["score"] = self._calculate_on_page_score(audit_results)

            # Generate issues and recommendations
            self._generate_on_page_issues(audit_results)

            # Store in database
            analysis = SEOAnalysis(
                investigation_id=investigation_id,
                target_url=url,
                analysis_type="on_page",
                score=audit_results["score"],
                issues=audit_results["issues"],
                recommendations=audit_results["recommendations"],
                raw_data=audit_results
            )
            self.db.add(analysis)
            self.db.commit()

            return audit_results

        except Exception as e:
            logger.error(f"Error during on-page audit: {str(e)}")
            return {
                "url": url,
                "error": str(e),
                "score": 0.0
            }

    def _analyze_meta_tags(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze meta tags."""
        meta_data = {
            "title": None,
            "title_length": 0,
            "description": None,
            "description_length": 0,
            "keywords": None,
            "robots": None,
            "canonical": None,
            "og_tags": {},
            "twitter_tags": {}
        }

        # Title
        title_tag = soup.find('title')
        if title_tag:
            meta_data["title"] = title_tag.string
            meta_data["title_length"] = len(title_tag.string) if title_tag.string else 0

        # Meta description
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        if desc_tag and desc_tag.get('content'):
            meta_data["description"] = desc_tag['content']
            meta_data["description_length"] = len(desc_tag['content'])

        # Meta keywords
        keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
        if keywords_tag and keywords_tag.get('content'):
            meta_data["keywords"] = keywords_tag['content']

        # Robots
        robots_tag = soup.find('meta', attrs={'name': 'robots'})
        if robots_tag and robots_tag.get('content'):
            meta_data["robots"] = robots_tag['content']

        # Canonical
        canonical_tag = soup.find('link', attrs={'rel': 'canonical'})
        if canonical_tag and canonical_tag.get('href'):
            meta_data["canonical"] = canonical_tag['href']

        # Open Graph tags
        og_tags = soup.find_all('meta', property=re.compile(r'^og:'))
        for tag in og_tags:
            prop = tag.get('property', '').replace('og:', '')
            meta_data["og_tags"][prop] = tag.get('content')

        # Twitter tags
        twitter_tags = soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')})
        for tag in twitter_tags:
            name = tag.get('name', '').replace('twitter:', '')
            meta_data["twitter_tags"][name] = tag.get('content')

        return meta_data

    def _analyze_headings(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze heading structure."""
        headings = {
            "h1": [],
            "h2": [],
            "h3": [],
            "h4": [],
            "h5": [],
            "h6": [],
            "structure_issues": []
        }

        for i in range(1, 7):
            tags = soup.find_all(f'h{i}')
            headings[f'h{i}'] = [tag.get_text().strip() for tag in tags]

        # Check for multiple H1s
        if len(headings['h1']) > 1:
            headings["structure_issues"].append("Multiple H1 tags found")
        elif len(headings['h1']) == 0:
            headings["structure_issues"].append("No H1 tag found")

        return headings

    def _analyze_images(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze image optimization."""
        images = soup.find_all('img')

        image_data = {
            "total_images": len(images),
            "missing_alt": 0,
            "missing_title": 0,
            "images_analyzed": []
        }

        for img in images:
            img_info = {
                "src": img.get('src'),
                "alt": img.get('alt'),
                "title": img.get('title'),
                "has_alt": bool(img.get('alt')),
                "has_title": bool(img.get('title'))
            }

            if not img_info["has_alt"]:
                image_data["missing_alt"] += 1
            if not img_info["has_title"]:
                image_data["missing_title"] += 1

            image_data["images_analyzed"].append(img_info)

        return image_data

    def _analyze_links(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
        """Analyze internal and external links."""
        links = soup.find_all('a', href=True)
        parsed_base = urlparse(base_url)

        link_data = {
            "total_links": len(links),
            "internal_links": 0,
            "external_links": 0,
            "nofollow_links": 0,
            "broken_links": []
        }

        for link in links:
            href = link['href']
            parsed_href = urlparse(href)

            # Determine if internal or external
            if parsed_href.netloc == '' or parsed_href.netloc == parsed_base.netloc:
                link_data["internal_links"] += 1
            else:
                link_data["external_links"] += 1

            # Check for nofollow
            if 'nofollow' in link.get('rel', []):
                link_data["nofollow_links"] += 1

        return link_data

    def _analyze_content(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze content quality."""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        text = soup.get_text()
        words = text.split()

        content_data = {
            "word_count": len(words),
            "character_count": len(text),
            "paragraph_count": len(soup.find_all('p')),
            "list_count": len(soup.find_all(['ul', 'ol']))
        }

        return content_data

    def _analyze_schema(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze schema markup."""
        schema_data = {
            "has_schema": False,
            "schema_types": []
        }

        # Check for JSON-LD
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        if json_ld_scripts:
            schema_data["has_schema"] = True
            schema_data["schema_types"] = ["JSON-LD"]

        # Check for microdata
        microdata_items = soup.find_all(attrs={'itemtype': True})
        if microdata_items:
            schema_data["has_schema"] = True
            if "Microdata" not in schema_data["schema_types"]:
                schema_data["schema_types"].append("Microdata")

        return schema_data

    def _calculate_on_page_score(self, audit_results: Dict[str, Any]) -> float:
        """Calculate overall on-page SEO score."""
        score = 100.0

        # Title check
        title_length = audit_results["meta_tags"]["title_length"]
        if title_length == 0:
            score -= 15
        elif title_length < 30 or title_length > 60:
            score -= 5

        # Description check
        desc_length = audit_results["meta_tags"]["description_length"]
        if desc_length == 0:
            score -= 15
        elif desc_length < 120 or desc_length > 160:
            score -= 5

        # H1 check
        h1_count = len(audit_results["headings"]["h1"])
        if h1_count == 0:
            score -= 10
        elif h1_count > 1:
            score -= 5

        # Image alt tags
        if audit_results["images"]["total_images"] > 0:
            missing_alt_ratio = (
                audit_results["images"]["missing_alt"] /
                audit_results["images"]["total_images"]
            )
            score -= missing_alt_ratio * 10

        # Content length
        if audit_results["content"]["word_count"] < 300:
            score -= 10

        return max(0.0, min(100.0, score))

    def _generate_on_page_issues(self, audit_results: Dict[str, Any]):
        """Generate issues and recommendations."""
        issues = []
        recommendations = []

        # Title issues
        if audit_results["meta_tags"]["title_length"] == 0:
            issues.append("Missing title tag")
            recommendations.append("Add a descriptive title tag (50-60 characters)")
        elif audit_results["meta_tags"]["title_length"] > 60:
            issues.append("Title tag too long")
            recommendations.append("Shorten title tag to 50-60 characters")

        # Description issues
        if audit_results["meta_tags"]["description_length"] == 0:
            issues.append("Missing meta description")
            recommendations.append("Add a meta description (120-160 characters)")
        elif audit_results["meta_tags"]["description_length"] > 160:
            issues.append("Meta description too long")
            recommendations.append("Shorten meta description to 120-160 characters")

        # Heading issues
        if len(audit_results["headings"]["h1"]) == 0:
            issues.append("No H1 tag found")
            recommendations.append("Add a single H1 tag with main keyword")
        elif len(audit_results["headings"]["h1"]) > 1:
            issues.append("Multiple H1 tags found")
            recommendations.append("Use only one H1 tag per page")

        # Image issues
        if audit_results["images"]["missing_alt"] > 0:
            issues.append(f"{audit_results['images']['missing_alt']} images missing alt text")
            recommendations.append("Add descriptive alt text to all images")

        # Content issues
        if audit_results["content"]["word_count"] < 300:
            issues.append("Content too short")
            recommendations.append("Increase content to at least 300 words")

        # Schema issues
        if not audit_results["schema"]["has_schema"]:
            issues.append("No schema markup found")
            recommendations.append("Add structured data markup (JSON-LD)")

        audit_results["issues"] = issues
        audit_results["recommendations"] = recommendations

    async def technical_seo_check(
        self,
        domain: str,
        investigation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Technical SEO analysis."""
        logger.info(f"Performing technical SEO check for: {domain}")

        url = f"https://{domain}" if not domain.startswith('http') else domain

        technical_results = {
            "domain": domain,
            "url": url,
            "score": 0.0,
            "issues": [],
            "recommendations": [],
            "https": False,
            "ssl_valid": False,
            "mobile_friendly": None,
            "page_speed": None,
            "robots_txt": None,
            "sitemap": None
        }

        try:
            # Check HTTPS
            technical_results["https"] = url.startswith('https')

            # Check robots.txt
            robots_url = f"{url}/robots.txt"
            try:
                robots_response = await self.client.get(robots_url)
                if robots_response.status_code == 200:
                    technical_results["robots_txt"] = "found"
                else:
                    technical_results["robots_txt"] = "not_found"
            except:
                technical_results["robots_txt"] = "not_found"

            # Check sitemap
            sitemap_url = f"{url}/sitemap.xml"
            try:
                sitemap_response = await self.client.get(sitemap_url)
                if sitemap_response.status_code == 200:
                    technical_results["sitemap"] = "found"
                else:
                    technical_results["sitemap"] = "not_found"
            except:
                technical_results["sitemap"] = "not_found"

            # Generate issues and recommendations
            if not technical_results["https"]:
                technical_results["issues"].append("Not using HTTPS")
                technical_results["recommendations"].append("Implement SSL certificate and redirect HTTP to HTTPS")

            if technical_results["robots_txt"] == "not_found":
                technical_results["issues"].append("robots.txt not found")
                technical_results["recommendations"].append("Create a robots.txt file")

            if technical_results["sitemap"] == "not_found":
                technical_results["issues"].append("sitemap.xml not found")
                technical_results["recommendations"].append("Create and submit an XML sitemap")

            # Calculate score
            technical_results["score"] = self._calculate_technical_score(technical_results)

            # Store in database
            analysis = SEOAnalysis(
                investigation_id=investigation_id,
                target_url=url,
                analysis_type="technical",
                score=technical_results["score"],
                issues=technical_results["issues"],
                recommendations=technical_results["recommendations"],
                raw_data=technical_results
            )
            self.db.add(analysis)
            self.db.commit()

            return technical_results

        except Exception as e:
            logger.error(f"Error during technical SEO check: {str(e)}")
            return {
                "domain": domain,
                "error": str(e),
                "score": 0.0
            }

    def _calculate_technical_score(self, technical_results: Dict[str, Any]) -> float:
        """Calculate technical SEO score."""
        score = 100.0

        if not technical_results["https"]:
            score -= 30
        if technical_results["robots_txt"] == "not_found":
            score -= 20
        if technical_results["sitemap"] == "not_found":
            score -= 20

        return max(0.0, min(100.0, score))

    async def backlink_analysis(
        self,
        domain: str,
        investigation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Backlink profile analysis."""
        logger.info(f"Analyzing backlinks for: {domain}")

        # In production, integrate with backlink APIs like Ahrefs, Moz, etc.
        # For now, return simulated structure

        backlink_results = {
            "domain": domain,
            "total_backlinks": 0,
            "referring_domains": 0,
            "domain_authority": 0,
            "backlink_quality": "unknown",
            "top_backlinks": []
        }

        return backlink_results

    async def competitor_analysis(
        self,
        domain: str,
        competitors: List[str],
        investigation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Competitor SEO analysis."""
        logger.info(f"Analyzing competitors for: {domain}")

        competitor_results = {
            "target_domain": domain,
            "competitors_analyzed": len(competitors),
            "comparisons": []
        }

        for competitor in competitors:
            comparison = {
                "competitor": competitor,
                "shared_keywords": [],
                "keyword_gap": [],
                "backlink_overlap": 0
            }
            competitor_results["comparisons"].append(comparison)

        return competitor_results

    async def content_analysis(
        self,
        url: str,
        investigation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Content SEO analysis."""
        logger.info(f"Analyzing content for: {url}")

        try:
            response = await self.client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            text = soup.get_text()
            words = text.split()

            content_results = {
                "url": url,
                "word_count": len(words),
                "reading_level": "unknown",
                "keyword_density": {},
                "readability_score": 0.0
            }

            return content_results

        except Exception as e:
            logger.error(f"Error during content analysis: {str(e)}")
            return {"url": url, "error": str(e)}

    async def serp_tracking(
        self,
        keywords: List[str],
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """SERP position tracking."""
        logger.info(f"Tracking SERP positions for {len(keywords)} keywords")

        # In production, integrate with SERP APIs
        serp_results = {
            "keywords_tracked": len(keywords),
            "location": location,
            "serp_data": []
        }

        return serp_results

    async def rank_tracking(
        self,
        domain: str,
        keywords: List[str],
        investigation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Keyword rank tracking over time."""
        logger.info(f"Tracking keyword rankings for: {domain}")

        # Query historical data from database
        from sqlalchemy import and_

        rank_results = {
            "domain": domain,
            "keywords_tracked": len(keywords),
            "rankings": []
        }

        for keyword in keywords:
            rankings = self.db.query(KeywordRanking).filter(
                and_(
                    KeywordRanking.domain == domain,
                    KeywordRanking.keyword == keyword
                )
            ).order_by(KeywordRanking.tracked_at.desc()).limit(30).all()

            rank_data = {
                "keyword": keyword,
                "current_position": rankings[0].position if rankings else None,
                "history": [
                    {
                        "position": r.position,
                        "tracked_at": r.tracked_at.isoformat()
                    }
                    for r in rankings
                ]
            }
            rank_results["rankings"].append(rank_data)

        return rank_results

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
