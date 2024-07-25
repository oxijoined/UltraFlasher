import hashlib
import json
import mmap
import sys
import tempfile
import time/
from os.path import dirname
from random import randint

import jmespath
import requests

from external.esptool import esptool
from modules import BFinitPassthrough, UnifiedConfig
from modules.classes import (
    DeviceType,
    ElrsUploadResult,
    FirmwareOptions,
    MCUType,
    RadioType,
)
from modules.get_path import load_file

sys.path.append(dirname(__file__) + "/external/esptool")

sys.path.append(dirname(__file__) + "/external")


class ELRS:
    def __init__(
        self,
        target: str,
        phrase: str,
        port: str,
        force: bool = False,
        erase=True,
    ) -> None:
        self.target = target
        self.target_json = json.loads(
            open(
                load_file("resources/targets.json"),
                "r",
            ).read()
        )
        self.phrase = phrase
        self.port = port
        self.baud = 420000
        self.mode = "uploadforce"
        self.erase = erase
        self.force = force
        self.config = jmespath.search(
            ".".join(
                map(
                    lambda s: f'"{s}"',
                    self.target.split("."),
                )
            ),
            self.target_json,
        )
        self.accept = self.config.get("prior_target_name")
        self.firmware_link = f"https://okcu.ru/elrs-web-flasher/firmware/3.2.1/FCC/{self.config.get('firmware')}/firmware.bin"
        print(self.firmware_link)
        self.options = FirmwareOptions(
            self.config["platform"] != "stm32",
            "features" in self.config and "buzzer" in self.config["features"],
            (
                MCUType.STM32
                if self.config["platform"] == "stm32"
                else (
                    MCUType.ESP32
                    if self.config["platform"] == "esp32"
                    else MCUType.ESP8266
                )
            ),
            DeviceType.RX if ".rx_" in self.target else DeviceType.TX,
            RadioType.SX127X if "_900." in self.target else RadioType.SX1280,
            self.config["lua_name"] if "lua_name" in self.config else "",
            self.config["stlink"]["bootloader"] if "stlink" in self.config else "",
            self.config["stlink"]["offset"] if "stlink" in self.config else 0,
            self.config["firmware"],
        )
        self.file = self.download_firmware()
        self.mm = mmap.mmap(
            self.file.fileno(),
            0,
        )
        self.pos = self.get_hardware(self.mm)
        self.patch_firmware()
        self.file.close()
        self.target = self.config.get("firmware")
        self.file = self.file.name

    def generateUID(
        self,
    ):
        uid = [int(item) if item.isdigit() else -1 for item in self.phrase.split(",")]
        if len(uid) == 6 and all(ele >= 0 and ele < 256 for ele in uid):
            uid = bytes(uid)
        else:
            uid = hashlib.md5(
                ('-DMY_BINDING_PHRASE="' + self.phrase + '"').encode()
            ).digest()[0:6]
        return uid

    def patch_uid(
        self,
    ):
        self.mm[pos] = 1
        self.mm[pos + 1 : pos + 7] = self.generateUID()
        pos += 7
        return pos

    def patch_unified(
        self,
    ):
        json_flags = {}
        json_flags["uid"] = [x for x in self.generateUID()]
        # json_flags["domain"] = 1
        json_flags["wifi-on-interval"] = 20

        json_flags["flash-discriminator"] = randint(
            1,
            2**32 - 1,
        )

        UnifiedConfig.doConfiguration(
            self.file,
            json.JSONEncoder().encode(json_flags),
            self.target,
            "tx" if self.options.deviceType is DeviceType.TX else "rx",
            "2400" if self.options.radioChip is RadioType.SX1280 else "900",
            (
                "32"
                if self.options.mcuType is MCUType.ESP32
                and self.options.deviceType is DeviceType.RX
                else ""
            ),
            self.options.luaName,
        )

    def patch_firmware(
        self,
    ):
        if self.options.mcuType is MCUType.STM32:
            raise Exception("STM32 IS NOT SUPPORTED YET")
        else:
            self.patch_unified()

    def get_hardware(
        self,
        mm,
    ):
        pos = mm.find(b"\xBE\xEF\xBA\xBE\xCA\xFE\xF0\x0D")
        if pos != -1:
            pos += 8 + 2  # Skip magic & version

        return pos

    def download_firmware(
        self,
    ):
        try:
            with tempfile.NamedTemporaryFile(
                prefix="elrs_firmware_",
                suffix=".bin",
                mode="wb",
                delete=False,
            ) as f:
                path = f.name
            response = requests.get(self.firmware_link)
            if response.status_code == 200:
                with open(
                    path,
                    "wb",
                ) as f:
                    f.write(response.content)
                print("Прошивка успешно скачана")
                return open(
                    path,
                    "r+b",
                )
            else:
                print(response.status_code)
                raise Exception("Ошибка при скачивании прошивки")
        except Exception as ex:
            print(ex)

    def upload_esp8266_bf(
        self,
    ):
        retval = BFinitPassthrough.main(
            [
                "-p",
                self.port,
                "-b",
                str(self.baud),
                "-r",
                self.options.firmware,
                "-a",
                self.mode,
                "--accept",
                self.accept,
            ]
        )

        if retval != ElrsUploadResult.Success:
            return retval
        try:
            cmd = [
                "--passthrough",
                "--chip",
                "esp8266",
                "--port",
                self.port,
                "--baud",
                str(self.baud),
                "--before",
                "no_reset",
                "--after",
                "soft_reset",
                "--no-stub",
                "write_flash",
            ]
            if self.erase:
                cmd.append("--erase-all")
            cmd.extend(
                [
                    "0x0000",
                    self.file,
                ]
            )
            esptool.main(cmd)
        except Exception as ex:
            print(ex)
            return ElrsUploadResult.ErrorGeneral
        return ElrsUploadResult.Success

    def upload_esp32_bf(
        self,
    ):
        retval = BFinitPassthrough.main(
            [
                "-p",
                self.port,
                "-b",
                str(self.baud),
                "-r",
                self.options.firmware,
                "-a",
                self.mode,
            ]
        )
        if retval != ElrsUploadResult.Success:
            return retval
        try:
            esptool.main(
                [
                    "--passthrough",
                    "--chip",
                    "esp32",
                    "--port",
                    self.port,
                    "--baud",
                    str(self.baud),
                    "--before",
                    "no_reset",
                    "--after",
                    "hard_reset",
                    "write_flash",
                    "-z",
                    "--flash_mode",
                    "dio",
                    "--flash_freq",
                    "40m",
                    "--flash_size",
                    "detect",
                    "0x10000",
                    self.file,
                ]
            )
        except Exception as ex:
            print(ex)
            return ElrsUploadResult.ErrorGeneral
        return ElrsUploadResult.Success

    def flash(
        self,
    ):
        self.baud = 420000
        for i in reversed(range(10)):
            print(f"{i}...")
            time.sleep(1)

        if self.options.mcuType == MCUType.ESP8266:
            return self.upload_esp8266_bf()
        elif self.options.mcuType == MCUType.ESP32:
            return self.upload_esp32_bf()

        return ElrsUploadResult.ErrorGeneral
