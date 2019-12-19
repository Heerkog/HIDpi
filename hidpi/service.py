import os
import sys
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
import socket

#define a bluez 5 profile object for our keyboard
class BluezProfile(dbus.service.Object):
    fd = -1

    @dbus.service.method("org.bluez.Profile1", in_signature="", out_signature="")
    def Release(self):
        print("Release")
        mainloop.quit()

    @dbus.service.method("org.bluez.Profile1", in_signature="", out_signature="")
    def Cancel(self):
        print("Cancel")

    @dbus.service.method("org.bluez.Profile1", in_signature="oha{sv}", out_signature="")
    def NewConnection(self, path, fd, properties):
        self.fd = fd.take()
        print("NewConnection(%s, %d)" % (path, self.fd))
        for key in properties.keys():
            if key == "Version" or key == "Features":
                print("  %s = 0x%04x" % (key, properties[key]))
            else:
                print("  %s = %s" % (key, properties[key]))

    @dbus.service.method("org.bluez.Profile1", in_signature="o", out_signature="")
    def RequestDisconnection(self, path):
        print("RequestDisconnection(%s)" % (path))

        if (self.fd > 0):
            os.close(self.fd)
            self.fd = -1

    def __init__(self, bus, path):
        dbus.service.Object.__init__(self, bus, path)


#create a bluetooth device to emulate a HID joystick
class BTJoystick:
    MY_ADDRESS = "B8:27:EB:77:31:44"
    MY_DEV_NAME = "RPi_HID_Joystick"
    control_port = 37  #17  #HID control port as specified in SDP > Protocol Descriptor List > L2CAP > HID Control Port
    interrupt_port = 39  #19  #HID interrupt port as specified in SDP > Additional Protocol Descriptor List > L2CAP > HID Interrupt Port
    PROFILE_DBUS_PATH="/bluez/heerkog/bthid_profile"  #dbus path of the bluez profile
    SDP_RECORD_PATH = sys.path[0] + "/../sdp/sdp_record_joystick.xml"  #file path of the sdp record to laod
    UUID="00001124-0000-1000-8000-00805f9b34fb"  #HumanInterfaceDeviceServiceClass UUID

    def __init__(self):
        print("Setting up BT device")
        self.init_bt_device()
        self.init_bluez_profile()

    #configure the bluetooth hardware device
    def init_bt_device(self):
        print("Configuring for name " + self.MY_DEV_NAME)
        #set the device class to a joystick and set the name
        os.system("hciconfig hci0 up")
        os.system("hciconfig hcio class 0x000508")
        os.system("hciconfig hcio name " + self.MY_DEV_NAME)

        #make the device discoverable
        os.system("hciconfig hcio piscan")

    #set up a bluez profile to advertise device capabilities from a loaded service record
    def init_bluez_profile(self):
        print("Configuring Bluez Profile")

        #setup profile options
        service_record = self.read_sdp_service_record()

        opts = {
            "ServiceRecord": service_record,
            "Role": "server",
            "RequireAuthentication": False,
            "RequireAuthorization": False
        }

        #retrieve a proxy for the bluez profile interface
        bus = dbus.SystemBus()
        manager = dbus.Interface(bus.get_object("org.bluez", "/org/bluez"), "org.bluez.ProfileManager1")

        profile = BluezProfile(bus, self.PROFILE_DBUS_PATH)

        manager.RegisterProfile(self.PROFILE_DBUS_PATH, self.UUID, opts)

        print("Profile registered ")

    #read and return an sdp record from a file
    def read_sdp_service_record(self):
        print("Reading service record: " + self.SDP_RECORD_PATH)

        try:
            fh = open(self.SDP_RECORD_PATH, "r")
        except:
            sys.exit("Failed to read SDP record.")

        return fh.read()

    #listen for incoming client connections
    def listen(self):
        print("Waiting for connections")
        self.control_socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_L2CAP)
        self.interrupt_socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_L2CAP)

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
        GLib.io_add_watch(self.control_socket.fileno(), GLib.IO_IN, self.accept_control)
        GLib.io_add_watch(self.interrupt_socket.fileno(), GLib.IO_IN, self.accept_interrupt)

        print("Watching sockets")

    def accept_control(self, source, cond):
        self.control_channel, cinfo = self.control_socket.accept()
        print("Got a connection on the control channel from " + cinfo[0])
        return True

    def accept_interrupt(self, source, cond):
        self.interrupt_channel, cinfo = self.interrupt_socket.accept()
        print("Got a connection on the interrupt channel from " + cinfo[0])
        return True

    #send a string to the bluetooth host machine
    def send_input_report(self, report):
        message = chr(report[0]) + chr(report[1]) + chr(report[2]) + chr(report[3]) + chr(report[4])

        print("Sending "+ message)
        self.cinterrupt.send(message)


#define a dbus HID service
class BTHIDService(dbus.service.Object):

    def __init__(self):
        print("Setting up service")
        #set up as a dbus service
        bus_name = dbus.service.BusName("nl.rug.ds.heerkog.bthidservice", bus=dbus.SystemBus())
        dbus.service.Object.__init__(self, bus_name, "/nl/rug/ds/heerkog/bthidservice")

        #create and setup our device
        self.device = BTJoystick()

        #start listening for connections
        self.device.listen()

    @dbus.service.method("nl.rug.ds.heerkog.bthidservice", in_signature="ay")
    def send_input_report(self, report):
        self.device.send_input_report(report)


#main routine
if __name__ == "__main__":
    # we an only run as root
    if not os.geteuid() == 0:
        sys.exit("Only root can run this script")

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    mainloop = GLib.MainLoop()
    myservice = BTHIDService()
    mainloop.run()