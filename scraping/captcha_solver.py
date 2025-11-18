"""CAPTCHA solving integration."""

from typing import Dict, Any, Optional
import httpx
from loguru import logger
from config.settings import settings


class CAPTCHASolver:
    """
    CAPTCHA solver integration for automated solving.

    Supports:
    - 2Captcha
    - Anti-Captcha
    - CapSolver
    - Manual solving fallback
    """

    def __init__(self, solver_type: str = None, api_key: str = None):
        """
        Initialize CAPTCHA solver.

        Args:
            solver_type: Type of solver (2captcha, anticaptcha, capsolver)
            api_key: API key for the solver service
        """
        self.solver_type = solver_type or settings.captcha_solver
        self.api_key = api_key or settings.captcha_api_key

        if not self.api_key:
            logger.warning("No CAPTCHA API key configured")

    async def solve_recaptcha_v2(
        self,
        site_key: str,
        page_url: str,
        **kwargs
    ) -> Optional[str]:
        """
        Solve reCAPTCHA v2.

        Args:
            site_key: reCAPTCHA site key
            page_url: URL of the page with CAPTCHA
            **kwargs: Additional parameters

        Returns:
            CAPTCHA solution token
        """
        if not self.api_key:
            logger.error("No CAPTCHA API key configured")
            return None

        try:
            if self.solver_type == "2captcha":
                return await self._solve_with_2captcha(
                    method="userrecaptcha",
                    googlekey=site_key,
                    pageurl=page_url,
                    **kwargs
                )
            elif self.solver_type == "anticaptcha":
                return await self._solve_with_anticaptcha(
                    type="NoCaptchaTaskProxyless",
                    websiteURL=page_url,
                    websiteKey=site_key,
                    **kwargs
                )
            else:
                logger.error(f"Unsupported solver type: {self.solver_type}")
                return None

        except Exception as e:
            logger.error(f"Error solving CAPTCHA: {e}")
            return None

    async def solve_recaptcha_v3(
        self,
        site_key: str,
        page_url: str,
        action: str = "verify",
        min_score: float = 0.3,
        **kwargs
    ) -> Optional[str]:
        """
        Solve reCAPTCHA v3.

        Args:
            site_key: reCAPTCHA site key
            page_url: URL of the page with CAPTCHA
            action: reCAPTCHA action
            min_score: Minimum score required
            **kwargs: Additional parameters

        Returns:
            CAPTCHA solution token
        """
        if not self.api_key:
            logger.error("No CAPTCHA API key configured")
            return None

        try:
            if self.solver_type == "2captcha":
                return await self._solve_with_2captcha(
                    method="userrecaptcha",
                    version="v3",
                    googlekey=site_key,
                    pageurl=page_url,
                    action=action,
                    min_score=min_score,
                    **kwargs
                )
            else:
                logger.error(f"reCAPTCHA v3 not supported for: {self.solver_type}")
                return None

        except Exception as e:
            logger.error(f"Error solving CAPTCHA: {e}")
            return None

    async def _solve_with_2captcha(self, **params) -> Optional[str]:
        """Solve CAPTCHA using 2Captcha service."""
        async with httpx.AsyncClient() as client:
            # Submit CAPTCHA
            submit_url = "http://2captcha.com/in.php"
            params["key"] = self.api_key
            params["json"] = 1

            response = await client.post(submit_url, data=params)
            result = response.json()

            if result.get("status") != 1:
                logger.error(f"2Captcha submission failed: {result}")
                return None

            captcha_id = result.get("request")

            # Poll for solution
            get_url = "http://2captcha.com/res.php"
            import asyncio
            for _ in range(60):  # Try for 2 minutes
                await asyncio.sleep(2)

                response = await client.get(get_url, params={
                    "key": self.api_key,
                    "action": "get",
                    "id": captcha_id,
                    "json": 1,
                })
                result = response.json()

                if result.get("status") == 1:
                    return result.get("request")
                elif result.get("request") != "CAPCHA_NOT_READY":
                    logger.error(f"2Captcha solving failed: {result}")
                    return None

            logger.error("2Captcha solving timeout")
            return None

    async def _solve_with_anticaptcha(self, **params) -> Optional[str]:
        """Solve CAPTCHA using Anti-Captcha service."""
        async with httpx.AsyncClient() as client:
            # Submit CAPTCHA
            submit_url = "https://api.anti-captcha.com/createTask"
            payload = {
                "clientKey": self.api_key,
                "task": params,
            }

            response = await client.post(submit_url, json=payload)
            result = response.json()

            if result.get("errorId") != 0:
                logger.error(f"Anti-Captcha submission failed: {result}")
                return None

            task_id = result.get("taskId")

            # Poll for solution
            get_url = "https://api.anti-captcha.com/getTaskResult"
            import asyncio
            for _ in range(60):
                await asyncio.sleep(2)

                response = await client.post(get_url, json={
                    "clientKey": self.api_key,
                    "taskId": task_id,
                })
                result = response.json()

                if result.get("status") == "ready":
                    return result.get("solution", {}).get("gRecaptchaResponse")
                elif result.get("errorId") != 0:
                    logger.error(f"Anti-Captcha solving failed: {result}")
                    return None

            logger.error("Anti-Captcha solving timeout")
            return None
