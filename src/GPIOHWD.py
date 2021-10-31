import RPi.GPIO as GPIO
import time
from enum import Flag, auto

BUTTON_PRESS_DELTA = 1


class ButtonState(Flag):
    NOT_PRESSED = auto()
    PRESSED = auto()
    DOUBLE_PRESSED = auto()
    AT_LEAST_TWICE_PRESSED = PRESSED | DOUBLE_PRESSED


class GPIOHWD(object):

    def __init__(self,):
        print("GPIO version: " + GPIO.VERSION)
        self._statusLed = -1
        self._powerLed = -1
        self._systemLed = -1
        self._playButton = -1
        self._volumeUpButton = -1
        self._volumeDownButton = -1
        self._nextButton = -1
        self._flashes = dict()
        self._times = dict.fromkeys(range(1, 41), 0)

    @property
    def statusLed(self):
        return self._statusLed

    @property
    def powerLed(self):
        return self._powerLed

    @property
    def systemLed(self):
        return self._systemLed

    @property
    def playButton(self):
        return self._playButton

    @property
    def volumeUpButton(self):
        return self._volumeUpButton

    @property
    def volumeDownButton(self):
        return self._volumeDownButton

    @property
    def nextButton(self):
        return self._nextButton

    def setSystemLed(self, channel):
        print("system led is set to ", channel)
        self._systemLed = channel

    def setStatusLed(self, channel):
        print("status led is set to ", channel)
        self._statusLed = channel

    def setPowerLed(self, channel):
        print("power led is set to ", channel)
        self._powerLed = channel

    def setPlayButton(self, channel):
        print("play button is set to ", channel)
        self._playButton = channel

    def setVolumeDownButton(self, channel):
        print("volume down button is set to ", channel)
        self._volumeDownButton = channel

    def setVolumeUpButton(self, channel):
        print("volume up button is set to ", channel)
        self._volumeUpButton = channel

    def setNextButton(self, channel):
        print("volume next button is set to ", channel)
        self._nextButton = channel

    def flashLed(self, channel, speed, time):
        self.stopFlash(channel)
        print("flashing led " + str(channel) + " at freq " + str(speed) +
              " with duty " + str(time))
        pwm = GPIO.PWM(channel, speed)
        pwm.start(time)
        self._flashes[channel] = pwm

    def stopFlash(self, channel):
        if channel in self._flashes:
            print("stop flashing led " + str(channel))
            pwm = self._flashes.pop(channel, None)
            pwm.stop()

    def updateLed(self, channel, turnOn):
        # print("led " + str(led) + " is set to " + str(turnOn))
        if turnOn is True:
            GPIO.output(channel, GPIO.LOW)
        else:
            GPIO.output(channel, GPIO.HIGH)

    def isButtonPressed(self, channel, supportDoublePress):
        isDetected = GPIO.event_detected(channel)
        curTime = time.time()

        if isDetected is False:
            return ButtonState.NOT_PRESSED

        if supportDoublePress is False:
            print("isButtonPressed " + str(channel) +
                  " detected: ButtonState.PRESSED")
            return ButtonState.PRESSED

        while(time.time() - curTime <= 1):
            time.sleep(0.2)
            secondEventDetected = GPIO.event_detected(channel)
            if secondEventDetected is True:
                print("isButtonPressed " + str(channel) +
                      " detected: ButtonState.DOUBLE_PRESSED")
                return ButtonState.DOUBLE_PRESSED
        print("isButtonPressed " + str(channel) +
              " detected: ButtonState.PRESSED")
        return ButtonState.PRESSED

    def clearButtonState(self, channel):
        self._times[channel] = 0

    def getInput(self, channel) -> bool:
        return GPIO.input(channel)

    def setup(self):
        GPIO.setmode(GPIO.BOARD)
        leds = [self._powerLed, self._statusLed, self._systemLed]
        buttons = [self._playButton, self._volumeUpButton,
                   self._volumeDownButton, self._nextButton]

        GPIO.setup(leds, GPIO.OUT)
        GPIO.setup(buttons, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(self._playButton, GPIO.RISING, bouncetime=500)
        GPIO.add_event_detect(self._nextButton, GPIO.RISING, bouncetime=500)
        GPIO.add_event_detect(self._volumeUpButton,
                              GPIO.RISING, bouncetime=300)
        GPIO.add_event_detect(self._volumeDownButton,
                              GPIO.RISING, bouncetime=300)

        GPIO.output(self._powerLed, GPIO.HIGH)
        GPIO.output(self._systemLed, GPIO.HIGH)
        GPIO.output(self._statusLed, GPIO.HIGH)

    def cleanup(self):
        GPIO.cleanup()
