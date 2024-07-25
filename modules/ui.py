# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'gui.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    Qt,
    QTime,
    QUrl,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFrame,
    QGroupBox,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QTabWidget,
    QTextEdit,
    QWidget,
)

import images_rc


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName("Dialog")
        Dialog.resize(622, 424)
        font = QFont()
        font.setFamilies(["Sitka Small Semibold"])
        font.setPointSize(9)
        font.setBold(True)
        font.setItalic(False)
        Dialog.setFont(font)
        Dialog.setStyleSheet(
            "background-color: rgba(36,36,36,255);\n" "color: rgb(255,255,255);"
        )
        self.TABS = QTabWidget(Dialog)
        self.TABS.setObjectName("TABS")
        self.TABS.setGeometry(QRect(0, 0, 631, 451))
        self.TABS.setMinimumSize(QSize(631, 0))
        self.TABS.setAutoFillBackground(False)
        self.TABS.setStyleSheet("")
        self.TABS.setTabPosition(QTabWidget.North)
        self.TABS.setTabShape(QTabWidget.Rounded)
        self.TABS.setElideMode(Qt.ElideRight)
        self.TABS.setDocumentMode(True)
        self.flashTab = QWidget()
        self.flashTab.setObjectName("flashTab")
        self.ElrsGroup = QGroupBox(self.flashTab)
        self.ElrsGroup.setObjectName("ElrsGroup")
        self.ElrsGroup.setGeometry(QRect(10, 80, 280, 150))
        self.ElrsGroup.setStyleSheet("border-radius: 4px;")
        self.FlashELRSButton = QPushButton(self.ElrsGroup)
        self.FlashELRSButton.setObjectName("FlashELRSButton")
        self.FlashELRSButton.setGeometry(QRect(20, 100, 240, 30))
        self.FlashELRSButton.setStyleSheet(
            "QPushButton {\n"
            "	border-radius: 4px;\n"
            "	background-color: #2fa572; \n"
            "}\n"
            "QPushButton:hover{\n"
            "	border-radius: 4px;\n"
            "	background-color: rgba(16,106,67,255);\n"
            "}"
        )
        self.TargetComboBox = QComboBox(self.ElrsGroup)
        self.TargetComboBox.setObjectName("TargetComboBox")
        self.TargetComboBox.setGeometry(QRect(20, 61, 240, 31))
        self.TargetComboBox.setStyleSheet(
            "background-color: rgba(59,59,59,255); border-radius: 4px;"
        )
        self.BindingPhraseInput = QPlainTextEdit(self.ElrsGroup)
        self.BindingPhraseInput.setObjectName("BindingPhraseInput")
        self.BindingPhraseInput.setGeometry(QRect(20, 20, 240, 31))
        self.BindingPhraseInput.setStyleSheet(
            "background-color: rgba(59,59,59,255); border-radius: 4px;"
        )
        self.BindingPhraseInput.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.FCGroup = QGroupBox(self.flashTab)
        self.FCGroup.setObjectName("FCGroup")
        self.FCGroup.setGeometry(QRect(10, 240, 280, 150))
        self.FCGroup.setStyleSheet("border-radius: 4px;")
        self.FlashFCButton = QPushButton(self.FCGroup)
        self.FlashFCButton.setObjectName("FlashFCButton")
        self.FlashFCButton.setGeometry(QRect(20, 100, 240, 30))
        self.FlashFCButton.setStyleSheet(
            "QPushButton {\n"
            "	border-radius: 4px;\n"
            "	background-color: #2fa572; \n"
            "}\n"
            "QPushButton:hover{\n"
            "	border-radius: 4px;\n"
            "	background-color: rgba(16,106,67,255);\n"
            "}"
        )
        self.FCConfigPath = QTextEdit(self.FCGroup)
        self.FCConfigPath.setObjectName("FCConfigPath")
        self.FCConfigPath.setGeometry(QRect(20, 60, 211, 30))
        self.FCConfigPath.setStyleSheet(
            "background-color: rgba(59,59,59,255);border-radius: 4px;"
        )
        self.FCConfigPath.setTextInteractionFlags(Qt.NoTextInteraction)
        self.FCFirmwarePath = QTextEdit(self.FCGroup)
        self.FCFirmwarePath.setObjectName("FCFirmwarePath")
        self.FCFirmwarePath.setGeometry(QRect(20, 20, 211, 30))
        self.FCFirmwarePath.setStyleSheet(
            "background-color: rgba(59,59,59,255);\n" "border-radius: 4px;"
        )
        self.FCFirmwarePath.setTextInteractionFlags(Qt.NoTextInteraction)
        self.ChooseFCConfigButton = QPushButton(self.FCGroup)
        self.ChooseFCConfigButton.setObjectName("ChooseFCConfigButton")
        self.ChooseFCConfigButton.setGeometry(QRect(220, 60, 40, 30))
        self.ChooseFCConfigButton.setStyleSheet(
            "QPushButton {\n"
            "	font: 20pt;\n"
            "	text-align: center;\n"
            "	border-radius: 4px;\n"
            "	background-color: #2fa572; \n"
            "}\n"
            "QPushButton:hover{\n"
            "	border-radius: 4px;\n"
            "	background-color: rgba(16,106,67,255);\n"
            "}"
        )
        self.ChooseFCFirmwareButton = QPushButton(self.FCGroup)
        self.ChooseFCFirmwareButton.setObjectName("ChooseFCFirmwareButton")
        self.ChooseFCFirmwareButton.setGeometry(QRect(220, 20, 40, 30))
        self.ChooseFCFirmwareButton.setStyleSheet(
            "QPushButton {\n"
            "	font: 20pt;\n"
            "	text-align: center;\n"
            "	border-radius: 4px;\n"
            "	background-color: #2fa572; \n"
            "}\n"
            "QPushButton:hover{\n"
            "	border-radius: 4px;\n"
            "	background-color: rgba(16,106,67,255);\n"
            "}"
        )
        self.LogsGroup = QGroupBox(self.flashTab)
        self.LogsGroup.setObjectName("LogsGroup")
        self.LogsGroup.setGeometry(QRect(300, 10, 310, 390))
        self.LogsGroup.setAutoFillBackground(False)
        self.LogsGroup.setStyleSheet("border-radius: 4px;")
        self.LogsTextBox = QTextEdit(self.LogsGroup)
        self.LogsTextBox.setObjectName("LogsTextBox")
        self.LogsTextBox.setGeometry(QRect(10, 20, 281, 351))
        self.LogsTextBox.setStyleSheet(
            "background-color: rgba(59,59,59,255); border-radius: 4px;"
        )
        self.LogsTextBox.setTextInteractionFlags(
            Qt.TextSelectableByKeyboard | Qt.TextSelectableByMouse
        )
        self.TABS.addTab(self.flashTab, "")
        self.motorsTab = QWidget()
        self.motorsTab.setObjectName("motorsTab")
        self.DroneImage = QLabel(self.motorsTab)
        self.DroneImage.setObjectName("DroneImage")
        self.DroneImage.setGeometry(QRect(300, 10, 281, 371))
        self.DroneImage.setStyleSheet("image: url(:/svgs/images/Group.svg);")
        self.FirstMotorButton = QPushButton(self.motorsTab)
        self.FirstMotorButton.setObjectName("FirstMotorButton")
        self.FirstMotorButton.setGeometry(QRect(480, 230, 70, 70))
        self.FirstMotorButton.setStyleSheet(
            "QPushButton {\n"
            "    color: #333;\n"
            "    border-radius: 20px;\n"
            "    border-style: outset;\n"
            "    background-color: #2fa572; \n"
            "    padding: 5px;\n"
            "    }\n"
            "\n"
            "QPushButton:hover {\n"
            "    background-color: rgba(16,106,67,255);\n"
            "    }\n"
            "\n"
            ""
        )
        self.SecondMotorButton = QPushButton(self.motorsTab)
        self.SecondMotorButton.setObjectName("SecondMotorButton")
        self.SecondMotorButton.setGeometry(QRect(480, 80, 70, 70))
        self.SecondMotorButton.setStyleSheet(
            "QPushButton {\n"
            "    color: #333;\n"
            "    border-radius: 20px;\n"
            "    border-style: outset;\n"
            "    background-color: #2fa572; \n"
            "    padding: 5px;\n"
            "    }\n"
            "\n"
            "QPushButton:hover {\n"
            "    background-color: rgba(16,106,67,255);\n"
            "    }\n"
            "\n"
            ""
        )
        self.FourthMotorButton = QPushButton(self.motorsTab)
        self.FourthMotorButton.setObjectName("FourthMotorButton")
        self.FourthMotorButton.setGeometry(QRect(330, 80, 70, 70))
        self.FourthMotorButton.setStyleSheet(
            "QPushButton {\n"
            "    color: #333;\n"
            "    border-radius: 20px;\n"
            "    border-style: outset;\n"
            "    background-color: #2fa572; \n"
            "    padding: 5px;\n"
            "    }\n"
            "\n"
            "QPushButton:hover {\n"
            "    background-color: rgba(16,106,67,255);\n"
            "    }\n"
            "\n"
            ""
        )
        self.ThirdMotorButton = QPushButton(self.motorsTab)
        self.ThirdMotorButton.setObjectName("ThirdMotorButton")
        self.ThirdMotorButton.setGeometry(QRect(330, 230, 70, 70))
        self.ThirdMotorButton.setStyleSheet(
            "QPushButton {\n"
            "    color: #333;\n"
            "    border-radius: 20px;\n"
            "    border-style: outset;\n"
            "    background-color: #2fa572; \n"
            "    padding: 5px;\n"
            "    }\n"
            "\n"
            "QPushButton:hover {\n"
            "    background-color: rgba(16,106,67,255);\n"
            "    }\n"
            "\n"
            ""
        )
        self.pushButton = QPushButton(self.motorsTab)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setGeometry(QRect(390, 340, 100, 32))
        self.pushButton.setStyleSheet(
            "QPushButton {\n"
            "	border-radius: 4px;\n"
            "	background-color: #2fa572; \n"
            "}\n"
            "QPushButton:hover{\n"
            "	border-radius: 4px;\n"
            "	background-color: rgba(16,106,67,255);\n"
            "}"
        )
        self.TABS.addTab(self.motorsTab, "")
        self.PortsGroup = QFrame(Dialog)
        self.PortsGroup.setObjectName("PortsGroup")
        self.PortsGroup.setGeometry(QRect(10, 40, 280, 60))
        self.PortsGroup.setStyleSheet("border-radius: 4px;")
        self.PortComboBox = QComboBox(self.PortsGroup)
        self.PortComboBox.setObjectName("PortComboBox")
        self.PortComboBox.setGeometry(QRect(20, 20, 221, 30))
        self.PortComboBox.setStyleSheet(
            "background-color: rgba(59,59,59,255); border-radius: 4px;"
        )
        self.UpdatePortsButton = QPushButton(self.PortsGroup)
        self.UpdatePortsButton.setObjectName("UpdatePortsButton")
        self.UpdatePortsButton.setGeometry(QRect(220, 20, 41, 31))
        self.UpdatePortsButton.setStyleSheet(
            "QPushButton {\n"
            "	font: 25pt;\n"
            "	text-align: center;\n"
            "	border-radius: 4px;\n"
            "	background-color: #2fa572; \n"
            "}\n"
            "QPushButton:hover{\n"
            "	border-radius: 4px;\n"
            "	background-color: rgba(16,106,67,255);\n"
            "}"
        )

        self.retranslateUi(Dialog)

        self.TABS.setCurrentIndex(1)

        QMetaObject.connectSlotsByName(Dialog)

    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", "Dialog", None))
        self.ElrsGroup.setTitle("")
        self.FlashELRSButton.setText(
            QCoreApplication.translate(
                "Dialog", "\u041f\u0440\u043e\u0448\u0438\u0442\u044c ELRS", None
            )
        )
        self.TargetComboBox.setCurrentText("")
        self.TargetComboBox.setPlaceholderText(
            QCoreApplication.translate(
                "Dialog", "\u0422\u0430\u0440\u0433\u0435\u0442 ELRS", None
            )
        )
        self.BindingPhraseInput.setPlaceholderText(
            QCoreApplication.translate(
                "Dialog", "Binding-\u0444\u0440\u0430\u0437\u0430", None
            )
        )
        self.FCGroup.setTitle("")
        self.FlashFCButton.setText(
            QCoreApplication.translate(
                "Dialog", "\u041f\u0440\u043e\u0448\u0438\u0442\u044c FC", None
            )
        )
        self.FCConfigPath.setPlaceholderText(
            QCoreApplication.translate(
                "Dialog",
                "\u0424\u0430\u0439\u043b \u043a\u043e\u043d\u0444\u0438\u0433\u0430",
                None,
            )
        )
        self.FCFirmwarePath.setPlaceholderText(
            QCoreApplication.translate(
                "Dialog",
                "\u0424\u0430\u0439\u043b \u043f\u0440\u043e\u0448\u0438\u0432\u043a\u0438",
                None,
            )
        )
        self.ChooseFCConfigButton.setText(
            QCoreApplication.translate("Dialog", "\u29eb", None)
        )
        self.ChooseFCFirmwareButton.setText(
            QCoreApplication.translate("Dialog", "\u29eb", None)
        )
        self.LogsGroup.setTitle(
            QCoreApplication.translate("Dialog", "\u041b\u043e\u0433\u0438", None)
        )
        self.TABS.setTabText(
            self.TABS.indexOf(self.flashTab),
            QCoreApplication.translate(
                "Dialog", "\u041f\u0440\u043e\u0448\u0438\u0432\u043a\u0430", None
            ),
        )
        self.DroneImage.setText("")
        self.FirstMotorButton.setText(QCoreApplication.translate("Dialog", "1", None))
        self.SecondMotorButton.setText(QCoreApplication.translate("Dialog", "2", None))
        self.FourthMotorButton.setText(QCoreApplication.translate("Dialog", "4", None))
        self.ThirdMotorButton.setText(QCoreApplication.translate("Dialog", "3", None))
        self.pushButton.setText(QCoreApplication.translate("Dialog", "Start", None))
        self.TABS.setTabText(
            self.TABS.indexOf(self.motorsTab),
            QCoreApplication.translate(
                "Dialog", "\u041c\u043e\u0442\u043e\u0440\u044b", None
            ),
        )
        self.PortComboBox.setPlaceholderText(
            QCoreApplication.translate("Dialog", "COM-\u041f\u043e\u0440\u0442", None)
        )
        self.UpdatePortsButton.setText(
            QCoreApplication.translate("Dialog", "\u21ba", None)
        )

    # retranslateUi
