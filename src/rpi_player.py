import json
import os
import time
import traceback
import pyudev
from GPIOHWD import GPIOHWD, ButtonState
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
    print("====> RPi player start")

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
            hwd.setSystemLed(data['gpio']['systemLed'])
            hwd.setNextButton(data['gpio']['nextButton'])
            hwd.setPlayButton(data['gpio']['playButton'])
            hwd.setVolumeUpButton(data['gpio']['volumeUpButton'])
            hwd.setVolumeDownButton(data['gpio']['volumeDownButton'])            

        player = Player()
        player.setPort('6600')
        player.setHost('localhost')
        player.connectMPD()

        def volumeUp():
            player.increaseVolume(5)

        def volumeDown():
            player.decreaseVolume(5)

        hwd.setup(volumeUp, volumeDown)

        hwd.flashLed(hwd.powerLed, 2, 50)
        hwd.flashLed(hwd.systemLed, 2, 50)
        hwd.flashLed(hwd.statusLed, 2, 50) 

        time.sleep(3)

        hwd.stopFlash(hwd.powerLed)
        hwd.stopFlash(hwd.statusLed)
        hwd.stopFlash(hwd.systemLed)

        print("setup complete")

        noSongsLed = False
        prevSongsLed = False
        # playPressed = 0
        playButtonState = ButtonState.NOT_PRESSED
        nextButtonState = ButtonState.NOT_PRESSED
        btnStatus = ButtonState.NOT_PRESSED

        while(True):
            hwd.updateLed(hwd.powerLed, True)

            pendrive = checkForUSBDevice(driveName)

            if pendrive != "":
                print("new music detected on drive", pendrive)
                hwd.flashLed(hwd.statusLed, 2, 50)
                # player.stop()
                player.disconnect()
                loadMusic(pendrive, "/mnt/usb/", "/var/lib/mpd/music/",
                                    "/var/lib/mpd/tag_cache")
                player.connectMPD()
                MPDClient.replay_gain_mode("album")
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
                if noSongsLed is False and prevSongsLed is True:
                    print("no songs found")
                    hwd.flashLed(hwd.systemLed, 0.5, 50)
                    noSongsLed = True
                    prevSongsLed = False
            else:
                if noSongsLed is True and prevSongsLed is False:
                    print("songs found")
                    hwd.stopFlash(hwd.systemLed)
                    noSongsLed = False
                    prevSongsLed = True

                # Next button

                nextButtonState = hwd.isButtonPressed(hwd.nextButton, True)
                if nextButtonState is ButtonState.DOUBLE_PRESSED:
                    player.prevSong()
                if nextButtonState is ButtonState.PRESSED:
                    player.nextSong()
                    # hwd.clearButtonState(hwd.nextButton)
                nextButtonState = ButtonState.NOT_PRESSED

                # Play button

                playButtonState = hwd.isButtonPressed(hwd.playButton, False)
                if playButtonState is ButtonState.DOUBLE_PRESSED:
                    player.seekCur(-15)
                if playButtonState is ButtonState.PRESSED:
                    player.playPause()
                playButtonState = ButtonState.NOT_PRESSED

                hwd.updateLed(hwd.statusLed, player.getState() == "play")

                # Volume up

                # btnStatus = hwd.isButtonPressed(hwd.volumeUpButton, False)
                # if btnStatus is ButtonState.PRESSED:
                #     player.increaseVolume(5)
                #     # hwd.clearButtonState(hwd.volumeUpButton)
                # btnStatus = ButtonState.NOT_PRESSED

                # # Volume down

                # btnStatus = hwd.isButtonPressed(hwd.volumeDownButton, False)
                # if btnStatus is ButtonState.PRESSED:
                #     player.decreaseVolume(5)
                #     # hwd.clearButtonState(hwd.volumeDownButton)
                # btnStatus = ButtonState.NOT_PRESSED

            time.sleep(0.2)

        input("Press Enter to exit...")
    except KeyboardInterrupt:
        print("exiting from button")
    except Exception:
        traceback.print_exc()

    hwd.cleanup()


if __name__ == '__main__':
    main()
