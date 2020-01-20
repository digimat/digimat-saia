from __future__ import division

import time

# python2-3 compatibility require 'pip install future'
from queue import Queue

from .request import SAIARequestReadDBX
from .request import SAIARequestReadStationNumber


class SAIATransfer(object):
    def __init__(self, server):
        assert server.__class__.__name__=='SAIAServer'
        self._server=server
        self._start=False
        self._done=False
        self._timeoutWatchdog=0
        self._request=None
        self._payload=None

    @property
    def server(self):
        return self._server

    @property
    def logger(self):
        return self.server.logger

    def isDebug(self):
        return self.server.isDebug()

    @property
    def link(self):
        return self.server.link

    def initiateTransfer(self):
        pass

    def processDataAndContinueTransfer(self, data):
        pass

    def finalizeTransferAndComputePayload(self):
        pass

    def onSuccess(self):
        pass

    def onFailure(self):
        pass

    def isActive(self):
        if self._start:
            return True
        return False

    def isDone(self):
        if self._done:
            return True
        return False

    def heartbeat(self):
        self._timeoutWatchdog=time.time()+15.0

    def submitRequest(self, request):
        if request and not self._request:
            self._request=request
            if not self.isActive():
                self.start()

    def start(self):
        try:
            self._payload=None
            self._done=False
            self._start=True
            self.heartbeat()
            if self.isDebug():
                self.logger.debug('%s:start()' % self.__class__.__name__)
            self.initiateTransfer()
        except:
            self.stop(False)

    def stop(self, result=False):
        self._start=False
        self._done=True
        if not result:
            self.logger.warning('%s:stop(%d)' % (self.__class__.__name__, result))
        elif self.isDebug():
            self.logger.debug('%s:stop(%d)' % (self.__class__.__name__, result))

        if result:
            try:
                self.finalizeTransferAndComputePayload()
                self.onSuccess()
                return
            except:
                pass
        try:
            self.onSuccess()
        except:
            pass

    def abort(self):
        self.stop(False)

    def setPayload(self, data):
        if self.isDone() and data and not self._payload:
            self._payload=data

    @property
    def payload(self):
        return self._payload

    def manager(self):
        activity=False
        if self.isActive():
            try:
                if time.time()>self._timeoutWatchdog:
                    self.logger.error('%s:watchdog()' % self.__class__.__name__)
                    self.stop(False)
                else:
                    if self._request:
                        if self._request.isDone():
                            request=self._request
                            self._request=None
                            if request.isSuccess():
                                data=request.reply
                                if data:
                                    self.processDataAndContinueTransfer(data)
                                if self._request:
                                    activity=True
                                else:
                                    self.stop(True)
                            else:
                                self.stop(False)
                        else:
                            if not self._request.isActive():
                                if self.link.isIdle():
                                    self._request.initiate()
                                    activity=True
                    else:
                        self.stop(True)
            except:
                self.logger.exception('%s:onRun()' % self.__class__.__name__)
                self.stop(False)

            return activity

    def submit(self):
        """
        submit or resubmit transfer to the server
        """
        if not self.isActive():
            self._payload=None
            self.server.submitTransfer(self)

    def __repr__(self):
        return '<%s(active=%d, done=%d)>' % (self.__class__.__name__, bool(self.isActive()), bool(self.isDone()))


class SAIATransferReadDeviceInformation(SAIATransfer):
    def send(self):
        if self._count>0:
            count=min(self._maxChunkSize, self._count)
            request=SAIARequestReadDBX(self.link)
            request.setup(address=self._address, count=count)
            self.submitRequest(request)

    def initiateTransfer(self):
        self._buffer=''
        self._address=0x00
        self._count=0x64
        self._maxChunkSize=0x20
        self.send()

    def processDataAndContinueTransfer(self, data):
        # keep care of accented chars ;)
        # TODO: using latin1 encoding by not sure if this is absolutely correct
        self._buffer+=data.decode('latin1')
        count=len(data)//4
        self._address+=count
        self._count-=count
        self.send()

    def finalizeTransferAndComputePayload(self):
        data={}
        for item in self._buffer.split('\n'):
            try:
                (key, value)=item.split('=')
                data[key.strip()]=value.strip()
            except:
                pass

        self.setPayload(data)

    def onSuccess(self):
        data=self.payload
        for key in data:
            self.server.setDeviceInfo(key, data[key])

        self.server.loadSymbols()


class SAIATransferDiscoverNodes(SAIATransfer):
    def send(self):
        request=SAIARequestReadStationNumber(self.link, broadcast=True)
        self.submitRequest(request)

    def initiateTransfer(self):
        self.send()

    def processDataAndContinueTransfer(self, data):
        pass

    def finalizeTransferAndComputePayload(self):
        pass

    def onSuccess(self):
        pass


class SAIATransferFromRequest(SAIATransfer):
    def __init__(self, request):
        super(SAIATransferFromRequest, self).__init__(request.server)
        self._wrappedRequest=request

    def initiateTransfer(self):
        self.submitRequest(self._wrappedRequest)


class SAIATransferQueue(object):
    def __init__(self, server):
        assert server.__class__.__name__=='SAIAServer'
        self._server=server
        self._queue=Queue()
        self._transfer=None

    @property
    def server(self):
        return self._server

    def isDebug(self):
        return self.server.isDebug()

    @property
    def logger(self):
        return self.server.logger

    def isEmpty(self):
        return self._queue.isEmpty()

    def count(self):
        return self._queue.qsize()

    def submit(self, transfer):
        assert isinstance(transfer, SAIATransfer)
        self._queue.put(transfer)
        if self.isDebug():
            self.logger.debug('queue:%s (size=%d)' % (transfer.__class__.__name__,
                                    self._queue.qsize()))

    def getNextTransfer(self):
        try:
            return self._queue.get(False)
        except:
            pass

    def manager(self):
        activity=False
        if self._transfer:
            activity=self._transfer.manager()
            if self._transfer.isDone():
                del self._transfer
                self._transfer=None
        else:
            self._transfer=self.getNextTransfer()
            if self._transfer:
                self._transfer.start()
                activity=True
        return activity

    def __repr__(self):
        return '<%s(%d items)>' % (self.__class__.__name__, self.count())
