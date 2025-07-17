from typing import cast

from loguru import logger
from port_ocean.context.event import event
from port_ocean.context.ocean import ocean
from port_ocean.core.ocean_types import ASYNC_GENERATOR_RESYNC_TYPE
from initialize_client import create_aikido_client
from kinds import Kinds
from integration import AikidoRepositoryResourceConfig, VulnerabilityResourceConfig
from webhook_processors.vulnerability_webhook_processor import VulnerabilityWebhookProcessor


@ocean.on_resync(Kinds.REPOSITORY)
async def on_resync_repos(kind: str) -> ASYNC_GENERATOR_RESYNC_TYPE:
    client = create_aikido_client()
    sel = cast(AikidoRepositoryResourceConfig, event.resource_config).selector
    logger.info(f"Syncing code repos (include_inactive={sel.include_inactive})")
    async for repos in client.list_repositories(
            include_inactive=sel.include_inactive, per_page=sel.per_page):
        logger.info(f"Received repo batch of size: {len(repos)}")
        yield repos


@ocean.on_resync(Kinds.VULNERABILITY)
async def on_resync_vulns(kind: str) -> ASYNC_GENERATOR_RESYNC_TYPE:
    client = create_aikido_client()
    sel = cast(VulnerabilityResourceConfig, event.resource_config).selector

    issues = await client.export_issues(
        filter_status="all",
        filter_issue_group_id=sel.filter_issue_group_id
    )
    yield issues

ocean.add_webhook_processor("/webhook", VulnerabilityWebhookProcessor)
