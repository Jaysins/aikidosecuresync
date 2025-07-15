from client import AikidoClient
from port_ocean.context.ocean import ocean


def create_aikido_client():
    cfg = ocean.integration_config

    return AikidoClient(
        host=cfg["aikido_host"],
        client_id=cfg["client_id"],
        client_secret=cfg["client_secret"],
    )
