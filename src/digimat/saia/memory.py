
from Queue import Queue

from .items import SAIABooleanItem
from .items import SAIAAnalogItem
from .items import SAIAItems


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
        count=self.optimizePullCount(32)
        return self.server.link.readFlags(self.index, count)

    def push(self):
        # TODO: associer items avec la request
        xxxx
        count=self.optimizePushCount(32)
        values=[]
        index0=self.index
        items=self.parents
        for n in range(count):
            item=items[index0+n]
            print item
            values.append(item.pushValue)

        print "->WRITEFLAGS", values
        return self.server.link.writeFlags(self.index, values)


class SAIAItemInput(SAIABooleanItem):
    def onInit(self):
        self.setReadOnly()

    def pull(self):
        count=self.optimizePullCount(32)
        return self.server.link.readInputs(self.index, count)


class SAIAItemOutput(SAIABooleanItem):
    def onInit(self):
        pass

    def pull(self):
        count=self.optimizePullCount(32)
        return self.server.link.readOutputs(self.index, count)

    def push(self):
        return self.server.link.writeOutputs(self.index, self.pushValue)


class SAIAItemRegister(SAIAAnalogItem):
    def onInit(self):
        pass

    def pull(self):
        count=self.optimizePullCount(16)
        return self.server.link.readRegisters(self.index, count)

    def push(self):
        return self.server.link.writeRegisters(self.index, self.pushValue)


class SAIABooleanItems(SAIAItems):
    pass


class SAIAFlags(SAIABooleanItems):
    def __init__(self, memory, maxsize=65535):
        super(SAIAFlags, self).__init__(memory, SAIAItemFlag, maxsize)


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


class SAIAMemory(object):
    def __init__(self, server, localNodeMode=False, enableOnTheFlyItemCreation=True):
        self._server=server
        self._localNodeMode=localNodeMode
        self._enableOnTheFlyItemCreation=enableOnTheFlyItemCreation
        self._inputs=SAIAInputs(self)
        self._outputs=SAIAOutputs(self)
        self._flags=SAIAFlags(self)
        self._registers=SAIARegisters(self)
        self._queuePendingPull=SAIAItemQueue()
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
            item=self._queuePendingPush.get(False)
            item.clearPush()
            return item
        except:
            pass

    def getNextPendingPull(self):
        try:
            while True:
                item=self._queuePendingPull.get(False)
                if item.isPendingPullRequest():
                    item.clearPull()
                    return item
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
            # print ">MEMORY"
            return True

    def dump(self):
        for items in self.items():
            if items:
                items.dump()


if __name__ == "__main__":
    pass
