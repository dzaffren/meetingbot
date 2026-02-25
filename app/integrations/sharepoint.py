from __future__ import annotations

import logging

from app.config import get_settings
from app.integrations.graph_client import get_graph_client
from app.models.minutes import MeetingMinutes

logger = logging.getLogger(__name__)


async def upload_minutes(minutes: MeetingMinutes) -> str:
    """
    Render MeetingMinutes to a Word document (.docx) and upload to SharePoint.

    Returns the SharePoint web URL of the uploaded file.

    Args:
        minutes: A populated MeetingMinutes instance.

    Returns:
        The SharePoint web URL string.
    """
    # TODO: Implement SharePoint upload.
    #
    # Pattern:
    #   from app.utils.document_generator import generate_word, minutes_filename
    #   settings = get_settings()
    #   graph = get_graph_client()
    #   filename = minutes_filename(minutes, "docx")
    #   docx_bytes = generate_word(minutes)
    #   upload_path = f"{settings.sharepoint_folder_path}/{filename}"
    #   result = await (
    #       graph.sites.by_site_id(settings.sharepoint_site_id)
    #       .drives.by_drive_id(settings.sharepoint_drive_id)
    #       .root.item_with_path(upload_path)
    #       .content.put(docx_bytes)
    #   )
    #   return result.web_url or ""
    raise NotImplementedError("TODO: implement upload_minutes()")


async def upload_pdf_minutes(minutes: MeetingMinutes) -> str:
    """
    Render MeetingMinutes to a PDF and upload to SharePoint.

    Args:
        minutes: A populated MeetingMinutes instance.

    Returns:
        The SharePoint web URL string.
    """
    # TODO: Implement PDF SharePoint upload.
    # Similar to upload_minutes() but uses generate_pdf() and .pdf extension.
    raise NotImplementedError("TODO: implement upload_pdf_minutes()")
