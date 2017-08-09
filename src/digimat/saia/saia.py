import time
import socket
import struct

import logging
import logging.handlers

from digimat.jobs import JobManager

from .server import SAIAServer
from .server import SAIASBusCRC

from .request import SAIARequest

from .response import SAIAResponseReadStationNumber
from .response import SAIAResponseReadProgramVersion
from .response import SAIAResponseReadPcdStatusOwn
from .response import SAIAResponseReadSystemInformation
from .response import SAIAResponseReadFlags
from .response import SAIAResponseACK
from .response import SAIAResponseNAK

from .ModbusDataLib import bin2boollist


# NOTICE
# ------
#
# This is a *partial* EtherSbus Implementation, allowing us (digimat.ch) to communicate with
# SAIA devices. Still in *alpha* phase (mostly untested yet, under development)
#
# SBus protocol (Serial or UDP) implementation is not public (bad point)
# So, reading Open Source projects is your best way to success
# Some good starting points may include :
#
# -- http://www.sbc-support.ch/faq/ --> EtherSBus
# -- https://github.com/boundary/wireshark/blob/master/epan/dissectors/packet-sbus.c
# -- http://mblogic.sourceforge.net/mbtools/sbpoll.html
#
# Using the SAIA PG5 debugger may also help understanding how things works.
# Wireshark (as mentionned above) has ain excellent protocol decoder and you will find .pcap samples.
#
# Don't forget that the SAIA dynamic addressing *won't* be your friend here ! Consider fixing
# to "static" (instead of default "dynamic" or "automatic") addresses all flags/registers you want to access.
#
# Frederic Hess
# S+T S.A (www.st-sa.ch)
# fhess@st-sa.ch


class SAIANode(object):
    SAIA_UDP_DEFAULT_PORT = 5050

    def __init__(self, lid=253, port=SAIA_UDP_DEFAULT_PORT, logServer='localhost', logLevel=logging.DEBUG):
        logger=logging.getLogger("SAIANode(%d)" % (port))
        logger.setLevel(logLevel)
        socketHandler = logging.handlers.SocketHandler(logServer, logging.handlers.DEFAULT_TCP_LOGGING_PORT)
        logger.addHandler(socketHandler)
        self._logger=logger

        self._socket=None
        self._lid=int(lid)
        self._localServer=SAIAServer(self, '127.0.0.1', self._lid, localNodeMode=True)
        self.logger.info('localServer(%d) registered' % self._lid)

        self._port=int(port)
        self._servers=[]
        self._indexServersByLid={}
        self._indexServersByHost={}
        self._timeoutSocketInhibit=0
        self._currentServer=0

        self.start()

    @property
    def logger(self):
        return self._logger

    @property
    def server(self):
        return self._localServer

    @property
    def memory(self):
        return self.server.memory

    @property
    def inputs(self):
        return self.memory.inputs

    @property
    def flags(self):
        return self.memory.flags

    @property
    def outputs(self):
        return self.memory.outputs

    @property
    def registers(self):
        return self.memory.registers

    def open(self):
        if self._socket:
            return self._socket

        try:
            if time.time()>=self._timeoutSocketInhibit:
                self._timeoutSocketInhibit=time.time()+3.0
                self.logger.info('Opening communication udp socket on port %d' % self._port)
                s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                # s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                # s.settimeout(3.0)
                s.setblocking(False)
                try:
                    s.bind(('', self._port))
                    self._socket=s
                    self.logger.info('UDP socket i/o opened (lid=%d).' % self._lid)
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

    def sendMessageToHost(self, data, host, port=None):
        try:
            s=self.open()
            if s:
                if port is None:
                    port=self._port
                size=s.sendto(data, (host, port))
                print("-->MESSAGE", host, port, size, len(data))
                if size==len(data):
                    return True
                self.logger.error('sendMessageToHost(%s)' % host)
        except:
            self.logger.exception('sendMessageToHost(%s)' % host)

    def decodeMessage(self, data):
        try:
            size=len(data)
            if size>=11 and size<=255:
                sizePayload=size-11
                if sizePayload>0:
                    (msize, mversion, mtype, msequence, tattribute,
                        payload, mcrc)=struct.unpack('>LBBHB %ds H' % sizePayload, data)

                    if mcrc==SAIASBusCRC(data[0:-2]):
                        self.logger.debug('RX msg type %d seq %d payload %d bytes' % (tattribute,
                            msequence, sizePayload))
                        return (tattribute, msequence, payload)

            self.logger.error('bad size/crc')
        except:
            self.logger.exception('decodeMessage')

    def onRequest(self, mseq, payload):
        try:
            (lid, cmd)=struct.unpack('> BB', payload[0:2])
            data=payload[2:]

            if lid==255 or lid==self._lid:
                if cmd==SAIARequest.COMMAND_READ_STATIONNUMBER:
                    return SAIAResponseReadStationNumber(self, mseq)

                elif cmd==SAIARequest.COMMAND_READ_PROGRAM_VERSION:
                    response=SAIAResponseReadProgramVersion(self, mseq)
                    return response

                # very minimal implementation
                elif cmd==SAIARequest.COMMAND_READ_SYSTEM_INFO:
                    response=SAIAResponseReadSystemInformation(self, mseq)
                    (b0, b1)=struct.unpack('>BB', data)
                    response.setup(b0, b1)
                    if b1==0:
                        return response
                    return

                elif cmd==SAIARequest.COMMAND_READ_PCD_STATUS_OWN:
                    return SAIAResponseReadPcdStatusOwn(self, mseq)

                elif cmd==SAIARequest.COMMAND_READ_FLAGS:
                    response=SAIAResponseReadFlags(self, mseq)
                    (count, index)=struct.unpack('>BH', data)
                    response.setup(index, count+1)
                    return response

                elif cmd==SAIARequest.COMMAND_WRITE_FLAGS:
                    flags=self.memory.flags
                    (bytecount, address, fiocount)=struct.unpack('>BHB', data[0:4])
                    if address>=0 and fiocount<=32:
                        values=bin2boollist(data[4:])
                        print values
                        for n in range(fiocount+1):
                            flags[address+n].value=values[n]
                        return SAIAResponseACK(self, mseq)

                print "<--REQUEST(seq=%d, cmd=0x%02x)" % (mseq, cmd), ' '.join(x.encode('hex') for x in data)
                return SAIAResponseNAK(self, mseq)
        except:
            self.logger.exception('onRequest')

    def dispatchMessage(self):
        try:
            s=self.open()
            (data, address)=s.recvfrom(2048)
            if data:
                host=address[0]
                port=address[1]
                (mtype, mseq, payload)=self.decodeMessage(data)

                if mtype==0:
                    try:
                        response=self.onRequest(mseq, payload)
                        if response:
                            self.sendMessageToHost(response.data, host, port)
                    except:
                        self.logger.exception('request')
                else:
                    server=self.getServerFromHost(address[0])
                    if server:
                        try:
                            server.onMessage(mtype, mseq, payload)
                        except:
                            self.logger.exception('onMessage()')
                    else:
                        self.logger.warning('unregistered server %s!' % address[0])

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

    def dump(self):
        return self.server.dump()


if __name__ == "__main__":
    pass
