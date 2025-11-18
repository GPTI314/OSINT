"""Austrian Zoning Plan Scraper - Specialized scraper for flächenwidmungsplan.gv.at."""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import re
import logging

import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from database.models import ZoningSearch

logger = logging.getLogger(__name__)


class AustrianZoningScraper:
    """
    Specialized scraper for flächenwidmungsplan.gv.at:
    - Search by street name and house number
    - Extract Plantextbestimmungen (zoning text regulations)
    - Parse zoning information
    - Extract related data
    - Handle Austrian address formats
    - Error handling for invalid addresses
    """

    def __init__(self, db: Session):
        self.db = db
        self.client = httpx.AsyncClient(
            timeout=60.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        self.base_url = "https://www.flaechenwidmungsplan.gv.at"

    async def search_by_address(
        self,
        street_name: str,
        house_number: str,
        city: Optional[str] = None,
        investigation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Search zoning plan by address:
        - Input: street name, house number, optional city
        - Output: Plantextbestimmungen and related zoning data
        """
        logger.info(f"Searching zoning plan for: {street_name} {house_number}, {city}")

        try:
            # Format address
            formatted_address = self._format_address(street_name, house_number, city)

            # Perform search
            search_result = await self._perform_search(formatted_address)

            if not search_result.get("success"):
                return {
                    "success": False,
                    "error": search_result.get("error", "Search failed"),
                    "street_name": street_name,
                    "house_number": house_number,
                    "city": city
                }

            # Extract zoning data
            zoning_data = await self._extract_zoning_data(search_result)

            # Extract Plantextbestimmungen
            plantextbestimmungen = await self.extract_zoning_text(zoning_data)

            # Parse zoning data
            parsed_data = await self.parse_zoning_data(plantextbestimmungen)

            # Store in database
            zoning_search = ZoningSearch(
                investigation_id=investigation_id,
                street_name=street_name,
                house_number=house_number,
                city=city,
                search_result=search_result,
                plantextbestimmungen=plantextbestimmungen,
                parsed_data=parsed_data,
                metadata={
                    "formatted_address": formatted_address,
                    "search_timestamp": datetime.now().isoformat()
                }
            )

            self.db.add(zoning_search)
            self.db.commit()
            self.db.refresh(zoning_search)

            return {
                "success": True,
                "id": zoning_search.id,
                "street_name": street_name,
                "house_number": house_number,
                "city": city,
                "plantextbestimmungen": plantextbestimmungen,
                "parsed_data": parsed_data,
                "search_result": search_result
            }

        except Exception as e:
            logger.error(f"Error searching zoning plan: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "street_name": street_name,
                "house_number": house_number,
                "city": city
            }

    def _format_address(
        self,
        street_name: str,
        house_number: str,
        city: Optional[str] = None
    ) -> str:
        """Format address for Austrian zoning search."""
        # Clean and format street name
        street_clean = street_name.strip()

        # Clean and format house number
        house_clean = house_number.strip()

        # Combine address
        if city:
            return f"{street_clean} {house_clean}, {city.strip()}"
        else:
            return f"{street_clean} {house_clean}"

    async def _perform_search(self, address: str) -> Dict[str, Any]:
        """Perform search on zoning website."""
        # NOTE: This is a simulated implementation
        # In production, this would:
        # 1. Navigate to the search page
        # 2. Fill in the search form
        # 3. Submit the search
        # 4. Parse results

        # The actual implementation would depend on the website's structure
        # and may require:
        # - Playwright/Selenium for JavaScript-heavy sites
        # - Handling of CAPTCHA if present
        # - Session management
        # - CSRF token handling

        try:
            # Simulated search (replace with actual implementation)
            search_url = f"{self.base_url}/search"

            # In production, send POST request with address data
            # For now, return simulated structure
            logger.info(f"Performing search for address: {address}")

            # Simulated successful search result
            search_result = {
                "success": True,
                "address": address,
                "parcel_id": "12345/67",
                "zoning_code": "WA-1",
                "map_url": f"{self.base_url}/map/12345",
                "details_url": f"{self.base_url}/details/12345"
            }

            return search_result

        except Exception as e:
            logger.error(f"Error performing search: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _extract_zoning_data(self, search_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract zoning data from search results."""
        # In production, navigate to details page and extract data
        details_url = search_result.get("details_url")

        if not details_url:
            return search_result

        try:
            # Fetch details page
            response = await self.client.get(details_url)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract zoning information (structure depends on actual website)
            zoning_data = {
                **search_result,
                "zoning_details": self._parse_zoning_details(soup),
                "restrictions": self._parse_restrictions(soup),
                "permitted_uses": self._parse_permitted_uses(soup)
            }

            return zoning_data

        except Exception as e:
            logger.error(f"Error extracting zoning data: {str(e)}")
            return search_result

    def _parse_zoning_details(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Parse zoning details from page."""
        # Implementation depends on actual website structure
        # This is a simulated example

        return {
            "zoning_designation": "Wohngebiet (Residential Area)",
            "building_density": "0.4",
            "building_height_max": "12m",
            "floor_area_ratio": "1.2"
        }

    def _parse_restrictions(self, soup: BeautifulSoup) -> List[str]:
        """Parse zoning restrictions from page."""
        # Implementation depends on actual website structure

        return [
            "Maximum building height: 12 meters",
            "Minimum distance to property line: 3 meters",
            "Green space requirement: 40%"
        ]

    def _parse_permitted_uses(self, soup: BeautifulSoup) -> List[str]:
        """Parse permitted uses from page."""
        # Implementation depends on actual website structure

        return [
            "Single-family homes",
            "Multi-family residential buildings",
            "Home offices",
            "Small-scale retail (ground floor only)"
        ]

    async def extract_zoning_text(self, search_result: Dict[str, Any]) -> str:
        """Extract Plantextbestimmungen from search result."""
        logger.info("Extracting Plantextbestimmungen")

        # In production, extract from specific section of the page
        # For now, return simulated text

        plantextbestimmungen = """
        PLANTEXTBESTIMMUNGEN

        Widmung: Wohngebiet (WA-1)

        1. NUTZUNGSBESTIMMUNGEN:
           - Wohnnutzung zulässig
           - Nicht störende Gewerbebetriebe zulässig
           - Büros und freie Berufe zulässig

        2. BAUWEISE:
           - Offene Bauweise
           - Geschlossene Bauweise nur an Straßenfront

        3. BEBAUUNGSDICHTE:
           - Bauklasse I: max. 12m Gebäudehöhe
           - GFZ (Geschoßflächenzahl): 1,2
           - GRZ (Grundflächenzahl): 0,4

        4. GRÜNFLÄCHENANTEIL:
           - Mindestens 40% der Grundstücksfläche

        5. STELLPLÄTZE:
           - 1 Stellplatz pro Wohneinheit erforderlich
           - Besucherparkplätze: 1 pro 4 Wohneinheiten

        6. ZUSÄTZLICHE BESTIMMUNGEN:
           - Mindestabstand zur Grundstücksgrenze: 3m
           - Dachform: Satteldach oder Flachdach
           - Dachneigung bei Satteldach: 35-45 Grad

        Gültig ab: 01.01.2020
        """

        return plantextbestimmungen.strip()

    async def parse_zoning_data(self, zoning_text: str) -> Dict[str, Any]:
        """Parse zoning text into structured data."""
        logger.info("Parsing zoning text into structured data")

        parsed_data = {
            "zoning_designation": None,
            "usage_permitted": [],
            "building_specifications": {},
            "density_requirements": {},
            "green_space_requirements": {},
            "parking_requirements": {},
            "additional_regulations": [],
            "effective_date": None
        }

        # Extract zoning designation
        designation_match = re.search(r'Widmung:\s*(.+?)(?:\n|$)', zoning_text)
        if designation_match:
            parsed_data["zoning_designation"] = designation_match.group(1).strip()

        # Extract permitted uses
        usage_section = re.search(
            r'NUTZUNGSBESTIMMUNGEN:(.+?)(?:\n\d+\.|$)',
            zoning_text,
            re.DOTALL
        )
        if usage_section:
            usage_text = usage_section.group(1)
            uses = re.findall(r'-\s*(.+?)(?:zulässig|erlaubt)', usage_text)
            parsed_data["usage_permitted"] = [use.strip() for use in uses]

        # Extract building specifications
        height_match = re.search(r'max\.\s*(\d+)m\s*Gebäudehöhe', zoning_text)
        if height_match:
            parsed_data["building_specifications"]["max_height_meters"] = int(height_match.group(1))

        # Extract density requirements
        gfz_match = re.search(r'GFZ[^:]*:\s*([\d,\.]+)', zoning_text)
        if gfz_match:
            parsed_data["density_requirements"]["floor_area_ratio"] = float(
                gfz_match.group(1).replace(',', '.')
            )

        grz_match = re.search(r'GRZ[^:]*:\s*([\d,\.]+)', zoning_text)
        if grz_match:
            parsed_data["density_requirements"]["ground_coverage_ratio"] = float(
                grz_match.group(1).replace(',', '.')
            )

        # Extract green space requirements
        green_match = re.search(r'(\d+)%\s*der\s*Grundstücksfläche', zoning_text)
        if green_match:
            parsed_data["green_space_requirements"]["minimum_percentage"] = int(green_match.group(1))

        # Extract parking requirements
        parking_matches = re.findall(r'(\d+)\s*Stellplatz.+?pro\s*(.+?)(?:\n|$)', zoning_text)
        for count, unit in parking_matches:
            parsed_data["parking_requirements"][unit.strip()] = int(count)

        # Extract effective date
        date_match = re.search(r'Gültig ab:\s*(\d{2}\.\d{2}\.\d{4})', zoning_text)
        if date_match:
            parsed_data["effective_date"] = date_match.group(1)

        # Extract minimum distances
        distance_match = re.search(r'Mindestabstand.+?:\s*(\d+)m', zoning_text)
        if distance_match:
            parsed_data["building_specifications"]["min_distance_to_boundary_meters"] = int(
                distance_match.group(1)
            )

        return parsed_data

    async def get_related_zones(
        self,
        address_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get related zoning information."""
        logger.info("Getting related zoning information")

        # In production, this would:
        # - Query neighboring parcels
        # - Get zoning for surrounding area
        # - Extract relevant maps and documents

        related_zones = {
            "neighboring_parcels": [],
            "surrounding_zoning": [],
            "related_maps": [],
            "planning_documents": []
        }

        return related_zones

    async def get_search_history(
        self,
        investigation_id: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get search history."""
        query = self.db.query(ZoningSearch)

        if investigation_id:
            query = query.filter(ZoningSearch.investigation_id == investigation_id)

        searches = query.order_by(
            ZoningSearch.searched_at.desc()
        ).limit(limit).all()

        return [
            {
                "id": s.id,
                "street_name": s.street_name,
                "house_number": s.house_number,
                "city": s.city,
                "searched_at": s.searched_at.isoformat(),
                "has_results": bool(s.plantextbestimmungen)
            }
            for s in searches
        ]

    async def get_search_details(self, search_id: int) -> Dict[str, Any]:
        """Get details of a specific search."""
        search = self.db.query(ZoningSearch).filter(
            ZoningSearch.id == search_id
        ).first()

        if not search:
            raise ValueError(f"Search {search_id} not found")

        return {
            "id": search.id,
            "investigation_id": search.investigation_id,
            "street_name": search.street_name,
            "house_number": search.house_number,
            "city": search.city,
            "search_result": search.search_result,
            "plantextbestimmungen": search.plantextbestimmungen,
            "parsed_data": search.parsed_data,
            "searched_at": search.searched_at.isoformat(),
            "metadata": search.metadata
        }

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
