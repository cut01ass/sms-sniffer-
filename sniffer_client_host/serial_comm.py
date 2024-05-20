import serial
import json

class SerialComm:
    def __init__(self, port, baud, databits, parity, stopbits, rtscts, dsrdtr):
        self.ser = serial.Serial(port=port, baudrate=baud, bytesize=databits, parity=parity, stopbits=stopbits, rtscts=rtscts, dsrdtr=dsrdtr, timeout=1)

    def send(self, data):
        self.ser.write(data.encode())

    def receive(self):
        try:
            data = self.ser.readline().decode().strip()
            if data:
                return json.loads(data)
            else:
                return "error"
        except:
            return "error"

    def close(self):
        self.ser.close()