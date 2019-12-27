from __future__ import absolute_import, print_function

import sys
import socket

import dbus
import dbus.service
import dbus.mainloop.glib

from gi.repository import GObject as gobject

import hidpi.hid

global mainloop

# Define a generic Bluez Profile object for our HID device
class BluezHIDProfile(dbus.service.Object):
    MY_ADDRESS = "b8:27:eb:77:31:44"  # Physical address of the Bluetooth adapter
    CONTROL_PORT = 17  # HID control port as specified in SDP > Protocol Descriptor List > L2CAP > HID Control Port
    INTERRUPT_PORT = 19  # HID interrupt port as specified in SDP > Additional Protocol Descriptor List > L2CAP > HID Interrupt Port

    control_socket = None
    interrupt_socket = None

    control_channel = None
    interrupt_channel = None


    def __init__(self, bus, path):
        # Register this Bluez Profile on the DBUS
        dbus.service.Object.__init__(self, bus, path)

        # Manually set up sockets
        # Bluez doesn't handle this automatically for HID profiles
        # (Probably because Bluez only returns a single communication channel and HID requires two always)
        self.control_socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_L2CAP)
        self.interrupt_socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_L2CAP)

        self.control_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.interrupt_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.control_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.interrupt_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        self.control_socket.bind((self.MY_ADDRESS, self.CONTROL_PORT))
        self.interrupt_socket.bind((self.MY_ADDRESS, self.INTERRUPT_PORT))

        # Maximum of one connection (HID virtual cable = True)
        self.control_socket.listen(1)
        self.interrupt_socket.listen(1)

        # Watch for connections on socket by adding an IO watch that calls an accept function
        self.listen(self.control_socket, self.accept_control)
        self.listen(self.interrupt_socket, self.accept_interrupt)

    # Bluez release call is used for the HID profile.
    # Close connections and exit gracefully
    @dbus.service.method("org.bluez.Profile1", in_signature="", out_signature="")
    def Release(self):
        gobject.source_remove(self.interrupt_socket.fileno())
        gobject.source_remove(self.control_socket.fileno())

        gobject.source_remove(self.interrupt_channel.fileno())
        gobject.source_remove(self.control_channel.fileno())

        self.interrupt_channel.close()
        self.control_channel.close()

        self.interrupt_socket.close()
        self.control_socket.close()

        print("Release")
        mainloop.exit()
        exit(0);

    @dbus.service.method("org.bluez.Profile1", in_signature="", out_signature="")
    def Cancel(self):
        print("Cancel")

    # Not used for HID profiles by Bluez
    @dbus.service.method("org.bluez.Profile1", in_signature="oha{sv}", out_signature="")
    def NewConnection(self, path, file_descriptor, properties):
        print("NewConnection(%s, %d)." % (path, self.file_descriptor))

    # Not used for HID profiles by Bluez
    @dbus.service.method("org.bluez.Profile1", in_signature="o", out_signature="")
    def RequestDisconnection(self, path):
        print("RequestDisconnection(%s)." % (path))

    # Start watching for connections on socket by adding an IO watch
    def listen(self, socket, func):
        gobject.io_add_watch(socket.fileno(), gobject.IO_IN | gobject.IO_PRI, func)

    # Accept a connection from the control socket and create a channel
    # Start watching for IO input and errors by adding an IO watch
    def accept_control(self, source, cond):
        self.control_channel, cinfo = self.control_socket.accept()
        gobject.io_add_watch(self.control_channel.fileno(), gobject.IO_ERR | gobject.IO_HUP, self.close_control)
        gobject.io_add_watch(self.control_channel.fileno(), gobject.IO_IN | gobject.IO_PRI, self.callback, self.control_channel)
        return False  # Stop watching, we only accept one connection

    # Accept a connection from the interrupt socket and create a channel
    # Start watching for IO input and errors by adding an IO watch
    def accept_interrupt(self, source, cond):
        self.interrupt_channel, cinfo = self.interrupt_socket.accept()
        gobject.io_add_watch(self.interrupt_channel.fileno(), gobject.IO_ERR | gobject.IO_HUP, self.close_interrupt)
        gobject.io_add_watch(self.interrupt_channel.fileno(), gobject.IO_IN | gobject.IO_PRI, self.callback, self.interrupt_channel)
        print("Got a connection on the interrupt channel from {0}.".format(cinfo[0]))
        return False

    # Receive messages from the HID host
    # When protocol messages are expected from the HID host, they are received here
    # Read and silently discard messages
    def callback(self, source, conditions, channel):
        status = True
        try:
            data = channel.recv(1024)
        except:
            status = False  # The channel was closed or experienced an error, remove IO watch
        return status

    # Close the control channel and start listening for new connections using the control socket
    # This is called when the control channel experiences an error or was closed by the HID host
    def close_control(self, source, condition):
        try:
            gobject.source_remove(source)  # Remove any remaining watch
            self.control_channel.close()
            self.control_channel = None

            self.listen(self.control_socket, self.accept_control)
        except:
            print("Close failed")
        return False

    # Close the interrupt channel and start listening for new connections using the interrupt socket
    # This is called when the interrupt channel experiences an error or was closed by the HID host
    def close_interrupt(self, source, condition):
        try:
            gobject.source_remove(source)  # Remove any remaining watch
            self.interrupt_channel.close()
            self.interrupt_channel = None

            self.listen(self.interrupt_socket, self.accept_interrupt)
        except:
            print("Close failed")
        return False

    # Send an input report given a device state represented by a bytearray
    def send_input_report(self, device_state):
        try:
            if self.interrupt_channel is not None:
                self.interrupt_channel.send(device_state)
        except:
            print("Error while attempting to send report.")
        return True  # Return True to support adding a timeout function


#create a bluetooth service to emulate a HID device
class BTHIDService:
    MY_DEV_NAME = "RPi_HID_Joystick"
    PROFILE_DBUS_PATH = "/nl/rug/ds/heerkog/hid"  #dbus path of the bluez profile
    SDP_RECORD_PATH = sys.path[0] + "sdp/sdp_record_joystick.xml"  #file path of the sdp record to laod
    UUID = "00001124-0000-1000-8000-00805f9b34fb"  #HumanInterfaceDeviceServiceClass UUID

    def __init__(self, loop):
        mainloop = loop
        print("Configuring Bluez Profile.")

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

        # Retrieve the system bus
        system_bus = dbus.SystemBus()

        # Retrieve the Bluez Bluetooth Adapter interface
        adapter_properties = dbus.Interface(system_bus.get_object("org.bluez", "/org/bluez/hci0"), "org.freedesktop.DBus.Properties")

        # Power the Bluetooth adapter
        adapter_properties.Set('org.bluez.Adapter1', 'Powered', dbus.Boolean(1))

        # Allow the Bluetooth Adapter to pair
        adapter_properties.Set('org.bluez.Adapter1', 'PairableTimeout', dbus.UInt32(0))
        adapter_properties.Set('org.bluez.Adapter1', 'Pairable', dbus.Boolean(1))

        # Allow the Bluetooth Adapter to be discoverable
        adapter_properties.Set('org.bluez.Adapter1', 'DiscoverableTimeout', dbus.UInt32(0))
        adapter_properties.Set('org.bluez.Adapter1', 'Discoverable', dbus.Boolean(1))

        # Create our Bluez HID Profile
        self.profile = BluezHIDProfile(system_bus, self.PROFILE_DBUS_PATH)

        # Retrieve the Bluez Bluetooth Profile Manager interface
        profile_manager = dbus.Interface(system_bus.get_object("org.bluez", "/org/bluez"), "org.bluez.ProfileManager1")

        # Register our Profile with the Bluez Bluetooth Profile Manager
        profile_manager.RegisterProfile(self.PROFILE_DBUS_PATH, self.UUID, opts)

        print("Profile registered.")

        #create our HID device and pass a pointer to the input report function of our profile
        self.joystick = hidpi.hid.Joystick(self.profile.send_input_report)

        print("Device added.")


    # Read and return an SDP record from a file
    def read_sdp_service_record(self):
        print("Reading service record: " + self.SDP_RECORD_PATH)

        try:
            fh = open(self.SDP_RECORD_PATH, "r")
        except:
            sys.exit("Failed to read SDP record.")

        return fh.read()
