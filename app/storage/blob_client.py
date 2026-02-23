from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone

from azure.storage.blob.aio import BlobServiceClient
from azure.storage.blob import generate_blob_sas, BlobSasPermissions

from app.config import get_settings

logger = logging.getLogger(__name__)


class BlobStore:
    """
    Async Blob Storage client for managing temporary meeting documents.

    Files are uploaded to the `meeting-docs` container with a metadata tag
    indicating the meeting_id. A Blob Storage lifecycle rule (configured
    separately) deletes blobs after `doc_ttl_days` days.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self._client = BlobServiceClient.from_connection_string(
            settings.azure_storage_connection_string
        )
        self._container = settings.azure_storage_container_meeting_docs
        self._ttl_days = settings.doc_ttl_days

    async def initialize(self) -> None:
        """Ensure the container exists."""
        container_client = self._client.get_container_client(self._container)
        try:
            await container_client.create_container()
            logger.info("Created blob container '%s'", self._container)
        except Exception:
            pass  # Already exists

    async def upload(
        self,
        data: bytes,
        filename: str,
        meeting_id: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Upload a file and return its blob name."""
        blob_name = f"{meeting_id}/{uuid.uuid4().hex}_{filename}"
        container_client = self._client.get_container_client(self._container)
        await container_client.upload_blob(
            name=blob_name,
            data=data,
            content_settings={"content_type": content_type},
            metadata={"meeting_id": meeting_id},
            overwrite=True,
        )
        logger.info("Uploaded blob '%s' for meeting '%s'", blob_name, meeting_id)
        return blob_name

    def get_sas_url(self, blob_name: str, expiry_hours: int = 24) -> str:
        """Generate a SAS URL for reading a blob."""
        settings = get_settings()
        # Extract account name and key from connection string
        parts = dict(
            part.split("=", 1)
            for part in settings.azure_storage_connection_string.split(";")
            if "=" in part
        )
        account_name = parts.get("AccountName", "")
        account_key = parts.get("AccountKey", "")

        sas_token = generate_blob_sas(
            account_name=account_name,
            container_name=self._container,
            blob_name=blob_name,
            account_key=account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.now(timezone.utc) + timedelta(hours=expiry_hours),
        )
        return f"https://{account_name}.blob.core.windows.net/{self._container}/{blob_name}?{sas_token}"

    async def download(self, blob_name: str) -> bytes:
        """Download blob content as bytes."""
        container_client = self._client.get_container_client(self._container)
        blob = await container_client.download_blob(blob_name)
        return await blob.readall()

    async def close(self) -> None:
        await self._client.close()


_store: BlobStore | None = None


def get_blob_store() -> BlobStore:
    global _store
    if _store is None:
        _store = BlobStore()
    return _store
