import time
import struct

from .request import SAIARequestReadStationNumber
from .request import SAIARequestReadFlags
from .request import SAIARequestWriteFlags
from .request import SAIARequestReadInputs
from .request import SAIARequestReadOutputs
from .request import SAIARequestWriteOutputs
from .request import SAIARequestReadRegisters
from .request import SAIARequestWriteRegisters

from .request import SAIASBusCRC
from .memory import SAIAMemory


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
                    if self.server.node.sendMessageToHost(self._request.data, self.server.host):
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
            request=SAIARequestReadInputs(self)
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

    def writeRegisters(self, index, count=1):
        if self.isIdle():
            request=SAIARequestWriteRegisters()
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
                    # TODO: can this cas happend ?
                    payload=None
                    (msize, mversion, mtype, msequence, tattribute,
                        mcrc)=struct.unpack('>LBBHB H', data)

            if mcrc==SAIASBusCRC(data[0:-2]):
                self.logger.debug('RX msg type %d seq %d payload %d bytes' % (tattribute, msequence, sizePayload))
                return (tattribute, msequence, payload)

            self.logger.error('bad size/crc')
        except:
            self.logger.exception('decodeMessage')

    def onMessage(self, mtype, mseq, payload):
        try:
            if mtype==0:    # Request
                # must be intercepted at higher level
                pass

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
                            (code,)=struct.unpack('>B', payload[0])
                            result=bool(code)
                            self.reset(result)
                        except:
                            self.logger.exception('processAck/Nak')

        except:
            self.logger.exception('onMessage')


class SAIAServer(object):
    def __init__(self, node, host, lid=None, localNodeMode=False):
        self._node=node
        self._host=host
        self._lid=lid
        self._memory=SAIAMemory(self, localNodeMode)
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
                self.node.declareServerLid(self, lid)
        except:
            pass

    @property
    def host(self):
        return self._host

    @property
    def node(self):
        return self._node

    @property
    def logger(self):
        return self.node.logger

    @property
    def memory(self):
        return self._memory

    @property
    def link(self):
        return self._link

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

    def onMessage(self, mtype, mseq, payload):
        return self.link.onMessage(mtype, mseq, payload)

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


if __name__ == "__main__":
    pass
