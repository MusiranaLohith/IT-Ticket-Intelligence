from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DeploymentConfig:

    project_root: Path = Path(
        "/home/whiteblack/Documents/IT-Ticket-Triage-System"
    )

    application_name: str = (
        "IT Ticket Triage System"
    )

    application_version: str = (
        "deployment-prototype-1.0"
    )

    host: str = "127.0.0.1"

    port: int = 8000

    production_ready: bool = False

    production_authorization: str = (
        "NOT_ESTABLISHED"
    )

    @property
    def deployment_root(self) -> Path:
        return self.project_root / "deployment"

    @property
    def packaged_runtime_root(self) -> Path:
        return (
            self.project_root
            / "modeling"
            / "FMP"
            / "deployment"
            / "runtime"
        )


CONFIG = DeploymentConfig()