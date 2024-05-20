import sys
from sniffer import SnifferThread, downloadFirmware, scanARFCN, getUSBDevices
from process_utils import killAllProcesses, resetAllPower
from serial_comm import SerialComm
from io import StringIO
import sys
import time
import ctypes

# 加载硬件库
hwlib = ctypes.CDLL('./hwlib.so')
# 加载显示库
display = ctypes.CDLL('./display.so')

def handleCommand(command):
    output = StringIO()
    sys.stdout = output

    if command == "flash":
        downloadFirmware(getUSBDevices())
    elif command == "scan":
        scanARFCN(getUSBDevices())
    elif command == "kill":
        killAllProcesses()
    elif command == "reset":
        resetAllPower(getUSBDevices())

    sys.stdout = sys.__stdout__
    result = output.getvalue()
    serial_comm_cmd.send(result)

def handleSMSRequest():
    sms_list = snifferThread.getSMSList()
    if sms_list:
        serial_comm_sms.send(sms_list)
    else:
        serial_comm_sms.send("error")

def displayMessage(self, message, size=1, color=0x0000, x=0, y=0):
    # 清空屏幕
    display.clear_display(0xFFFF)
    
    # 设置字符大小、颜色和起始位置
    char_width = 5 * size
    char_height = 8 * size
    
    # 计算消息的总宽度和高度
    lines = message.split('\n')
    max_line_width = max(len(line) for line in lines)
    total_width = max_line_width * char_width
    total_height = len(lines) * char_height
    
    # 计算居中显示的起始位置
    screen_width = 240
    screen_height = 320
    start_x = x if x != 0 else (screen_width - total_width) // 2
    start_y = y if y != 0 else (screen_height - total_height) // 2
    
    # 遍历消息字符串,绘制每个字符
    current_x = start_x
    current_y = start_y
    for char in message:
        if char == '\n':
            current_x = start_x
            current_y += char_height
        else:
            display.draw_char(color, current_x, current_y, char)
            current_x += char_width

if __name__ == '__main__':
    snifferThread = SnifferThread()
    snifferThread.start()

    hwlib.init_hw()
    display.init_display(0xFF200060, 0xFF200080)
    serial_comm_cmd = SerialComm('/dev/ttyUSB5', 9600)
    serial_comm_sms = SerialComm('/dev/ttyUSB6', 9600)

    while True:
        command = serial_comm_cmd.receive()
        if command:
            if command == "flash":
                snifferThread.displayMessage("Flashing...")
                handleCommand(command)
                if not snifferThread.isFlashed:
                    snifferThread.displayMessage("Completed!")
                    snifferThread.isFlashed = True
                else:
                    snifferThread.displayMessage("Error\nFlashed Before!")
            elif command == "scan":
                if snifferThread.isFlashed:
                    snifferThread.displayMessage("Sniffing...")
                    handleCommand(command)
                    snifferThread.displayMessage("Session running")
                else:
                    snifferThread.displayMessage("Error\nFlash first!")
            else:
                handleCommand(command)

        sms_request = serial_comm_sms.receive()
        if sms_request == "get_sms":
            handleSMSRequest()

        button_state = hwlib.get_button_state()
        if button_state & 0x1:
            snifferThread.displayMessage("Sniffing...")
            scanARFCN(getUSBDevices())
            snifferThread.displayMessage("Session running")
        elif button_state & 0x2:
            if not snifferThread.isFlashed:
                snifferThread.displayMessage("Flashing...")
                downloadFirmware(getUSBDevices())
                snifferThread.displayMessage("Completed!")
                snifferThread.isFlashed = True
            else:
                snifferThread.displayMessage("Error\nFlashed Before!")
        else:
            snifferThread.displayMessage("SMS Sniffer\nMade by\nY.Wang")