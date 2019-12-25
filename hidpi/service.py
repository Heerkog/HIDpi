from __future__ import absolute_import, print_function

import os
import sys
import socket

import dbus
import dbus.service
import dbus.mainloop.glib

from gi.repository import GObject as gobject

import hidpi.hid

global mainloop

#define a bluez 5 profile object for our keyboard
class BluezHIDProfile(dbus.service.Object):
    MY_ADDRESS = "b8:27:eb:77:31:44"
    CONTROL_PORT = 17  #HID control port as specified in SDP > Protocol Descriptor List > L2CAP > HID Control Port
    INTERRUPT_PORT = 19  #HID interrupt port as specified in SDP > Additional Protocol Descriptor List > L2CAP > HID Interrupt Port

    file_descriptor = -1
    control_socket = None
    interrupt_socket = None

    control_channel = None
    interrupt_channel = None

    def __init__(self, bus, path):
        dbus.service.Object.__init__(self, bus, path)

        self.control_socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_L2CAP)
        self.interrupt_socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_L2CAP)

        # self.control_socket.setblocking(0)
        # self.interrupt_socket.setblocking(0)

        self.control_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.interrupt_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.control_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.interrupt_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        self.control_socket.bind((self.MY_ADDRESS, self.CONTROL_PORT))
        self.interrupt_socket.bind((self.MY_ADDRESS, self.INTERRUPT_PORT))

        self.control_socket.listen(1)
        self.interrupt_socket.listen(1)

        # self.control_channel, cinfo = self.control_socket.accept()
        # self.interrupt_channel, cinfo = self.interrupt_socket.accept()

        gobject.io_add_watch(self.control_socket.fileno(), gobject.IO_IN | gobject.IO_PRI, self.accept_control)
        gobject.io_add_watch(self.interrupt_socket.fileno(), gobject.IO_IN | gobject.IO_PRI, self.accept_interrupt)

    @dbus.service.method("org.bluez.Profile1", in_signature="", out_signature="")
    def Release(self):
        print("Release")
        mainloop.exit()

    @dbus.service.method("org.bluez.Profile1", in_signature="", out_signature="")
    def Cancel(self):
        print("Cancel")

    @dbus.service.method("org.bluez.Profile1", in_signature="oha{sv}", out_signature="")
    def NewConnection(self, path, file_descriptor, properties):
        self.file_descriptor = file_descriptor.take()

        print("NewConnection(%s, %d)" % (path, self.file_descriptor))

    @dbus.service.method("org.bluez.Profile1", in_signature="o", out_signature="")
    def RequestDisconnection(self, path):
        print("RequestDisconnection(%s)" % (path))

        if (self.file_descriptor > 0):
            os.close(self.file_descriptor)
            self.file_descriptor = -1


    def accept_control(self, source, cond):
        self.control_channel, cinfo = self.control_socket.accept()
        gobject.io_add_watch(self.control_channel.fileno(), gobject.IO_ERR | gobject.IO_HUP, self.close, self.control_channel)
        gobject.io_add_watch(self.control_channel.fileno(), gobject.IO_IN | gobject.IO_PRI, self.callback, self.control_channel)
        print("Got a connection on the control channel from " + cinfo[0])
        return False

    def accept_interrupt(self, source, cond):
        print("Accept interrupt")
        self.interrupt_channel, cinfo = self.interrupt_socket.accept()
        gobject.io_add_watch(self.interrupt_channel.fileno(), gobject.IO_ERR | gobject.IO_HUP, self.close, self.interrupt_channel)
        gobject.io_add_watch(self.interrupt_channel.fileno(), gobject.IO_IN | gobject.IO_PRI, self.callback, self.interrupt_channel)
        print("Got a connection on the interrupt channel from " + cinfo[0])
        return False

    def callback(self, source, conditions, channel):
        try:
            data = channel.recv(1)
            print("{0}".format(data))
        except:
            print("No data")
        return True

    def close(self, source, condition, channel):
        print("Channel error {0}".format(channel.getsockname()))
        try:
            channel.close()
        except:
            print("Close failed")

    def send_input_report(self, report):
        try:
            message = bytearray()
            message.append(chr(report[0]))
            message.append(chr(report[1]))
            message.append(chr(report[2]))
            message.append(chr(report[3]))
            message.append(chr(report[4]))

            print("Sending {0}".format(message))
            self.interrupt_channel.send(message)
        except ConnectionResetError:
            self.file_descriptor = -1

#create a bluetooth service to emulate a HID joystick
class BTHIDService:
    MY_DEV_NAME = "RPi_HID_Joystick"
    PROFILE_DBUS_PATH = "/nl/rug/ds/heerkog/hid"  #dbus path of the bluez profile
    SDP_RECORD_PATH = sys.path[0] + "sdp/sdp_record_joystick.xml"  #file path of the sdp record to laod
    UUID = "00001124-0000-1000-8000-00805f9b34fb"  #HumanInterfaceDeviceServiceClass UUID

    def __init__(self, loop):
        mainloop = loop
        print("Configuring Bluez Profile")

        #setup profile options
        service_record = self.read_sdp_service_record()

        opts = {
            "ServiceRecord": service_record,
            "Name": self.MY_DEV_NAME,
            "Role": "server",
            "AutoConnect": True,
            "RequireAuthentication": False,
            "RequireAuthorization": False
        }

        #retrieve a proxy for the bluez profile interface
        system_bus = dbus.SystemBus()

        adapter_properties = dbus.Interface(system_bus.get_object("org.bluez", "/org/bluez/hci0"), "org.freedesktop.DBus.Properties")
        adapter_properties.Set('org.bluez.Adapter1', 'Powered', dbus.Boolean(1))

        adapter_properties.Set('org.bluez.Adapter1', 'PairableTimeout', dbus.UInt32(0))
        adapter_properties.Set('org.bluez.Adapter1', 'Pairable', dbus.Boolean(1))

        adapter_properties.Set('org.bluez.Adapter1', 'DiscoverableTimeout', dbus.UInt32(0))
        adapter_properties.Set('org.bluez.Adapter1', 'Discoverable', dbus.Boolean(1))

        self.profile = BluezHIDProfile(system_bus, self.PROFILE_DBUS_PATH)

        profile_manager = dbus.Interface(system_bus.get_object("org.bluez", "/org/bluez"), "org.bluez.ProfileManager1")
        profile_manager.RegisterProfile(self.PROFILE_DBUS_PATH, self.UUID, opts)

        print("Profile registered")

        #create joystick class
        self.joystick = hidpi.hid.Joystick(self.profile)

    #read and return an sdp record from a file
    def read_sdp_service_record(self):
        print("Reading service record: " + self.SDP_RECORD_PATH)

        try:
            fh = open(self.SDP_RECORD_PATH, "r")
        except:
            sys.exit("Failed to read SDP record.")

        return fh.read()
