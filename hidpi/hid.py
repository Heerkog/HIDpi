from gpiozero import Button


#Class that represents the Joystick state
class Joystick:

    def __init__(self, report_function):
        #Define the Joystick state
        self.state = [
            0xA1,  #this is an input report
            0x04,  #Usage report = Joystick
            0x7F,  #X-axis between 0 and 255
            0x7F,  #Y-axis between 0 and 255
            0x00]  #unsigned char representing 3 buttons, rest empty
        self.report_function = report_function

        #Set up GPIO input
        self.up_button = Button("GPIO17")     #Up signal
        self.down_button = Button("GPIO18")   #Down signal
        self.left_button = Button("GPIO22")   #Left signal
        self.right_button = Button("GPIO23")  #Right signal

        #Bind state update methods to events
        self.up_button.when_pressed = self.x_axis_event
        self.up_button.when_released = self.x_axis_event
        self.down_button.when_pressed = self.x_axis_event
        self.down_button.when_released = self.x_axis_event
        self.left_button.when_pressed = self.y_axis_event
        self.left_button.when_released = self.y_axis_event
        self.right_button.when_pressed = self.y_axis_event
        self.right_button.when_released = self.y_axis_event

    def x_axis_event(self):
        self.state[2] = 127 + int(self.down_button.is_pressed) * 127 - int(self.up_button.is_pressed) * 127
        self.send_report()

    def y_axis_event(self):
        self.state[3] = 127 + int(self.right_button.is_pressed) * 127 - int(self.left_button.is_pressed) * 127
        self.send_report()

    def set_button1_down(self):
        self.state[4] = self.state[4] + 128;
        self.send_report()

    def set_button1_up(self):
        self.state[4] = self.state[4] - 128;
        self.send_report()

    def set_button2_down(self):
        self.state[4] = self.state[4] + 64;
        self.send_report()

    def set_button2_up(self):
        self.state[4] = self.state[4] - 64;
        self.send_report()

    def set_button3_down(self):
        self.state[4] = self.state[4] + 32;
        self.send_report()

    def set_button3_up(self):
        self.state[4] = self.state[4] - 32;
        self.send_report()

    def get_state(self):
        return self.state

    def send_report(self):
        print("Sending x:" + self.state[2] + " y:" + self.state[3] + " b:" + self.state[4])
        report = ""
        report += chr(self.state[0])
        report += chr(self.state[1])
        report += chr(self.state[2])
        report += chr(self.state[3])
        report += chr(self.state[4])

        self.report_function(report)
        return True
