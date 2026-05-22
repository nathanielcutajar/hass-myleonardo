from dataclasses import dataclass

from .coordinator import (
    MyLeonardoAdvancedCoordinator,
    MyLeonardoCoordinator,
    MyLeonardoEnergyCoordinator,
    MyLeonardoModbusCoordinator,
)


@dataclass
class MyLeonardoRuntimeData:
    """Runtime-only data attached to the config entry."""

    realtime: MyLeonardoCoordinator | MyLeonardoModbusCoordinator | None = None
    energy: MyLeonardoEnergyCoordinator | None = None
    advanced: MyLeonardoAdvancedCoordinator | None = None
