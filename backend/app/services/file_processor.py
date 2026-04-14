"""File content extraction service."""

import json
import csv
import io
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def extract_text_from_file(file_path: str, mime_type: str) -> Optional[str]:
    """Extract text content from a file based on its MIME type."""
    path = Path(file_path)

    if not path.exists():
        logger.error(f"File not found: {file_path}")
        return None

    try:
        # Plain text
        if mime_type in ("text/plain", "text/x-python", "application/sql", "text/sql"):
            return path.read_text(encoding="utf-8", errors="ignore")

        # CSV
        if mime_type == "text/csv":
            content = path.read_text(encoding="utf-8", errors="ignore")
            reader = csv.reader(io.StringIO(content))
            rows = [" | ".join(row) for row in reader]
            return "\n".join(rows)

        # JSON
        if mime_type == "application/json":
            content = path.read_text(encoding="utf-8", errors="ignore")
            data = json.loads(content)
            return json.dumps(data, indent=2, ensure_ascii=False)

        # XML / HTML
        if mime_type in ("application/xml", "text/xml", "text/html"):
            return path.read_text(encoding="utf-8", errors="ignore")

        # SQL
        if "sql" in mime_type or path.suffix.lower() == ".sql":
            return path.read_text(encoding="utf-8", errors="ignore")

        # PDF
        if mime_type == "application/pdf":
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(file_path)
                text = ""
                for page in doc:
                    text += page.get_text()
                return text
            except ImportError:
                logger.warning("PyMuPDF not available for PDF processing")
                return None
            except Exception as e:
                logger.error(f"PDF extraction failed: {e}")
                return None

        # DOCX
        if mime_type in ("application/vnd.openxmlformats-officedocument.wordprocessingml.document",):
            try:
                from docx import Document
                doc = Document(file_path)
                return "\n".join([para.text for para in doc.paragraphs])
            except ImportError:
                logger.warning("python-docx not available for DOCX processing")
                return None
            except Exception as e:
                logger.error(f"DOCX extraction failed: {e}")
                return None

        # XLSX
        if mime_type in ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",):
            try:
                import pandas as pd
                df = pd.read_excel(file_path, engine="openpyxl")
                return df.to_string()
            except ImportError:
                logger.warning("pandas/openpyxl not available for XLSX processing")
                return None
            except Exception as e:
                logger.error(f"XLSX extraction failed: {e}")
                return None

        # Unknown — try as text
        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return None

    except Exception as e:
        logger.error(f"Error extracting text from {file_path}: {e}")
        return None
