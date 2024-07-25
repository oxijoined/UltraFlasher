import time

import serial

from fc_flasher.main import _get_dfu_devices, download


class FC:
    def __init__(
        self,
        port,
        file,
        configFile,
        baud_rate=115200,
        timeout=20,
    ) -> None:
        self.port = port
        self.file = file
        self.configFile = configFile
        self.baud_rate = baud_rate
        self.timeout = timeout

    def dfu(
        self,
    ):
        MAX_ATTEMPTS = 20
        TIMEOUT = 1

        if _get_dfu_devices():
            return True

        with serial.Serial(
            port=self.port,
            baudrate=self.baud_rate,
            timeout=self.timeout,
        ) as ser:
            ser.write("#\n".encode())
            time.sleep(TIMEOUT)
            ser.write("dfu\n".encode())
            try:
                ser.write("bl\n".encode())
            except:
                pass
            try:
                ser.close()
            except:
                pass

        for _ in range(MAX_ATTEMPTS):
            time.sleep(TIMEOUT)
            dfu_devices = _get_dfu_devices()

            if dfu_devices:
                return True

        raise Exception("Не удалось перейти в dfu")

    def flash(
        self,
    ):
        print(
            self.file,
            "firmware",
        )
        download(
            filename=self.file,
        )

    def upload_config(
        self,
    ):
        commands = []
        ser = None

        # Пытаемся 10 раз установить серийное соединение
        for attempt in range(
            1,
            11,
        ):  # 10 попыток
            try:
                ser = serial.Serial(
                    port=self.port,
                    baudrate=self.baud_rate,
                    timeout=self.timeout,
                )
                print(f"[+] Успешная инициализация на попытке {attempt}")
                break  # Если соединение установлено, выходим из цикла
            except Exception as e:
                print(
                    f"[!] Ошибка при последовательной инициализации на попытке {attempt}: {e}"
                )
                time.sleep(2)  # Ожидание перед следующей попыткой

        # Если соединение не установлено после всех попыток, возвращаем ошибку
        if ser is None:
            print("[!] Ошибка: не удалось установить серийное соединение")
            return

        # Загрузка команд из файла
        with open(
            self.configFile,
            "r",
            encoding="utf-8",
        ) as f:
            for line in f:
                if not line.startswith("#") and "dump" not in line and len(line) > 1:
                    commands.append(f"{line.strip()}")

        ser.write("#\n".encode())
        time.sleep(1)
        # Отправка команд
        for (
            i,
            command,
        ) in enumerate(commands):
            print(f"Загружено команд {i+1}/{len(commands)}")
            try:
                ser.write((f"{command}\n").encode())
                time.sleep(0.1)
            except Exception:
                print(f"[!] Ошибка при записи команды {command}")

        ser.close()
        print("Конфиг загружен")
        time.sleep(5)
