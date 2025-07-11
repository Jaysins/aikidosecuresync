from typing import AsyncGenerator, cast

from loguru import logger
from port_ocean.context.event import event
from port_ocean.context.ocean import ocean
from port_ocean.core.ocean_types import ASYNC_GENERATOR_RESYNC_TYPE

from client import AikidoClient
from integration import ObjectKind, CodeRepoResourceConfig, VulnerabilityResourceConfig, UserResourceConfig


def initialize_aikido_client() -> AikidoClient:
    cfg = ocean.integration_config
    return AikidoClient(
        host=cfg["aikido_host"],
        client_id=cfg["client_id"],
        client_secret=cfg["client_secret"],
    )


@ocean.on_resync(ObjectKind.CODE_REPOSITORY)
async def on_resync_repos(kind: str) -> ASYNC_GENERATOR_RESYNC_TYPE:
    client = initialize_aikido_client()
    sel = cast(CodeRepoResourceConfig, event.resource_config).selector
    logger.info(f"Syncing code repos (include_inactive={sel.include_inactive})")
    async for repos in client.list_repositories(
            include_inactive=sel.include_inactive, per_page=sel.per_page):
        logger.info(f"Received repo batch of size: {len(repos)}")
        yield repos


@ocean.on_resync(ObjectKind.VULNERABILITY)
async def on_resync_vulns(kind: str) -> ASYNC_GENERATOR_RESYNC_TYPE:
    client = initialize_aikido_client()
    sel = cast(VulnerabilityResourceConfig, event.resource_config).selector
    logger.info(f"Syncing vulnerabilities for repo_id={sel.repo_id}")
    async for groups in client.list_open_issue_groups(repo_id=sel.repo_id, per_page=sel.per_page):
        logger.info(f"Received vulnerability batch of size: {len(groups)}")
        yield groups


@ocean.on_resync(ObjectKind.USER)
async def on_resync_users(kind: str) -> ASYNC_GENERATOR_RESYNC_TYPE:
    client = initialize_aikido_client()
    sel = cast(UserResourceConfig, event.resource_config).selector
    logger.info(f"Syncing users (team={sel.filter_team_id}, inactive={sel.include_inactive})")
    async for users in client.list_users(
            filter_team_id=sel.filter_team_id,
            include_inactive=sel.include_inactive,
            per_page=sel.per_page
    ):
        logger.info(f"Received user batch of size: {len(users)}")
        yield users
