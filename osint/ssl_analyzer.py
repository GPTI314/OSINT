"""SSL/TLS certificate analysis."""

from typing import Dict, Any, Optional
import ssl
import socket
from datetime import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from loguru import logger


class SSLAnalyzer:
    """
    SSL/TLS certificate analyzer.

    Features:
    - Certificate retrieval
    - Expiration checking
    - Issuer information
    - Subject Alternative Names
    - Signature algorithm
    - Public key info
    """

    def __init__(self):
        """Initialize SSL analyzer."""
        logger.info("SSL analyzer initialized")

    async def analyze(self, domain: str, port: int = 443) -> Dict[str, Any]:
        """
        Analyze SSL certificate for a domain.

        Args:
            domain: Domain name
            port: Port number (default: 443)

        Returns:
            Certificate analysis data
        """
        try:
            logger.debug(f"Analyzing SSL certificate: {domain}:{port}")

            # Get certificate
            cert_pem = self._get_certificate(domain, port)
            if not cert_pem:
                return {"error": "Failed to retrieve certificate"}

            # Parse certificate
            cert = x509.load_pem_x509_certificate(
                cert_pem.encode(),
                default_backend()
            )

            # Extract certificate details
            analysis = {
                "subject": self._get_subject(cert),
                "issuer": self._get_issuer(cert),
                "version": cert.version.name,
                "serial_number": str(cert.serial_number),
                "not_valid_before": cert.not_valid_before.isoformat(),
                "not_valid_after": cert.not_valid_after.isoformat(),
                "expired": datetime.utcnow() > cert.not_valid_after.replace(tzinfo=None),
                "days_until_expiry": (cert.not_valid_after.replace(tzinfo=None) - datetime.utcnow()).days,
                "signature_algorithm": cert.signature_algorithm_oid._name,
                "public_key_algorithm": cert.public_key().__class__.__name__,
                "san": self._get_san(cert),
                "self_signed": self._is_self_signed(cert),
            }

            logger.info(f"SSL certificate analyzed: {domain}")
            return analysis

        except Exception as e:
            logger.error(f"Error analyzing SSL certificate for {domain}: {e}")
            return {"error": str(e)}

    def _get_certificate(self, domain: str, port: int) -> Optional[str]:
        """Retrieve SSL certificate from server."""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert_der = ssock.getpeercert(binary_form=True)
                    cert_pem = ssl.DER_cert_to_PEM_cert(cert_der)
                    return cert_pem
        except Exception as e:
            logger.error(f"Error retrieving certificate: {e}")
            return None

    def _get_subject(self, cert: x509.Certificate) -> Dict[str, str]:
        """Extract subject from certificate."""
        subject = {}
        for attribute in cert.subject:
            subject[attribute.oid._name] = attribute.value
        return subject

    def _get_issuer(self, cert: x509.Certificate) -> Dict[str, str]:
        """Extract issuer from certificate."""
        issuer = {}
        for attribute in cert.issuer:
            issuer[attribute.oid._name] = attribute.value
        return issuer

    def _get_san(self, cert: x509.Certificate) -> list:
        """Extract Subject Alternative Names."""
        try:
            san_ext = cert.extensions.get_extension_for_oid(
                x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME
            )
            return [str(name) for name in san_ext.value]
        except x509.ExtensionNotFound:
            return []

    def _is_self_signed(self, cert: x509.Certificate) -> bool:
        """Check if certificate is self-signed."""
        return cert.subject == cert.issuer
