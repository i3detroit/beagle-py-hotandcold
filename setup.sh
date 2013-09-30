#!/bin/sh
mount /dev/mmcblk0p1 /mnt
cp uEnv.txt /mnt/
cp getty\@tty1.service /etc/systemd/system/getty-target-wants/
systemctl --system daemon-reload 
systemctl disable gdm.service
systemctl stop gdm.service
systemctl restart getty\@tty1.service
opkg update
opkg install python-misc python-compiler
systemctl enable dropbear.socket
systemctl start dropbear.socket
