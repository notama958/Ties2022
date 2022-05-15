#!/bin/bash
#sudo pulseaudio -D
pulseaudio --start
bluetoothctl power on
bluetoothctl connect <bluetooth_speaker_MAC_address>
