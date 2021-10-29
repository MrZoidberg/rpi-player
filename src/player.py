from mpd import (MPDClient, CommandError)
from socket import error as SocketError
import traceback


class Player(object):

    def __init__(self,):
        self.setPort('6600')
        self.setHost('localhost')
        self.client = MPDClient()

    def setPort(self, _port):
        self.port = _port

    def setHost(self, _host):
        self.host = _host

    def connectMPD(self):
        try:
            con_id = {'host': self.host, 'port': self.port}
            self.client.connect(**con_id)
        except SocketError:
            print("mpd connection error")
            print(traceback.print_exc())
            return False

        print(self.client.status())
        return True

    def disconnect(self):
        try:
            self.client.disconnect()
        except SocketError:
            print("mpd connection error")
            print(traceback.print_exc())

    def getState(self) -> str:
        try:
            return self.client.status()["state"]
        except CommandError:
            print("mpc command error")
            print(traceback.print_exc())
        except SocketError:
            print("mpd connection error")
            print(traceback.print_exc())

    def getStatus(self) -> dict:
        try:
            return self.client.status()
        except CommandError:
            print("mpc command error")
            print(traceback.print_exc())
        except SocketError:
            print("mpd connection error")
            print(traceback.print_exc())

    def getStats(self):
        try:
            return self.client.stats()
        except CommandError:
            print("mpc command error")
            print(traceback.print_exc())
        except SocketError:
            print("mpd connection error")
            print(traceback.print_exc())

    def play(self):
        try:
            state = self.client.status()["state"]
            if state == "stop" or state == "pause":
                print("play")
                self.client.play()
        except CommandError:
            print("mpc command error")
            print(traceback.print_exc())
        except SocketError:
            print("mpd connection error")
            print(traceback.print_exc())

    def playPause(self):
        try:
            state = self.client.status()["state"]
            if state == "stop" or state == "pause":
                print("play")
                self.client.play()
            else:
                print("pause")
                self.client.pause()
        except CommandError:
            print("mpc command error")
            print(traceback.print_exc())
        except SocketError:
            print("mpd connection error")
            print(traceback.print_exc())

    def increaseVolume(self, delta):
        volume = int(self.client.status()["volume"])
        volume += delta
        volume = min(100, volume)
        print("increasing volume to " + str(volume))
        self.client.setvol(str(volume))

    def decreaseVolume(self, delta):
        volume = int(self.client.status()["volume"])
        volume -= delta
        volume = max(0, volume)
        print("decreasing volume to " + str(volume))
        self.client.setvol(str(volume))

    def nextSong(self):
        print("next song")
        try:
            self.client.next()
        except CommandError:
            print("mpc command error")
            print(traceback.print_exc())
        except SocketError:
            print("mpd connection error")
            print(traceback.print_exc())

    def prevSong(self):
        print("prev song")
        try:
            self.client.previous()
        except CommandError:
            print("mpc command error")
            print(traceback.print_exc())
        except SocketError:
            print("mpd connection error")
            print(traceback.print_exc())

    def seekCur(self, time):
        print("seek")
        curSongPos = float(self.getStatus()["elapsed"])
        print(curSongPos)
        curSongPos += time
        try:
            self.client.seekcur(curSongPos)
        except CommandError:
            print("mpc command error")
            print(traceback.print_exc())
        except SocketError:
            print("mpd connection error")
            print(traceback.print_exc())

    def currentSongInfo(self) -> dict:
        try:
            return self.client.currentsong()
        except CommandError:
            print("mpc command error")
            print(traceback.print_exc())
        except SocketError:
            print("mpd connection error")
            print(traceback.print_exc())

    # def seekCur(self, delta):
        # print("seek current. delta: " + delta)
        # self.client.seekcur(delta)
        # os.system("mpc seekthrough " + delta)
        # time.sleep(2)
