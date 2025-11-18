"""
CAPTCHA Solver
Integration with various CAPTCHA solving services
"""

from typing import Optional, Dict, Any
from enum import Enum
import time
from loguru import logger

try:
    from twocaptcha import TwoCaptcha
    TWOCAPTCHA_AVAILABLE = True
except ImportError:
    TWOCAPTCHA_AVAILABLE = False
    logger.warning("2captcha-python not installed")

try:
    from anticaptchaofficial.recaptchav2proxyless import recaptchaV2Proxyless
    from anticaptchaofficial.recaptchav3proxyless import recaptchaV3Proxyless
    from anticaptchaofficial.imagecaptcha import imagecaptcha
    ANTICAPTCHA_AVAILABLE = True
except ImportError:
    ANTICAPTCHA_AVAILABLE = False
    logger.warning("anticaptchaofficial not installed")


class CaptchaType(Enum):
    """CAPTCHA types"""
    RECAPTCHA_V2 = "recaptcha_v2"
    RECAPTCHA_V3 = "recaptcha_v3"
    IMAGE = "image"
    HCAPTCHA = "hcaptcha"
    FUNCAPTCHA = "funcaptcha"


class CaptchaService(Enum):
    """CAPTCHA solving services"""
    TWO_CAPTCHA = "2captcha"
    ANTI_CAPTCHA = "anticaptcha"


class CaptchaSolver:
    """
    Unified CAPTCHA solver supporting multiple services
    """

    def __init__(
        self,
        service: CaptchaService,
        api_key: str,
        timeout: int = 120
    ):
        """
        Initialize CAPTCHA solver.

        Args:
            service: CAPTCHA solving service to use
            api_key: API key for the service
            timeout: Maximum time to wait for solution (seconds)
        """
        self.service = service
        self.api_key = api_key
        self.timeout = timeout

        if service == CaptchaService.TWO_CAPTCHA and not TWOCAPTCHA_AVAILABLE:
            raise ImportError("2captcha-python is not installed. Install with: pip install 2captcha-python")

        if service == CaptchaService.ANTI_CAPTCHA and not ANTICAPTCHA_AVAILABLE:
            raise ImportError("anticaptchaofficial is not installed. Install with: pip install anticaptchaofficial")

        if service == CaptchaService.TWO_CAPTCHA:
            self.solver = TwoCaptcha(api_key)

        logger.info(f"Initialized CaptchaSolver with {service.value}")

    def solve_recaptcha_v2(
        self,
        site_key: str,
        page_url: str,
        invisible: bool = False,
        data_s: Optional[str] = None
    ) -> Optional[str]:
        """
        Solve reCAPTCHA v2.

        Args:
            site_key: Site key of the reCAPTCHA
            page_url: URL of the page with CAPTCHA
            invisible: Whether it's invisible reCAPTCHA
            data_s: Optional data-s parameter

        Returns:
            CAPTCHA solution token or None if failed
        """
        try:
            logger.info(f"Solving reCAPTCHA v2 for {page_url}")

            if self.service == CaptchaService.TWO_CAPTCHA:
                params = {
                    'sitekey': site_key,
                    'url': page_url,
                    'invisible': 1 if invisible else 0
                }
                if data_s:
                    params['data-s'] = data_s

                result = self.solver.recaptcha(**params)
                solution = result.get('code')

            elif self.service == CaptchaService.ANTI_CAPTCHA:
                solver = recaptchaV2Proxyless()
                solver.set_verbose(1)
                solver.set_key(self.api_key)
                solver.set_website_url(page_url)
                solver.set_website_key(site_key)

                if invisible:
                    solver.set_is_invisible(1)

                solution = solver.solve_and_return_solution()
                if not solution:
                    logger.error(f"Anti-Captcha error: {solver.error_code}")
                    return None

            else:
                logger.error(f"Unsupported service: {self.service}")
                return None

            logger.info("Successfully solved reCAPTCHA v2")
            return solution

        except Exception as e:
            logger.error(f"Failed to solve reCAPTCHA v2: {e}")
            return None

    def solve_recaptcha_v3(
        self,
        site_key: str,
        page_url: str,
        action: str = "verify",
        min_score: float = 0.3
    ) -> Optional[str]:
        """
        Solve reCAPTCHA v3.

        Args:
            site_key: Site key of the reCAPTCHA
            page_url: URL of the page with CAPTCHA
            action: Action name
            min_score: Minimum score required

        Returns:
            CAPTCHA solution token or None if failed
        """
        try:
            logger.info(f"Solving reCAPTCHA v3 for {page_url}")

            if self.service == CaptchaService.TWO_CAPTCHA:
                result = self.solver.recaptcha(
                    sitekey=site_key,
                    url=page_url,
                    version='v3',
                    action=action,
                    score=min_score
                )
                solution = result.get('code')

            elif self.service == CaptchaService.ANTI_CAPTCHA:
                solver = recaptchaV3Proxyless()
                solver.set_verbose(1)
                solver.set_key(self.api_key)
                solver.set_website_url(page_url)
                solver.set_website_key(site_key)
                solver.set_page_action(action)
                solver.set_min_score(min_score)

                solution = solver.solve_and_return_solution()
                if not solution:
                    logger.error(f"Anti-Captcha error: {solver.error_code}")
                    return None

            else:
                logger.error(f"Unsupported service: {self.service}")
                return None

            logger.info("Successfully solved reCAPTCHA v3")
            return solution

        except Exception as e:
            logger.error(f"Failed to solve reCAPTCHA v3: {e}")
            return None

    def solve_image_captcha(
        self,
        image_path: Optional[str] = None,
        image_base64: Optional[str] = None
    ) -> Optional[str]:
        """
        Solve image-based CAPTCHA.

        Args:
            image_path: Path to CAPTCHA image file
            image_base64: Base64-encoded CAPTCHA image

        Returns:
            CAPTCHA solution text or None if failed
        """
        try:
            logger.info("Solving image CAPTCHA")

            if self.service == CaptchaService.TWO_CAPTCHA:
                if image_path:
                    result = self.solver.normal(image_path)
                elif image_base64:
                    result = self.solver.normal(image_base64)
                else:
                    logger.error("Either image_path or image_base64 must be provided")
                    return None

                solution = result.get('code')

            elif self.service == CaptchaService.ANTI_CAPTCHA:
                solver = imagecaptcha()
                solver.set_verbose(1)
                solver.set_key(self.api_key)

                if image_path:
                    solution = solver.solve_and_return_solution(image_path)
                elif image_base64:
                    # Anti-Captcha expects file path, need to save base64 to temp file
                    import tempfile
                    import base64

                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as f:
                        f.write(base64.b64decode(image_base64))
                        temp_path = f.name

                    solution = solver.solve_and_return_solution(temp_path)

                    # Clean up temp file
                    import os
                    os.unlink(temp_path)
                else:
                    logger.error("Either image_path or image_base64 must be provided")
                    return None

                if not solution:
                    logger.error(f"Anti-Captcha error: {solver.error_code}")
                    return None

            else:
                logger.error(f"Unsupported service: {self.service}")
                return None

            logger.info(f"Successfully solved image CAPTCHA: {solution}")
            return solution

        except Exception as e:
            logger.error(f"Failed to solve image CAPTCHA: {e}")
            return None

    def solve_hcaptcha(
        self,
        site_key: str,
        page_url: str
    ) -> Optional[str]:
        """
        Solve hCaptcha.

        Args:
            site_key: Site key of the hCaptcha
            page_url: URL of the page with CAPTCHA

        Returns:
            CAPTCHA solution token or None if failed
        """
        try:
            logger.info(f"Solving hCaptcha for {page_url}")

            if self.service == CaptchaService.TWO_CAPTCHA:
                result = self.solver.hcaptcha(
                    sitekey=site_key,
                    url=page_url
                )
                solution = result.get('code')
                logger.info("Successfully solved hCaptcha")
                return solution

            else:
                logger.error(f"hCaptcha not supported by {self.service.value}")
                return None

        except Exception as e:
            logger.error(f"Failed to solve hCaptcha: {e}")
            return None

    def get_balance(self) -> Optional[float]:
        """
        Get account balance.

        Returns:
            Account balance or None if failed
        """
        try:
            if self.service == CaptchaService.TWO_CAPTCHA:
                balance = self.solver.balance()
                logger.info(f"2Captcha balance: ${balance}")
                return float(balance)

            elif self.service == CaptchaService.ANTI_CAPTCHA:
                # Anti-Captcha balance check requires making a solver instance
                solver = recaptchaV2Proxyless()
                solver.set_key(self.api_key)
                balance = solver.get_balance()
                logger.info(f"Anti-Captcha balance: ${balance}")
                return float(balance)

            return None

        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            return None


class MockCaptchaSolver:
    """
    Mock CAPTCHA solver for testing purposes.
    Always returns a fake solution after a short delay.
    """

    def __init__(self, delay: float = 2.0):
        """
        Initialize mock solver.

        Args:
            delay: Delay before returning solution (seconds)
        """
        self.delay = delay
        logger.warning("Using MockCaptchaSolver - for testing only!")

    def solve_recaptcha_v2(self, *args, **kwargs) -> str:
        """Mock reCAPTCHA v2 solution"""
        time.sleep(self.delay)
        return "mock_recaptcha_v2_solution_token"

    def solve_recaptcha_v3(self, *args, **kwargs) -> str:
        """Mock reCAPTCHA v3 solution"""
        time.sleep(self.delay)
        return "mock_recaptcha_v3_solution_token"

    def solve_image_captcha(self, *args, **kwargs) -> str:
        """Mock image CAPTCHA solution"""
        time.sleep(self.delay)
        return "mock_solution_text"

    def solve_hcaptcha(self, *args, **kwargs) -> str:
        """Mock hCaptcha solution"""
        time.sleep(self.delay)
        return "mock_hcaptcha_solution_token"

    def get_balance(self) -> float:
        """Mock balance"""
        return 999.99
