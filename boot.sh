# Manually stop and start the Bluetooth service
sudo /etc/init.d/bluetooth stop &>/dev/null &
sleep 1
sudo service bluetooth stop &>/dev/null &
sleep 2
sudo /usr/sbin/bluetoothd --nodetach --debug &>/dev/null &

# Wait for the service to start
sleep 2

# Start the Python script
sudo python -m hidpi
