import bluetooth


class Advertiser:
    service_uuid = "ec20ee5f-491d-4f9c-adb6-26250bdcfbd1"
    service_class = "1124"    # Human Interface Device (HID)

    def __init__(self):
        self.server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

    def advertise(self):
        self.server_sock.bind(("B8:27:EB:77:31:44", bluetooth.PORT_ANY))
        print("bound")
        self.server_sock.listen(1)
        print("listening on port %d" % self.server_sock.getsockname()[1])
        print(bluetooth.HEADSET_CLASS)
        bluetooth.advertise_service(self.server_sock, "FooBar Service", self.service_uuid, [self.service_class])
        print("advertising")

    def accept(self):
        client_sock, address = self.server_sock.accept()
        print("Accepted connection from ", address)
        return client_sock

    def disconnect(self, client_sock):
        client_sock.close()

    def close(self):
        self.server_sock.close()
