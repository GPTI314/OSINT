"""LinkedIn Data Extraction Engine - Profile and company data extraction."""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import re
import logging

import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from database.models import LinkedInProfile, LinkedInCompany, LinkedInVertical, VerticalFilter
from config.settings import settings

logger = logging.getLogger(__name__)


class LinkedInExtractor:
    """
    LinkedIn data extraction and vertical creation:
    - Profile extraction
    - Company page extraction
    - Employee list extraction
    - Connection network analysis
    - Post and content extraction
    - Skill extraction
    - Experience extraction
    - Education extraction
    - Recommendation extraction
    - Vertical creation (industry, location, company size, etc.)
    - List management and filtering
    """

    def __init__(self, db: Session):
        self.db = db
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

    async def extract_profile(
        self,
        profile_url: str,
        investigation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Extract complete LinkedIn profile."""
        logger.info(f"Extracting LinkedIn profile: {profile_url}")

        try:
            # Check if profile already exists
            existing_profile = self.db.query(LinkedInProfile).filter(
                LinkedInProfile.profile_url == profile_url
            ).first()

            if existing_profile:
                logger.info(f"Profile already exists in database: {profile_url}")
                return self._profile_to_dict(existing_profile)

            # In production, this would use LinkedIn API or scraping with authentication
            # For now, return simulated structure
            profile_data = await self._scrape_profile(profile_url)

            # Store in database
            profile = LinkedInProfile(
                investigation_id=investigation_id,
                profile_url=profile_url,
                full_name=profile_data.get("full_name"),
                headline=profile_data.get("headline"),
                location=profile_data.get("location"),
                industry=profile_data.get("industry"),
                current_company=profile_data.get("current_company"),
                current_position=profile_data.get("current_position"),
                company_size=profile_data.get("company_size"),
                experience=profile_data.get("experience", []),
                education=profile_data.get("education", []),
                skills=profile_data.get("skills", []),
                connections_count=profile_data.get("connections_count"),
                recommendations_count=profile_data.get("recommendations_count"),
                posts_count=profile_data.get("posts_count"),
                metadata=profile_data
            )

            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)

            return self._profile_to_dict(profile)

        except Exception as e:
            logger.error(f"Error extracting profile: {str(e)}")
            return {
                "profile_url": profile_url,
                "error": str(e)
            }

    async def _scrape_profile(self, profile_url: str) -> Dict[str, Any]:
        """Scrape LinkedIn profile data."""
        # IMPORTANT: In production, use LinkedIn API with proper authentication
        # Scraping LinkedIn without permission may violate their Terms of Service

        # Simulated profile data structure
        profile_data = {
            "full_name": "John Doe",
            "headline": "Software Engineer at Tech Company",
            "location": "San Francisco Bay Area",
            "industry": "Technology",
            "current_company": "Tech Company",
            "current_position": "Software Engineer",
            "company_size": "1001-5000",
            "connections_count": 500,
            "recommendations_count": 15,
            "posts_count": 42,
            "experience": [
                {
                    "company": "Tech Company",
                    "title": "Software Engineer",
                    "start_date": "2020-01",
                    "end_date": None,
                    "duration": "4 years",
                    "description": "Working on backend systems"
                }
            ],
            "education": [
                {
                    "school": "University Name",
                    "degree": "Bachelor of Science",
                    "field": "Computer Science",
                    "start_year": 2014,
                    "end_year": 2018
                }
            ],
            "skills": [
                "Python", "JavaScript", "AWS", "Docker", "Kubernetes"
            ]
        }

        return profile_data

    def _profile_to_dict(self, profile: LinkedInProfile) -> Dict[str, Any]:
        """Convert profile model to dictionary."""
        return {
            "id": profile.id,
            "profile_url": profile.profile_url,
            "full_name": profile.full_name,
            "headline": profile.headline,
            "location": profile.location,
            "industry": profile.industry,
            "current_company": profile.current_company,
            "current_position": profile.current_position,
            "company_size": profile.company_size,
            "experience": profile.experience,
            "education": profile.education,
            "skills": profile.skills,
            "connections_count": profile.connections_count,
            "recommendations_count": profile.recommendations_count,
            "posts_count": profile.posts_count,
            "extracted_at": profile.extracted_at.isoformat()
        }

    async def extract_company(
        self,
        company_url: str,
        investigation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Extract company page data."""
        logger.info(f"Extracting LinkedIn company: {company_url}")

        try:
            # Check if company already exists
            existing_company = self.db.query(LinkedInCompany).filter(
                LinkedInCompany.company_url == company_url
            ).first()

            if existing_company:
                logger.info(f"Company already exists in database: {company_url}")
                return self._company_to_dict(existing_company)

            # In production, use LinkedIn API
            company_data = await self._scrape_company(company_url)

            # Store in database
            company = LinkedInCompany(
                investigation_id=investigation_id,
                company_url=company_url,
                company_name=company_data.get("company_name"),
                industry=company_data.get("industry"),
                company_size=company_data.get("company_size"),
                headquarters=company_data.get("headquarters"),
                website=company_data.get("website"),
                description=company_data.get("description"),
                employee_count=company_data.get("employee_count"),
                followers_count=company_data.get("followers_count"),
                specialties=company_data.get("specialties", []),
                metadata=company_data
            )

            self.db.add(company)
            self.db.commit()
            self.db.refresh(company)

            return self._company_to_dict(company)

        except Exception as e:
            logger.error(f"Error extracting company: {str(e)}")
            return {
                "company_url": company_url,
                "error": str(e)
            }

    async def _scrape_company(self, company_url: str) -> Dict[str, Any]:
        """Scrape LinkedIn company data."""
        # Simulated company data structure
        company_data = {
            "company_name": "Tech Company Inc.",
            "industry": "Technology",
            "company_size": "1001-5000 employees",
            "headquarters": "San Francisco, CA",
            "website": "https://www.techcompany.com",
            "description": "Leading technology company specializing in software solutions",
            "employee_count": 2500,
            "followers_count": 50000,
            "specialties": [
                "Software Development",
                "Cloud Computing",
                "Artificial Intelligence",
                "Data Analytics"
            ]
        }

        return company_data

    def _company_to_dict(self, company: LinkedInCompany) -> Dict[str, Any]:
        """Convert company model to dictionary."""
        return {
            "id": company.id,
            "company_url": company.company_url,
            "company_name": company.company_name,
            "industry": company.industry,
            "company_size": company.company_size,
            "headquarters": company.headquarters,
            "website": company.website,
            "description": company.description,
            "employee_count": company.employee_count,
            "followers_count": company.followers_count,
            "specialties": company.specialties,
            "extracted_at": company.extracted_at.isoformat()
        }

    async def extract_employees(
        self,
        company_url: str,
        filters: Optional[Dict[str, Any]] = None,
        investigation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Extract employee list with filters."""
        logger.info(f"Extracting employees for company: {company_url}")

        # In production, use LinkedIn API with proper filters
        employee_data = {
            "company_url": company_url,
            "total_employees": 0,
            "employees": [],
            "filters_applied": filters or {}
        }

        # Simulated employee list (would be actual API calls)
        simulated_employees = [
            {
                "profile_url": "https://linkedin.com/in/employee1",
                "name": "Jane Smith",
                "position": "Senior Engineer",
                "location": "San Francisco, CA"
            },
            {
                "profile_url": "https://linkedin.com/in/employee2",
                "name": "Bob Johnson",
                "position": "Product Manager",
                "location": "New York, NY"
            }
        ]

        # Apply filters if provided
        if filters:
            simulated_employees = self._apply_employee_filters(
                simulated_employees, filters
            )

        employee_data["employees"] = simulated_employees
        employee_data["total_employees"] = len(simulated_employees)

        return employee_data

    def _apply_employee_filters(
        self,
        employees: List[Dict[str, Any]],
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply filters to employee list."""
        filtered = employees

        if "location" in filters:
            location_filter = filters["location"].lower()
            filtered = [
                e for e in filtered
                if location_filter in e.get("location", "").lower()
            ]

        if "position" in filters:
            position_filter = filters["position"].lower()
            filtered = [
                e for e in filtered
                if position_filter in e.get("position", "").lower()
            ]

        return filtered

    async def create_vertical(
        self,
        criteria: Dict[str, Any],
        investigation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create vertical from LinkedIn data:
        - Industry vertical
        - Geographic vertical
        - Company size vertical
        - Job title vertical
        - Skill-based vertical
        - Experience level vertical
        """
        logger.info(f"Creating LinkedIn vertical with criteria: {criteria}")

        vertical_name = criteria.get("name", "Unnamed Vertical")
        vertical_type = criteria.get("type", "custom")

        # Query profiles and companies based on criteria
        profile_ids, company_ids = await self._query_by_criteria(criteria)

        # Create vertical
        vertical = LinkedInVertical(
            investigation_id=investigation_id,
            vertical_name=vertical_name,
            vertical_type=vertical_type,
            criteria=criteria,
            profile_ids=profile_ids,
            company_ids=company_ids,
            metadata={
                "total_profiles": len(profile_ids),
                "total_companies": len(company_ids)
            }
        )

        self.db.add(vertical)
        self.db.commit()
        self.db.refresh(vertical)

        return self._vertical_to_dict(vertical)

    async def _query_by_criteria(
        self,
        criteria: Dict[str, Any]
    ) -> tuple:
        """Query profiles and companies by criteria."""
        from sqlalchemy import and_, or_

        profile_query = self.db.query(LinkedInProfile)
        company_query = self.db.query(LinkedInCompany)

        # Apply industry filter
        if "industry" in criteria:
            industry = criteria["industry"]
            profile_query = profile_query.filter(
                LinkedInProfile.industry == industry
            )
            company_query = company_query.filter(
                LinkedInCompany.industry == industry
            )

        # Apply location filter
        if "location" in criteria:
            location = criteria["location"]
            profile_query = profile_query.filter(
                LinkedInProfile.location.ilike(f"%{location}%")
            )
            company_query = company_query.filter(
                LinkedInCompany.headquarters.ilike(f"%{location}%")
            )

        # Apply company size filter
        if "company_size" in criteria:
            company_size = criteria["company_size"]
            profile_query = profile_query.filter(
                LinkedInProfile.company_size == company_size
            )
            company_query = company_query.filter(
                LinkedInCompany.company_size.ilike(f"%{company_size}%")
            )

        # Apply job title filter
        if "job_title" in criteria:
            job_title = criteria["job_title"]
            profile_query = profile_query.filter(
                LinkedInProfile.current_position.ilike(f"%{job_title}%")
            )

        # Execute queries
        profiles = profile_query.all()
        companies = company_query.all()

        profile_ids = [p.id for p in profiles]
        company_ids = [c.id for c in companies]

        return profile_ids, company_ids

    def _vertical_to_dict(self, vertical: LinkedInVertical) -> Dict[str, Any]:
        """Convert vertical model to dictionary."""
        return {
            "id": vertical.id,
            "vertical_name": vertical.vertical_name,
            "vertical_type": vertical.vertical_type,
            "criteria": vertical.criteria,
            "profile_ids": vertical.profile_ids,
            "company_ids": vertical.company_ids,
            "created_at": vertical.created_at.isoformat(),
            "updated_at": vertical.updated_at.isoformat(),
            "metadata": vertical.metadata
        }

    async def filter_vertical(
        self,
        vertical_id: int,
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Filter and refine vertical."""
        logger.info(f"Filtering vertical {vertical_id} with filters: {filters}")

        vertical = self.db.query(LinkedInVertical).filter(
            LinkedInVertical.id == vertical_id
        ).first()

        if not vertical:
            raise ValueError(f"Vertical {vertical_id} not found")

        # Apply additional filters to existing vertical
        filtered_profile_ids = await self._apply_vertical_filters(
            vertical.profile_ids, filters
        )

        # Update vertical
        vertical.profile_ids = filtered_profile_ids
        vertical.metadata["total_profiles"] = len(filtered_profile_ids)
        vertical.metadata["last_filtered"] = datetime.now().isoformat()
        vertical.updated_at = datetime.now()

        # Record filter applied
        filter_record = VerticalFilter(
            vertical_id=vertical_id,
            filter_type=filters.get("type", "custom"),
            filter_value=str(filters),
            metadata=filters
        )
        self.db.add(filter_record)

        self.db.commit()
        self.db.refresh(vertical)

        return self._vertical_to_dict(vertical)

    async def _apply_vertical_filters(
        self,
        profile_ids: List[int],
        filters: Dict[str, Any]
    ) -> List[int]:
        """Apply filters to profile IDs."""
        if not profile_ids:
            return []

        from sqlalchemy import and_

        query = self.db.query(LinkedInProfile).filter(
            LinkedInProfile.id.in_(profile_ids)
        )

        # Apply filters
        if "min_connections" in filters:
            query = query.filter(
                LinkedInProfile.connections_count >= filters["min_connections"]
            )

        if "skills" in filters:
            # Filter by skills (profiles must have at least one of the specified skills)
            skills = filters["skills"]
            # This is a simplified check - in production, use JSON operators
            for skill in skills:
                query = query.filter(
                    LinkedInProfile.skills.contains([skill])
                )

        filtered_profiles = query.all()
        return [p.id for p in filtered_profiles]

    async def export_vertical(
        self,
        vertical_id: int,
        format: str = 'json'
    ) -> Dict[str, Any]:
        """Export vertical data."""
        logger.info(f"Exporting vertical {vertical_id} as {format}")

        vertical = self.db.query(LinkedInVertical).filter(
            LinkedInVertical.id == vertical_id
        ).first()

        if not vertical:
            raise ValueError(f"Vertical {vertical_id} not found")

        # Get full profile and company data
        profiles = self.db.query(LinkedInProfile).filter(
            LinkedInProfile.id.in_(vertical.profile_ids)
        ).all() if vertical.profile_ids else []

        companies = self.db.query(LinkedInCompany).filter(
            LinkedInCompany.id.in_(vertical.company_ids)
        ).all() if vertical.company_ids else []

        export_data = {
            "vertical": self._vertical_to_dict(vertical),
            "profiles": [self._profile_to_dict(p) for p in profiles],
            "companies": [self._company_to_dict(c) for c in companies]
        }

        if format == 'csv':
            # Convert to CSV format (simplified)
            export_data["format"] = "csv"
            export_data["csv_data"] = self._convert_to_csv(export_data)
        elif format == 'excel':
            # Convert to Excel format
            export_data["format"] = "excel"
        else:
            # Default JSON format
            export_data["format"] = "json"

        return export_data

    def _convert_to_csv(self, export_data: Dict[str, Any]) -> str:
        """Convert export data to CSV format."""
        # Simplified CSV conversion
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            "Name", "Position", "Company", "Location", "Industry", "Connections"
        ])

        # Data rows
        for profile in export_data["profiles"]:
            writer.writerow([
                profile.get("full_name", ""),
                profile.get("current_position", ""),
                profile.get("current_company", ""),
                profile.get("location", ""),
                profile.get("industry", ""),
                profile.get("connections_count", "")
            ])

        return output.getvalue()

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
