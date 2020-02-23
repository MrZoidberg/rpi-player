import RPi.GPIO as GPIO


class GPIOHWD(object):

    def __init__(self,):
        print("GPIO version: " + GPIO.VERSION)
        self._statusLed = -1
        self._powerLed = -1
        self._playButton = -1
        self._volumeUpButton = -1
        self._volumeDownButton = -1
        self._nextButton = -1
        self.flashes = dict()

    @property
    def statusLed(self):
        return self._statusLed

    @property
    def powerLed(self):
        return self._powerLed

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

    def setStatusLed(self, _led):
        print("status led is set to ",_led)
        self._statusLed = _led

    def setPowerLed(self, _led):
        print("power led is set to ",_led)
        self._powerLed = _led

    def setPlayButton(self, _button):
        print("play button is set to ",_button)
        self._playButton = _button

    def setVolumeDownButton(self, _button):
        print("volume down button is set to ",_button)
        self._volumeDownButton = _button

    def setVolumeUpButton(self, _button):
        print("volume up button is set to ",_button)
        self._volumeUpButton = _button

    def setNextButton(self, _button):
        print("volume next button is set to ",_button)
        self._nextButton = _button

    def flashLed(self, led, speed, time):
        self.stopFlash(led)
        print("flashing led " + str(led) + " at freq " + str(speed) +
              " with duty " + str(time))
        pwm = GPIO.PWM(led, speed)
        pwm.start(time)
        self.flashes[led] = pwm

    def stopFlash(self, led):
        if led in self.flashes:
            print("stop flashing led " + str(led))
            pwm = self.flashes.pop(led, None)
            pwm.stop()

    def updateLed(self, led, turnOn):
        # self.stopFlash(led)
        if turnOn is True:
            GPIO.output(led, GPIO.LOW)
        else:
            GPIO.output(led, GPIO.HIGH)

    def isButtonPressed(self, led):
        return GPIO.event_detected(led)

    def getInput(self, led):
        return GPIO.input(led)

    def setup(self):
        GPIO.setmode(GPIO.BOARD)
        leds = [self._powerLed, self._statusLed]
        buttons = [self._playButton, self._volumeUpButton,
                   self._volumeDownButton, self._nextButton]

        GPIO.setup(leds, GPIO.OUT)
        GPIO.setup(buttons, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(self._nextButton, GPIO.RISING)
        GPIO.add_event_detect(self._volumeUpButton, GPIO.FALLING)
        GPIO.add_event_detect(self._volumeDownButton, GPIO.FALLING)

        GPIO.output(self._powerLed, GPIO.HIGH)
        GPIO.output(self._statusLed, GPIO.LOW)

    def cleanup(self):
        GPIO.cleanup()
