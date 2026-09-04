import logging
from pathlib import PurePath

logger = logging.getLogger(__name__)


def extract_text(file_path: str) -> str:
    """Mock OCR extraction with basic path validation for the MVP."""
    if not file_path or not PurePath(file_path).suffix:
        raise ValueError("A document file path with an extension is required.")
    logger.info("ocr_extract_started", extra={"file_path": file_path})
    return "Patient P001 was seen for cardiology referral. HbA1c ordered."
