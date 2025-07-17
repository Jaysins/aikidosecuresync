from typing import Literal

from port_ocean.core.handlers.port_app_config.api import APIPortAppConfig
from port_ocean.core.handlers.port_app_config.models import PortAppConfig, ResourceConfig, Selector
from port_ocean.core.integrations.base import BaseIntegration
from pydantic.fields import Field


class RepositorySelector(Selector):
    include_inactive: bool = Field(
        default=False,
        description="Include inactive repositories",
    )
    per_page: int = Field(
        default=100,
        description="Items per page (10–200)",
    )


class VulnerabilitySelector(Selector):
    format: Literal["json", "csv"] = Field(
        default="json",
        description="Response format",
    )
    filter_status: Literal["all", "open", "ignored", "snoozed", "closed"] = Field(
        default="all",
        description="Filter issues by status",
    )
    filter_team_id: int | None = Field(
        default=None,
        description="Filter issues by team ID",
    )
    filter_issue_group_id: int | None = Field(
        default=None,
        description="Filter issues by issue group ID",
    )
    filter_code_repo_id: int | None = Field(
        default=None,
        description="Filter issues by code repository ID",
    )
    filter_container_repo_id: int | None = Field(
        default=None,
        description="Filter issues by container repository ID",
    )
    filter_container_repo_name: str | None = Field(
        default=None,
        description="Filter issues by container repository name",
    )
    filter_domain_id: int | None = Field(
        default=None,
        description="Filter issues by domain ID",
    )
    filter_issue_type: str | None = Field(
        default=None,
        description="Filter issues by type (e.g. open_source, cloud, iac)",
    )
    filter_severities: str | None = Field(
        default=None,
        description="Comma‑separated list of severities to include",
    )


class AikidoRepositoryResourceConfig(ResourceConfig):
    selector: RepositorySelector
    kind: Literal["repository"]


class VulnerabilityResourceConfig(ResourceConfig):
    selector: VulnerabilitySelector
    kind: Literal["vulnerability"]


class AikidoPortAppConfig(PortAppConfig):
    resources: list[
        AikidoRepositoryResourceConfig
        | VulnerabilityResourceConfig
        ] = Field(default_factory=list)


class AikidoIntegration(BaseIntegration):
    class AppConfigHandlerClass(APIPortAppConfig):
        CONFIG_CLASS = AikidoPortAppConfig
