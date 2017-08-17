# import struct
import time

from threading import RLock
from threading import Event


from .formaters import SAIAValueFormaterFloat32
from .formaters import SAIAValueFormaterSwappedFloat32
from .formaters import SAIAValueFormaterInteger10
from .formaters import SAIAValueFormaterFFP


class SAIAItem(object):
    def __init__(self, parent, index, value=0, delayRefresh=None, readOnly=False):
        self._parent=parent
        self._index=index
        self._value=self.validateValue(value)
        self._pushValue=None
        self._stamp=0
        self._readOnly=readOnly
        self._delayRefresh=delayRefresh
        self._eventPush=Event()
        self._eventPull=Event()
        self.onInit()
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
    def memory(self):
        return self.server.memory

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
        self._readOnly=state

    def isReadOnly(self):
        if self._readOnly:
            return True

    def signalPush(self, value):
        if self.parent.isLocalNodeMode():
            self.setValue(value)
        else:
            if not self._eventPush.isSet():
                self._eventPush.set()
                self._parent.signalPush(self)
            with self._parent._lock:
                self._pushValue=value

    def clearPush(self):
        self._eventPush.clear()

    def signalPull(self):
        if not self.parent.isLocalNodeMode():
            if not self._eventPull.isSet():
                self._eventPull.set()
                self._parent.signalPull(self)

    def optimizePullCount(self, maxcount=8):
        """
        Try to increase item read count until maximum allowed (maxcount)
        Only consecutive items are taken in account (no whole allowed)
        """

        try:
            count=1
            items=self.parent

            index=self.index+1
            while count<maxcount:
                item=items.item(index)
                if not item:
                    break
                index+=1
                count+=1

                # Cancel pull request as it will be requested here
                # We don't cancel the pull queue. Theses items will simply
                # be skiped by the pull manager
                item.clearPull()

            return count
        except:
            pass
        return 1

    def clearPull(self):
        self._eventPull.clear()

    def isPendingPullRequest(self):
        if self._eventPull.isSet():
            return True

    def setValue(self, value, force=False):
        # we must be able to setValue from a readItemResponse
        if value is not None and force or not self.isReadOnly():
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
            if not self.isReadOnly():
                value=self.validateValue(value)
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

    def refresh(self):
        self.signalPull()

    def clear(self):
        self.value=0

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

    def set(self):
        self.on()

    def clear(self):
        self.off()

    def toggle(self):
        self.value=not self.value

    def strValue(self):
        if self.value:
            return 'ON'
        return 'OFF'


class SAIAAnalogItem(SAIAItem):
    def validateValue(self, value):
        try:
            if type(value)==float:
                formater=SAIAValueFormaterFFP()
                return formater.encode(value)

            return int(value)
        except:
            pass
        return value

    @property
    def float32(self):
        formater=SAIAValueFormaterFloat32()
        return formater.decode(self.getValue())

    @float32.setter
    def float32(self, value):
        formater=SAIAValueFormaterFloat32()
        self.setValue(formater.encode(value))

    @property
    def sfloat32(self):
        formater=SAIAValueFormaterSwappedFloat32()
        return formater.decode(self.getValue())

    @sfloat32.setter
    def sfloat32(self, value):
        formater=SAIAValueFormaterSwappedFloat32()
        self.setValue(formater.encode(value))

    @property
    def int10(self):
        formater=SAIAValueFormaterInteger10()
        return formater.decode(self.getValue())

    @int10.setter
    def int10(self, value):
        formater=SAIAValueFormaterInteger10()
        self.setValue(formater.encode(value))

    @property
    def ffp(self):
        formater=SAIAValueFormaterFFP()
        return formater.decode(self.getValue())

    @ffp.setter
    def ffp(self, value):
        formater=SAIAValueFormaterFFP()
        self.setValue(formater.encode(value))

    @property
    def float(self):
        formater=SAIAValueFormaterFFP()
        return formater.decode(self.getValue())

    @float.setter
    def float(self, value):
        formater=SAIAValueFormaterFFP()
        self.setValue(formater.encode(value))

    def strValue(self):
        if self.value is not None:
            return '%d' % self.value
        return '<null>'


class SAIAItems(object):
    def __init__(self, memory, itemType, maxsize, readOnly=False):
        self._memory=memory
        self._localNodeMode=memory.isLocalNodeMode()
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

    def isLocalNodeMode(self):
        return self._localNodeMode

    def setReadOnly(self, state=True):
        self._readOnly=state

    def isReadOnly(self):
        if self._readOnly:
            return True

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

    def isIndexValid(self, index):
        if self.validateIndex(index) is not None:
            return True

    def item(self, index):
        try:
            with self._lock:
                return self._indexItem[self.validateIndex(index)]
        except:
            pass

    def isItemDeclared(self, index):
        if self.item(index):
            return True

    def __getitem__(self, index):
        item=self.item(index)
        if item:
            return item
        if self.memory.isOnTheFlyItemCreationEnabled():
            return self.declare(index)

    def declare(self, index, value=0):
        index=self.validateIndex(index)
        if index is not None:
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

    def declareRange(self, index, count, value=0):
        items=[]
        for n in range(count):
            item=self.declare(index+n, value)
            items.append(item)
        return items

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
        count=min(8, len(self._items))
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

    def clear(self):
        with self._lock:
            for item in self._items:
                item.clear()


if __name__ == "__main__":
    pass
