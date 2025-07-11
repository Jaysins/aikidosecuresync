import asyncio
import time
from typing import Any, AsyncGenerator

import httpx
from aiolimiter import AsyncLimiter
from loguru import logger
from port_ocean.utils import http_async_client
from httpx import Timeout


class Endpoints:
    REPOSITORIES = "/api/public/v1/repositories/code"
    ISSUE_GROUPS = "/api/public/v1/open-issue-groups"


class AikidoClient:
    TOKEN_PATH = "/api/oauth/token"

    def __init__(self, host: str, client_id: str, client_secret: str) -> None:
        self.host = host.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret
        self.http_client = http_async_client
        self.http_client.timeout = Timeout(30)

        self.rate_limiter = AsyncLimiter(1000, 3600)
        self._semaphore = asyncio.Semaphore(5)
        self._token: str | None = None
        self._token_expires_at: float = 0

    async def _fetch_access_token(self) -> None:
        url = f"{self.host}{self.TOKEN_PATH}"
        logger.debug("Requesting new Aikido access token")
        resp = await self.http_client.post(
            url,
            data={"grant_type": "client_credentials"},
            auth=httpx.BasicAuth(self.client_id, self.client_secret),
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        self._token = data["access_token"]
        self._token_expires_at = time.time() + data.get("expires_in", 300)
        self.http_client.headers.update({"Authorization": f"Bearer {self._token}"})

    async def _ensure_token(self) -> None:
        if not self._token or time.time() >= self._token_expires_at - 30:
            await self._fetch_access_token()

    async def _send_api_request(
            self,
            method: str,
            path: str,
            params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        await self._ensure_token()
        async with self.rate_limiter, self._semaphore:
            url = f"{self.host}{path}"
            logger.debug(f"Aikido request → {method} {url} params={params}")
            resp = await self.http_client.request(method, url=url, params=params)
            resp.raise_for_status()
            return resp

    async def list_repositories(
            self,
            include_inactive: bool = False,
            page: int = 0,
            per_page: int = 20
    ) -> AsyncGenerator[list[dict[str, Any]], None]:
        while True:
            resp = await self._send_api_request(
                "GET",
                Endpoints.REPOSITORIES,
                params={"page": page, "per_page": per_page, "include_inactive": include_inactive},
            )
            data = resp.json()

            repos = data
            if not repos:
                break
            yield repos
            page += 1

    async def list_open_issue_groups(
            self,
            repo_id: int | None = None,
            page: int = 0,
            per_page: int = 20
    ) -> AsyncGenerator[list[dict[str, Any]], None]:
        while True:
            params: dict[str, Any] = {"page": page, "per_page": per_page}
            if repo_id is not None:
                params["filter_code_repo_id"] = repo_id
            resp = await self._send_api_request(
                "GET",
                Endpoints.ISSUE_GROUPS,
                params=params,
            )
            groups = resp.json()
            if not groups:
                break
            yield groups
            page += 1
