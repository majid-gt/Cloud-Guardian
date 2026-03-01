import serial
import serial.tools.list_ports
import json
import time


class SerialManager:
    def __init__(self, baudrate=115200):
        self.baudrate = baudrate
        self.port = None
        self.connection = None

    def find_esp32(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if "USB" in port.description or "CP210" in port.description or "CH340" in port.description:
                self.port = port.device
                return self.port
        return None

    def connect(self):
        if not self.port:
            raise Exception("ESP32 not found")

        self.connection = serial.Serial(self.port, self.baudrate, timeout=5)
        time.sleep(2)

        # Flush boot messages
        self.connection.reset_input_buffer()

    def send_json(self, data):
        message = json.dumps(data) + "\n"
        self.connection.write(message.encode())

    def receive_json(self):
        while True:
            raw = self.connection.readline()

            if not raw:
                continue

            try:
                response = raw.decode(errors="ignore").strip()
            except:
                continue

            if not response:
                continue

            if not response.startswith("{"):
                continue

            return json.loads(response)

    def close(self):
        if self.connection:
            self.connection.close()