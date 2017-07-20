import time
import socket
import struct

from threading import RLock
from threading import Event
from Queue import Queue
# from threading import Thread

import logging
import logging.handlers

# from SBusMsg import SBusClientMessages
# from SBusMsg import SBusServerMessages

from ModbusDataLib import bin2boollist
from ModbusDataLib import boollist2bin

from digimat.jobs import JobManager


# SBus hints
# https://github.com/boundary/wireshark/blob/master/epan/dissectors/packet-sbus.c


# This is the precalculated hash table for CCITT V.41.
SAIASBusCRCTable = [
    0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5, 0x60c6, 0x70e7,
    0x8108, 0x9129, 0xa14a, 0xb16b, 0xc18c, 0xd1ad, 0xe1ce, 0xf1ef,
    0x1231, 0x0210, 0x3273, 0x2252, 0x52b5, 0x4294, 0x72f7, 0x62d6,
    0x9339, 0x8318, 0xb37b, 0xa35a, 0xd3bd, 0xc39c, 0xf3ff, 0xe3de,
    0x2462, 0x3443, 0x0420, 0x1401, 0x64e6, 0x74c7, 0x44a4, 0x5485,
    0xa56a, 0xb54b, 0x8528, 0x9509, 0xe5ee, 0xf5cf, 0xc5ac, 0xd58d,
    0x3653, 0x2672, 0x1611, 0x0630, 0x76d7, 0x66f6, 0x5695, 0x46b4,
    0xb75b, 0xa77a, 0x9719, 0x8738, 0xf7df, 0xe7fe, 0xd79d, 0xc7bc,
    0x48c4, 0x58e5, 0x6886, 0x78a7, 0x0840, 0x1861, 0x2802, 0x3823,
    0xc9cc, 0xd9ed, 0xe98e, 0xf9af, 0x8948, 0x9969, 0xa90a, 0xb92b,
    0x5af5, 0x4ad4, 0x7ab7, 0x6a96, 0x1a71, 0x0a50, 0x3a33, 0x2a12,
    0xdbfd, 0xcbdc, 0xfbbf, 0xeb9e, 0x9b79, 0x8b58, 0xbb3b, 0xab1a,
    0x6ca6, 0x7c87, 0x4ce4, 0x5cc5, 0x2c22, 0x3c03, 0x0c60, 0x1c41,
    0xedae, 0xfd8f, 0xcdec, 0xddcd, 0xad2a, 0xbd0b, 0x8d68, 0x9d49,
    0x7e97, 0x6eb6, 0x5ed5, 0x4ef4, 0x3e13, 0x2e32, 0x1e51, 0x0e70,
    0xff9f, 0xefbe, 0xdfdd, 0xcffc, 0xbf1b, 0xaf3a, 0x9f59, 0x8f78,
    0x9188, 0x81a9, 0xb1ca, 0xa1eb, 0xd10c, 0xc12d, 0xf14e, 0xe16f,
    0x1080, 0x00a1, 0x30c2, 0x20e3, 0x5004, 0x4025, 0x7046, 0x6067,
    0x83b9, 0x9398, 0xa3fb, 0xb3da, 0xc33d, 0xd31c, 0xe37f, 0xf35e,
    0x02b1, 0x1290, 0x22f3, 0x32d2, 0x4235, 0x5214, 0x6277, 0x7256,
    0xb5ea, 0xa5cb, 0x95a8, 0x8589, 0xf56e, 0xe54f, 0xd52c, 0xc50d,
    0x34e2, 0x24c3, 0x14a0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
    0xa7db, 0xb7fa, 0x8799, 0x97b8, 0xe75f, 0xf77e, 0xc71d, 0xd73c,
    0x26d3, 0x36f2, 0x0691, 0x16b0, 0x6657, 0x7676, 0x4615, 0x5634,
    0xd94c, 0xc96d, 0xf90e, 0xe92f, 0x99c8, 0x89e9, 0xb98a, 0xa9ab,
    0x5844, 0x4865, 0x7806, 0x6827, 0x18c0, 0x08e1, 0x3882, 0x28a3,
    0xcb7d, 0xdb5c, 0xeb3f, 0xfb1e, 0x8bf9, 0x9bd8, 0xabbb, 0xbb9a,
    0x4a75, 0x5a54, 0x6a37, 0x7a16, 0x0af1, 0x1ad0, 0x2ab3, 0x3a92,
    0xfd2e, 0xed0f, 0xdd6c, 0xcd4d, 0xbdaa, 0xad8b, 0x9de8, 0x8dc9,
    0x7c26, 0x6c07, 0x5c64, 0x4c45, 0x3ca2, 0x2c83, 0x1ce0, 0x0cc1,
    0xef1f, 0xff3e, 0xcf5d, 0xdf7c, 0xaf9b, 0xbfba, 0x8fd9, 0x9ff8,
    0x6e17, 0x7e36, 0x4e55, 0x5e74, 0x2e93, 0x3eb2, 0x0ed1, 0x1ef0
]


def SAIASBusCRC(inpdata):
    """Calculate a CCIT V.41 CRC hash function based on the polynomial
        X^16 + X^12 + X^5 + 1 for SAIA S-Bus (initializer = 0x0000)
    Parameters: inpdata (string) = The string to calculate the crc on.
    Return: (integer) = The calculated CRC.
    """
    # This uses the built-in reduce rather than importing it from functools
    # in order to provide compatiblity with Python 2.5. This may have to be
    # changed in future for Python 3.x
    return reduce(lambda crc, newchar:
        SAIASBusCRCTable[((crc >> 8) ^ ord(newchar)) & 0xFF] ^ ((crc << 8) & 0xFFFF),
            inpdata, 0x0000)


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


class SAIAValueFormater(object):
    def __init__(self, logger):
        self._logger=logger
        self.logger.debug('creating value formater %s' % self.__class__.__name__)
        self.onInit()
        self.check()

    def init(self, *args, **kwds):
        return self.onInit(*args, **kwds)

    @property
    def logger(self):
        return self._logger

    def onInit(self, *args, **kwds):
        pass

    def uint32(self, data32bits):
        return struct.unpack('>I', data32bits)

    def decode(self, value):
        return value

    def encode(self, value):
        return value

    def check(self):
        value=50
        raw=self.encode(value)
        error=abs(self.decode(raw)-value)
        print "ERROR", error
        # self.logger.error('%s:buggy?' % self.__class__.__name__)


class SAIAValueFormaterFloat32(SAIAValueFormater):

    def encode(self, value):
        return self.uint32(struct.pack('>f', value))

    def pack(self, value):
        data=struct.pack('>I', int(value*10.0))


class SAIAItem(object):
    def __init__(self, parent, index, value=None, delayRefresh=None, readOnly=False):
        self._parent=parent
        self._index=index
        self._formater=None
        self._value=self.validateValue(value)
        self._pushValue=None
        self._stamp=0
        self._readOnly=readOnly
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

    def setFormater(self, formater):
        try:
            if issubclass(formater, SAIAValueFormater):
                self._formater=formater
        except:
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
        self._readOnly=state

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

    def convertUserValueToDeviceValue(self, value):
        try:
            if self._formater:
                return self._formater.encode(value)
        except:
            pass
        return value

    def convertDeviceValueToUserValue(self, value):
        try:
            if self._formater:
                return self._formater.decode(value)
        except:
            pass
        return value

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
        if self.age()>self.getRefreshDelay():
            self.signalPull()

    def strValue(self):
        return str(self.value)

    def __repr__(self):
        return '%s.%s[%d](value=%s, age=%ds)' % (self.server,
            self.__class__.__name__,
            self.index, self.strValue(), self.age())


class SAIAAnalogItem(SAIAItem):

    # Rule : item value is *always* stored in a raw UINT32 form
    # This is our native format ('>I'

    def valueFromFloat32(self, float32):
        try:
            data=struct.pack('>f', float32)
            return struct.unpack('>I', data)
        except:
            pass


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
        self.setReadOnly()

    def pull(self):
        return self.server.link.readInputs(self.index, 1)


class SAIAItemOutput(SAIABooleanItem):
    def onInit(self):
        self.logger.debug('creating item %d->output[%d]' % (self.server.lid, self.index))

    def pull(self):
        return self.server.link.readOutputs(self.index, 1)

    def push(self):
        return self.server.link.writeOutputs(self.index, self.value)


class SAIAItems(object):
    def __init__(self, memory, itemType, maxsize, readOnly=False):
        self._memory=memory
        self._lock=RLock()
        self._itemType=itemType
        self._maxsize=maxsize
        self._readOnly=readOnly
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

    def setReadOnly(self, state=True):
        self._readOnly=state

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
            item.setReadOnly(self._readOnly)
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
        self.setReadOnly()


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

    COMMAND_READ_FLAGS = 0x02
    COMMAND_READ_INPUTS = 0x03
    COMMAND_READ_OUTPUTS = 0x05
    COMMAND_READ_REGISTERS = 0x06
    COMMAND_WRITE_FLAGS = 0x0b
    COMMAND_WRITE_OUTPUTS = 0x0c
    COMMAND_WRITE_REGISTERS = 0x0d
    COMMAND_READ_STATIONNUMBER = 0x1d

    def __init__(self, link, retry=3):
        self._link=link
        self._retry=retry
        self._data=None
        self._command=0
        self._stamp=0
        self._ready=False
        self._sequence=0
        self.onInit()

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

    def initiate(self):
        return self.link.initiate(self)

    def safeMakeArray(self, item):
        if type(item) in (list, tuple):
            return item

        items=[]
        if item:
            items.append(item)
        return items

    def safeMakeBoolArray(self, item):
        items=self.safeMakeArray()
        return map(bool, items)

    def createFrameWithPayload(self, payload=None):
        """
        Add hedear (data size) and footer (crc) to the given data
        plus typical frame attributes
        """

        # Typical Request Format
        # ----------------------
        # frame length,
        # protocol number (0,1), protocol type (0), frame type (0=REQ, 1=RESP, 2=ACK/NAK),
        # station address, command
        # [data]
        # crc

        if payload:
            sizePayload=len(payload)
            fformat='>L BBHB BB %ds' % sizePayload
            fsize=13+sizePayload
            frame=struct.pack(fformat,
                fsize,
                0, 0, self._sequence, 0,
                self.server.lid, self._command,
                payload)
        else:
            fformat='>L BBHB BB'
            fsize=13
            frame=struct.pack(fformat,
                fsize,
                0, 0, self._sequence, 0,
                self.server.lid, self._command)

        return struct.pack('>%ds H' % len(frame), frame, SAIASBusCRC(frame))

    def encode(self):
        """
        create binary data frame from request data
        header (size) and footer (crc) will be added around this
        """
        return None

    def ready(self):
        self._ready=True

    def isReady(self):
        if self._ready:
            return True

    def build(self):
        try:
            if self.isReady():
                self._sequence=self.link.generateMsgSeq()
                self._data=self.createFrameWithPayload(self.encode())
                self._stamp=time.time()
            else:
                self.logger.error('%s:unable to encode (not ready)' % self.__class__)
                return None
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

    def validateMessage(self, sequence, payload=None):
        if self.isReady():
            if sequence==self._sequence:
                return True

    def processResponse(self, payload):
        return False

    def onSuccess(self):
        pass

    def onFailure(self):
        pass


class SAIARequestReadStationNumber(SAIARequest):
    def onInit(self):
        self._command=SAIARequest.COMMAND_READ_STATIONNUMBER
        self.ready()

    def encode(self):
        return None

    def processResponse(self, payload):
        lid=int(payload[0])
        print "RECEIVED LID", lid
        self.server.setLid(lid)
        return True

    def onFailure(self):
        print "DEBUG: Simulate LID rx"
        self.server.setLid(1)


class SAIARequestReadItem(SAIARequest):
    def setup(self, address, count=1):
        self._address=address
        self._count=count
        self.ready()

    def encode(self):
        # count = number of item to read - 1
        return struct.pack('>BH',
                self._count-1, self._address)

    def data2uint32list(self, data):
        return list(struct.unpack('>%dI' % (len(data) / 4), data))


class SAIARequestReadFlags(SAIARequestReadItem):
    def onInit(self):
        self._command=SAIARequest.COMMAND_READ_FLAGS

    def processResponse(self, payload):
        flags=self.memory.flags

        index=self._address
        count=self._count
        values=bin2boollist(payload)
        print index, count, values

        for n in range(count):
            print "FLAG(%d)=%d" % (index+n, values[n])
            flags[index+n].setValue(values[n])

        return True


class SAIARequestReadInputs(SAIARequestReadItem):
    def onInit(self):
        self._command=SAIARequest.COMMAND_READ_INPUTS

    def processResponse(self, payload):
        inputs=self.memory.inputs

        index=self._address
        count=self._count
        values=bin2boollist(payload)
        print index, count, values

        for n in range(count):
            print "INPUT(%d)=%d" % (index+n, values[n])
            inputs[index+n].setValue(values[n])

        return True


class SAIARequestReadOutputs(SAIARequestReadItem):
    def onInit(self):
        self._command=SAIARequest.COMMAND_READ_OUTPUTS

    def processResponse(self, payload):
        outputs=self.memory.outputs

        index=self._address
        count=self._count
        values=bin2boollist(payload)
        print index, count, values

        for n in range(count):
            print "OUTPUT(%d)=%d" % (index+n, values[n])
            outputs[index+n].setValue(values[n])

        return True


class SAIARequestReadRegisters(SAIARequestReadItem):
    def onInit(self):
        self._command=SAIARequest.COMMAND_READ_REGISTERS

    def processResponse(self, payload):
        registers=self.memory.registers

        index=self._address
        count=self._count
        values=self.data2uint32list(payload)
        print index, count, values

        for n in range(count):
            item=registers[index+n]
            deviceValue=values[n]
            value=item.convertDeviceValueToUserValue(deviceValue)
            print "REGISTER(%d)=%f (%u)" % (index+n, value, deviceValue)
            registers[index+n].setValue(value)

        return True


class SAIARequestWriteFlags(SAIARequest):
    def onInit(self):
        self._command=SAIARequest.COMMAND_WRITE_FLAGS

    def setup(self, address, values):
        self._address=address
        self._values=self.safeMakeBoolArray(values)
        self.ready()

    def encode(self):
        data=boollist2bin(self._values)

        # bytecount = number item to write (as msg length + 2)
        bytecount=len(data)+2
        fiocount=len(self._values)-1

        return struct.pack('>BHB %ds',  bytecount, self._address, fiocount, data)


class SAIARequestWriteOutputs(SAIARequestWriteFlags):
    def onInit(self):
        self._command=SAIARequest.COMMAND_WRITE_OUTPUTS


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
                    else:
                        self.setState(SAIALink.COMMSTATE_ERROR)
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
        if self.isIdle():
            if request is not None and request.isReady():
                self._request=request
                self.setState(SAIALink.COMMSTATE_PENDINGREQUEST)
                return True

    def readFlags(self, index, count=1):
        if self.isIdle():
            request=SAIARequestReadFlags(self)
            request.setup(index, count)
            return self.initiate(request)

    def writeFlags(self, index, values):
        if self.isIdle():
            request=SAIARequestWriteFlags(self)
            request.setup(index, values)
            return self.initiate(request)

    def readInputs(self, index, count=1):
        if self.isIdle():
            request=SAIARequestReadFlags(self)
            request.setup(index, count)
            return self.initiate(request)

    def readOutputs(self, index, count=1):
        if self.isIdle():
            request=SAIARequestReadOutputs(self)
            request.setup(index, count)
            return self.initiate(request)

    def writeOutputs(self, index, values):
        if self.isIdle():
            request=SAIARequestWriteOutputs(self)
            request.setup(index, values)
            return self.initiate(request)

    def readRegisters(self, index, count=1):
        if self.isIdle():
            request=SAIARequestReadRegisters()
            request.setup(index, count)
            return self.initiate(request)

    def readStationNumber(self):
        if self.isIdle():
            request=SAIARequestReadStationNumber(self)
            return self.initiate(request)

    def decodeMessage(self, data):
        try:
            size=len(data)
            if size>=11 and size<=255:
                sizePayload=size-11
                if sizePayload>0:
                    (msize, mversion, mtype, msequence, tattribute,
                        payload, mcrc)=struct.unpack('>LBBHB %ds H' % sizePayload, data)
                else:
                    payload=None
                    (msize, mversion, mtype, msequence, tattribute,
                        mcrc)=struct.unpack('>LBBHB H', data)

            if mcrc==SAIASBusCRC(data[0:-2]):
                self.logger.debug('RX type %d seq %d payload %d bytes' % (tattribute, msequence, sizePayload))
                return (tattribute, msequence, payload)

            self.logger.error('bad size/crc')
        except:
            self.logger.exception('decodeMessage')

    def onMessage(self, data):
        try:
            (mtype, mseq, payload)=self.decodeMessage(data)
            print "<--MESSAGE", mtype, mseq, len(payload)

            if mtype==0:    # Request
                print "TODO: Process RemoteRequest?"

            elif mtype==1:  # Response
                if self.isWaitingResponse():
                    if self._request.validateMessage(mseq, payload):
                        try:
                            result=self._request.processResponse(payload)
                            self.reset(result)
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
            self.link.readStationNumber()

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


if __name__ == "__main__":
    pass
