from modules.ELRS import ELRS
from modules.serial_finder import get_serial_port

elrs = ELRS(target="betafpv.rx_900.plain", phrase="010101", port=get_serial_port())
elrs.flash()
