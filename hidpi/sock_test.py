import os
import sys
from gi.repository import GLib as glib
import time
import socket

def accept_control(self, source, cond):
    control_channel, cinfo = self.control_socket.accept()
    print("Got a connection on the control channel from " + cinfo[0])
    return True

if __name__ == '__main__':
    if not os.geteuid() == 0:
        sys.exit("Only root can run this script")

    MY_ADDRESS = "b8:27:eb:77:31:44"
    control_port = 12  #HID control port as specified in SDP > Protocol Descriptor List > L2CAP > HID Control Port

    print("Setting up connections")

    control_socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_L2CAP)
    control_socket.bind((MY_ADDRESS, control_port))
    control_socket.setblocking(0)
    control_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    control_socket.listen(1)

    glib.io_add_watch(control_socket.fileno(), glib.IO_IN, accept_control)
    print("Watching sockets")

    time.pause()