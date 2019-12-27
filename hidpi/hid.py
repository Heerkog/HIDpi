from gpiozero import Button


#Class that represents a general HID device state
class HumanInterfaceDevice:

    def __init__(self, report_function):
        self.state = [
            0xA1]  #this is an input report
        self.report_function = report_function

    def get_state(self):
        return self.state

    def send_report(self):
        report = ""
        for val in self.state:
            report += chr(val)

        self.report_function(report)

        return True


#Class that represents the Joystick state
class Joystick(HumanInterfaceDevice):

    def __init__(self, report_function):
        super.__init__(report_function)

        #Define the Joystick state
        self.state = [
            0xA1,  #this is an input report
            0x00,  #X-axis between -127 and 127
            0x00,  #Y-axis between -127 and 127
            0x00]  #unsigned char representing 3 buttons, rest empty

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
        x = (int(self.right_button.is_pressed) - int(self.left_button.is_pressed)) * 127
        # If x is negative, manually flag the sign bit to allow for conversion from int to char
        if x < 0:
            x = abs(x) + 128
        self.state[1] = x
        self.send_report()

    def y_axis_event(self):
        y = (int(self.up_button.is_pressed) - int(self.down_button.is_pressed)) * 127
        # If y is negative, manually flag the sign bit to allow for conversion from int to char
        if y < 0:
            y = abs(y) + 128
        self.state[2] = y
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
