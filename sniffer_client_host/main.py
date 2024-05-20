import sys
import serial
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QListWidgetItem, QWidget, QFileDialog, QComboBox, QMessageBox, QLabel, QSpinBox, QCheckBox, QDialog, QTextEdit
from PyQt5.QtGui import QFont
from serial_comm import SerialComm
from serial.tools import list_ports

class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('About')
        self.setGeometry(100, 100, 400, 230)

        layout = QVBoxLayout()

        aboutText = QTextEdit()
        aboutText.setReadOnly(True)
        aboutText.setPlainText("This is an implementation of an SMS sniffer based on the osmocombb GSM protocol stack. It consists of a Linux-based sniffer server, an Android app, and a desktop QT application, responsible for running the SMS sniffer service, controlling the sniffer service, and monitoring and processing the sniffing process and results, respectively.\n\nThe initial version was written in April 2018. A tribute to that summer six years ago.\n\n                                                                    Bensen Wang\n                                                                             14/05/24")
        layout.addWidget(aboutText)

        self.setLayout(layout)

class SMSWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('SMS Receiver')
        self.setGeometry(100, 100, 600, 400)

        mainLayout = QHBoxLayout()

        # Serial Settings Area
        settingLayout = QVBoxLayout()

        portLabel = QLabel('Port:')
        settingLayout.addWidget(portLabel)

        self.portComboBox = QComboBox()
        self.portComboBox.addItems([port.device for port in list_ports.comports()])
        settingLayout.addWidget(self.portComboBox)

        baudLabel = QLabel('Baud Rate:')
        settingLayout.addWidget(baudLabel)

        self.baudComboBox = QComboBox()
        self.baudComboBox.addItems(['9600', '19200', '38400', '57600', '115200'])
        settingLayout.addWidget(self.baudComboBox)

        dataBitsLabel = QLabel('Data Bits:')
        settingLayout.addWidget(dataBitsLabel)

        self.dataBitsSpinBox = QSpinBox()
        self.dataBitsSpinBox.setRange(5, 8)
        self.dataBitsSpinBox.setValue(8)
        settingLayout.addWidget(self.dataBitsSpinBox)

        parityLabel = QLabel('Parity:')
        settingLayout.addWidget(parityLabel)

        self.parityComboBox = QComboBox()
        self.parityComboBox.addItems(['None', 'Even', 'Odd', 'Mark', 'Space'])
        settingLayout.addWidget(self.parityComboBox)

        stopBitsLabel = QLabel('Stop Bits:')
        settingLayout.addWidget(stopBitsLabel)

        self.stopBitsComboBox = QComboBox()
        self.stopBitsComboBox.addItems(['1', '1.5', '2'])
        settingLayout.addWidget(self.stopBitsComboBox)

        self.rtsCheckBox = QCheckBox('RTS')
        settingLayout.addWidget(self.rtsCheckBox)

        self.dtrCheckBox = QCheckBox('DTR')
        settingLayout.addWidget(self.dtrCheckBox)
        connectButton = QPushButton('Connect')
        connectButton.clicked.connect(self.connectSerial)
        settingLayout.addWidget(connectButton)

        mainLayout.addLayout(settingLayout)

        # SMS List Area
        smsLayout = QVBoxLayout()

        self.smsList = QListWidget()
        smsLayout.addWidget(self.smsList)

        buttonLayout = QHBoxLayout()

        self.getSMSButton = QPushButton('Get SMS')
        self.getSMSButton.setEnabled(False)
        self.getSMSButton.clicked.connect(self.getSMS)
        buttonLayout.addWidget(self.getSMSButton)

        self.exportButton = QPushButton('Export SMS')
        self.exportButton.setEnabled(False)
        self.exportButton.clicked.connect(self.exportSMS)
        buttonLayout.addWidget(self.exportButton)

        aboutButton = QPushButton('About')
        aboutButton.clicked.connect(self.showAbout)
        buttonLayout.addWidget(aboutButton)

        smsLayout.addLayout(buttonLayout)

        mainLayout.addLayout(smsLayout)

        centralWidget = QWidget()
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

    def connectSerial(self):
        port = self.portComboBox.currentText()
        baud = int(self.baudComboBox.currentText())
        databits = self.dataBitsSpinBox.value()
        parity_str = self.parityComboBox.currentText()
        if parity_str == 'None':
            parity = serial.PARITY_NONE
        elif parity_str == 'Even':
            parity = serial.PARITY_EVEN
        elif parity_str == 'Odd':
            parity = serial.PARITY_ODD
        elif parity_str == 'Mark':
            parity = serial.PARITY_MARK
        elif parity_str == 'Space':
            parity = serial.PARITY_SPACE
        stopbits = float(self.stopBitsComboBox.currentText())
        rtscts = self.rtsCheckBox.isChecked()
        dsrdtr = self.dtrCheckBox.isChecked()

        self.serial_comm = SerialComm(port, baud, databits, parity, stopbits, rtscts, dsrdtr)
        
        self.getSMSButton.setEnabled(True)
        self.exportButton.setEnabled(True)


    def getSMS(self):
        self.serial_comm.send("get_sms")
        sms_list = self.serial_comm.receive()

        if sms_list == "error":
            QMessageBox.critical(self, "Error", "No SMS found.")
        else:
            self.smsList.clear()
            for sms in sms_list:
                item = QListWidgetItem(f"From: {sms['number']}\nContent: {sms['content']}\nTimestamp: {sms['timestamp']}")
                self.smsList.addItem(item)

    def exportSMS(self):
        fileName, _ = QFileDialog.getSaveFileName(self, "Export SMS", "", "Text Files (*.txt)")
        if fileName:
            with open(fileName, 'w') as file:
                for i in range(self.smsList.count()):
                    item = self.smsList.item(i)
                    file.write(item.text() + '\n\n')

    def showAbout(self):
        aboutDialog = AboutDialog()
        aboutDialog.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setFont(QFont('Arial', 10))
    window = SMSWindow()
    window.show()
    sys.exit(app.exec_())