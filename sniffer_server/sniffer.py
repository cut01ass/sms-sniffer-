import socket
import struct
import queue
import time
from PyQt5.QtCore import QThread, pyqtSignal
from display import init_display, clear_display, draw_char
from hwlib import get_button_state
import sqlite3
import subprocess

class SnifferThread(QThread):
    newMessageSignal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.messageQueue = queue.Queue()
        self.sms_list = []
        self.isFlashed = False

        # 初始化显示屏
        init_display(0xFF200060, 0xFF200080)
        
    def getButtonState(self):
        return get_button_state()

    def displayMessage(self, message):
        # 清空屏幕
        clear_display(0xFFFF)

        # 设置字符颜色和起始位置
        color = 0x0000
        x = 0
        y = 0

        # 遍历消息字符串,绘制每个字符
        for char in message:
            if char == '\n':
                x = 0
                y += 8
            else:
                draw_char(color, x, y, char)
                x += 6

    def covert_cellphone_num(self, num):
        """
        Convert the cellphone number to the correct format.
        """
        phone_number = []
        for i in num:
            i = ord(i)
            i = (i << 4 & 0xF0) + (i >> 4 & 0x0F)
            phone_number.append(chr(i))
    
        return ("".join(phone_number).encode('hex'))[:-1]

    def GetCurrentTime(self):
        """
        Get the current timestamp.
        """
        return time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time()))

    def handleNewMessage(self, message):
        print(f"New message from {message['number']}: {message['content']}")
        message['center'] = to_number
        message['is_uplink'] = is_uplink
        message['timestamp'] = self.GetCurrentTime()
        self.sms_list.append(message)

    def getSMSList(self):
        sms_list = self.sms_list
        self.sms_list = []
        return sms_list

    def run(self):
        """
        Run the sniffer thread.
        """
        try:
            skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            skt.bind(('127.0.0.1', 4729))
            print("GSM sniffer is working!!! Enjoy it.")
            while True:
                data, _ = skt.recvfrom(2048)
                self.messageQueue.put(data)

                while not self.messageQueue.empty():
                    data = self.messageQueue.get()
                    if data[0:2] == b'\x02\x04':  # GSM_TAP header Version02 & HeaderLength 16bytes
                        self.handle_gsm_sms(data)
        except Exception as e:
            print(e)

    def handle_gsm_sms(self, data):
        """
        Handle GSM SMS data.
        """
        address_field = struct.unpack('B', data[16:17])[0]
        control_field = struct.unpack('B', data[17:18])[0]
        length_field = struct.unpack('B', data[18:19])[0]

        if (address_field >> 2) & 0x1F == 3 and (control_field & 0x01) == 0x00:  # GSM SMS and frame type == information frame
            seg_len = (length_field >> 2) & 0x3F
            has_segments = ((length_field >> 1) & 0x01 == 0x1)
            gsm_sms_segs = data[19:19 + seg_len]

            if not has_segments:
                gsm_sms = gsm_sms_segs
                self.parse_sms(gsm_sms)

    def parse_sms(self, gsm_sms):
        """
        Parse SMS data.
        """
        if len(gsm_sms) > 10 and ord(gsm_sms[0:1]) & 0x0F == 0x09 and ord(gsm_sms[1:2]) == 0x01 and ord(gsm_sms[2:3]) > 0x10:  # SMS Message
            try:
                is_uplink = (ord(gsm_sms[3:4]) == 0x00)
                print("SMS Type: Uplink" if is_uplink else "SMS Type: Downlink")

                if is_uplink:
                    self.handle_uplink_sms(gsm_sms)
                else:
                    self.handle_downlink_sms(gsm_sms)
            except Exception as e:
                print('--------- Exception ----------------')
                print(e)
                print('--------- Exception ----------------')

    def handle_uplink_sms(self, gsm_sms):
        """
        Handle uplink SMS.
        """
        to_number_len = struct.unpack('B', gsm_sms[6:7])[0] - 1
        to_number = gsm_sms[8:8 + to_number_len]
        to_number = self.covert_cellphone_num(to_number)

        sms_submit = struct.unpack('B', gsm_sms[7 + to_number_len + 2:7 + to_number_len + 2 + 1])[0]
        if sms_submit & 0x03 == 0x01:
            has_tpudhi = ((struct.unpack('B', gsm_sms[7 + to_number_len + 2:7 + to_number_len + 2 + 1])[0] & 0x40) == 0x40)
            has_tpvpf = ((struct.unpack('B', gsm_sms[7 + to_number_len + 2:7 + to_number_len + 2 + 1])[0] >> 3 & 0x02) == 0x02)
            from_number_len = struct.unpack('B', gsm_sms[8 + to_number_len + 3:8 + to_number_len + 3 + 1])[0]
            from_number_len = (from_number_len // 2) + (from_number_len % 2)
            from_number = gsm_sms[8 + to_number_len + 3 + 2:8 + to_number_len + 3 + 2 + from_number_len]
            from_number = self.covert_cellphone_num(from_number)
            self.parse_sms_content(gsm_sms, to_number, from_number, is_uplink=True, has_tpudhi=has_tpudhi, has_tpvpf=has_tpvpf)

    def handle_downlink_sms(self, gsm_sms):
        """
        Handle downlink SMS.
        """
        to_number_len = struct.unpack('B', gsm_sms[5:6])[0] - 1
        to_number = gsm_sms[7:7 + to_number_len]
        to_number = self.covert_cellphone_num(to_number)

        sms_deliver = struct.unpack('B', gsm_sms[7 + to_number_len + 2:7 + to_number_len + 2 + 1])[0]
        if sms_deliver & 0x03 == 0x0:
            has_tpudhi = ((struct.unpack('B', gsm_sms[7 + to_number_len + 2:7 + to_number_len + 2 + 1])[0] & 0x40) == 0x40)
            from_number_len = struct.unpack('B', gsm_sms[7 + to_number_len + 3:7 + to_number_len + 3 + 1])[0]
            from_number_len = (from_number_len // 2) + (from_number_len % 2)
            from_number = gsm_sms[7 + to_number_len + 3 + 2:7 + to_number_len + 3 + 2 + from_number_len]
            from_number = self.covert_cellphone_num(from_number)
            self.parse_sms_content(gsm_sms, to_number, from_number, is_uplink=False, has_tpudhi=has_tpudhi)
        else:
            print('--------------------------------------')
            print("SMS Status Report")
            print('--------------------------------------')

    def parse_sms_content(self, gsm_sms, to_number, from_number, is_uplink, has_tpudhi, has_tpvpf=False):
        """
        Parse the content of the SMS.
        """
        header_len = 0
        if has_tpudhi:
            header_len = struct.unpack('B', gsm_sms[7 + len(to_number) + 3 + 2 + len(from_number) + 10:7 + len(to_number) + 3 + 2 + len(from_number) + 10 + 1])[0]

        mms = struct.unpack('B', gsm_sms[7 + len(to_number) + 3 + 2 + len(from_number) + 1:7 + len(to_number) + 3 + 2 + len(from_number) + 1 + 1])[0]
        is_mms = ((mms >> 2) & 0x03) == 0x01

        if has_tpvpf:
            if header_len == 0:
                sms = gsm_sms[8 + len(to_number) + 3 + 2 + len(from_number) + 3 + 1:]
            else:
                sms = gsm_sms[8 + len(to_number) + 3 + 2 + len(from_number) + 3 + header_len + 1 + 1:]
        else:
            if header_len == 0:
                sms = gsm_sms[7 + len(to_number) + 3 + 2 + len(from_number) + 10:]
            else:
                sms = gsm_sms[7 + len(to_number) + 3 + 2 + len(from_number) + 10 + header_len + 1:]

        if not is_mms:
            content = sms.decode('UTF-16BE', errors='ignore')
            print('--------------------------------------')
            print(content)
            print('--------------------------------------')
            saveToDB([from_number, to_number, is_uplink, content, self.GetCurrentTime()])
            self.handleNewMessage({'number': from_number, 'content': content})
        else:
            print('--------------------------------------')
            print("MMS Message")
            print('--------------------------------------')
            
def saveToDB(posData):
    """
    Save SMS data to the database.
    """
    try:
        cx = sqlite3.connect("smslog.db")
        cx.text_factory = str
        cu = cx.cursor()

        phone = posData[0]
        center = posData[1]
        smstype = str(posData[2])
        content = str(posData[3]) 
        date = posData[4]

        cu.execute("INSERT INTO sms (phone, center, type, content, date) VALUES (?, ?, ?, ?, ?)", (phone, center, smstype, content, date))
        cx.commit()
        print('[√] Inserted successfully!')
        cu.close()
        cx.close()
    except Exception as e:
        print(e)
        
def downloadFirmware(devices):
    """
    Download firmware to the devices.
    """
    for device in devices:
        try:
            print(f"Downloading firmware to device: {device}")
            downloadCommand = ['xterm', "-T", "osmocon for " + device, '-e', sys.path[0] + '/osmocombb_x64/osmocon', '-m', 'c123xor', '-s', '/tmp/osmocom_l2_' + device.split('USB')[1], '-p', device, sys.path[0] + '/osmocombb_x64/layer1.compalram.bin']
            downloadProcess = subprocess.Popen(downloadCommand, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            time.sleep(1)
        except Exception as e:
            print(f"Error downloading firmware to device {device}: {str(e)}")

def scanARFCN(devices):
    """
    Scan ARFCN on the devices.
    """
    for device in devices:
        try:
            print(f"Scanning ARFCN on device: {device}")
            devIndex = device.split('USB')[1]
            cellLogshell = [sys.path[0] + "/osmocombb_x64/cell_log", "-s", "/tmp/osmocom_l2_" + devIndex, "-O"]
            arfcnScan = subprocess.Popen(cellLogshell, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            scanlog = arfcnScan.communicate()
            arfcnScan.wait()
            scanloginfo = ";".join(scanlog)
            scanbase = re.findall(r"ARFCN\=[^)]+\)", scanloginfo)

            logfile = open(sys.path[0] + "/arfcn_" + devIndex + ".log", "w+")
            for line in scanbase:
                logfile.write(str(line) + "\r\n")
            logfile.write('Date: ' + GetCurrentTime())
            logfile.close()
        except Exception as e:
            print(f"Error scanning ARFCN on device {device}: {str(e)}")
            
def getUSBDevices():
    """
    Get the list of USB devices.
    """
    devices = []
    try:
        output = subprocess.check_output(['lsusb']).decode('utf-8')
        lines = output.split('\n')
        for line in lines:
            if 'Prolific Technology' in line:
                devices.append(line.split()[5])
    except Exception as e:
        print(e)
    return devices
