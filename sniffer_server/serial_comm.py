import serial
import json

class SerialComm:
    def __init__(self, port, baudrate):
        self.serial = serial.Serial(port, baudrate)

    def send(self, data):
        json_data = json.dumps(data)
        self.serial.write(json_data.encode())

    def receive(self):
        if self.serial.in_waiting > 0:
            data = self.serial.readline().decode().strip()
            return data
        return None