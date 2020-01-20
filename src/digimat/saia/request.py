from __future__ import print_function  # Python 2/3 compatibility
from __future__ import division

import struct
import time
from functools import reduce
from builtins import bytes

from .ModbusDataLib import bin2boollist
from .ModbusDataLib import boollist2bin

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


def SAIASBusCRC_old(data):
    """Calculate a CCIT V.41 CRC hash function based on the polynomial
        X^16 + X^12 + X^5 + 1 for SAIA S-Bus (initializer = 0x0000)
    Parameters: inpdata (string) = The string to calculate the crc on.
    Return: (integer) = The calculated CRC.
    """
    # This uses the built-in reduce rather than importing it from functools
    # in order to provide compatiblity with Python 2.5. This may have to be
    # changed in future for Python 3.x
    crc=reduce(lambda crc, newchar:
        SAIASBusCRCTable[((crc >> 8) ^ ord(newchar)) & 0xFF] ^ ((crc << 8) & 0xFFFF),
           data, 0x0000)
    return crc


def SAIASBusCRC(data):
    crc=0
    # using bytes() for Python2/3 compatibility
    for b in bytes(data):
        crc=SAIASBusCRCTable[((crc >> 8) ^ b) & 0xFF] ^ ((crc << 8) & 0xFFFF)
    return crc


def SAIASBusCRCTableCheck():
    """
    Simple CRC table consistency check
    """
    if sum(SAIASBusCRCTable)==8388480:
        return True


class SAIARequest(object):

    COMMAND_READ_FLAGS = 0x02
    COMMAND_READ_INPUTS = 0x03
    COMMAND_READ_OUTPUTS = 0x05
    COMMAND_READ_REGISTERS = 0x06
    COMMAND_READ_TIMERS = 0x07
    COMMAND_READ_COUNTERS = 0x00

    COMMAND_WRITE_FLAGS = 0x0b
    COMMAND_WRITE_OUTPUTS = 0x0d
    COMMAND_WRITE_REGISTERS = 0x0e
    COMMAND_WRITE_TIMERS = 0x0f
    COMMAND_WRITE_COUNTERS = 0x0a

    COMMAND_READ_PCD_STATUS_OWN = 0x1b
    COMMAND_READ_STATIONNUMBER = 0x1d
    COMMAND_READ_PROGRAM_VERSION = 0x20
    COMMAND_READ_SYSTEM_INFO = 0xab

    COMMAND_CLEAR_ALL = 0x5a
    COMMAND_CLEAR_FLAGS = 0x5b
    COMMAND_CLEAR_OUTPUTS = 0x5c
    COMMAND_CLEAR_REGISTERS = 0x5d
    COMMAND_CLEAR_TIMERS = 0x5e
    # No request for clearing counters

    COMMAND_RESTART_COLD_ALL = 0x39
    COMMAND_RESTART_COLD_FLAG = 0xa6

    COMMAND_RUN_CPU_ALL = 0x30
    COMMAND_STOP_CPU_ALL = 0x44
    COMMAND_RESTART_CPU_ALL = 0x6b
    COMMAND_READ_DBX = 0x9f

    COMMAND_READ_PCD_STATUS_OWN = 0x1b

    def __init__(self, link, retry=3, broadcast=False):
        assert link.__class__.__name__=='SAIALink'
        self._link=link
        self._broadcast=broadcast
        self._retry=retry
        self._data=None
        self._dataReply=None
        self._command=0
        self._stamp=0
        self._ready=False
        self._start=False
        self._done=False
        self._result=False
        self._sequence=0
        self.onInit()
        SAIASBusCRCTableCheck()

    def onInit(self):
        pass

    def setup(self):
        pass

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

    @property
    def sequence(self):
        return self._sequence

    def initiate(self):
        return self.link.initiate(self)

    def safeMakeArray(self, item):
        if type(item) in (list, tuple):
            return item

        items=[]
        if item is not None:
            items.append(item)
        return items

    def safeMakeBoolArray(self, item):
        items=self.safeMakeArray(item)
        return map(bool, items)

    def createFrameWithPayload(self, payload=None):
        """
        Add hedear (data size) and footer (crc) to the given data
        plus typical frame attributes
        """

        # Typical Request Format
        # ----------------------
        # frame length,
        # protocol number (0,1), protocol type (0), sequence, frame type (0=REQ, 1=RESP, 2=ACK/NAK),
        # station address, command
        # [data]
        # crc

        if payload:
            sizePayload=len(payload)
            fsize=13+sizePayload
            frame=struct.pack('>L BBHB BB %ds' % sizePayload,
                fsize,
                0, 0, self._sequence, 0,
                self.server.lid, self._command,
                payload)
        else:
            fsize=13
            frame=struct.pack('>L BBHB BB',
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
        return False

    def isActive(self):
        if self._start and not self.isDone():
            return True
        return False

    def isDone(self):
        if self._done:
            return True
        return False

    def isSuccess(self):
        if self.isDone() and self._result:
            return True
        return False

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

    @property
    def reply(self):
        return self._dataReply

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
        self._dataReply=payload
        return True

    def onSuccess(self):
        pass

    def onFailure(self):
        pass

    def start(self):
        self._start=True
        self._done=False
        self._result=False

    def stop(self, success):
        self._done=True
        try:
            if success:
                self.onSuccess()
                self._result=True
            else:
                self.onFailure()
        except:
            pass

    def data2uint32list(self, data):
        return list(struct.unpack('>%dI' % (len(data) // 4), data))

    def __repr__(self):
        return '%s(mseq=%d)' % (self.__class__.__name__, self.sequence)

    def __str__(self):
        return self.__repr__()

    def data2strhex(self, data):
        return ' '.join(x.encode('hex') for x in data)


class SAIARequestReadStationNumber(SAIARequest):
    def onInit(self):
        self._command=SAIARequest.COMMAND_READ_STATIONNUMBER
        self.ready()

    def encode(self):
        return None

    def processResponse(self, payload):
        (lid,)=struct.unpack('>B', payload)
        self.server.setLid(lid)
        return True

    def onFailure(self):
        pass


class SAIARequestReadPcdStatusOwn(SAIARequest):
    def onInit(self):
        self._command=SAIARequest.COMMAND_READ_PCD_STATUS_OWN
        self.ready()

    def encode(self):
        return None

    def processResponse(self, payload):
        (status,)=struct.unpack('>B', payload)
        self.server.setStatus(status)
        return True


class SAIARequestRunCpuAll(SAIARequest):
    def onInit(self):
        self._command=SAIARequest.COMMAND_RUN_CPU_ALL
        self.ready()

    def encode(self):
        return None


class SAIARequestStopCpuAll(SAIARequest):
    def onInit(self):
        self._command=SAIARequest.COMMAND_STOP_CPU_ALL
        self.ready()

    def encode(self):
        return None


class SAIARequestRestartCpuAll(SAIARequest):
    def onInit(self):
        self._command=SAIARequest.COMMAND_RESTART_CPU_ALL
        self.ready()

    def encode(self):
        return None


# class SAIARequestReadSystemInformation(SAIARequest):
    # def onInit(self):
        # self._command=SAIARequest.COMMAND_READ_SYSTEM_INFO
        # self.ready()

    # def setup(self, block):
        # self._block=block

    # def encode(self):
        # return struct.pack('>BB', 0x00, self._block)

    # def processResponse(self, payload):
        # return True

    # def onFailure(self):
        # pass


class SAIARequestReadDBX(SAIARequest):
    def onInit(self):
        self._command=SAIARequest.COMMAND_READ_DBX

    def setup(self, address, count):
        self._address=address
        self._count=count
        self._response=None
        self.ready()

    def encode(self):
        # address if 3 bytes long
        buf=struct.pack('>L', self._address)[1:]
        # 0x06 : ?
        return struct.pack('>BBB3s', self._count-1, 0x00, 0x06, buf)


# class SAIARequestRunProcedureOwn(SAIARequest):
    # def onInit(self):
        # self._command=SAIARequest.COMMAND_RUN_PROCEDURE_OWN
        # self.ready()

    # def encode(self):
        # return None


class SAIARequestReadItems(SAIARequest):
    def setup(self, item, maxcount=1):
        self._item=item
        self._count=self.optimizePullCount(maxcount)
        self.ready()

    @property
    def item(self):
        return self._item

    def items(self):
        return self.item.parent

    def optimizePullCount(self, maxcount):
        """
        Try to increase item read count
        Only consecutive items are taken in account (no hole allowed)
        """

        try:
            count=1
            item=self.item
            while count<maxcount:
                item=item.next()
                # if not item or not item.isPendingPullRequest():
                # better try to systematically read multiples items
                if not item:
                    break
                count+=1

            return count
        except:
            pass
        return 1

    def encode(self):
        # count = number of item to read - 1
        return struct.pack('>BH',
                self._count-1, self.item.index)

    def extractValuesFromPayload(self, payload):
        return None

    def processResponse(self, payload):
        index0=self.item.index
        count=self._count
        values=self.extractValuesFromPayload(payload)

        items=self.items()

        for n in range(count):
            # decode only pre-declared (existing) items
            # this allow sending grouped read requests
            item=items.item(index0+n)
            if item:
                item.setValue(values[n], force=True)
                item.clearPull()

        return True

    def __repr__(self):
        return '%s(mseq=%d, index=%d, count=%d)' % (self.__class__.__name__,
            self.sequence, self.item.index, self._count)


class SAIARequestReadAnalogItems(SAIARequestReadItems):
    def extractValuesFromPayload(self, payload):
        return self.data2uint32list(payload)


class SAIARequestReadRegisters(SAIARequestReadAnalogItems):
    def onInit(self):
        self._command=SAIARequest.COMMAND_READ_REGISTERS


class SAIARequestReadTimers(SAIARequestReadAnalogItems):
    def onInit(self):
        self._command=SAIARequest.COMMAND_READ_TIMERS


class SAIARequestReadCounters(SAIARequestReadAnalogItems):
    def onInit(self):
        self._command=SAIARequest.COMMAND_READ_COUNTERS


class SAIARequestReadBooleanItems(SAIARequestReadItems):
    def extractValuesFromPayload(self, payload):
        return bin2boollist(payload)


class SAIARequestReadFlags(SAIARequestReadBooleanItems):
    def onInit(self):
        self._command=SAIARequest.COMMAND_READ_FLAGS


class SAIARequestReadInputs(SAIARequestReadBooleanItems):
    def onInit(self):
        self._command=SAIARequest.COMMAND_READ_INPUTS


class SAIARequestReadOutputs(SAIARequestReadBooleanItems):
    def onInit(self):
        self._command=SAIARequest.COMMAND_READ_OUTPUTS


class SAIARequestWriteItems(SAIARequest):
    def setup(self, item, maxcount=1):
        self._item=item

        values=[item.pushValue]
        while len(values)<maxcount:
            item=item.next()
            if not item or not item.isPendingPushRequest():
                break
            values.append(item.pushValue)

        self._values=self.safeMakeArray(values)
        self.ready()

    @property
    def item(self):
        return self._item

    def items(self):
        return self.item.parent

    def refreshItems(self):
        try:
            items=self.items()
            index0=self.item.index
            for n in range(len(self._values)):
                item=items[index0+n]
                item.clearPush()
                if item:
                    item.refresh(urgent=True)
        except:
            pass

    def onSuccess(self):
        # after push (write oending value), we need a refresh to update the actual value
        self.refreshItems()

    def onFailure(self):
        pass


class SAIARequestWriteBooleanItems(SAIARequestWriteItems):
    def encode(self):
        data=boollist2bin(self._values)

        # TODO: not ideal, but fix zthe problem for python2->3 conversion
        # as when need bytes instead of str
        data=struct.pack('%dB' % len(data), *[ord(c) for c in data])

        # bytecount = number item to write (as msg length + 2)
        bytecount=len(data)+2
        fiocount=len(self._values)-1

        return struct.pack('>BHB %ds' % len(data), bytecount, self.item.index, fiocount, data)

    def __repr__(self):
        return '%s(mseq=%d, index=%d, values=%s)' % (self.__class__.__name__,
            self.sequence, self.item.index, str(self._values))


class SAIARequestWriteFlags(SAIARequestWriteBooleanItems):
    def onInit(self):
        self._command=SAIARequest.COMMAND_WRITE_FLAGS


class SAIARequestWriteOutputs(SAIARequestWriteBooleanItems):
    def onInit(self):
        self._command=SAIARequest.COMMAND_WRITE_OUTPUTS


class SAIARequestWriteAnalogItems(SAIARequestWriteItems):
    def dwordlist2bin(self, dwordlist):
        return struct.pack('>%dL' % len(dwordlist), *dwordlist)

    def encode(self):
        data=self.dwordlist2bin(self._values)
        bytecount=len(data)+1
        return struct.pack('>BH %ds' % len(data), bytecount, self.item.index, data)

    def __repr__(self):
        return '%s(mseq=%d, index=%d, values=%s)' % (self.__class__.__name__,
            self.sequence, self.item.index, str(self._values))


class SAIARequestWriteRegisters(SAIARequestWriteAnalogItems):
    def onInit(self):
        self._command=SAIARequest.COMMAND_WRITE_REGISTERS


class SAIARequestWriteTimers(SAIARequestWriteAnalogItems):
    def onInit(self):
        self._command=SAIARequest.COMMAND_WRITE_TIMERS


class SAIARequestWriteCounters(SAIARequestWriteAnalogItems):
    def onInit(self):
        self._command=SAIARequest.COMMAND_WRITE_COUNTERS


if __name__ == "__main__":
    pass
