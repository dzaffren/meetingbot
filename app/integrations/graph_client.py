from __future__ import annotations

import logging

from azure.identity.aio import ClientSecretCredential
from msgraph import GraphServiceClient
from msgraph.generated.models.o_data_errors.o_data_error import ODataError

from app.config import get_settings

logger = logging.getLogger(__name__)


def get_graph_client() -> GraphServiceClient:
    """
    Return an authenticated Microsoft Graph SDK client using app-only auth
    (client credentials flow). The client is scoped to the default Graph scope.
    """
    settings = get_settings()
    credential = ClientSecretCredential(
        tenant_id=settings.azure_tenant_id,
        client_id=settings.azure_client_id,
        client_secret=settings.azure_client_secret,
    )
    scopes = ["https://graph.microsoft.com/.default"]
    return GraphServiceClient(credentials=credential, scopes=scopes)


__all__ = ["get_graph_client", "ODataError"]
