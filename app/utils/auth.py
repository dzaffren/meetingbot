from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Token acquisition helpers
# ---------------------------------------------------------------------------

async def get_app_token(scope: str = "https://graph.microsoft.com/.default") -> str:
    """
    Acquire an Azure AD app-only token (client credentials flow).

    Used by integrations that call Microsoft Graph without a delegated user context
    (Planner task creation, SharePoint upload, user resolution).

    Args:
        scope: The OAuth2 scope to request. Defaults to Graph API.

    Returns:
        A bearer token string.
    """
    # TODO: Implement using azure-identity ClientSecretCredential.
    #
    # Example:
    #   from azure.identity.aio import ClientSecretCredential
    #   from app.config import get_settings
    #   s = get_settings()
    #   credential = ClientSecretCredential(s.azure_tenant_id, s.azure_client_id, s.azure_client_secret)
    #   token = await credential.get_token(scope)
    #   return token.token
    raise NotImplementedError("TODO: implement get_app_token()")


# ---------------------------------------------------------------------------
# Bot Framework auth (placeholder — used in Phase 2 Teams integration)
# ---------------------------------------------------------------------------

def validate_bot_token(auth_header: Optional[str], channel_id: str = "msteams") -> bool:
    """
    Validate an incoming Bot Framework JWT token from Teams.

    Phase 2 placeholder — called from the `/api/messages` endpoint to verify
    that the request originated from the Bot Framework service.

    Args:
        auth_header: The raw "Authorization: Bearer <token>" header value.
        channel_id: Expected channel identifier (default: "msteams").

    Returns:
        True if the token is valid, False otherwise.
    """
    # TODO: Implement using botframework-connector JwtTokenValidation.
    #
    # Example (Phase 2):
    #   from botframework.connector.auth import JwtTokenValidation, SimpleCredentialProvider
    #   credentials = SimpleCredentialProvider(app_id, app_password)
    #   claims = await JwtTokenValidation.validate_auth_header(auth_header, credentials, channel_id, ...)
    #   return claims is not None
    logger.warning("validate_bot_token() not yet implemented — allowing all requests (dev mode)")
    return True
