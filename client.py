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
    USERS = "/api/public/v1/users"
    ISSUE_DETAIL = "/api/public/v1/issues/{}"
    ISSUES_EXPORT = "/api/public/v1/issues/export"


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
            try:
                resp = await self.http_client.request(method, url=url, params=params)
                resp.raise_for_status()
                return resp
            except httpx.HTTPStatusError as e:
                logger.error(f"Request failed: {method} {url} status={e.response.status_code}")
            except httpx.RequestError as e:
                logger.error(f"Request error: {method} {url} error={str(e)}")

    async def _get_paginated(
            self,
            path: str,
            params: dict[str, Any] | None = None,
            per_page: int = 20
    ) -> AsyncGenerator[list[dict[str, Any]], None]:
        page = 0
        while True:
            paginated_params = (params or {}).copy()
            paginated_params.update({"page": page, "per_page": per_page})

            resp = await self._send_api_request("GET", path, params=paginated_params)
            data = resp.json()

            if not data:
                break
            yield data
            page += 1

    async def list_repositories(
            self,
            include_inactive: bool = False,
            per_page: int = 20
    ) -> AsyncGenerator[list[dict[str, Any]], None]:
        params = {"include_inactive": include_inactive}
        async for repos in self._get_paginated(
                Endpoints.REPOSITORIES,
                params=params,
                per_page=per_page
        ):
            yield repos

    async def list_open_issue_groups(
            self,
            repo_id: int | None = None,
            per_page: int = 20
    ) -> AsyncGenerator[list[dict[str, Any]], None]:
        params = {}
        if repo_id is not None:
            params["filter_code_repo_id"] = repo_id

        async for groups in self._get_paginated(
                Endpoints.ISSUE_GROUPS,
                params=params,
                per_page=per_page
        ):
            yield groups

    async def get_issue(
            self,
            issue_id: int
    ) -> dict[str, Any]:
        """
        Fetch the details of a single Aikido issue by ID.
        GET /api/public/v1/issues/{issue_id}
        """
        path = Endpoints.ISSUE_DETAIL.format(issue_id)
        resp = await self._send_api_request("GET", path)
        return resp.json()

    async def export_issues(
            self,
            format_: str = "json",
            filter_status: str = "all",
            filter_team_id: int | None = None,
            filter_issue_group_id: int | None = None,
            filter_code_repo_id: int | None = None,
            filter_container_repo_id: int | None = None,
            filter_container_repo_name: str | None = None,
            filter_domain_id: int | None = None,
            filter_issue_type: str | None = None,
            filter_severities: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Fetch a full export of issues from Aikido.

        GET /api/public/v1/issues/export
        """
        params: dict[str, Any] = {"format": format_, "filter_status": filter_status}

        # Add any optional filters if provided
        if filter_team_id is not None:
            params["filter_team_id"] = filter_team_id
        if filter_issue_group_id is not None:
            params["filter_issue_group_id"] = filter_issue_group_id
        if filter_code_repo_id is not None:
            params["filter_code_repo_id"] = filter_code_repo_id
        if filter_container_repo_id is not None:
            params["filter_container_repo_id"] = filter_container_repo_id
        if filter_container_repo_name is not None:
            params["filter_container_repo_name"] = filter_container_repo_name
        if filter_domain_id is not None:
            params["filter_domain_id"] = filter_domain_id
        if filter_issue_type is not None:
            params["filter_issue_type"] = filter_issue_type
        if filter_severities is not None:
            params["filter_severities"] = filter_severities

        resp = await self._send_api_request("GET", Endpoints.ISSUES_EXPORT, params=params)

        return resp.json()
