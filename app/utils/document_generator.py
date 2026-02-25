from __future__ import annotations

import io
import logging
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Word (.docx) generation
# ---------------------------------------------------------------------------

def generate_word(minutes) -> bytes:
    """
    Render a MeetingMinutes object as a Word (.docx) document.

    Args:
        minutes: A MeetingMinutes Pydantic model instance.

    Returns:
        Raw bytes of the generated .docx file.

    Usage:
        docx_bytes = generate_word(minutes)
        # Return as HTTP response or pass to SharePoint uploader
    """
    # TODO: Implement using python-docx.
    #
    # Suggested structure:
    #   doc = Document()
    #   doc.add_heading(minutes.title, level=1)
    #   doc.add_paragraph(f"Date: {minutes.date}  |  Meeting ID: {minutes.meeting_id}")
    #   doc.add_heading("Attendees", level=2)
    #   doc.add_paragraph(", ".join(minutes.attendees))
    #   doc.add_heading("Summary", level=2)
    #   doc.add_paragraph(minutes.summary)
    #   doc.add_heading("Key Decisions", level=2)
    #   for d in minutes.key_decisions: doc.add_paragraph(f"• {d}")
    #   doc.add_heading("Action Items", level=2)
    #   table = doc.add_table(rows=1, cols=4); ... populate table ...
    #   buf = io.BytesIO(); doc.save(buf); return buf.getvalue()
    raise NotImplementedError("TODO: implement generate_word()")


# ---------------------------------------------------------------------------
# PDF generation
# ---------------------------------------------------------------------------

def generate_pdf(minutes) -> bytes:
    """
    Render a MeetingMinutes object as a PDF document.

    Args:
        minutes: A MeetingMinutes Pydantic model instance.

    Returns:
        Raw bytes of the generated PDF file.

    Usage:
        pdf_bytes = generate_pdf(minutes)
        # Return as HTTP response
    """
    # TODO: Implement using reportlab.
    #
    # Suggested structure (reportlab platypus):
    #   from reportlab.lib.pagesizes import A4
    #   from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Spacer
    #   from reportlab.lib.styles import getSampleStyleSheet
    #   from reportlab.lib import colors
    #
    #   buf = io.BytesIO()
    #   doc = SimpleDocTemplate(buf, pagesize=A4)
    #   styles = getSampleStyleSheet()
    #   story = []
    #   story.append(Paragraph(minutes.title, styles["Title"]))
    #   story.append(Paragraph(minutes.summary, styles["Normal"]))
    #   ... add decisions, action items table ...
    #   doc.build(story)
    #   return buf.getvalue()
    raise NotImplementedError("TODO: implement generate_pdf()")


# ---------------------------------------------------------------------------
# File name helper
# ---------------------------------------------------------------------------

def minutes_filename(minutes, extension: str = "docx") -> str:
    """Return a sanitised file name for the minutes document, e.g. '2025-01-15 - Q3 Review.docx'."""
    safe_title = minutes.title.replace("/", "-").replace("\\", "-").strip()
    return f"{minutes.date.isoformat()} - {safe_title}.{extension}"
