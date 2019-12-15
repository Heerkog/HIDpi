import bluetooth


class Advertiser:
    uuid = "ec20ee5f-491d-4f9c-adb6-26250bdcfbd1"

    def __init__(self):
        self.server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

    def advertise(self):
        port = bluetooth.get_available_port(bluetooth.RFCOMM)
        print("Failed to create port")
        self.server_sock.bind(("B8:27:EB:77:31:44", port))
        print("bound")
        self.server_sock.listen(1)
        print("listening on port %d" % port)
        bluetooth.advertise_service(self.server_sock, "FooBar Service", self.uuid, [0x0508])
        print("advertising")

    def accept(self):
        client_sock, address = self.server_sock.accept()
        print("Accepted connection from ", address)
        return client_sock

    def disconnect(self, client_sock):
        client_sock.close()

    def close(self):
        self.server_sock.close()
