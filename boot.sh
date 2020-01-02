# Manually stop and start the Bluetooth service
sudo service dbus restart &>/dev/null &
sleep 5
sudo /etc/init.d/bluetooth stop &>/dev/null &
sleep 5
sudo service bluetooth stop &>/dev/null &
sleep 5
sudo /usr/sbin/bluetoothd --nodetach --compat --debug -p time &>/dev/null &

# Wait for the service to start
sleep 10

# Start the Python script
sudo python -m hidpi
