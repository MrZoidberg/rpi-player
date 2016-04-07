RPi-Player
=========

###RPI Audiobook Player

this is my modification of [The One Button Audiobook Player](http://blogs.fsfe.org/clemens/2012/10/30/the-one-button-audiobook-player/) written by Michael Clemens

###Schematics
TODO:
![Schematics]()

###Run
```Shell
sudo /etc/init.d/rpi_player start
```

###Requirements
mpd
mpc
python-pyudev
[python-mpd2](https://github.com/Mic92/python-mpd2)

###Install
1. Setup your RPi with Raspbian
2. Install requirements
3. Copy rpi-player to sd card:
   ```Shell
   mkdir /rpi-player
   git clone https://github.com/MrZoidberg/rpi-player.git /rpi-player
   ```
4. Setup audio output. I've used 3.5mm jack: ```Shell sudo amixer cset numid=3 1```
5. (Optinal)Configure your mpd. With this config file it will save song position after reboot:
   ```Shell
   sudo cp /rpi-player/mpd.conf  /etc/mpd.conf
   ```
6. Copy run script into /etc/init.d: ```Shell sudo cp rpi-player /etc/init.d``` and
   make sure it's executable ```Shell chmod 755 /etc/init.d/rpi-player```

###Notes
I've tested it on Raspberry Pi model B+ with RASPBIAN and latest firmware.
