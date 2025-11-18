"""Health Check and Sanity Validation API Routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import get_db
from health.health_checker import HealthChecker
from health.sanity_validator import SanityValidator
from auth.dependencies import get_current_user
from database.models import User

router = APIRouter()


@router.get("/health")
async def basic_health_check():
    """Basic health check endpoint (no authentication required)."""
    return {
        "status": "healthy",
        "message": "OSINT Platform is running"
    }


@router.get("/health/detailed")
async def detailed_health_check(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Detailed health check (requires authentication)."""
    checker = HealthChecker(db)

    try:
        result = await checker.run_full_health_check()

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await checker.close()


@router.get("/health/database")
async def check_database_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check database health."""
    checker = HealthChecker(db)

    try:
        result = await checker.check_database_health()

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await checker.close()


@router.get("/health/api")
async def check_api_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check API health."""
    checker = HealthChecker(db)

    try:
        result = await checker.check_api_health()

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await checker.close()


@router.get("/health/external-services")
async def check_external_services(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check external services health."""
    checker = HealthChecker(db)

    try:
        result = await checker.check_external_services()

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await checker.close()


@router.get("/health/queue")
async def check_queue_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check task queue health."""
    checker = HealthChecker(db)

    try:
        result = await checker.check_queue_health()

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await checker.close()


@router.get("/health/integrations")
async def check_integration_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check integration health."""
    checker = HealthChecker(db)

    try:
        result = await checker.check_integration_health()

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await checker.close()


@router.get("/health/metrics")
async def get_performance_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get performance metrics."""
    checker = HealthChecker(db)

    try:
        result = await checker.get_performance_metrics()

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await checker.close()


@router.get("/sanity")
async def run_sanity_checks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Run sanity validation checks."""
    validator = SanityValidator(db)

    try:
        result = await validator.run_sanity_checks()

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sanity/data-integrity")
async def check_data_integrity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check data integrity."""
    validator = SanityValidator(db)

    try:
        result = await validator.validate_data_integrity()

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sanity/configuration")
async def check_configuration(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check configuration."""
    validator = SanityValidator(db)

    try:
        result = await validator.validate_configuration()

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sanity/integrations")
async def check_integrations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check integration configurations."""
    validator = SanityValidator(db)

    try:
        result = await validator.validate_integrations()

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
