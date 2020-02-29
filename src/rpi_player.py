import json
import os
import time
import traceback
import pyudev
from GPIOHWD import GPIOHWD
from player import Player


def checkForUSBDevice(driveName):
    res = ""
    context = pyudev.Context()
    try:
        for device in context.list_devices(subsystem='block',
                                           DEVTYPE='partition'):
            if device.get('ID_FS_LABEL') == driveName:
                    res = device.device_node
        return res
    except Exception:
        return res


def loadMusic(device, mountPoint, musicDir, tagCacheDir):        
    os.system("mkdir -p "+mountPoint)
    os.system("mount "+device+" "+mountPoint)
    os.system("/etc/init.d/mpd stop")
    os.system("rm -rf "+musicDir+"*")
    os.system("cp "+mountPoint+"* "+musicDir)
    os.system("umount "+mountPoint)
    os.system("rm "+tagCacheDir)
    os.system("/etc/init.d/mpd start")
    os.system("mpc clear")
    os.system("mpc listall | mpc add")
    os.system("/etc/init.d/mpd restart")


def main():
    hwd = None    
    print ("====> RPi player start")

    try:
        # parent = current_thread()
        hwd = GPIOHWD()
        driveName = "AUDIO"
        with open('config.json') as json_file:
            data = json.load(json_file)       
            driveName = data['driveLabel']  
            print("use drive with label", driveName)
            hwd.setStatusLed(data['gpio']['statusLed'])
            hwd.setPowerLed(data['gpio']['powerLed'])
            hwd.setNextButton(data['gpio']['nextButton'])
            hwd.setPlayButton(data['gpio']['playButton'])
            hwd.setVolumeUpButton(data['gpio']['volumeUpButton'])
            hwd.setVolumeDownButton(data['gpio']['volumeDownButton'])
            hwd.setup()

        
        hwd.flashLed(hwd.powerLed, 2, 50)
        hwd.flashLed(hwd.statusLed, 2, 50)

        player = Player()
        player.setPort('6600')
        player.setHost('localhost')        
        player.connectMPD()

        time.sleep(5)
        hwd.stopFlash(hwd.powerLed)
        hwd.stopFlash(hwd.statusLed)
        hwd.updateLed(hwd.powerLed, True)
        print("setup complete")

        noSongsLed = False
        prevSongsLed = False
        playPressed = 0
        while(True):
            pendrive = checkForUSBDevice(driveName)

            if pendrive != "":
                print("new music detected on drive", pendrive)
                hwd.flashLed(hwd.statusLed, 2, 50)

                player.disconnect()
                loadMusic(pendrive, "/mnt/usb/", "/var/lib/mpd/music/",
                                    "/var/lib/mpd/tag_cache")
                player.connectMPD()
                print("new music added")
                hwd.flashLed(hwd.statusLed, 0.5, 50)
                print("waiting for usb drive unmount...")
                while checkForUSBDevice(driveName) == pendrive:
                    time.sleep(0.5)
                print("usb drive removed")
                hwd.cleanup()
                hwd.setup()

            songsCount = player.getStats()["songs"]

            if songsCount == 0:
                if noSongsLed is False & prevSongsLed is True:
                    print("no songs found")
                    hwd.flashLed(hwd.statusLed, 0.5, 50)
                    noSongsLed = True
                    prevSongsLed = False
            else:
                if noSongsLed is True & prevSongsLed is False:
                    print("songs found")
                    hwd.stopFlash(hwd.statusLed)
                    noSongsLed = False
                    prevSongsLed = True

                if hwd.isButtonPressed(hwd.playButton):
                    player.playPause()

                hwd.updateLed(hwd.statusLed, player.getState() == "play")

                if hwd.isButtonPressed(hwd.volumeUpButton):
                    player.increaseVolume(2)

                if hwd.isButtonPressed(hwd.volumeDownButton):
                    player.decreaseVolume(2)

                if hwd.isButtonPressed(hwd.nextButton):
                    player.nextSong()

            time.sleep(0.1)

        input("Press Enter to exit...")
    except KeyboardInterrupt:
        print("exiting from button")
    except Exception:
        traceback.print_exc()

    hwd.cleanup()

if __name__ == '__main__':
    main()
