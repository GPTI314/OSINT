"""SEO/SEM API Routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database.connection import get_db
from seo_sem.seo_analyzer import SEOAnalyzer
from seo_sem.sem_analyzer import SEMAnalyzer
from auth.dependencies import get_current_user
from database.models import User, SEOAnalysis, KeywordRanking

router = APIRouter()


# Request/Response Models
class SEOAnalysisRequest(BaseModel):
    url: str = Field(..., description="URL to analyze")
    analysis_type: str = Field(default="on_page", description="Type of SEO analysis")
    investigation_id: Optional[int] = None


class KeywordAnalysisRequest(BaseModel):
    domain: str = Field(..., description="Domain to analyze")
    keywords: List[str] = Field(..., description="List of keywords to analyze")
    location: Optional[str] = None
    investigation_id: Optional[int] = None


class BacklinkAnalysisRequest(BaseModel):
    domain: str = Field(..., description="Domain for backlink analysis")
    investigation_id: Optional[int] = None


class CompetitorAnalysisRequest(BaseModel):
    domain: str = Field(..., description="Target domain")
    competitors: List[str] = Field(..., description="List of competitor domains")
    investigation_id: Optional[int] = None


class SEMKeywordResearchRequest(BaseModel):
    seed_keywords: List[str] = Field(..., description="Seed keywords for research")
    location: Optional[str] = None
    investigation_id: Optional[int] = None


class AdCopyAnalysisRequest(BaseModel):
    ad_copies: List[dict] = Field(..., description="List of ad copies to analyze")
    investigation_id: Optional[int] = None


class LandingPageAnalysisRequest(BaseModel):
    url: str = Field(..., description="Landing page URL to analyze")
    investigation_id: Optional[int] = None


# SEO Endpoints
@router.post("/seo/analyze")
async def analyze_seo(
    request: SEOAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Perform comprehensive SEO analysis."""
    analyzer = SEOAnalyzer(db)

    try:
        if request.analysis_type == "on_page":
            result = await analyzer.on_page_audit(
                request.url,
                request.investigation_id
            )
        elif request.analysis_type == "technical":
            result = await analyzer.technical_seo_check(
                request.url,
                request.investigation_id
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown analysis type: {request.analysis_type}"
            )

        return {
            "success": True,
            "analysis_type": request.analysis_type,
            "result": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await analyzer.close()


@router.post("/seo/keywords/analyze")
async def analyze_keywords(
    request: KeywordAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Analyze keyword rankings and opportunities."""
    analyzer = SEOAnalyzer(db)

    try:
        result = await analyzer.analyze_keywords(
            request.domain,
            request.keywords,
            request.investigation_id,
            request.location
        )

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await analyzer.close()


@router.get("/seo/keywords/{domain}")
async def get_keyword_rankings(
    domain: str,
    limit: int = Query(default=100, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get keyword rankings for a domain."""
    try:
        rankings = db.query(KeywordRanking).filter(
            KeywordRanking.domain == domain
        ).order_by(KeywordRanking.tracked_at.desc()).limit(limit).all()

        return {
            "success": True,
            "domain": domain,
            "total_keywords": len(rankings),
            "keywords": [
                {
                    "keyword": r.keyword,
                    "position": r.position,
                    "search_volume": r.search_volume,
                    "difficulty": r.difficulty,
                    "cpc": r.cpc,
                    "tracked_at": r.tracked_at.isoformat()
                }
                for r in rankings
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/seo/backlinks")
async def analyze_backlinks(
    request: BacklinkAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Analyze backlink profile."""
    analyzer = SEOAnalyzer(db)

    try:
        result = await analyzer.backlink_analysis(
            request.domain,
            request.investigation_id
        )

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await analyzer.close()


@router.post("/seo/competitors")
async def analyze_competitors(
    request: CompetitorAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Analyze competitor SEO."""
    analyzer = SEOAnalyzer(db)

    try:
        result = await analyzer.competitor_analysis(
            request.domain,
            request.competitors,
            request.investigation_id
        )

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await analyzer.close()


@router.get("/seo/analysis/{domain}")
async def get_seo_analysis_history(
    domain: str,
    limit: int = Query(default=10, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get SEO analysis history for a domain."""
    try:
        analyses = db.query(SEOAnalysis).filter(
            SEOAnalysis.target_url.like(f"%{domain}%")
        ).order_by(SEOAnalysis.analyzed_at.desc()).limit(limit).all()

        return {
            "success": True,
            "domain": domain,
            "total_analyses": len(analyses),
            "analyses": [
                {
                    "id": a.id,
                    "analysis_type": a.analysis_type,
                    "score": a.score,
                    "issues_count": len(a.issues) if a.issues else 0,
                    "analyzed_at": a.analyzed_at.isoformat()
                }
                for a in analyses
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# SEM Endpoints
@router.post("/sem/keyword-research")
async def sem_keyword_research(
    request: SEMKeywordResearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """SEM keyword research."""
    analyzer = SEMAnalyzer(db)

    try:
        result = await analyzer.keyword_research(
            request.seed_keywords,
            request.location,
            request.investigation_id
        )

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await analyzer.close()


@router.post("/sem/ad-copy-analysis")
async def analyze_ad_copy(
    request: AdCopyAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Analyze ad copy effectiveness."""
    analyzer = SEMAnalyzer(db)

    try:
        result = await analyzer.ad_copy_analysis(
            request.ad_copies,
            request.investigation_id
        )

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await analyzer.close()


@router.post("/sem/landing-page-analysis")
async def analyze_landing_page(
    request: LandingPageAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Analyze landing page optimization."""
    analyzer = SEMAnalyzer(db)

    try:
        result = await analyzer.landing_page_analysis(
            request.url,
            request.investigation_id
        )

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await analyzer.close()
