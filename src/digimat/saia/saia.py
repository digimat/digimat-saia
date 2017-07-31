import time
import socket

import logging
import logging.handlers

from digimat.jobs import JobManager

from server import SAIAServer

# NOTICE
# ------
#
# This is a *partial* EtherSbus Implementation, allowing us (digimat.ch) to communicate with
# SAIA devices. Still in *alpha* phase
#
# SBus protocol (Serial or UDP) implementation is not public (bad point)
# So, reading Open Source projects is your best way to success
# Some good starting points may be :
#
# -- https://github.com/boundary/wireshark/blob/master/epan/dissectors/packet-sbus.c
# -- http://mblogic.sourceforge.net/mbtools/sbpoll.html
#
# Using the SAIA PG5 debugger may also help understanding how things works.
# Wireshark (as mentionned above) has ain excellent protocol decoder and you will find .pcap samples.
#
# Don't forget that the SAIA dynamic addressing *won't* be your friend here ! Think to fix
# to static addresses all flags/registers you want to access.
#
# Frederic Hess
# S+T S.A (www.st-sa.ch)
# fhess@st-sa.ch


class SAIAClient(object):
    SAIA_UDP_DEFAULT_PORT = 5050

    def __init__(self, port=SAIA_UDP_DEFAULT_PORT, logServer='localhost', logLevel=logging.DEBUG):
        logger=logging.getLogger("SAIAClient(%d)" % (port))
        logger.setLevel(logLevel)
        socketHandler = logging.handlers.SocketHandler(logServer, logging.handlers.DEFAULT_TCP_LOGGING_PORT)
        logger.addHandler(socketHandler)
        self._logger=logger

        self._socket=None
        self._port=port
        self._servers=[]
        self._indexServersByLid={}
        self._indexServersByHost={}
        self._timeoutSocketInhibit=0
        self._currentServer=0

    @property
    def logger(self):
        return self._logger

    def open(self):
        if self._socket:
            return self._socket

        try:
            if time.time()>=self._timeoutSocketInhibit:
                self._timeoutSocketInhibit=time.time()+3.0
                self.logger.info('Opening client socket on port %d' % self._port)
                s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                s.setblocking(False)
                s.settimeout(5.0)
                try:
                    s.bind(('', self._port))
                    self._socket=s
                    return self._socket
                except:
                    self.logger.exception('bind()')
                    s.close()
        except:
            self.logger.exception('open()')

    def close(self):
        try:
            if self._socket:
                self.logger.info('socket:close()')
                self._socket.close()
        except:
            pass

        self._socket=None

    def getServerFromHost(self, host):
        try:
            return self._indexServersByHost[host]
        except:
            pass

    def getServerFromLid(self, lid):
        try:
            return self._indexServersByLid[int(lid)]
        except:
            pass

    def getServer(self, key):
        server=self.getServerFromHost(key)
        if server is None:
            server=self.getServerFromLid(key)
        return server

    def __getitem__(self, key):
        return self.getServer(key)

    def registerServer(self, host, lid=None, port=SAIA_UDP_DEFAULT_PORT):
        server=self.getServerFromHost(host)
        if server is None:
            server=SAIAServer(self, host, lid)
            self._servers.append(server)
            self._indexServersByHost[host]=server
            self.logger.info('server(%s:%d) registered' % (host, port))
        return server

    def declareServerLid(self, server, lid):
        if self.getServerFromLid():
            self.logger.error('duplicate server lid %d' % lid)
            return

        try:
            del self._indexServersByLid[server.lid]
        except:
            pass

        try:
            if lid>=0 and lid<255:
                self._indexServersByLid[lid]=server
                self.logger.info('assign server %s with lid %d' % (server.host, lid))
                return True
        except:
            pass

    def sendMessageToHost(self, data, host):
        try:
            s=self.open()
            if s:
                size=s.sendto(data, (host, self._port))
                print "-->MESSAGE", host, size
                if size==len(data):
                    return True
                print "******NOSEND!"
        except:
            self.logger.exception('sendMessageToHost(%s)' % host)

    def dispatchMessage(self):
        try:
            s=self.open()
            (data, address)=s.recv(2048)
            if data:
                server=self.getServerFromHost(address[0])
                if server:
                    try:
                        server.onMessage(data)
                    except:
                        self.logger.exception('onMessage()')
                else:
                    self.logger.warning('unregistered server!')

                return True
        except:
            pass

    def manager(self):
        count=32
        while count>0:
            count-=1
            if not self.dispatchMessage():
                break

        if self._servers:
            count=min(8, len(self._servers))
            while count>0:
                count-=1
                try:
                    server=self._servers[self._currentServer]
                    self._currentServer+=1

                    try:
                        server.manager()
                    except:
                        self.logger.exception('manager')
                except:
                    self._currentServer=0
                    break

    def start(self):
        try:
            if self._jobManager:
                return
        except:
            pass

        self._jobManager=JobManager(self.logger)
        self._jobManager.addJobFromFunction(self.manager)
        self._jobManager.start()

    def stop(self):
        try:
            self._jobManager.stop()
        except:
            pass
        self._jobManager=None


if __name__ == "__main__":
    pass
