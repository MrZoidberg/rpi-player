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
            print "mpd connection error"
            print traceback.print_exc()
            return False

        print self.client.status()
        return True

    def disconnect(self):
        try:
            self.client.disconnect()
        except SocketError:
            print "mpd connection error"
            print traceback.print_exc()

    def getState(self):
        try:
            return self.client.status()["state"]
        except SocketError:
            print "mpd connection error"
            print traceback.print_exc()

    def getStats(self):
        try:
            return self.client.stats()
        except SocketError:
            print "mpd connection error"
            print traceback.print_exc()

    def playPause(self):
        state = self.client.status()["state"]
        if state == "stop" or state == "pause":
            print "play"
            self.client.play()
        else:
            print "pause"
            self.client.pause()

    def increaseVolume(self, delta):
        volume = int(self.client.status()["volume"])
        volume += delta
        print "settings volume to " + str(volume)
        self.client.setvol(str(volume))

    def decreaseVolume(self, delta):
        volume = int(self.client.status()["volume"])
        volume -= delta
        print "settings volume to " + str(volume)
        self.client.setvol(str(volume))

    def nextSong(self):
        print "next song"
        self.client.next()

    def prevSong(self):
        print "prev song"
        self.client.previous()

    def seekCur(self, time):
        print "seek"
        self.client.seekcur(time)
