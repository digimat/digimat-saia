from Queue import Queue

from .items import SAIABooleanItem
from .items import SAIAAnalogItem
from .items import SAIAItems


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


class SAIAItemFlag(SAIABooleanItem):
    def onInit(self):
        pass

    def pull(self):
        return self.server.link.readFlags(self.index, 1)

    def push(self):
        return self.server.link.writeFlags(self.index, self.pushValue)


class SAIAItemInput(SAIABooleanItem):
    def onInit(self):
        self.setReadOnly()

    def pull(self):
        return self.server.link.readInputs(self.index, 1)


class SAIAItemOutput(SAIABooleanItem):
    def onInit(self):
        pass

    def pull(self):
        return self.server.link.readOutputs(self.index, 1)

    def push(self):
        return self.server.link.writeOutputs(self.index, self.pushvalue)


class SAIARegister(SAIAAnalogItem):
    def onInit(self):
        pass

    def pull(self):
        return self.server.link.readRegisters(self.index, 1)

    def push(self):
        return self.server.link.writeRegisters(self.index, self.pushvalue)


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
    def __init__(self, server, localNodeMode=False, enableOnTheFlyItemCreation=True):
        self._server=server
        self._localNodeMode=localNodeMode
        self._enableOnTheFlyItemCreation=enableOnTheFlyItemCreation
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


if __name__ == "__main__":
    pass
