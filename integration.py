from typing import Literal

from port_ocean.core.handlers.port_app_config.api import APIPortAppConfig
from port_ocean.core.handlers.port_app_config.models import PortAppConfig, ResourceConfig, Selector
from port_ocean.core.integrations.base import BaseIntegration
from pydantic.fields import Field


class ObjectKind:
    CODE_REPOSITORY = "CodeRepository"
    VULNERABILITY = "Vulnerability"


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


class AikidoPortAppConfig(PortAppConfig):
    resources: list[
        CodeRepoResourceConfig
        | VulnerabilityResourceConfig
        | ResourceConfig
        ] = Field(default_factory=list)


class AikidoIntegration(BaseIntegration):
    class AppConfigHandlerClass(APIPortAppConfig):
        CONFIG_CLASS = AikidoPortAppConfig
