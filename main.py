import os
import sys
import threading
import time
from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import QThread, Signal

from modules import activation_ui, serial_finder, ui
from modules.classes import ElrsUploadResult
from modules.ELRS import ELRS
from modules.FC import FC
from modules.get_path import load_file
from modules.targets import get_targets


class QtTextHandler:

    def __init__(self):
        self.log_file_path = os.path.expanduser("~") + "/ultra_flasher.logs"
        with open(
            self.log_file_path, "w", encoding="utf-8"
        ) as f:  # Очистить файл логов при каждом запуске
            f.write("")

    def write(self, message):
        with open(self.log_file_path, "a", errors="ignore", encoding="utf-8") as f:
            f.write(message)

    def isatty(self):
        return False

    def flush(self):
        pass


class DaemonService(QThread):
    newText = Signal(str)

    def __init__(self, log_file_path):
        super().__init__()
        self.log_file_path = log_file_path
        self.last_position = 0

    def run(self):
        while True:
            with open(self.log_file_path, "r", encoding="utf-8", errors="ignore") as f:
                f.seek(self.last_position)
                new_text = f.read()
                self.last_position = f.tell()
            if new_text:
                self.newText.emit(new_text)
            time.sleep(0.5)


class UI(ui.Ui_Dialog):

    def __init__(self) -> None:
        super().__init__()
        self.old_com_ports = []
        self.mainWindow = QtWidgets.QMainWindow()
        self.mainWindow.setWindowIcon(QtGui.QIcon(load_file("resources/app.ico")))
        self.setupUi(self.mainWindow)
        self.setup_buttons()
        self.setup_misc()
        self.daemon_service = DaemonService(self.qt_text_handler.log_file_path)
        self.daemon_service.newText.connect(self.update_text)
        self.daemon_service.start()
        self.update_com_ports()
        self.mainWindow.show()

    def update_text(self, text):
        self.LogsTextBox.setPlainText(f"{self.LogsTextBox.toPlainText()}{text}")
        self.LogsTextBox.verticalScrollBar().setValue(
            self.LogsTextBox.verticalScrollBar().maximum()
        )

    def setup_misc(self):
        targets = get_targets()
        self.set_combo_values(self.TargetComboBox, targets, False)
        self.qt_text_handler = QtTextHandler()
        self.mainWindow.setWindowTitle("ELRS Flasher")
        sys.stdout = self.qt_text_handler
        sys.stderr = self.qt_text_handler

    def setup_buttons(self):
        self.ChooseFCConfigButton.clicked.connect(self.choose_fc_config)
        self.ChooseFCFirmwareButton.clicked.connect(self.choose_fc_firmware)
        self.UpdatePortsButton.clicked.connect(self.update_com_ports)
        self.FlashELRSButton.clicked.connect(self.start_elrs_thread)
        self.FlashFCButton.clicked.connect(self.start_fc_thread)

        self.FCConfigPath.setContextMenuPolicy(
            QtCore.Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.FCConfigPath.customContextMenuRequested.connect(
            lambda _: self.FCConfigPath.clear()
        )

        self.FCFirmwarePath.setContextMenuPolicy(
            QtCore.Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.FCFirmwarePath.customContextMenuRequested.connect(
            lambda _: self.FCFirmwarePath.clear()
        )

    def clear_fc_config(self):
        print(1)

    def start_elrs_thread(self):

        error_message = None

        if not self.PortComboBox.currentText():
            error_message = "Выберите COM порт перед продолжением."
        elif self.PortComboBox.currentText() not in serial_finder.serial_ports():
            error_message = "COM порт отключен."
            self.update_com_ports()
        elif not self.TargetComboBox.currentText():
            error_message = "Выберите таргет перед продолжением."
        elif not self.BindingPhraseInput.toPlainText():
            error_message = "Введите binding-фразу перед продолжением."

        if error_message:
            QtWidgets.QMessageBox.warning(self.mainWindow, "Ошибка", error_message)
            return

        threading.Thread(target=self.flash_elrs, daemon=True).start()

    def start_fc_thread(self):

        error_message = None

        if not self.PortComboBox.currentText():
            error_message = "Выберите COM порт перед продолжением."
        elif self.PortComboBox.currentText() not in serial_finder.serial_ports():
            error_message = "COM порт отключен."
            self.update_com_ports()
        elif (
            not self.FCConfigPath.toPlainText()
            and not self.FCFirmwarePath.toPlainText()
        ):
            error_message = "Неверные параметры."

        if error_message:
            QtWidgets.QMessageBox.warning(self.mainWindow, "Ошибка", error_message)
            return

        threading.Thread(target=self.flash_fc, daemon=True).start()

    def flash_fc(self):
        com = self.PortComboBox.currentText()
        firmwareFile = self.FCFirmwarePath.toPlainText()
        configFile = self.FCConfigPath.toPlainText()

        fc = FC(com, firmwareFile, configFile)

        if not firmwareFile and configFile:
            print("Пытаемся залить конфиг")
            for i in reversed(range(15)):
                print(f"{i}...")
                time.sleep(1)
            return fc.upload_config()

        elif firmwareFile:
            print("Пробуем перейти в DFU")
            if fc.dfu():
                print("Найдено DFU устройство")
                fc.flash()
                if configFile:
                    print("Пробуем залить конфиг")
                    for i in reversed(range(15)):
                        print(f"{i}...")
                        time.sleep(1)
                    fc.upload_config()

    def flash_elrs(self):
        target = self.TargetComboBox.currentText()
        binding_phrase = self.BindingPhraseInput.toPlainText()
        com = self.PortComboBox.currentText()

        elrs = ELRS(
            target=target, phrase=binding_phrase, port=com, force=True, erase=False
        )
        status = elrs.flash()
        if status == ElrsUploadResult.Success:
            print("Успешно")
        elif status == ElrsUploadResult.ErrorGeneral:
            print("Произошла ошибка при прошивке")
        elif status == ElrsUploadResult.ErrorMismatch:
            print("Произошла ошибка при выборе таргета")

    def set_combo_values(self, combo_box, new_values, select_last=True):
        combo_box.clear()
        combo_box.addItems(new_values)
        if new_values and select_last:
            combo_box.setCurrentIndex(0)

    def log_com_port_changes(
        self,
        current_ports,
    ):
        if current_ports:
            print(f"[!] Обнаружено новое устройство {' '.join(current_ports)}")
        else:
            print("[!] Устройство было отключено")

    def update_com_ports(self):
        current_ports = serial_finder.serial_ports()
        if self.old_com_ports != current_ports:
            self.log_com_port_changes(current_ports)
            self.old_com_ports = current_ports
            self.set_combo_values(self.PortComboBox, current_ports)

    def choose_fc_config(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(
            self.mainWindow,
            "Open file",
            str(Path.home()),
            filter=("Config file (*.txt)"),
        )
        if fname[0]:
            self.FCConfigPath.setText(fname[0])

    def choose_fc_firmware(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(
            self.mainWindow,
            "Open file",
            str(Path.home()),
            filter=("Firmware file (*.hex)"),
        )
        if fname[0]:
            self.FCFirmwarePath.setText(fname[0])


def main_window():
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    UI()
    sys.exit(app.exec())


if __name__ == "__main__":
    main_window()
