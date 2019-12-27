from gpiozero import Button
import struct

#Class that represents a general HID device state
class HumanInterfaceDevice(object):

    def __init__(self, report_function):
        self.report_function = report_function

        self.state = bytearray()
        self.state.append(struct.pack("B", 0xA1))  # this is an input report

    def get_state(self):
        return self.state

    def send_report(self):
        print("x: {0} y: {1} b: {2}".format(self.state[1], self.state[2], self.state[3]))
        self.report_function(self.state)
        return True


#Class that represents the Joystick state
class Joystick(HumanInterfaceDevice):

    def __init__(self, report_function):
        super(Joystick, self).__init__(report_function)

        #Define the Joystick state
        self.state.append(struct.pack("b", 0x00))  # X-axis between -127 and 127
        self.state.append(struct.pack("b", 0x00))  # Y-axis between -127 and 127
        self.state.append(struct.pack("B", 0x00))  # unsigned char representing 3 buttons, rest of bits are constants

        #Set up GPIO input
        self.up_button = Button("GPIO17")     #Up signal
        self.down_button = Button("GPIO18")   #Down signal
        self.left_button = Button("GPIO22")   #Left signal
        self.right_button = Button("GPIO23")  #Right signal

        #Bind state update methods to events
        self.left_button.when_pressed = self.x_axis_event
        self.left_button.when_released = self.x_axis_event
        self.right_button.when_pressed = self.x_axis_event
        self.right_button.when_released = self.x_axis_event
        self.up_button.when_pressed = self.y_axis_event
        self.up_button.when_released = self.y_axis_event
        self.down_button.when_pressed = self.y_axis_event
        self.down_button.when_released = self.y_axis_event

    def x_axis_event(self):
        self.state[1] = struct.pack("b", (int(self.right_button.is_pressed) - int(self.left_button.is_pressed)) * 127)
        self.send_report()

    def y_axis_event(self):
        self.state[2] = struct.pack("b", (int(self.up_button.is_pressed) - int(self.down_button.is_pressed)) * 127)
        self.send_report()

    def set_button1_down(self):
        # Raise the first bit
        self.state[3] = self.state[3] + 128;
        self.send_report()

    def set_button1_up(self):
        # Lower the first bit
        self.state[3] = self.state[3] - 128;
        self.send_report()

    def set_button2_down(self):
        # Raise the second bit
        self.state[3] = self.state[3] + 64;
        self.send_report()

    def set_button2_up(self):
        # Lower the second bit
        self.state[3] = self.state[3] - 64;
        self.send_report()

    def set_button3_down(self):
        # Raise the third bit
        self.state[3] = self.state[3] + 32;
        self.send_report()

    def set_button3_up(self):
        # Lower the third bit
        self.state[3] = self.state[3] - 32;
        self.send_report()
