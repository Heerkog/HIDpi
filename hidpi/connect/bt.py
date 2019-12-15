import bluetooth
import os

class Advertiser:
    service_uuid = "ec20ee5f-491d-4f9c-adb6-26250bdcfbd1"
    service_class = "1124"  # Human Interface Device (HID)

    def __init__(self):
        os.system("hciconfig hci0 class 0x000508")
        os.system("hciconfig hci0 name HIDpi")
        # Make device discoverable
        os.system("hciconfig hci0 piscan")
        self.server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

    def advertise(self):
        try:
            self.server_sock.bind(("B8:27:EB:77:31:44", bluetooth.PORT_ANY))
            self.server_sock.listen(1)
            bluetooth.advertise_service(self.server_sock, "Joystick", self.service_uuid, [self.service_class])
        except:
            print("Failed to advertise service.")
        print("Waiting for connection on RFCOMM channel %d" %  self.server_sock.getsockname()[1])

    def accept(self):
        print("Accepting")
        client_sock, address = self.server_sock.accept()
        print("Accepted connection from ", address)
        return client_sock

    def disconnect(self, client_sock):
        client_sock.close()

    def close(self):
        self.server_sock.close()
