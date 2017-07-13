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
        self._pushValue=None
        self._stamp=0
        self._readOnly=False
        self._delayRefresh=delayRefresh
        self.onInit()
        self._eventPush=Event()
        self._eventPull=Event()
        self.logger.debug('creating %s' % (self))

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

    def signalPush(self, value):
        if not self._eventPush.isSet():
            self._eventPush.set()
            self._parent.signalPush(self)
        with self._parent._lock:
            self._pushValue=value

    def clearPush(self):
        self._eventPush.clear()

    def signalPull(self):
        if not self._eventPull.isSet():
            self._eventPull.set()
            self._parent.signalPull(self)

    def clearPull(self):
        self._eventPull.clear()

    def setValue(self, value):
        if not self._readOnly:
            value=self.validateValue(value)
            with self._parent._lock:
                self._stamp=time.time()
                self._value=value

    def getValue(self):
        return self._value

    @property
    def value(self):
        with self._parent._lock:
            return self.getValue()

    @value.setter
    def value(self, value):
        with self._parent._lock:
            if not self._readOnly:
                if self._value!=value:
                    self.signalPush(value)

    @property
    def pushValue(self):
        with self._parent._lock:
            return self._pushValue

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

    def strValue(self):
        return str(self.value)

    def __repr__(self):
        return '%s.%s[%d](value=%s, age=%ds)' % (self.server,
            self.__class__.__name__,
            self.index, self.strValue(), self.age())


class SAIABooleanItem(SAIAItem):
    def validateValue(self, value):
        try:
            return bool(value)
        except:
            return False

    def on(self):
        self.value=True

    def off(self):
        self.value=False

    def toggle(self):
        self.value=not self.value

    def strValue(self):
        if self.value:
            return 'ON'
        return 'OFF'


class SAIAItemFlag(SAIABooleanItem):
    def onInit(self):
        pass

    def pull(self):
        return self.server.link.readFlags(self.index, 1)

    def push(self):
        return self.server.link.writeFlags(self.index, self.value)


class SAIAItemInput(SAIABooleanItem):
    def onInit(self):
        self.logger.debug('creating item %d->input[%d]' % (self.server.lid, self.index))

    def pull(self):
        return self.server.link.readInputs(self.index, 1)

    def push(self):
        print "TODO: input->push"


class SAIAItemOutput(SAIABooleanItem):
    def onInit(self):
        self.logger.debug('creating item %d->output[%d]' % (self.server.lid, self.index))

    def pull(self):
        return self.server.link.readOutputs(self.index, 1)

    def push(self):
        print "TODO: output->push"


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
        count=min(8, len(self._tems))
        while count>0:
            count-=1
            try:
                item=self._items[self._currentItem]
                self._currentItem+=1

                try:
                    item.manager()
                except:
                    self.logger.exception('manager()')
            except:
                self._currentItem=0
                break

    def dump(self):
        for item in self._items:
            print(item)


class SAIAFlags(SAIAItems):
    def __init__(self, memory, maxsize=65535):
        super(SAIAFlags, self).__init__(memory, SAIAItemFlag, maxsize)


class SAIAInputs(SAIAItems):
    def __init__(self, memory, maxsize=65535):
        super(SAIAInputs, self).__init__(memory, SAIAItemInput, maxsize)


class SAIAOutputs(SAIAItems):
    def __init__(self, memory, maxsize=65535):
        super(SAIAOutputs, self).__init__(memory, SAIAItemOutput, maxsize)


class SAIAMemory(object):
    def __init__(self, server):
        self._server=server
        self._inputs=SAIAInputs(self)
        self._outputs=SAIAOutputs(self)
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

    def dump(self):
        for items in self.items():
            if items:
                items.dump()


class SAIARequest(object):

    COMMAND_READ_FLAGS = 2
    COMMAND_READ_INPUTS = 3
    COMMAND_READ_OUTPUTS = 5
    COMMAND_READ_REGISTERS = 6
    COMMAND_WRITE_FLAGS = 11
    COMMAND_WRITE_OUTPUTS = 12
    COMMAND_WRITE_REGISTERS = 14
    COMMAND_READ_STATIONNUMBER = 0x1d

    def __init__(self, link, retry=3):
        self._link=link
        self._retry=retry
        self._data=None
        self._command=0
        self._stamp=0
        self.onInit()
        self._valid=False
        self._sequence=0

    def onInit(self):
        pass

    def setup(self):
        self.validate()

    @property
    def link(self):
        return self._link

    @property
    def server(self):
        return self.link.server

    @property
    def memory(self):
        return self.server.memory

    @property
    def logger(self):
        return self.link.logger

    # to be overridden
    def encode(self):
        raise NotImplementedError

    def validate(self):
        self._valid=True

    def build(self):
        try:
            self._sequence=self.link.generateMsgSeq()
            self._data=self.encode()
            self._stamp=time.time()
        except:
            self.logger.exception('request:build()')
        return self._data

    @property
    def data(self):
        if self._data:
            return self._data
        return self.build()

    def age(self):
        return time.time()-self._stamp

    def consumeRetry(self):
        if self._retry>0:
            self._retry-=1
            self._stamp=time.time()
            return True

    def isValid(self):
        if self._valid:
            return True

    def validateMessage(self, sequence, payload=None):
        if self.isValid:
            if sequence==self._sequence:
                return True

    def processResponse(self, payload):
        return False

    def onSuccess(self):
        pass

    def onFailure(self):
        pass


class SAIARequestReadFlags(SAIARequest):
    def onInit(self):
        self._command=SAIARequest.COMMAND_READ_FLAGS

    @property
    def flags(self):
        return self.memory.flags

    def setup(self, address, count=1):
        self._address=address
        self._count=count
        self.validate()

    def encode(self):
        if self.isValid():
            factory=SBusClientMessages()
            data=factory.SBRequest(self._sequence,
                self.link.server.lid,
                self._command,
                self._count,
                self._address)

        return data

    def processResponse(self, payload):
        flags=self.flags

        index=self._address
        count=self._count
        values=bin2boollist(payload)
        print index, count, values

        for n in range(count):
            print "FLAG(%d)=%d" % (index+n, values[n])
            flags[index+n].setValue(values[n], False)

    def onFailure(self):
        # read will be automatically refreshed by pooling
        # no need to re-pull
        pass


class SAIARequestWriteFlags(SAIARequest):
    def onInit(self):
        self._command=SAIARequest.COMMAND_WRITE_FLAGS

    @property
    def flags(self):
        return self.memory.flags

    # def setup(self, address, values):
        # self._address=address
        # try:
        # self.validate()

    # def encode(self):
        # if self.isValid():
            # factory=SBusClientMessages()
            # data=factory.SBRequest(self._sequence,
                # self.link.server.lid,
                # self._command,
                # self._count,
                # self._address)

        # return data

    # def onSuccess(self):
        # flags=self.flags

        # index=self._address
        # count=self._count

        # for n in range(count):
            # print "READAFTERWRITEFLAG(%d)" % (index+n)
            # flags[index+n].refresh()

    def onFailure(self):
        # read will be automatically refreshed by pooling
        # no need to re-pull
        pass


class SAIALink(object):

    COMMSTATE_IDLE = 0
    COMMSTATE_PENDINGREQUEST = 1
    COMMSTATE_WAITRESPONSE = 2
    COMMSTATE_ERROR = 10
    COMMSTATE_SUCCESS = 11

    def __init__(self, server, delayXmitInhibit=0.1):
        self._server=server
        self._request=None
        self._state=None
        self._timeout=0
        self._timeoutXmitInhibit=0
        self._delayXmitInhibit=delayXmitInhibit
        self._retry=0
        self._msgseq=0
        self.reset()

    @property
    def server(self):
        return self._server

    @property
    def logger(self):
        return self.server.logger

    def generateMsgSeq(self):
        self._msgseq+=1
        if self._msgseq>65535:
            self._msgseq=1
        return self._msgseq

    def setState(self, state, timeout=0):
        self._state=state
        self._timeout=time.time()+timeout

    def setXmitInhibitDelay(self, delay):
        self._delayXmitInhibit=delay

    def reset(self, success=False):
        try:
            if success:
                self._request.onSuccess()
            else:
                self._request.onFailure()
        except:
            pass

        self._request=None
        self.setState(SAIALink.COMMSTATE_IDLE)

    def isIdle(self):
        if self._state==SAIALink.COMMSTATE_IDLE:
            return True

    def isWaitingResponse(self):
        if self._state==SAIALink.COMMSTATE_WAITRESPONSE:
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
            if self._state==SAIALink.COMMSTATE_IDLE:
                return

            elif self._state==SAIALink.COMMSTATE_PENDINGREQUEST:
                if time.time()<self._timeoutXmitInhibit:
                    return

                if self._request.consumeRetry():
                    if self.server.client.sendMessageToHost(self._request.data, self.server.host):
                        self._timeoutXmitInhibit=time.time()+self._delayXmitInhibit
                        self.setState(SAIALink.COMMSTATE_WAITRESPONSE, 2.0)
                        return

                self.reset()
                return

            elif self._state==SAIALink.COMMSTATE_WAITRESPONSE:
                if self.isTimeout():
                    self.logger.error('response timeout!')
                    self.setState(SAIALink.COMMSTATE_PENDINGREQUEST)
                return

            elif self._state==SAIALink.COMMSTATE_ERROR:
                if self.isElapsed(3.0):
                    self.logger.error('link:error')
                    self.reset()
                return

            elif self._state==SAIALink.COMMSTATE_SUCCESS:
                self.reset(True)
                return

            else:
                self.logger.error('link:unkown state %d' % self._state)
                self.setState(SAIALink.COMMSTATE_ERROR)
                return

        except:
            self.logger.exception('link.manager')
            self.setState(SAIALink.COMMSTATE_ERROR)

    def initiate(self, request):
        if self.isIdle() and request is not None:
            self._request=request
            self.setState(SAIALink.COMMSTATE_PENDINGREQUEST)
            return True

    def readFlags(self, index, count=1):
        request=SAIARequestReadFlags(self)
        request.setup(index, count)
        return self.initiate(request)

    def writeFlags(self, index, values):
        request=SAIARequestWriteFlags(self)
        request.setup(index, values)
        return self.initiate(request)

    def readInputs(self, index, count=1):
        print "TODO: readInputs()"
        pass

    def readOutputs(self, index, count=1):
        print "TODO: readOutput()"
        pass

    def readRegisters(self, index, count=1):
        print "TODO: readRegisters()"
        pass

    def onMessage(self, data):
        try:
            (mtype, mseq, payload)=self._msgfactory.SBResponse(data)
            print "<--MESSAGE", mtype, mseq, len(payload)

            if mtype==0:    # Request
                print "TODO: Process RemoteRequest?"

            elif mtype==1:  # Response
                if self.isWaitingResponse():
                    if self._request.validateMessage(mseq, payload):
                        try:
                            self._request.processResponse(payload)
                        except:
                            self.logger.exception('processResponse')

            elif mtype==2:  # Ack/Nak
                if self.isWaitingResponse():
                    if self._request.validateMessage(mseq):
                        try:
                            code=int(payload[0])
                            result=bool(code)
                            self.reset(result)
                        except:
                            self.logger.exception('processAck/Nak')

        except:
            self.logger.exception('onMessage')


class SAIAServer(object):
    def __init__(self, client, host, lid=None):
        self._client=client
        self._host=host
        self._lid=lid
        self._memory=SAIAMemory(self)
        self._link=SAIALink(self)
        self.setLid(lid)

    def isLidValid(self, lid):
        try:
            if lid>=0 and lid<255:
                return True
        except:
            pass

    @property
    def lid(self):
        if self.isLidValid(self._lid):
            return self._lid

        # broadcast (don't care)<Del> address
        return 255

    def setLid(self, lid):
        try:
            if self.isLidValid(lid):
                self._lid=lid
                self.client.declareServerLid(self, lid)
        except:
            pass

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
        if self.isLidValid(self._lid):
            self._memory.manager()
        else:
            print "TODO: readStationNumber"

    def __repr__(self):
        return '%s(%d)' % (self.host, self.lid)

    def dump(self):
        self.memory.dump()


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
