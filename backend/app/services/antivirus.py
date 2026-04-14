"""ClamAV antivirus scanning service."""

import logging
from typing import Tuple

logger = logging.getLogger(__name__)


async def scan_file(content: bytes) -> Tuple[bool, str]:
    """
    Scan file content with ClamAV.

    Returns:
        Tuple of (is_clean, message)
    """
    try:
        import pyclamd
        from app.config import settings

        cd = pyclamd.ClamdNetworkSocket(host=settings.CLAMAV_HOST, port=settings.CLAMAV_PORT)
        result = cd.scan_stream(content)

        if result is None:
            return True, "File is clean"
        else:
            virus_name = list(result.values())[0][1] if result else "Unknown"
            return False, f"Virus detected: {virus_name}"
    except ImportError:
        logger.warning("pyclamd not available, skipping antivirus scan")
        return True, "Antivirus scan skipped (pyclamd not available)"
    except Exception as e:
        logger.warning(f"ClamAV scan failed: {e}. Allowing file through.")
        return True, f"Antivirus scan skipped: {e}"
