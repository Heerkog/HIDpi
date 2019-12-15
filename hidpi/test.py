import bluetooth

server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )

server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)
print("listening on port %d" % server_sock.getsockname()[1])

uuid = "1e0ca4ea-299d-4335-93eb-27fcfe7fa848"
bluetooth.advertise_service( server_sock, "FooBar Service", uuid )

client_sock,address = server_sock.accept()
print("Accepted connection from ",address)

data = client_sock.recv(1024)
print("received [%s]" % data)

client_sock.close()
server_sock.close()