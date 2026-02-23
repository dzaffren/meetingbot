from __future__ import annotations

import logging
from typing import Any

from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosResourceNotFoundError

from app.config import get_settings

logger = logging.getLogger(__name__)

# Container names
CONTAINER_SESSIONS = "meeting_sessions"
CONTAINER_MINUTES = "minutes"
CONTAINER_TASKS = "tasks"
CONTAINER_HISTORY = "conversation_history"

_ALL_CONTAINERS = [CONTAINER_SESSIONS, CONTAINER_MINUTES, CONTAINER_TASKS, CONTAINER_HISTORY]


class CosmosStore:
    """
    Async Cosmos DB client wrapping CRUD operations for all MeetingBot containers.
    Call `await store.initialize()` on startup to ensure containers exist.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self._client = CosmosClient(settings.azure_cosmos_endpoint, settings.azure_cosmos_key)
        self._db_name = settings.azure_cosmos_database
        self._db = None

    async def initialize(self) -> None:
        """Create database and containers if they don't exist."""
        self._db = await self._client.create_database_if_not_exists(id=self._db_name)
        for name in _ALL_CONTAINERS:
            await self._db.create_container_if_not_exists(
                id=name,
                partition_key={"paths": ["/id"], "kind": "Hash"},
            )
        logger.info("Cosmos DB initialized (db=%s)", self._db_name)

    async def upsert(self, container: str, item: dict[str, Any]) -> dict[str, Any]:
        c = self._db.get_container_client(container)
        return await c.upsert_item(item)

    async def get(self, container: str, item_id: str) -> dict[str, Any] | None:
        c = self._db.get_container_client(container)
        try:
            return await c.read_item(item=item_id, partition_key=item_id)
        except CosmosResourceNotFoundError:
            return None

    async def delete(self, container: str, item_id: str) -> None:
        c = self._db.get_container_client(container)
        try:
            await c.delete_item(item=item_id, partition_key=item_id)
        except CosmosResourceNotFoundError:
            pass

    async def query(self, container: str, query: str, params: list | None = None) -> list[dict]:
        c = self._db.get_container_client(container)
        items = c.query_items(query=query, parameters=params or [])
        return [item async for item in items]

    async def close(self) -> None:
        await self._client.close()


# Module-level singleton
_store: CosmosStore | None = None


def get_cosmos_store() -> CosmosStore:
    global _store
    if _store is None:
        _store = CosmosStore()
    return _store
