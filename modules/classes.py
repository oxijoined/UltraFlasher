from enum import Enum
from typing import NamedTuple


class ElrsUploadResult:
    # SUCCESS
    Success = 0
    # ERROR: Unspecified
    ErrorGeneral = -1
    # ERROR: target mismatch
    ErrorMismatch = -2


class MCUType(Enum):
    STM32 = 0
    ESP32 = 1
    ESP8266 = 2


class DeviceType(Enum):
    TX = 0
    RX = 1
    TX_Backpack = 2
    VRx_Backpack = 3


class RadioType(Enum):
    SX127X = 0
    SX1280 = 1


class FirmwareOptions(NamedTuple):
    hasWiFi: bool
    hasBuzzer: bool
    mcuType: MCUType
    deviceType: DeviceType
    radioChip: RadioType
    luaName: str
    bootloader: str
    offset: int
    firmware: str
