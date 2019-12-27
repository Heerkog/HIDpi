# Bluetooth GPIO Joystick for Raspberry Pi
A Python script that takes GPIO input to emulate a Bluetooth joystick device.

# How it works
The script emulates a Bluetooth human interface device (HID) in the form of a joystick device with 3 buttons.
It takes as input GPIO signals as button presses on the Raspberry Pi's **GPIO17**, **GPIO18**, **GPIO22**, **GPIO23**, **GPIO24**, **GPIO25**, and **GPIO27** pins.
These signals are then send to the HID host that is connected to the HID device using Bluetooth.
Since we are using GPIO input, the joystick state is either centered without any GPIO signals or fully extended with GPIO signals.
As a result, the device operates more alike a d-pad than an analogue joystick that supports degrees of movement.

The different GPIO pins represent the following actions:
  * Up: **GPIO17**
  * Down: **GPIO18**
  * Left: **GPIO22**
  * Right: **GPIO23**
  * Button 1: **GPIO24**
  * Button 2: **GPIO25**
  * Button 3: **GPIO27**

To account for degrees of movement, one should extend the `hid.Joystick` class and use different input methods.

# Installation
Run `setup.sh`

# Bluetooth setup
The Raspberry pi Bluetooth