# import sys

# python2-3 compatibility require 'pip install future'
from queue import Queue

from .items import SAIABooleanItem
from .items import SAIAAnalogItem
from .items import SAIAItems

from .request import SAIARequestReadFlags
from .request import SAIARequestWriteFlags
from .request import SAIARequestReadInputs
from .request import SAIARequestReadOutputs
from .request import SAIARequestWriteOutputs
from .request import SAIARequestReadRegisters
from .request import SAIARequestWriteRegisters

from .symbol import SAIASymbol


class SAIAItemQueue(Queue):
    def _init(self, maxsize):
        self._queue=[]

    def _qsize(self):
        return len(self._queue)

    def _put(self, item):
        if item not in self._queue:
            self._queue.insert(0, item)

    def _get(self):
        item=self._queue.pop()
        return item


class SAIAItemFlag(SAIABooleanItem):
    def onInit(self):
        pass

    def pull(self):
        request=SAIARequestReadFlags(self.server.link)
        request.setup(self, maxcount=96)
        return request.initiate()

    def push(self):
        request=SAIARequestWriteFlags(self.server.link)
        request.setup(self, maxcount=96)
        return request.initiate()

    @property
    def tag(self):
        try:
            return self.server.symbols.flag(self.index).tag
        except:
            pass


class SAIAItemInput(SAIABooleanItem):
    def onInit(self):
        self.setReadOnly()

    def pull(self):
        request=SAIARequestReadInputs(self.server.link)
        request.setup(self, maxcount=96)
        return request.initiate()


class SAIAItemOutput(SAIABooleanItem):
    def onInit(self):
        pass

    def pull(self):
        request=SAIARequestReadOutputs(self.server.link)
        request.setup(self, maxcount=96)
        return request.initiate()

    def push(self):
        request=SAIARequestWriteOutputs(self.server.link)
        request.setup(self, maxcount=96)
        return request.initiate()


class SAIAItemRegister(SAIAAnalogItem):
    def onInit(self):
        pass

    def pull(self):
        request=SAIARequestReadRegisters(self.server.link)
        request.setup(self, maxcount=32)
        return request.initiate()

    def push(self):
        request=SAIARequestWriteRegisters(self.server.link)
        request.setup(self, maxcount=32)
        return request.initiate()

    @property
    def tag(self):
        try:
            return self.server.symbols.register(self.index).tag
        except:
            pass


class SAIABooleanItems(SAIAItems):
    pass


class SAIAFlags(SAIABooleanItems):
    def __init__(self, memory, maxsize=65535):
        super(SAIAFlags, self).__init__(memory, SAIAItemFlag, maxsize)

    def resolveIndex(self, key):
        try:
            if isinstance(key, SAIASymbol) and key.isFlag():
                return key.index
            return self.server.symbols.flag(key).index
        except:
            pass

    @property
    def symbols(self):
        return self.server.symbols.flags


class SAIAInputs(SAIABooleanItems):
    def __init__(self, memory, maxsize=65535):
        super(SAIAInputs, self).__init__(memory, SAIAItemInput, maxsize)
        self.setReadOnly()


class SAIAOutputs(SAIABooleanItems):
    def __init__(self, memory, maxsize=65535):
        super(SAIAOutputs, self).__init__(memory, SAIAItemOutput, maxsize)


class SAIAAnalogItems(SAIAItems):
    pass


class SAIARegisters(SAIAAnalogItems):
    def __init__(self, memory, maxsize=65535):
        super(SAIARegisters, self).__init__(memory, SAIAItemRegister, maxsize)

    def resolveIndex(self, key):
        try:
            if isinstance(key, SAIASymbol) and key.isRegister():
                return key.index
            return self.server.symbols.register(key).index
        except:
            pass

    @property
    def symbols(self):
        return self.server.symbols.registers


class SAIAMemory(object):
    def __init__(self, server, localNodeMode=False, enableOnTheFlyItemCreation=True):
        assert server.__class__.__name__=='SAIAServer'
        self._server=server
        self._localNodeMode=localNodeMode
        self._enableOnTheFlyItemCreation=enableOnTheFlyItemCreation
        self._inputs=SAIAInputs(self)
        self._outputs=SAIAOutputs(self)
        self._flags=SAIAFlags(self)
        self._registers=SAIARegisters(self)
        self._queuePendingPull=SAIAItemQueue()
        self._queuePendingPriorityPull=SAIAItemQueue()
        self._queuePendingPush=SAIAItemQueue()
        self._readOnly=False

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

    def count(self):
        count=0
        for items in self.items():
            count+=items.count()
        return count

    def setReadOnly(self, state=True):
        self._readOnly=state

    def isReadOnly(self):
        if self._readOnly:
            return True

    def enableOnTheFlyItemCreation(self, state=True):
        self._enableOnTheFlyItemCreation=state

    def disableOnTheFlyItemCreation(self):
        self.enableOnTheFlyItemCreation(False)

    def isOnTheFlyItemCreationEnabled(self):
        if self._enableOnTheFlyItemCreation:
            return True

    def items(self):
        return (self._inputs, self._outputs, self._flags, self._registers)

    def isLocalNodeMode(self):
        return self._localNodeMode

    def refresh(self):
        for items in self.items():
            try:
                items.refresh()
            except:
                pass

    def getNextPendingPush(self):
        try:
            count=32
            while count>0:
                item=self._queuePendingPush.get(False)
                if item.isPendingPushRequest():
                    item.clearPush()
                    return item
                count-=1
        except:
            pass

    def getNextPendingPull(self):
        count=32
        try:
            while count>0:
                item=self._queuePendingPriorityPull.get(False)
                if item.isPendingPullRequest():
                    item.clearPull()
                    return item
                count-=1
        except:
            pass

        try:
            while count>0:
                item=self._queuePendingPull.get(False)
                if item.isPendingPullRequest():
                    item.clearPull()
                    return item
                count-=1
        except:
            pass

    def manager(self):
        activity=False
        try:
            for items in self.items():
                items.manager()
        except:
            self.logger.exception('items:manager')

        if self.server.link.isIdle():
            item=self.getNextPendingPush()
            if item:
                item.push()
                activity=True

            item=self.getNextPendingPull()
            if item:
                item.pull()
                activity=True

        if activity:
            return True

    def dump(self):
        for items in self.items():
            if items:
                items.dump()

    def __repr__(self):
        return '<%s(%d items, queues %dR:%dR!:%dW)>' % (self.__class__.__name__,
            self.count(),
            self._queuePendingPull.qsize(),
            self._queuePendingPriorityPull.qsize(),
            self._queuePendingPush.qsize())


if __name__ == "__main__":
    pass
