import bluetooth

class advertiser:
    uuid = "ec20ee5f-491d-4f9c-adb6-26250bdcfbd1"

    def advertise(self):
        try:
            self.server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
            self.port = bluetooth.get_available_port( bluetooth.RFCOMM )
            self.server_sock.bind(("", self.port))
            self.server_sock.listen(1)
            print("listening on port %d" % self.port)
            bluetooth.advertise_service( self.server_sock, "FooBar Service", self.uuid, [0x0508] )
        except:
            print("Failed to advertise Bluetooth HID service")

    def accept(self):
        client_sock,address = self.server_sock.accept()
        print("Accepted connection from ",address)
        return client_sock

    def disconnect(self, client_sock):
        client_sock.close()

    def close(self):
        self.server_sock.close()