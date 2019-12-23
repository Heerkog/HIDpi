import os
import sys
from gi.repository import GLib as glib
from signal import pause
import socket

global control_socket

def accept_control(source, cond):
    control_channel, cinfo = control_socket.accept()
    print("Got a connection on the control channel from " + cinfo[0])
    control_channel.close()
    control_socket.close()
    return True

if __name__ == '__main__':
    if not os.geteuid() == 0:
        sys.exit("Only root can run this script")

    MY_ADDRESS = "b8:27:eb:77:31:44"
    control_port = 19  #HID control port as specified in SDP > Protocol Descriptor List > L2CAP > HID Control Port

    print("Setting up connections")

    control_socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_L2CAP)
    control_socket.setblocking(0)
    control_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    control_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    control_socket.bind((MY_ADDRESS, control_port))
    control_socket.listen(1)

    glib.io_add_watch(control_socket.fileno(), glib.IO_IN, accept_control)
    print("Watching sockets")

    pause()