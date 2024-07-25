import logging
import os
import platform
import subprocess
import sys
import threading
import time
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk

import modules.serial_finder as serial_finder
from modules.classes import ElrsUploadResult
from modules.ELRS import ELRS
from modules.FC import FC
from modules.get_path import load_file
from modules.license import check_license
from modules.targets import get_targets

# https://nav.dl.sourceforge.net/project/libusb-win32/libusb-win32-releases/1.2.7.3/libusb-win32-devel-filter-1.2.7.3.exe

FILE_TYPES = {
    "config": [
        (
            "Text Files",
            "*.txt",
        )
    ],
    "fc_firmware": [
        (
            "Hex files",
            "*.hex",
        )
    ],
    "elrs_firmware": [
        (
            "Binary Files",
            "*.bin",
        )
    ],
}


def setup_logger():
    home_path = os.path.expanduser("~")
    file_path = os.path.join(
        home_path,
        "flasher_logs.txt",
    )

    logger = logging.getLogger("logger")
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(
        file_path,
        encoding="utf-8",
    )
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


logger = setup_logger()


class TkinterTextHandler(logging.Handler):
    def __init__(
        self,
        text_widget,
    ):
        super().__init__()
        self.text_widget = text_widget

    def write(
        self,
        message,
    ):
        logger.info(message)
        self.text_widget.insert(
            ctk.END,
            message,
        )
        self.text_widget.see(ctk.END)

    def emit(
        self,
        record,
    ):
        formatted_message = self.format(record)
        self.write_message(formatted_message)

    def isatty(
        self,
    ):
        return False


class FlasherApp(ctk.CTk):
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )
        self.title("ELRS Flasher")
        self.geometry("1000x700")
        self.old_com_ports = []
        self.initialize_ui()
        self.update_com_ports()
        self.resizable(False, False)
        self.setup_misc()
        sys.stdout = TkinterTextHandler(self.log_text)
        sys.stderr = TkinterTextHandler(self.log_text)
        elevate()

    def setup_misc(
        self,
    ):
        pass

    def initialize_ui(
        self,
    ):
        self.configure_grid()
        left_frame = self.create_left_frame()
        right_frame = self.create_right_frame()

        left_frame.pack(
            side=ctk.LEFT,
            padx=20,
            pady=20,
            fill=ctk.BOTH,
            expand=True,
        )
        right_frame.pack(
            side=ctk.RIGHT,
            padx=20,
            pady=20,
            fill=ctk.BOTH,
            expand=True,
        )

    def configure_grid(
        self,
    ):
        self.grid_columnconfigure(
            0,
            weight=1,
        )
        self.grid_columnconfigure(
            1,
            weight=1,
        )

    def create_left_frame(
        self,
    ):
        left_frame = ctk.CTkFrame(self)
        self.populate_left_frame(left_frame)
        return left_frame

    def create_right_frame(
        self,
    ):
        right_frame = ctk.CTkFrame(self)
        self.populate_right_frame(right_frame)
        return right_frame

    def create_flash_buttons(
        self,
        frame,
    ):
        buttons_frame = ctk.CTkFrame(frame)  # создаем новый фрейм для кнопок
        buttons_frame.pack(
            pady=10,
            fill="x",
        )  # добавляем его в родительский фрейм

        self.flash_elrs_btn = ctk.CTkButton(
            buttons_frame,
            text="Прошить ELRS",
            command=self.start_elrs_flash_thread,
        )
        self.flash_elrs_btn.pack(
            side=ctk.LEFT,
            padx=10,
            pady=50,
        )  # располагаем кнопку слева в новом фрейме

        self.flash_fc_button = ctk.CTkButton(
            buttons_frame,
            text="Прошить FC",
            command=self.start_fc_flash,
        )
        self.flash_fc_button.pack(
            side=ctk.RIGHT,
            padx=10,
            pady=50,
        )  # располагаем кнопку справа в новом фрейме

        # if os.name == "nt":  # Для Windows
        #     (
        #         current_ver,
        #         latest_ver,
        #     ) = update()
        # else:
        #     current_ver = 1
        #     latest_ver = 1
        # self.version_label = ctk.CTkLabel(
        #     buttons_frame,
        #     text=f"Текущая версия: {current_ver}"
        #     if current_ver is None or int(current_ver) >= int(latest_ver)
        #     else f"Текущая версия: {current_ver}\n(Доступно обновление)",
        # )
        # self.version_label.pack(pady=10)

    def populate_left_frame(
        self,
        frame,
    ):
        self.create_comport_dropdown(frame)
        self.create_separator(frame)
        self.create_elrs_firmware_section(frame)
        self.create_target_dropdown(frame)
        self.create_separator(frame)
        self.create_fc_firmware_section(frame)
        self.create_config_file_section(frame)
        self.create_flash_buttons(frame)  # новый метод для добавления кнопок

    def populate_right_frame(
        self,
        frame,
    ):
        log_label = ctk.CTkLabel(
            frame,
            text="Логи",
        )
        log_label.pack(
            pady=2,
            side=ctk.TOP,
        )
        self.log_text = ctk.CTkTextbox(
            frame,
            height=250,
            width=600,
        )
        self.log_text.pack(
            pady=2,
            expand=True,
            fill=ctk.BOTH,
        )

    def create_comport_dropdown(
        self,
        frame,
    ):
        comport_label = ctk.CTkLabel(
            frame,
            text="Выберите нужный COM порт",
        )
        comport_label.pack(pady=2)
        self.update_ports_btn = ctk.CTkButton(
            frame,
            text="Обновить COM-порты",
            command=self.update_com_ports,
        )
        self.update_ports_btn.pack(
            pady=10,
        )  # располагаем кнопку слева в новом фрейме
        self.comport_var = ctk.StringVar()
        self.comport_combobox = ctk.CTkComboBox(
            frame,
            variable=self.comport_var,
            values=serial_finder.serial_ports(),
            width=300,
        )
        self.comport_combobox.pack(pady=2)

    def create_separator(
        self,
        frame,
    ):
        separator = ttk.Separator(
            frame,
            orient="horizontal",
        )
        separator.pack(
            fill="x",
            pady=20,
        )

    def create_elrs_firmware_section(
        self,
        frame,
    ):
        file_label = ctk.CTkLabel(
            frame,
            text="Введите binding-фразу",
        )
        file_label.pack(pady=2)
        self.bindingPhraseVar = ctk.StringVar()
        phrase_entry = ctk.CTkEntry(
            frame,
            textvariable=self.bindingPhraseVar,
            width=300,
        )
        phrase_entry.pack(pady=2)

    def create_target_dropdown(
        self,
        frame,
    ):
        target_label = ctk.CTkLabel(
            frame,
            text="Выберите нужный таргет ELRS",
        )
        target_label.pack(pady=2)
        self.target_var = ctk.StringVar()
        target_dropdown = ctk.CTkComboBox(
            frame,
            variable=self.target_var,
            values=get_targets(),
            width=300,
        )
        target_dropdown.pack(pady=2)

    def create_flash_elrs_button(
        self,
        frame,
    ):
        self.flash_elrs_btn = ctk.CTkButton(
            frame,
            text="Прошить ELRS",
            command=self.start_elrs_flash_thread,
        )
        self.flash_elrs_btn.pack(pady=2)

    def create_fc_firmware_section(
        self,
        frame,
    ):
        fc_file_label = ctk.CTkLabel(
            frame,
            text="Выберите файл прошивки FC",
        )
        fc_file_label.pack(pady=2)
        self.fc_firmware_file_var = ctk.StringVar()
        fc_file_entry = ctk.CTkEntry(
            frame,
            textvariable=self.fc_firmware_file_var,
            width=300,
        )
        fc_file_entry.pack(pady=2)
        browse_fc_firmware_button = ctk.CTkButton(
            frame,
            text="Выбрать",
            command=self.browse_for_fc_firmware,
        )
        browse_fc_firmware_button.pack(pady=2)

    def create_config_file_section(
        self,
        frame,
    ):
        config_file_label = ctk.CTkLabel(
            frame,
            text="Выберите файл конфигурации FC",
        )
        config_file_label.pack(pady=2)
        self.config_file_var = ctk.StringVar()
        config_file_entry = ctk.CTkEntry(
            frame,
            textvariable=self.config_file_var,
            width=300,
        )
        config_file_entry.pack(pady=2)
        browse_config_file_button = ctk.CTkButton(
            frame,
            text="Выбрать",
            command=self.browse_for_config_file,
        )
        browse_config_file_button.pack(pady=2)

    def create_flash_fc_button(
        self,
        frame,
    ):
        self.flash_fc_button = ctk.CTkButton(
            frame,
            text="Прошить FC",
            command=self.start_fc_flash,
        )
        self.flash_fc_button.pack(pady=2)

    def start_elrs_flash_thread(
        self,
    ):
        if not check_license():
            exit()
        threading.Thread(
            target=self.flash_elrs,
            daemon=True,
        ).start()

    def start_fc_flash(
        self,
    ):
        if not check_license():
            exit()
        threading.Thread(
            target=self.flash_fc,
            daemon=True,
        ).start()

    def start_elrs_flash(
        self,
    ):
        threading.Thread(
            target=self.flash_elrs,
            daemon=True,
        ).start()

    def flash_fc(
        self,
    ):
        comVar = self.comport_var.get()
        firmware_file = self.fc_firmware_file_var.get()
        config_file = self.config_file_var.get()

        config_file = config_file if config_file != "" else None

        self.flash_fc_button.configure(state=ctk.DISABLED)
        self.flash_elrs_btn.configure(state=ctk.DISABLED)
        try:
            fc = FC(
                comVar,
                firmware_file,
                config_file,
            )
            if not firmware_file and config_file:
                print("Пытаемся залить конфиг")
                for i in reversed(range(15)):
                    print(f"{i}...")
                    time.sleep(1)
                fc.upload_config()
            elif firmware_file:
                print("Пробуем перейти в DFU")
                if fc.dfu():
                    print("Найдено DFU устройство")
                    fc.flash()
                    if config_file is not None:
                        for i in reversed(range(15)):
                            print(f"{i}...")
                            time.sleep(1)
                        fc.upload_config()
            else:
                messagebox.showwarning(
                    "Warning",
                    "Неверные параметры",
                )
        except Exception as ex:
            print(ex)
        finally:
            self.flash_fc_button.configure(state=ctk.NORMAL)
            self.flash_elrs_btn.configure(state=ctk.NORMAL)

    def flash_elrs(
        self,
    ):
        targetVar = self.target_var.get()
        bindingPhrase = self.bindingPhraseVar.get()
        comVar = self.comport_var.get()

        if not targetVar:
            print("Не выбран таргет")
            messagebox.showwarning(
                "Warning",
                "Выберите таргет",
            )
            return

        if not bindingPhrase:
            print("Не выбран файл прошивки")
            messagebox.showwarning(
                "Warning",
                "Введите binding-фразу",
            )
            return

        if not comVar:
            print("Не выбран серийный порт")
            messagebox.showwarning(
                "Warning",
                "Выберите COM порт",
            )
            return

        self.flash_fc_button.configure(state=ctk.DISABLED)
        self.flash_elrs_btn.configure(state=ctk.DISABLED)

        elrs = ELRS(
            target=targetVar,
            phrase=bindingPhrase,
            port=comVar,
            force=True,
            erase=False,
        )
        try:
            status = elrs.flash()
            if status == ElrsUploadResult.Success:
                print("Успешно")
            elif status == ElrsUploadResult.ErrorGeneral:
                print("Произошла ошибка при прошивке")
            elif status == ElrsUploadResult.ErrorMismatch:
                print("Произошла ошибка при выборе таргета")
        except Exception as ex:
            print(ex)
            self.flash_elrs_btn.configure(state=ctk.NORMAL)
            self.flash_fc_button.configure(state=ctk.NORMAL)
        finally:
            self.flash_elrs_btn.configure(state=ctk.NORMAL)
            self.flash_fc_button.configure(state=ctk.NORMAL)

    def choose_file(
        self,
        file_var,
        file_type,
    ):
        file_type_options = FILE_TYPES.get(
            file_type,
            [
                (
                    "All Files",
                    "*.*",
                )
            ],
        )
        if file := filedialog.askopenfilename(filetypes=file_type_options):
            file_var.set(file)

    def browse_for_config_file(
        self,
    ):
        self.choose_file(
            self.config_file_var,
            "config",
        )

    def browse_for_fc_firmware(
        self,
    ):
        self.choose_file(
            self.fc_firmware_file_var,
            "fc_firmware",
        )

    def update_com_ports(
        self,
    ):
        current_ports = serial_finder.serial_ports()
        if self.old_com_ports != current_ports:
            self.log_com_port_changes(current_ports)
            self.old_com_ports = current_ports
            self.comport_combobox.set(
                self.old_com_ports[0] if self.old_com_ports else ""
            )
            self.comport_combobox.configure(values=self.old_com_ports)
        else:
            print("Нет изменений")
        # self.after(
        #     500,
        #     self.update_com_ports,
        # )

    def log_com_port_changes(
        self,
        current_ports,
    ):
        if current_ports:
            print(f"[!] Обнаружено новое устройство {' '.join(current_ports)}")
        else:
            print("[!] Устройство было отключено")


def is_admin():
    import ctypes

    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def elevate():
    if platform.system() == "Windows":
        import ctypes

        command = [
            rf'{load_file("resources/install-filter.exe")}',
            "install",
            "--device=USB\\Vid_0483.Pid_df11.Rev_2200",
        ]
        if not is_admin():
            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                sys.executable,
                " ".join(sys.argv),
                None,
                1,
            )
            sys.exit()
        else:
            subprocess.call(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if hwnd := ctypes.windll.kernel32.GetConsoleWindow():
                ctypes.windll.user32.ShowWindow(
                    hwnd,
                    0,
                )


class ActivationApp(ctk.CTk):
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )
        self.title("Активация")
        self.geometry("300x200")
        self.success = False

        # Создание StringVar для хранения ключа
        self.key_var = ctk.StringVar()

        # Создание и размещение элементов
        self.entry = ctk.CTkEntry(
            self,
            textvariable=self.key_var,
        )
        self.entry.pack(
            side=ctk.TOP,
            pady=40,
        )

        self.button = ctk.CTkButton(
            self,
            text="Активировать",
            command=self.on_activate_click,
        )
        self.button.pack(
            side=ctk.TOP,
            pady=5,
        )

        self.label = ctk.CTkLabel(
            self,
            text="",
        )
        self.label.pack(
            side=ctk.TOP,
            pady=5,
        )

    def on_activate_click(
        self,
    ):
        key = self.key_var.get()
        if result := check_license(key):
            self.success = True
            self.destroy()
        else:
            self.label.configure(text="Активация не удалась!")


def request_key_and_check_license():
    app_activation = ActivationApp()
    app_activation.mainloop()
    return app_activation.success


if __name__ == "__main__":
    ctk.set_default_color_theme("green")
    result = check_license()

    if result is None or result is False:
        result = request_key_and_check_license()

    if result:
        app = FlasherApp()
        app.mainloop()
