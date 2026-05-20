from dataclasses import dataclass

from .coordinator import (
    MyLeonardoAdvancedCoordinator,
    MyLeonardoCoordinator,
    MyLeonardoEnergyCoordinator,
)


@dataclass
class MyLeonardoRuntimeData:
    """Runtime-only data attached to the config entry."""

    realtime: MyLeonardoCoordinator
    energy: MyLeonardoEnergyCoordinator
    advanced: MyLeonardoAdvancedCoordinator
