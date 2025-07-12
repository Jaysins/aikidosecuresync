from typing import Literal

from port_ocean.core.handlers.port_app_config.api import APIPortAppConfig
from port_ocean.core.handlers.port_app_config.models import PortAppConfig, ResourceConfig, Selector
from port_ocean.core.integrations.base import BaseIntegration
from pydantic.fields import Field


class ObjectKind:
    CODE_REPOSITORY = "CodeRepository"
    VULNERABILITY = "Vulnerability"
    USER = "User"
    ISSUE = "Issue"
    OPEN_ISSUE_GROUP = "OpenIssueGroup"


class RepositorySelector(Selector):
    include_inactive: bool = Field(
        default=False,
        description="Include inactive repositories",
    )
    per_page: int = Field(
        default=20,
        description="Items per page (10–200)",
    )


class VulnerabilitySelector(Selector):
    repo_id: int | None = Field(
        alias="filter_code_repo_id",
        default=None,
        description="Filter vulnerabilities by Code Repository ID",
    )
    per_page: int = Field(
        default=20,
        description="Items per page (10–20)",
    )


class CodeRepoResourceConfig(ResourceConfig):
    selector: RepositorySelector
    kind: Literal["CodeRepository"]


class VulnerabilityResourceConfig(ResourceConfig):
    selector: VulnerabilitySelector
    kind: Literal["Vulnerability"]


class UserSelector(Selector):
    filter_team_id: int | None = Field(
        alias="filter_team_id",
        default=None,
        description="Only users in this team"
    )
    include_inactive: int = Field(
        default=0,
        description="0 to exclude inactive, 1 to include"
    )
    per_page: int = Field(
        default=20,
        description="Items per page"
    )


class AikidoIssueSelector(Selector):
    format: str = Field(
        default="json",
        description="Response format (default: json)"
    )
    filter_status: str = Field(
        default="all",
        description="Filter by status (default: all)"
    )
    filter_team_id: int = Field(
        default=None,
        description="Filter by Team ID"
    )
    filter_issue_group_id: int = Field(
        default=None,
        description="Filter by Issue Group ID"
    )
    filter_code_repo_id: int = Field(
        default=None,
        description="Filter by Code Repository ID"
    )
    filter_container_repo_id: int = Field(
        default=None,
        description="Filter by Container Repository ID"
    )
    filter_container_repo_name: str = Field(
        default=None,
        description="Filter by Container Repository Name"
    )
    filter_domain_id: int = Field(
        default=None,
        description="Filter by Domain ID"
    )
    filter_issue_type: str = Field(
        default=None,
        description="Filter by Issue Type"
    )
    filter_severities: str = Field(
        default=None,
        description="Filter by severities (comma-separated)"
    )
    per_page: int = Field(
        default=20,
        description="Items per page"
    )


class UserResourceConfig(ResourceConfig):
    selector: UserSelector
    kind: Literal["User"]


class AikidoIssueResourceConfig(ResourceConfig):
    selector: AikidoIssueSelector
    kind: Literal["Issue"]


class AikidoPortAppConfig(PortAppConfig):
    resources: list[
        CodeRepoResourceConfig
        | VulnerabilityResourceConfig
        | UserResourceConfig
        | AikidoIssueResourceConfig
        ] = Field(default_factory=list)


class AikidoIntegration(BaseIntegration):
    class AppConfigHandlerClass(APIPortAppConfig):
        CONFIG_CLASS = AikidoPortAppConfig
