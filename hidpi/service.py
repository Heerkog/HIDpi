import os
import sys
import dbus
import dbus.service
from gi.repository import GLib as glib
import dbus.mainloop.glib
from hidpi.hid import Joystick
import bluetooth


dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

global mainloop

#define a bluez 5 profile object for our keyboard
class BluezProfile(dbus.service.Object):
    file_descriptor = -1
    interrupt_channel = None

    def __init__(self, bus, name, path):
        bus_name=dbus.service.BusName(name,bus)
        dbus.service.Object.__init__(self, bus_name, path)

    @dbus.service.method("org.bluez.Profile1", in_signature="", out_signature="")
    def Release(self):
        print("Release")
        mainloop.quit()

    @dbus.service.method("org.bluez.Profile1", in_signature="", out_signature="")
    def Cancel(self):
        print("Cancel")

    @dbus.service.method("org.bluez.Profile1", in_signature="oha{sv}", out_signature="")
    def NewConnection(self, path, file_descriptor, properties):
        self.file_descriptor = file_descriptor.take()
        self.interrupt_channel = socket.fromfd(file_descriptor, socket.AF_BLUETOOTH, socket.SOCK_STREAM)

        print("NewConnection(%s, %d)" % (path, self.file_descriptor))

        for key in properties.keys():
            if key == "Version" or key == "Features":
                print("  %s = 0x%04x" % (key, properties[key]))
            else:
                print("  %s = %s" % (key, properties[key]))

        glib.io_add_watch(self.interrupt_channel, glib.PRIORITY_DEFAULT, glib.IO_IN | glib.IO_PRI, self.interrupt_channel)

    @dbus.service.method("org.bluez.Profile1", in_signature="o", out_signature="")
    def RequestDisconnection(self, path):
        print("RequestDisconnection(%s)" % (path))

        if (self.file_descriptor > 0):
            os.close(self.file_descriptor)
            self.file_descriptor = -1

    def interrupt_callback(self, file_descriptor, conditions):
        data = os.read(file_descriptor, 1024)
        print("{0}".format(data))
        return True

    def interrupt_write(self, value):
        try:
            os.write(self.file_descriptor, value.encode('utf8'))
        except ConnectionResetError:
            self.file_descriptor = -1

#create a bluetooth device to emulate a HID joystick
class BTHIDService:
    MY_ADDRESS = "B8:27:EB:77:31:44"
    MY_DEV_NAME = "RPi_HID_Joystick"
    control_port = 15  #HID control port as specified in SDP > Protocol Descriptor List > L2CAP > HID Control Port
    interrupt_port = 16  #HID interrupt port as specified in SDP > Additional Protocol Descriptor List > L2CAP > HID Interrupt Port
    PROFILE_DBUS_PATH = "/nl/rug/ds/heerkog/hid"  #dbus path of the bluez profile
    PROFILE_DBUS_NAME = "nl.rug.ds.heerkog.hid"  #dbus mame of the bluez profile
    SDP_RECORD_PATH = sys.path[0] + "/sdp/sdp_record_joystick.xml"  #file path of the sdp record to laod
    UUID = "00001124-0000-1000-8000-00805f9b34fb"  #HumanInterfaceDeviceServiceClass UUID

    def __init__(self):
        dbus.mainloop.glib.threads_init()
        print("Setting up service")
        #create joystick class
        self.joystick = Joystick(self)

        self.listen()
        mainloop = glib.MainLoop()
        print("Configuring Bluez Profile")

        #setup profile options
        service_record = self.read_sdp_service_record()

        opts = {
            "ServiceRecord": service_record,
            "Role": "server",
            "AutoConnect": True,
            "RequireAuthentication": False,
            "RequireAuthorization": False
        }

        #retrieve a proxy for the bluez profile interface
        system_bus = dbus.SystemBus()

        adapter_properties = dbus.Interface(system_bus.get_object("org.bluez", "/org/bluez/hci0"), "org.freedesktop.DBus.Properties")
        adapter_properties.Set('org.bluez.Adapter1', 'Powered', dbus.Boolean(1))
        adapter_properties.Set('org.bluez.Adapter1', 'Pairable', dbus.Boolean(1))
        adapter_properties.Set('org.bluez.Adapter1', 'Discoverable', dbus.Boolean(1))

        # self.profile = BluezProfile(system_bus, self.PROFILE_DBUS_NAME, self.PROFILE_DBUS_PATH)

        profile_manager = dbus.Interface(system_bus.get_object("org.bluez", "/org/bluez"), "org.bluez.ProfileManager1")
        profile_manager.RegisterProfile(self.PROFILE_DBUS_PATH, self.UUID, opts)

        print("Profile registered")

        # self.btkservice = system_bus.get_object(self.PROFILE_DBUS_NAME, self.PROFILE_DBUS_PATH)
        # self.iface = dbus.Interface(self.btkservice, self.PROFILE_DBUS_NAME)

        print("Profile ")

        mainloop.run()

    #listen for incoming client connections
    def listen(self):
        print("Waiting for connections")
        self.control_socket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        self.interrupt_socket = bluetooth.BluetoothSocket(bluetooth.L2CAP)

        #Set sockets to non-blocking
        self.control_socket.setblocking(0)
        self.interrupt_socket.setblocking(0)

        #bind these sockets to a port
        self.control_socket.bind((self.MY_ADDRESS, self.control_port))
        self.interrupt_socket.bind((self.MY_ADDRESS, self.interrupt_port))

        #Start listening on the server sockets with limit of 1 connection
        self.control_socket.listen(1)
        self.interrupt_socket.listen(1)

        #Define channels
        self.control_channel = None
        self.interrupt_channel = None

        #Watch sockets
        glib.io_add_watch(self.control_socket.fileno(), glib.IO_IN, self.accept_control)
        glib.io_add_watch(self.interrupt_socket.fileno(), glib.IO_IN, self.accept_interrupt)

        print("Watching sockets")

    def accept_control(self, source, cond):
        self.control_channel, cinfo = self.control_socket.accept()
        print("Got a connection on the control channel from " + cinfo[0])
        return True

    def accept_interrupt(self, source, cond):
        self.interrupt_channel, cinfo = self.interrupt_socket.accept()
        print("Got a connection on the interrupt channel from " + cinfo[0])
        return True

    #read and return an sdp record from a file
    def read_sdp_service_record(self):
        print("Reading service record: " + self.SDP_RECORD_PATH)

        try:
            fh = open(self.SDP_RECORD_PATH, "r")
        except:
            sys.exit("Failed to read SDP record.")

        return fh.read()

    #send a string to the bluetooth host machine
    def send_input_report(self, report):
        message = chr(report[0]) + chr(report[1]) + chr(report[2]) + chr(report[3]) + chr(report[4])

        print("Sending "+ message)
        self.profile.interrupt_write(message)