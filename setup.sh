#!/bin/sh
echo EST5EDT > /etc/timezone
rm /etc/localtime
ln -s /usr/share/zoneinfo/America/New_York /etc/localtime
mount /dev/mmcblk0p1 /mnt
cp uEnv.txt /mnt/
cp getty\@tty1.service /etc/systemd/system/getty-target-wants/
cp serial-getty\@ttyO0.service /etc/systemd/system/getty-target-wants/
systemctl --system daemon-reload 
systemctl disable gdm.service
systemctl stop gdm.service
systemctl restart getty\@tty1.service
systemctl restart serial-getty\@ttyO0.service
systemctl enable dropbear.socket
systemctl start dropbear.socket
opkg update
opkg install python-pyserial python-misc python-compiler python-pip python-setuptools python-smbus libapr-1-0 libneon27 libaprutil-1-0 subversion libsdl-image-1.2-dev libsdl-mixer-1.2-dev libsdl-ttf-2.0-dev directfb-dev
#opkg install python-dev libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsdl1.2-dev libsmpeg-dev python-numpy subversion libportmidi-dev ffmpeg libswscale-dev libavformat-dev libavcodec-dev
pip install Adafruit_BBIO
ln -s /usr/include/libv4l1-videodev.h   /usr/include/linux/videodev.h
tar xzf SDL-1.2.15.tar.gz
cd SDL-1.2.15
./configure --prefix=/usr
make
make install
cd ..
tar xzf pygame-1.9.0release.tar.gz 
cd pygame-1.9.0release
touch readme.html
python setup.py 
cd ..
tar xzf pywapi-0.3.5.tar.gz
cd pywapi-0.3.5
python setup.py install
cd ..
cp hotandcold.service /lib/systemd/system
systemctl enable hotandcold.service 
systemctl start hotandcold.service 

