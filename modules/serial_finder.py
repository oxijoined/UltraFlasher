import contextlib
import glob
import sys

import serial


def serial_ports():
    """Список доступных последовательных портов

    :raises Exception:
        На неподдерживаемых или неизвестных платформах
    :returns:
        Список доступных последовательных портов в системе
    """
    result = []
    ports = []

    with contextlib.suppress(ImportError):
        from serial.tools.list_ports import comports

        if comports:
            __ports = list(comports())
            ports.extend(
                port.device
                for port in __ports
                if (
                    (
                        port.manufacturer
                        and port.manufacturer
                        in [
                            "FTDI",
                            "Betaflight",
                        ]
                    )
                    or (port.product and "STM32" in port.product)
                    or (port.vid and port.vid == 0x0483)
                )
            )
    if not ports:
        platform = sys.platform.lower()
        if platform.startswith("win"):
            ports = [f"COM{i + 1}" for i in range(256)]
        elif platform.startswith("linux") or platform.startswith("cygwin"):
            ports = glob.glob("/dev/ttyACM*")
            ports.extend(glob.glob("/dev/ttyUSB*"))
        elif platform.startswith("darwin"):
            ports = glob.glob("/dev/tty.usbmodem*")
            ports.extend(glob.glob("/dev/tty.SLAB*"))
            ports.extend(glob.glob("/dev/tty.usbserial*"))
        else:
            raise Exception("Неподдерживаемая платформа")

    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (
            OSError,
            serial.SerialException,
        ) as error:
            if "permission denied" in str(error).lower():
                raise Exception(
                    "У вас нет прав на использование последовательного порта!"
                ) from error
    result.reverse()
    return result


def get_serial_port(
    debug=True,
):
    result = serial_ports()
    if debug:
        for port in result:
            print(f"  {port}")

    if len(result) == 0:
        raise Exception(
            "Не обнаружено подходящего последовательного порта или порт уже открыт"
        )

    return result[0]


if __name__ == "__main__":
    results = get_serial_port(True)
