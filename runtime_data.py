from dataclasses import dataclass

from .coordinator import (
    MyLeonardoAdvancedCompleteCoordinator,
    MyLeonardoAdvancedCoordinator,
    MyLeonardoCoordinator,
    MyLeonardoEnergyCoordinator,
    MyLeonardoMonthlyEnergyCoordinator,
    MyLeonardoModbusCoordinator,
)


@dataclass
class MyLeonardoRuntimeData:
    """Runtime-only data attached to the config entry."""

    realtime: MyLeonardoCoordinator | MyLeonardoModbusCoordinator | None = None
    energy: MyLeonardoEnergyCoordinator | None = None
    energy_monthly: MyLeonardoMonthlyEnergyCoordinator | None = None
    advanced: MyLeonardoAdvancedCoordinator | None = None
    advanced_complete: MyLeonardoAdvancedCompleteCoordinator | None = None
