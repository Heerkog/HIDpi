import bluetooth


class Advertiser:
    uuid = "ec20ee5f-491d-4f9c-adb6-26250bdcfbd1"

    def __init__(self):
        self.server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

    def advertise(self):
        try:
            port = bluetooth.get_available_port(bluetooth.RFCOMM)
            print("created port")
            self.server_sock.bind(("", port))
            print("bound")
            self.server_sock.listen(1)
            print("listening on port %d" % port)
            bluetooth.advertise_service(self.server_sock, "FooBar Service", self.uuid, [0x0508])
            print("advertising")
        except:
            print("Failed to advertise Bluetooth HID service")

    def accept(self):
        client_sock, address = self.server_sock.accept()
        print("Accepted connection from ", address)
        return client_sock

    def disconnect(self, client_sock):
        client_sock.close()

    def close(self):
        self.server_sock.close()
