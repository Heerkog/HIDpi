# Bluetooth GPIO Joystick for Raspberry Pi
A Python script that takes GPIO input to emulate a Bluetooth joystick device.

# How it works
The script emulates a Bluetooth human interface device (HID) in the form of a joystick device with 3 buttons.
It takes as input GPIO signals as button presses on the Raspberry Pi's **GPIO17**, **GPIO18**, **GPIO22**, **GPIO23**, **GPIO24**, **GPIO25**, and **GPIO27** pins.
These signals are then send to the HID host that is connected to the HID device using Bluetooth.

The different GPIO pins represent the following actions:
  * North/Up: **GPIO18**
  * South/Down: **GPIO17**
  * West/Left: **GPIO23**
  * East/Right: **GPIO22**
  * Button 1: **GPIO24**
  * Button 2: **GPIO25**
  * Button 3: **GPIO27**

Since we are using GPIO input, the joystick state is either centered without any GPIO signals or fully extended with GPIO signals.
That is, the device state is either centered, or in a fully extended north, northeast, east, southeast, south, southwest, west, or northwest position.
As a result, the device operates more alike a d-pad than an analogue joystick that supports degrees of movement.
To account for degrees of movement, one should extend the `hid.Joystick` class and use different input methods.

# Installation
  * Install git bash using the command `sudo apt-get install git-core -y`.
  * Create a directory for the service, and enter it.
  * Clone this repository with the command `git clone https://github.com/Heerkog/HIDpi.git`.
  * Execute `sudo setup.sh` to install all required packages.

# Bluetooth setup
To make the Raspberry Pi discoverable as a HID device, a number of settings must be changed manually.
These settings change the Bluetooth device name and class of the Raspberry Pi from a generic desktop device to a HID main device with a joystick subclass.
If you want to keep using your Raspberry Pi as a generic desktop device, you may skip these steps.
 
The Raspberry pi Bluetooth stack settings can be initialized using the following commands: 

  * `cd /usr/local/etc`
  * `sudo ln -s /etc/bluetooth bluetooth` 

To change the settings, we edit two lines in the main.conf configuration file:

  * `nano ./bluetooth/main.conf`
  
Change the following two settings (and remove the # at the start of these two lines, if there):

```
Name = Bluetooth Joystick
Class = 0x000508
```

# Execution
To execute the HID service, we must run the bluetooth service in the compatibility and debug mode.
To achieve this, we must edit the `dbus-org.bluez.service` file by executing the following command:

  * `sudo nano /etc/systemd/system/dbus-org.bluez.service`
  
Edit the `ExecStart=` line under the `[Service]` heading to specify:
```
ExecStart=/usr/lib/bluetooth/bluetoothd --nodetach --compat --debug -p time
```

Next, we must create a settings file with the Bluetooth adapter's physical address and a fixed pin.
We use a fixed pin because we don't want to have to log in to the Raspberry Pi every time we want to pair with another device.

To create a settings file copy the `sample_settings.xml` file using the following command:
  * `cp sample_settings.xml settings.xml`
  
Then edit the `settings.xml` file:
  * `Nano settings.xml`

Change the `address` value in the file to the physical address of your Raspberry Pi's Bluetooth adapter.
To find the physical address of your adapter, you may execute the `sudo bluetoothctl show` command.
Next, change the `pin` value to one of your own choosing.

Finally, reboot and run the `boot.sh` script.

# Running as a service
To automatically start the service during boot, add the `hid.service` file as a start up service. 
First, edit the `hid.service` file to include the correct path to where you cloned this repository.
Then execute the following commands:
  * `sudo cp hid.service /etc/systemd/system/`
  * `sudo systemctl enable hid.service`
  * `sudo systemctl daemon-reload`
  * `sudo systemctl start hid.service`
  
You may check whether the service is working with:
  * `sudo systemctl status hid.service`
  
# Device discovery
The device is discoverable for 30 seconds after the service started.
To make it discoverable again for 30 seconds, trigger any of the assigned GPIO signals.

# Resources
The following resources were of interest during development:

* Bluetooth HID
  * [Bluetooth HID specification](https://www.bluetooth.org/docman/handlers/DownloadDoc.ashx?doc_id=246761)
  * [Bluetooth assigned numbers list](https://www.bluetooth.com/specifications/assigned-numbers/)
  * [Bluetooth device class list](http://domoticx.com/bluetooth-class-of-device-lijst-cod/)
* USB HID
  * [USB HID specification](https://www.usb.org/document-library/device-class-definition-hid-111)
  * [USB report descriptor tool](https://www.usb.org/document-library/hid-descriptor-tool)
  * [USB HID report descriptor tutorial](https://eleccelerator.com/tutorial-about-usb-hid-report-descriptors/)
* [Bluez Bluetooth stack](https://git.kernel.org/pub/scm/bluetooth/bluez.git)
  * [Adapter API](https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/adapter-api.txt)
  * [Agent API](https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/agent-api.txt)
  * [Profile API](https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/profile-api.txt)
  * [Simple Agent example](https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/test/simple-agent)
  * [HFC example](https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/test/test-hfp)
* Repositories - note that these use depricated Bluez tools and packages
  * [mLabviet/BL_keyboard_RPI](https://github.com/mlabviet/BL_keyboard_RPI)
  * [AnesBenmerzoug/Bluetooth_HID](https://github.com/AnesBenmerzoug/Bluetooth_HID)

# Prototype for R-net use

A prototype was developed for use with R-net compatible wheelchairs. The following elements were used:

* A Raspberry Pi Zero.
* An R-net input/output module.
* A voltage convertor/isolation board 
  (Specifically, the AL-ZARD DST-1R8P-P 24v to 3.3v optocoupler isolation board).
* A DE-9 connector.
* A micro-USB connector.

The prototype takes as input directional signals from the R-net input/output module's output connector. 
The R-net module's output consists of a DE-9 connector with the following pin layout:

| Pin | Function |
|-----| -------- |
| 1   | Forward  |
| 2   | Reverse  |
| 3   | Left     |
| 4   | Right    |
| 5   | Speed +  |
| 6   | Speed -  |
| 7   | Horn     |
| 8   | Common   |
| 9   | NC       |

Each pin has an output rating of 0.5A 24Vdc, is normally open, and should be closed to common (i.e., pin 8).

Since the Raspberry Pi Zero operates at 3.3V, the 24V directional signals are first converted and 
isolated using a voltage convertion/isolation board by connecting pins 1 through 7 of the R-net 
module to the positive 24V inputs of the voltage convertor/isolation board. Pin 8 of the R-net 
module (common) is shared and connected to each negative input.

The 3.3V output side of the voltage convertion/isolation board is connected to the Raspberry Pi 
Zero's GPIO header. That is, the positive input is connected to one of the header's 3.3Vdc power 
pins, the negative to one of the header's ground pins, and outputs 1 through 7 to the **GPIO18**, 
**GPIO17**, **GPIO23**, **GPIO22**, **GPIO24**, **GPIO25**, and **GPIO27** pins, respectively.

The Raspberry Pi Zero is powered using its micro-USB connector.

The final prototype looks like this:

![Overview](https://github.com/Heerkog/HIDpi/blob/master/figures/overview.jpg =500x)

![Details](https://github.com/Heerkog/HIDpi/blob/master/figures/inside.jpg =500x)

![Case](https://github.com/Heerkog/HIDpi/blob/master/figures/case.jpg =500x)
  

# Repository overview
The repository is structured as follows:

* `figures` - directory containing the figures included in this read.me file.
* `hidpi` - main Python module.
  * `__init__.py` - module initialization. 
  * `__main__.py` - module main.
  * `hid.py` - Python scripts related to the human interface device classes.
  * `service.py` - Python scripts related to the Bluez Bluetooth service.
* `sdp` - directory containing files related to the Bluetooth Service Discovery Protocol (SDP).
  * `input_report_descriptor` - directory containing generated USB report descriptor files. Files are unused, as the report is included in the SDP file. Added for completeness.
    * `Joystick3Buttons.h` - header file version of the USB report descriptor.
    * `Joystick3Buttons.hid` - binary version of the USB report descriptor.
    * `Joystick3Buttons.txt` - text file version of the USB report descriptor.
  * `sdp_record_joystick.xml` - the sdp file used by the script.
  * `sdp_record_joystick_annotated.xml` - annotated version of the sdp file used.
* `.gitignore` - repository ignore file.
* `LICENSE.txt` - MIT License that covers this repository.
* `README.md` - read me file containing this text.
* `boot.sh` - shell script that starts the Python module.
* `hid.service` - service file that allows the to start service during boot.
* `sample_settings.xml` - example of a settings file used by the python service script.
* `setup.sh` - shell script that installs required packages.
