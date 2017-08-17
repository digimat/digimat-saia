import time
import socket
import struct

import logging
import logging.handlers

from digimat.jobs import JobManager


from .singleton import Singleton

from .server import SAIAServer
from .server import SAIASBusCRC
from .server import SAIAServers

from .request import SAIARequest

from .response import SAIAResponseReadStationNumber
from .response import SAIAResponseReadProgramVersion
from .response import SAIAResponseReadPcdStatusOwn
from .response import SAIAResponseReadSystemInformation
from .response import SAIAResponseReadInputs
from .response import SAIAResponseReadOutputs
from .response import SAIAResponseReadFlags
from .response import SAIAResponseReadRegisters
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


class SAIANodeRequestHandler(object):
    """
    BaseClass for handling incoming request on local node
    Every subclass will be automatically registered as a command-request handler associated
    with the .COMMAND value. Class name can be anything you want.
    """

    COMMAND = None

    def __init__(self, node):
        self._node=node

    @property
    def node(self):
        return self._node

    @property
    def logger(self):
        return self.node.logger

    @property
    def sequence(self):
        return self._sequence

    def handler(self, data=None):
        self.logger.error('%s:no handler!', self.__class__.__name__)

    def bin2dwordlist(self, data):
        return list(struct.unpack('>%dL' % (len(data) / 4), data))

    def invoke(self, sequence, data):
        self._sequence=sequence

        try:
            self.logger.debug('<--%s(seq=%d)' % (self.__class__.__name__, self.sequence))
            response=self.handler(data)
            if response:
                return response
        except:
            self._node.logger.exception(self.__class__.__name__)

        return self.nak()

    def ack(self):
        return SAIAResponseACK(self.node, self.sequence)

    def nak(self):
        return SAIAResponseNAK(self.node, self.sequence)


class SAIAHandler_READ_STATIONNUMBER(SAIANodeRequestHandler):
    COMMAND = SAIARequest.COMMAND_READ_STATIONNUMBER

    def handler(self, data):
        return SAIAResponseReadStationNumber(self.node, self.sequence)


class SAIAHandler_READ_PROGRAM_VERSION(SAIANodeRequestHandler):
    COMMAND = SAIARequest.COMMAND_READ_PROGRAM_VERSION

    def handler(self, data):
        return SAIAResponseReadProgramVersion(self.node, self.sequence)


class SAIAHandler_READ_SYSTEM_INFO(SAIANodeRequestHandler):
    COMMAND = SAIARequest.COMMAND_READ_SYSTEM_INFO

    def handler(self, data):
        # very minimal implementation since we don't have protocol description yet
        response=SAIAResponseReadSystemInformation(self.node, self.sequence)
        (b0, b1)=struct.unpack('>BB', data)
        response.setup(b0, b1)
        if b1==0:
            return response


class SAIAHandler_READ_PCD_STATUS_OWN(SAIANodeRequestHandler):
    COMMAND = SAIARequest.COMMAND_READ_PCD_STATUS_OWN

    def handler(self, data):
        return SAIAResponseReadPcdStatusOwn(self.node, self.sequence)


class SAIAHandler_READ_INPUTS(SAIANodeRequestHandler):
    COMMAND = SAIARequest.COMMAND_READ_INPUTS

    def handler(self, data):
        (count, index)=struct.unpack('>BH', data)
        response=SAIAResponseReadInputs(self.node, self.sequence)
        response.setup(index, count+1)
        return response


class SAIAHandler_READ_OUTPUTS(SAIANodeRequestHandler):
    COMMAND = SAIARequest.COMMAND_READ_OUTPUTS

    def handler(self, data):
        (count, index)=struct.unpack('>BH', data)
        response=SAIAResponseReadOutputs(self.node, self.sequence)
        response.setup(index, count+1)
        return response


class SAIAHandler_READ_FLAGS(SAIANodeRequestHandler):
    COMMAND = SAIARequest.COMMAND_READ_FLAGS

    def handler(self, data):
        (count, index)=struct.unpack('>BH', data)
        response=SAIAResponseReadFlags(self.node, self.sequence)
        response.setup(index, count+1)
        return response


class SAIAHandler_READ_REGISTERS(SAIANodeRequestHandler):
    COMMAND = SAIARequest.COMMAND_READ_REGISTERS

    def handler(self, data):
        (count, index)=struct.unpack('>BH', data)
        response=SAIAResponseReadRegisters(self.node, self.sequence)
        response.setup(index, count+1)
        return response


class SAIAHandler_WRITE_OUTPUTS(SAIANodeRequestHandler):
    COMMAND = SAIARequest.COMMAND_WRITE_OUTPUTS

    def handler(self, data):
        if not self.node.memory.isReadOnly():
            items=self.node.memory.outputs
            (bytecount, address, fiocount)=struct.unpack('>BHB', data[0:4])
            if address>=0 and fiocount<=32:
                values=bin2boollist(data[4:])
                for n in range(fiocount+1):
                    items[address+n].value=values[n]
                return self.ack()


class SAIAHandler_WRITE_FLAGS(SAIANodeRequestHandler):
    COMMAND = SAIARequest.COMMAND_WRITE_FLAGS

    def handler(self, data):
        if not self.node.memory.isReadOnly():
            items=self.node.memory.flags
            (bytecount, address, fiocount)=struct.unpack('>BHB', data[0:4])
            if address>=0 and fiocount<=32:
                values=bin2boollist(data[4:])
                for n in range(fiocount+1):
                    items[address+n].value=values[n]
                return self.ack()


class SAIAHandler_WRITE_REGISTERS(SAIANodeRequestHandler):
    COMMAND = SAIARequest.COMMAND_WRITE_REGISTERS

    def handler(self, data):
        if not self.node.memory.isReadOnly():
            items=self.node.memory.registers
            (bytecount, address)=struct.unpack('>BH', data[0:3])
            if address>=0:
                values=self.bin2dwordlist(data[3:])
                for n in range(len(values)):
                    items[address+n].value=values[n]
                return self.ack()


class SAIAHandler_CLEAR_OUTPUTS(SAIANodeRequestHandler):
    COMMAND = SAIARequest.COMMAND_CLEAR_OUTPUTS

    def handler(self, data):
        if not self.node.memory.isReadOnly():
            self.node.memory.outputs.clear()
            return self.ack()


class SAIAHandler_CLEAR_FLAGS(SAIANodeRequestHandler):
    COMMAND = SAIARequest.COMMAND_CLEAR_FLAGS

    def handler(self, data):
        if not self.node.memory.isReadOnly():
            self.node.memory.flags.clear()
            return self.ack()


class SAIAHandler_CLEAR_REGISTERS(SAIANodeRequestHandler):
    COMMAND = SAIARequest.COMMAND_CLEAR_REGISTERS

    def handler(self, data):
        if not self.node.memory.isReadOnly():
            self.node.memory.registers.clear()
            return self.ack()


class SAIAHandler_CLEAR_ALL(SAIANodeRequestHandler):
    COMMAND = SAIARequest.COMMAND_CLEAR_ALL

    def handler(self, data):
        if not self.node.memory.isReadOnly():
            self.node.memory.outputs.clear()
            self.node.memory.flags.clear()
            self.node.memory.registers.clear()
            self.node.memory.registers.clear()
            return self.ack()


# class SAIAHandler_RESTART_COLD_ALL(SAIANodeRequestHandler):
    # COMMAND = SAIARequest.COMMAND_RESTART_COLD_ALL

    # def handler(self, data):
        # self.node._jobs.stop()
        # return self.ack()


# class SAIAHandler_RESTART_COLD_FLAG(SAIAHandler_RESTART_COLD_ALL):
    # COMMAND = SAIARequest.COMMAND_RESTART_COLD_FLAG


class SAIANodeHandler(Singleton):
    def __init__(self, node):
        self._node=node
        self._handlers={}
        self.registerAllHandlers()

    @property
    def node(self):
        return self._node

    @property
    def logger(self):
        return self.node.logger

    def registerHandler(self, cls):
        try:
            command=cls.COMMAND
            if command is not None and not self.handler(command):
                self._handlers[command]=cls(self.node)
                self.logger.debug('Registering node command 0x%02X handler %s' % (command, cls.__name__))
        except:
            pass

    def registerAllHandlers(self):
        def get_all_subclasses(cls):
            """ Generator of all class's subclasses. """
            try:
                for subclass in cls.__subclasses__():
                    yield subclass
                    for subclass in get_all_subclasses(subclass):
                        yield subclass
            except TypeError:
                return

        def all_subclasses(classname):
            for cls in get_all_subclasses(object):
                if cls.__name__.split('.')[-1] == classname:
                    break
            else:
                raise ValueError('class %s not found' % classname)
            direct_subclasses = cls.__subclasses__()
            return direct_subclasses + [g for s in direct_subclasses
                for g in all_subclasses(s.__name__)]

        try:
            subcls=all_subclasses('SAIANodeRequestHandler')
            for cls in subcls:
                if cls.COMMAND is not None:
                    self.registerHandler(cls)
        except:
            pass

    def handler(self, command):
        try:
            return self._handlers[command]
        except:
            pass

    def invoke(self, command, sequence, data):
        handler=self.handler(command)
        if handler:
            try:
                return handler.invoke(sequence, data)
            except:
                pass


class SAIANode(object):
    def __init__(self, lid=253, port=SAIAServer.UDP_DEFAULT_PORT, logger=None):
        if logger is None:
            logger=logging.getLogger("SAIANode(%d)" % (port))
            logger.setLevel(logging.DEBUG)
            socketHandler = logging.handlers.SocketHandler('localhost', logging.handlers.DEFAULT_TCP_LOGGING_PORT)
            logger.addHandler(socketHandler)

        self._logger=logger

        self._socket=None
        self._lid=int(lid)
        self._localServer=SAIAServer(self, 'localnode', self._lid, localNodeMode=True)
        self.logger.info('localServer(%d) registered' % self._lid)

        self._servers=SAIAServers(self)

        self._port=int(port)
        self._timeoutSocketInhibit=0

        self._handler=SAIANodeHandler(self)

        self.start()

    @property
    def logger(self):
        return self._logger

    @property
    def server(self):
        return self._localServer

    @property
    def servers(self):
        return self._servers

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

    def __getitem__(self, key):
        return self.servers[key]

    def open(self):
        if self._socket:
            return self._socket

        try:
            if time.time()>=self._timeoutSocketInhibit:
                self._timeoutSocketInhibit=time.time()+3.0
                self.logger.info('Opening communication udp socket on port %d' % self._port)
                s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
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

    def data2strhex(self, data):
        return ' '.join(x.encode('hex') for x in data)

    def sendMessageToHost(self, data, host, port=None):
        try:
            s=self.open()
            if s:
                if port is None:
                    port=self._port
                size=s.sendto(data, (host, port))
                # self.logger.debug('-->%s:%d %s' % (host, port, self.data2strhex(data)))
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
                        return (tattribute, msequence, payload)

            self.logger.error('bad size/crc')
        except:
            self.logger.exception('decodeMessage')

    def onRequest(self, mseq, payload):
        try:
            (lid, cmd)=struct.unpack('> BB', payload[0:2])

            if lid==255 or lid==self._lid:
                data=payload[2:]
                response=self._handler.invoke(cmd, mseq, data)
                if not response:
                    self.logger.error("RequestHandler(seq=%d,  cmd=0x%02X)[%s] not implemented" % (mseq, cmd, self.data2strhex(data)))
                    response=SAIAResponseNAK(self, mseq)

                return response
        except:
            self.logger.exception('onRequest')
            return SAIAResponseNAK(self, mseq)

    def dispatchMessage(self):
        try:
            s=self.open()
            (data, address)=s.recvfrom(2048)
            if data:
                host=address[0]
                port=address[1]
                (mtype, mseq, payload)=self.decodeMessage(data)
                # self.logger.debug('<--%s:%d seq=%d %s' % (host, port, mseq, self.data2strhex(data)))

                if mtype==0:
                    try:
                        response=self.onRequest(mseq, payload)
                        if response:
                            data=response.data
                            if data is not None:
                                self.sendMessageToHost(response.data, host, port)
                            else:
                                response=SAIAResponseNAK(self, mseq)
                                self.sendMessageToHost(response.data, host, port)
                    except:
                        self.logger.exception('request')
                else:
                    server=self.servers.getFromHost(address[0])
                    if server:
                        try:
                            server.onMessage(mtype, mseq, payload)
                        except:
                            self.logger.exception('onMessage()')
                    else:
                        self.logger.warning('undeclared server %s!' % address[0])

                return True
        except:
            pass

    def manager(self):
        activity=False

        count=32
        while count>0:
            count-=1
            if not self.dispatchMessage():
                break
            activity=True

        activity=self.servers.manager()

        # Small booster, allowing to be more reactive
        # during data burst, and more sleepy when idle
        try:
            if activity:
                self._activityCounter=3

            if self._activityCounter>0:
                # bypass default job manager sleep (0.1)
                self.sleep(0.01)
                self._activityCounter-=1
                return True
        except:
            pass

        return False

    def start(self):
        try:
            if self._jobs:
                return
        except:
            pass

        self._jobs=JobManager(self.logger)
        self._jobSAIA=self._jobs.addJobFromFunction(self.manager)
        self._jobs.start()

    def stop(self):
        try:
            self._jobs.stop()
        except:
            pass
        self._jobSAIA=None
        self._jobs=None

    def isRunning(self):
        try:
            return self._jobSAIA.isRunning()
        except:
            pass

    def sleep(self, delay):
        try:
            self._jobSAIA.sleep(delay)
        except:
            self.logger.exception('sleep')
            time.sleep(delay)

    def __del__(self):
        self.stop()

    def dump(self):
        self.server.dump()
        self.servers.dump()


if __name__ == "__main__":
    pass
