"""Shared layer subpackage for the ``system`` feature folder."""

from modules.shared.src.system.contract_system_aggregate import ISystemAggregate
from modules.shared.src.system.contract_system_protocol import (
    ISystemConfigurationProtocol,
    ISystemDoctorProtocol,
    ISystemJobProtocol,
    IWorkspaceProtocol,
)

__all__ = [
    "ISystemAggregate",
    "ISystemConfigurationProtocol",
    "ISystemDoctorProtocol",
    "ISystemJobProtocol",
    "IWorkspaceProtocol",
]
