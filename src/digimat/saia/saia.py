import time
import socket

from threading import RLock
from threading import Event
from Queue import Queue
# from threading import Thread

import logging
import logging.handlers

from SBusMsg import SBusClientMessages
# from SBusMsg import SBusServerMessages

from ModbusDataLib import bin2boollist

from digimat.jobs import JobManager

# SBus hints
# https://github.com/boundary/wireshark/blob/master/epan/dissectors/packet-sbus.c


# http://stackoverflow.com/questions/1581895/how-check-if-a-task-is-already-in-python-queue
class UniqueQueue(Queue):
    def put(self, item, block=True, timeout=None):
        if item not in self.queue:  # fix join bug
            Queue.put(self, item, block, timeout)

    def _init(self, maxsize):
        self.queue = set()

    def _put(self, item):
        self.queue.add(item)

    def _get(self):
        return self.queue.pop()


class SAIAItem(object):
    def __init__(self, parent, index, value=None, delayRefresh=None):
        self._parent=parent
        self._index=index
        self._value=self.validateValue(value)
        self._stamp=0
        self._readOnly=False
        self._delayRefresh=delayRefresh
        self.onInit()
        self._eventPush=Event()
        self._eventPull=Event()

    @property
    def parent(self):
        return self._parent

    @property
    def logger(self):
        return self.parent.logger

    @property
    def server(self):
        return self.parent.server

    @property
    def index(self):
        return self._index

    def onInit(self):
        pass

    def setRefreshDelay(self, delay):
        self._delayRefresh=delay

    def getRefreshDelay(self):
        try:
            if self._delayRefresh is not None:
                return self._delayRefresh
            return self.parent.getRefreshDelay()
        except:
            return 60

    def validateValue(self, value):
        return value

    def setReadOnly(self, state=True):
        self._readOnly=True

    def signalPush(self):
        if not self._eventPush.isSet():
            self._eventPush.set()
            self._parent.signalPush(self)

    def clearPush(self):
        self._eventPush.clear()

    def signalPull(self):
        if not self._eventPull.isSet():
            self._eventPull.set()
            self._parent.signalPull(self)

    def clearPull(self):
        self._eventPull.clear()

    def setValue(self, value, signalPush=True):
        if not self._readOnly:
            value=self.validateValue(value)
            with self._parent._lock:
                self._stamp=time.time()
                if value != self._value:
                    self._value=value
                    if signalPush:
                        self.signalPush()

    def getValue(self):
        return self._value

    @property
    def value(self):
        with self._parent._lock:
            return self.getValue()

    @value.setter
    def value(self, value):
        with self._parent._lock:
            self.setValue(value)

    def age(self):
        with self._parent._lock:
            return time.time()-self._stamp

    def pull(self):
        return False

    def push(self):
        return False

    def manager(self):
        if self.age()>self.getRefrehDelay():
            self.signalPull()


class SAIAItemFlag(SAIAItem):
    def validateValue(self, value):
        try:
            return bool(value)
        except:
            return False

    def onInit(self):
        self.logger.debug('creating item %d->flag[%d]' % (self.server.lid, self.index))

    def on(self):
        self.value=True

    def off(self):
        self.value=False

    def toggle(self):
        self.value=not self.value

    def pull(self):
        return self.server.link.readFlags(self.index, 1)

    def push(self):
        print "TODO: flag->push"
        return False


class SAIAItems(object):
    def __init__(self, memory, itemType, maxsize):
        self._memory=memory
        self._lock=RLock()
        self._itemType=itemType
        self._maxsize=maxsize
        self._items=[]
        self._indexItem={}
        self._currentItem=0
        self._delayRefresh=60

    @property
    def memory(self):
        return self._memory

    @property
    def server(self):
        return self.memory.server

    @property
    def logger(self):
        return self.memory.logger

    def setRefreshDelay(self, delay):
        self._delayRefresh=delay

    def getRefreshDelay(self):
        return self._delayRefresh

    def validateIndex(self, index):
        try:
            n=int(index)
            if n>=0 and n<self._maxsize:
                return n
        except:
            pass

    def item(self, index):
        try:
            with self._lock:
                return self._items[self.validateIndex(index)]
        except:
            pass

    def __getitem__(self, index):
        item=self.item(index)
        if item:
            return item
        return self.declare(index)

    def declare(self, index, value=None):
        if self.validateIndex(index):
            item=self.item(index)
            if item:
                return item

            item=self._itemType(self, index, value)
            with self._lock:
                self._items.append(item)
                self._indexItem[index]=item
                item.signalPull()
                return item

    def declareRange(self, index, count, value=None):
        while count>0:
            self.declare(index, value)
            index+=1

    def signalPush(self, item=None):
        if item is None:
            for item in self._items:
                self.memory._queuePendingPush.put(item)
        else:
            self.memory._queuePendingPush.put(item)

    def signalPull(self, item=None):
        if item is None:
            for item in self._items:
                self.memory._queuePendingPull.put(item)
        else:
            self.memory._queuePendingPull.put(item)

    def refresh(self):
        self.signalPull()

    def manager(self):
        try:
            self._items[self._currentItem].manager()
            self._currentItem+=1
        except:
            self._currentItem=0


class SAIAFlags(SAIAItems):
    def __init__(self, memory, maxsize=65535):
        super(SAIAFlags, self).__init__(memory, SAIAItemFlag, maxsize)


class SAIAMemory(object):
    def __init__(self, server):
        self._server=server
        self._inputs=None
        self._outputs=None
        self._flags=SAIAFlags(self)
        self._registers=None
        self._queuePendingPull=UniqueQueue()
        self._queuePendingPush=UniqueQueue()

    @property
    def server(self):
        return self._server

    @property
    def logger(self):
        return self.server.logger

    @property
    def inputs(self):
        return self._inputs

    @property
    def outputs(self):
        return self._outputs

    @property
    def flags(self):
        return self._flags

    @property
    def registers(self):
        return self._registers

    def items(self):
        return (self._inputs, self._outputs, self._flags, self._registers)

    def refresh(self):
        for items in self.items():
            try:
                items.refresh()
            except:
                pass

    def getNextPendingPush(self):
        try:
            item=self._queuePendingPush.get(False)
            item.clearPush()
            return item
        except:
            pass

    def getNextPendingPull(self):
        try:
            item=self._queuePendingPull.get(False)
            item.clearPull()
            return item
        except:
            pass

    def manager(self):
        try:
            for items in self.items():
                items.manager()
        except:
            pass

        if self.server.link.isIdle():
            item=self.getNextPendingPush()
            if item:
                item.push()

            item=self.getNextPendingPull()
            if item:
                item.pull()


class SAIARequest(object):

    SAIA_COMMAND_READ_FLAGS = 2
    SAIA_COMMAND_READ_INPUTS = 3
    SAIA_COMMAND_READ_OUTPUTS = 5
    SAIA_COMMAND_READ_REGISTERS = 6
    SAIA_COMMAND_WRITE_FLAGS = 11
    SAIA_COMMAND_WRITE_OUTPUTS = 12
    SAIA_COMMAND_WRITE_REGISTERS = 14

    def __init__(self, link):
        self._link=link
        self._msgseq=0
        self._msgfactory=SBusClientMessages()
        self._command=None
        self._address=None
        self._count=0
        self._data=None

    @property
    def link(self):
        return self._link

    @property
    def logger(self):
        return self.link.logger

    @property
    def data(self):
        return self._data

    def reset(self):
        self._command=None
        self._address=None
        self._count=0
        self._data=None
        self._stamp=time.time()
        self._retry=0

    def generateMsgSeq(self):
        self._msgseq+=1
        if self._msgseq>65535:
            self._msgseq=1
        return self._msgseq

    def age(self):
        return time.time()-self._stamp

    def consumeRetry(self):
        if self._retry>0:
            self._retry-=1
            return True

    def build(self, command, address, count=1, payload=None):
        try:
            data=self._msgfactory.SBRequest(self.generateMsgSeq(),
                self.link.server.lid,
                command, count, address,
                payload)

            self.reset()

            self._command=command
            self._dataAddr=address
            self._dataCount=count
            self._data=data
            self._retry=3

            return data
        except:
            self.logger.exception('request:build')

    def processRemoteRequest(self, payload):
        self.logger.error('received RemoteRequest -- not implemented yet!')

    def processReadFlagsResponse(self, payload):
        flags=self.link.server.memory.flags

        index=self._dataAddr
        count=self._dataCount
        values=bin2boollist(payload)
        print index, count, values

        for n in range(count):
            print "FLAG(%d)=%d" % (index+n, values[n])
            flags[index+n].setValue(values[n], False)

    def processReadInputsResponse(self, payload):
        self.logger.error('TODO')

    def processReadOutputsResponse(self, payload):
        self.logger.error('TODO')

    def processReadRegistersResponse(self, payload):
        self.logger.error('TODO')

    def processRequestResponse(self, payload):
        if self._command==SAIARequest.SAIA_COMMAND_READ_FLAGS:
            return self.processReadFlagsResponse(payload)
        if self._command==SAIARequest.SAIA_COMMAND_READ_INPUTS:
            return self.processReadInputsResponse(payload)
        if self._command==SAIARequest.SAIA_COMMAND_READ_OUTPUTS:
            return self.processReadOuputsResponse(payload)
        if self._command==SAIARequest.SAIA_COMMAND_READ_REGISTERS:
            return self.processReadRegistersResponse(payload)

        self.logger.error('processRequestResponse(%s) un implemented!' % self._command)

    def abortRequest(self):
        self.logger.error('request:abort')
        print "TODO: restart communication"
        pass

    def processRequestAck(self, result):
        pass

    def processMessage(self, data):
        try:
            (mtype, mseq, payload)=self._msgfactory.SBResponse(data)
            print "MESSAGE", mtype, mseq, len(payload)

            if mtype==0:    # Request
                self.processRemoteRequest(payload)

            elif mtype==1:  # Response
                if mseq==self._msgseq and self.link.isWaitingResponse():
                    self.processRequestReponse(payload)

            elif mtype==2:  # Ack/Nak
                if mseq==self._msgseq and self.link.isWaitingResponse():
                    result=bool(payload[0])
                    self.processRequestAck(result)

        except:
            self.logger.exception('processResponse')


class SAIALink(object):

    SAIA_COMMSTATE_IDLE = 0
    SAIA_COMMSTATE_PENDINGREQUEST = 1
    SAIA_COMMSTATE_WAITRESPONSE = 2
    SAIA_COMMSTATE_ERROR = 10

    def __init__(self, server, delayXmitInhibit=0.2):
        self._server=server
        self._request=SAIARequest(self)
        self._state=None
        self._timeout=0
        self._timeoutXmitInhibit=0
        self._delayXmitInhibit=delayXmitInhibit
        self._retry=0
        self.reset()

    @property
    def server(self):
        return self._server

    @property
    def logger(self):
        return self.server.logger

    def setState(self, state, timeout=0):
        self._state=state
        self._timeout=time.time()+timeout

    def setXmitInhibitDelay(self, delay):
        self._delayXmitInhibit=delay

    def reset(self):
        self.setState(SAIALink.SAIA_COMMSTATE_IDLE)

    def isIdle(self):
        if self._state==SAIALink.SAIA_COMMSTATE_IDLE:
            return True

    def isWaitingResponse(self):
        if self._state==SAIALink.SAIA_COMMSTATE_WAITRESPONSE:
            return True

    def isTimeout(self):
        if time.time()>=self._timeout:
            return True

    def age(self):
        return time.time()-self._timeout

    def isElapsed(self, age):
        return self.age()>=age

    def manager(self):
        try:
            if self._state==SAIALink.SAIA_COMMSTATE_IDLE:
                return

            elif self._state==SAIALink.SAIA_COMMSTATE_PENDINGREQUEST:
                if time.time()<self._timeoutXmitInhibit:
                    return

                if self._delayXmitInhibit>0:
                    self._timeoutXmitInhibit=time.time()+self._delayXmitInhibit

                if self._request.consumeRetry():
                    if self.server.client.sendMessageToHost(self._request.data, self.server.host):
                        self.setState(SAIALink.SAIA_COMMSTATE_WAITRESPONSE, 3.0)
                        return

                print "*****LINK-RESET"
                self._request.abortRequest()
                self.reset()
                return

            elif self._state==SAIALink.SAIA_COMMSTATE_WAITRESPONSE:
                if self.isTimeout():
                    self.logger.error('response timeout!')
                    self.setState(SAIALink.SAIA_COMMSTATE_PENDINGREQUEST)
                return

            elif self._state==SAIALink.SAIA_COMMSTATE_ERROR:
                if self.isElapsed(3.0):
                    self.logger.error('link:error')
                    self.reset()
                return

            else:
                self.logger.error('link:unkown state %d' % self._state)
                self.setState(SAIALink.SAIA_COMMSTATE_ERROR)
                return

        except:
            self.logger.exception('link.manager')
            self.setState(SAIALink.SAIA_COMMSTATE_ERROR)

    def initiateRequest(self, command, address, count, payload=None):
        if self.isIdle() and self._request.build(command, address, count, payload):
            self.setState(SAIALink.SAIA_COMMSTATE_PENDINGREQUEST)
            return True

    def readFlags(self, index, count=1):
        return self.initiateRequest(SAIARequest.SAIA_COMMAND_READ_FLAGS, index, count)

    def readInputs(self, index, count=1):
        return self.initiateRequest(SAIARequest.SAIA_COMMAND_READ_INPUTS, index, count)

    def readOutputs(self, index, count=1):
        return self.initiateRequest(SAIARequest.SAIA_COMMAND_READ_OUTPUTS, index, count)

    def readRegisters(self, index, count=1):
        return self.initiateRequest(SAIARequest.SAIA_COMMAND_READ_REGISTERS, index, count)

    def onMessage(self, data):
        self._request.processMessage(data)


class SAIAServer(object):
    def __init__(self, client, lid, host):
        self._client=client
        self._lid=lid
        self._host=host
        self._memory=SAIAMemory(self)
        self._link=SAIALink(self)

    @property
    def lid(self):
        return self._lid

    @property
    def host(self):
        return self._host

    @property
    def client(self):
        return self._client

    @property
    def logger(self):
        return self.client.logger

    @property
    def memory(self):
        return self._memory

    @property
    def link(self):
        return self._link

    def onMessage(self, data):
        return self.link.onMessage(data)

    def manager(self):
        self._link.manager()
        self._memory.manager()


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
                s.settimeout(5.0)
                s.setblocking(False)
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
            return self._indexServersByLid[lid]
        except:
            pass

    def __getitem__(self, key):
        return self.getServerFromLid(key)

    def registerServer(self, lid, host, port=SAIA_UDP_DEFAULT_PORT):
        server=self.getServerFromLid(lid)
        if server is None:
            server=SAIAServer(self, lid, host)
            self._servers.append(server)
            self._indexServersByLid[lid]=server
            self._indexServersByHost[host]=server
            self.logger.info('server(%d, %s:%d) registered' % (lid, host, port))
        return server

    def sendMessageToHost(self, data, host):
        try:
            s=self.open()
            if s:
                size=s.sendto(data, (host, self._port))
                print host, size
                if size==len(data):
                    return True
                print "******NOSEND!"
        except:
            self.logger.exception('sendMessageToHost(%s)' % host)

    def dispatchMessage(self):
        try:
            s=self.open()
            (data, address)=s.recv(4096)
            if data:
                server=self.getServer(address[0])
                if server:
                    try:
                        server.onMessage(data)
                        return True
                    except:
                        self.logger.exception('onMessage()')
                else:
                    self.logger.warning('unregistered server!')
        except:
            pass

    def manager(self):
        count=32
        while count>0:
            if not self.dispatchMessage():
                break
            count-=1

        if self._servers:
            for server in self._servers:
                try:
                    server.manager()
                except:
                    self.logger.exception('manager()')

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

    #######################################################
    # def GetFlagsBool(self, addr):
        # """Read flags from the host (command 2).
        # addr (integer) = SBus flags address.
        # """
        # return ModbusDataLib.bin2boollist(self._SBusRequest(2, addr, 1, None))[0]

    #######################################################
    # def GetInputsBool(self, addr):
        # """Read inputs from the host (command 3).
        # addr (integer) = SBus inputs address.
        # """
        # return ModbusDataLib.bin2boollist(self._SBusRequest(3, addr, 1, None))[0]

    #######################################################
    # def GetOutputsBool(self, addr):
        # """Read outputs from the host (command 5).
        # addr (integer) = SBus outputs address.
        # """
        # return ModbusDataLib.bin2boollist(self._SBusRequest(5, addr, 1, None))[0]

    #######################################################
    # def GetRegistersInt(self, addr):
        # """Read registers from the host (command 6).
        # addr (integer) = SBus registers address.
        # """
        # return SBusMsg.signedbin2int32list(self._SBusRequest(6, addr, 1, None))[0]

    #######################################################
    # def GetRegistersIntList(self, addr, qty):
        # """Read registers from the host (command 6).
        # addr (integer) = SBus registers address.
        # qty (integer) = Number of registers.
        # """
        # return SBusMsg.signedbin2int32list(self._SBusRequest(6, addr, qty, None))

    #######################################################
    # def SetFlagsBool(self, addr, data):
        # """Write flags to the host (command 11).
        # addr (integer) = SBus flags address.
        # data (string) = Packed binary string with the data to write.
        # """
        # bindata = ModbusDataLib.boollist2bin([data])
        # self._SBusRequest(11, addr, 1, bindata)

    #######################################################
    # def SetOutputsBool(self, addr, data):
        # """Write outputs to the host (command 13).
        # addr (integer) = SBus outputs address.
        # data (string) = Packed binary string with the data to write.
        # """
        # bindata = ModbusDataLib.boollist2bin([data])
        # self._SBusRequest(13, addr, 1, bindata)

    #######################################################
    # def SetRegistersInt(self, addr, data):
        # """Write registers to the host (command 14).
        # addr (integer) = Modbus discrete inputs address.
        # data (string) = Packed binary string with the data to write.
        # """
        # bindata = SBusMsg.signedint32list2bin([data])
        # self._SBusRequest(14, addr, 1, bindata)

    #######################################################
    # def SetRegistersIntList(self, addr, qty, data):
        # """Write registers to the host (command 14).
        # addr (integer) = Modbus discrete inputs address.
        # qty (integer) = Number of registers.
        # data (string) = Packed binary string with the data to write.
        # """
        # bindata = SBusMsg.signedint32list2bin(data)
        # self._SBusRequest(14, addr, qty, bindata)


if __name__ == "__main__":
    pass
