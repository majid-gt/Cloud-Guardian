import getpass
from core.hardware.serial_manager import SerialManager


class VaultClient:
    def __init__(self):
        self.serial_manager = SerialManager()

    def unlock(self):
        port = self.serial_manager.find_esp32()
        if not port:
            raise Exception("Hardware vault not detected")

        self.serial_manager.connect()

        password = getpass.getpass("Enter ESP32 vault password: ")

        self.serial_manager.send_json({
            "command": "unlock",
            "password": password
        })

        response = self.serial_manager.receive_json()
        self.serial_manager.close()

        if response.get("status") != "ok":
            raise Exception("Authentication failed")

        return {
            "aws_access_key_id": response["access_key"],
            "aws_secret_access_key": response["secret_key"],
            "region": response["region"]
        }
        
    def change_password(self):
        port = self.serial_manager.find_esp32()
        if not port:
            raise Exception("Hardware vault not detected")

        self.serial_manager.connect()

        import getpass
        old_password = getpass.getpass("Enter current password: ")
        new_password = getpass.getpass("Enter new password: ")
        confirm_password = getpass.getpass("Confirm new password: ")

        if new_password != confirm_password:
            self.serial_manager.close()
            raise Exception("New passwords do not match")

        self.serial_manager.send_json({
            "command": "change_password",
            "old_password": old_password,
            "new_password": new_password
        })

        response = self.serial_manager.receive_json()
        self.serial_manager.close()

        if response.get("status") != "password_changed":
            raise Exception("Password change failed")

        print("✅ Password changed successfully.")