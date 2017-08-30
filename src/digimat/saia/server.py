import time
import struct
import ipaddress
from datetime import datetime

from threading import RLock

from .request import SAIARequestReadStationNumber

from .transfer import SAIATransferQueue
from .transfer import SAIATransferReadDeviceInformation
from .transfer import SAIATransferDiscoverNodes

from .request import SAIASBusCRC
from .memory import SAIAMemory
from .symbol import SAIASymbols


class SAIALink(object):

    COMMSTATE_IDLE = 0
    COMMSTATE_PENDINGREQUEST = 1
    COMMSTATE_WAITRESPONSE = 2
    COMMSTATE_ERROR = 10
    COMMSTATE_SUCCESS = 11

    def __init__(self, server, delayXmitInhibit=0):
        assert server.__class__.__name__=='SAIAServer'
        self._server=server
        self._request=None
        self._state=None
        self._timeout=0
        self._timeoutXmitInhibit=0
        self._delayXmitInhibit=delayXmitInhibit
        self._timeoutWatchdog=time.time()+60
        self._alive=False
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
            self._request.stop(success)
        except:
            pass
        self._request=None
        self.setState(SAIALink.COMMSTATE_IDLE)

    def isAlive(self):
        if self._alive:
            return True

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

    def data2strhex(self, data):
        return ' '.join(x.encode('hex') for x in data)

    def manager(self):
        try:
            if self._state==SAIALink.COMMSTATE_IDLE:
                if self.isAlive() and time.time()>=self._timeoutWatchdog:
                    self._alive=False
                    self.logger.error('%s:link dead!' % self.server)
                return

            elif self._state==SAIALink.COMMSTATE_PENDINGREQUEST:
                if time.time()<self._timeoutXmitInhibit:
                    return

                if self._request.consumeRetry():
                    data=self._request.data
                    host=self.server.host
                    if self._request._broadcast:
                        host='255.255.255.255'
                    self.logger.debug('%s<--%s' % (host, self._request))

                    if self.server.node.sendMessageToHost(data, host):
                        self._timeoutXmitInhibit=time.time()+self._delayXmitInhibit
                        if self._request._broadcast:
                            self.setState(SAIALink.COMMSTATE_SUCCESS)
                        else:
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
                self._request.start()
                self.setState(SAIALink.COMMSTATE_PENDINGREQUEST)
                return True

    def readStationNumber(self):
        if self.isIdle():
            request=SAIARequestReadStationNumber(self)
            return self.initiate(request)

    # def readSystemInformation(self, block=0):
        # if self.isIdle():
            # request=SAIARequestReadSystemInformation(self)
            # request.setup(block)
            # return self.initiate(request)

    def decodeMessage(self, data):
        try:
            size=len(data)
            if size>=11 and size<=255:
                sizePayload=size-11
                if sizePayload>0:
                    (msize, mversion, mtype, msequence, tattribute,
                        payload, mcrc)=struct.unpack('>LBBHB %ds H' % sizePayload, data)
                    if mcrc==SAIASBusCRC(data[0:-2]):
                        return (tattribute, msequence, payload)

            self.logger.error('bad size/crc')
        except:
            self.logger.exception('decodeMessage')

    def onMessage(self, mtype, mseq, payload):
        try:
            self._timeoutWatchdog=time.time()+120.0
            if mtype==0:    # Request
                # must be intercepted at higher level
                pass

            elif mtype==1:  # Response
                if self.isWaitingResponse():
                    if self._request.validateMessage(mseq, payload):
                        try:
                            self.logger.debug('%s-->%s:processResponse(%d bytes)' % (self.server.host, self._request, len(payload)))
                            result=self._request.processResponse(payload)
                            self.reset(result)
                        except:
                            self.logger.exception('processResponse')

            elif mtype==2:  # Ack/Nak
                if self.isWaitingResponse():
                    if self._request.validateMessage(mseq):
                        try:
                            (code,)=struct.unpack('>B', payload[0])
                            if code==0:
                                self.logger.debug('%s-->ACK(mseq=%d)' % (self.server.host, mseq))
                                self.reset(True)
                            else:
                                self.logger.error('%s-->ACK(mseq=%d, code=%d)' % (self.server.host, mseq, code))
                                self.reset(False)
                        except:
                            self.logger.exception('processAck/Nak')

        except:
            self.logger.exception('onMessage')


class SAIAServer(object):

    UDP_DEFAULT_PORT = 5050

    def __init__(self, node, host, lid=None, localNodeMode=False, mapfile=None, nodeDiscoverPeriod=0):
        assert node.__class__.__name__=='SAIANode'
        self._lock=RLock()
        self._node=node
        self._host=host
        self._lid=lid
        self._memory=SAIAMemory(self, localNodeMode)
        self._link=SAIALink(self)
        self._deviceInfo={}
        self._transfers=SAIATransferQueue(self)
        self.setLid(lid)
        self._symbols=SAIASymbols()
        self.loadSymbols(mapfile)
        if not self.isLocalNodeMode():
            self.submitTransferReadDeviceInformation()
        else:
            self._periodNodeDiscover=0
            self._timeoutNodeDiscover=0
            if self.node.isInteractiveMode() or nodeDiscoverPeriod>0:
                period=max(30, nodeDiscoverPeriod)
                self.enableNodeDiscover(period=period)

    def isLidValid(self, lid):
        try:
            if lid>=0 and lid<255:
                return True
        except:
            pass

    @property
    def lid(self):
        with self._lock:
            if self.isLidValid(self._lid):
                return self._lid

        # broadcast (don't care)<Del> address
        return 255

    @property
    def address(self):
        return self.lid

    def isLocalNodeMode(self):
        return self._memory.isLocalNodeMode()

    def enableNodeDiscover(self, period=60):
        if self.isLocalNodeMode() and period>0:
            self._timeoutNodeDiscover=0
            self._periodNodeDiscover=period
            self.logger.info('Network node scanning process enabled (%ds) for server %s' % (period, self.host))

    def setLid(self, lid):
        try:
            with self._lock:
                if self.isLidValid(lid):
                    self.node.servers.assignServerLid(self, lid)
        except:
            pass

    def loadSymbols(self, mapfile=None):
        try:
            if not mapfile:
                mapfile=self.getDeviceInfo('DeviceName')+'.map'

            self._symbols.load(mapfile)
            self.logger.info('%d symbols loaded for server %s' % (self._symbols.count(), self.host))
            if self.node.isInteractiveMode():
                self.logger.info('Interactive mode : dynamic mount symbols on server.symbols object')
                self._symbols.mount()
        except:
            pass

    @property
    def symbols(self):
        return self._symbols

    def setDeviceInfo(self, key, value):
        try:
            if key and value:
                with self._lock:
                    self._deviceInfo[key.lower()]=value
                    self.logger.info('server(%s)->%s=%s' % (self._host, key, value))
                    if key.lower()=='devicename':
                        self.node.servers.mount(self)
        except:
            pass

    def getDeviceInfo(self, key):
        try:
            with self._lock:
                return self._deviceInfo[key.lower()]
        except:
            pass

    def getDeviceDateTimeInfo(self, key):
        stamp=self.getDeviceInfo(key)
        try:
            return datetime.strptime(stamp, '%Y/%m/%d %H:%M:%S')
        except:
            pass

    @property
    def deviceName(self):
        return self.getDeviceInfo('deviceName')

    @property
    def deviceType(self):
        return self.getDeviceInfo('pcdType')

    @property
    def buildTime(self):
        return self.getDeviceDateTimeInfo('buildDataTime')

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

    def isAlive(self):
        return self.link.isAlive()

    def onMessage(self, mtype, mseq, payload):
        return self.link.onMessage(mtype, mseq, payload)

    def refresh(self):
        self.memory.refresh()

    def manager(self):
        activity=False
        if self._link.manager():
            activity=True

        if self.isLocalNodeMode():
            if self._transfers.manager():
                activity=True

            if self._memory.manager():
                activity=True

            if self._periodNodeDiscover>0 and time.time()>self._timeoutNodeDiscover:
                self.submitTransferDiscoverNodes()
                self._timeoutNodeDiscover=time.time()+self._periodNodeDiscover
        else:
            if self.isLidValid(self._lid):
                if self._transfers.manager():
                    activity=True

                if self._memory.manager():
                    activity=True
            else:
                self.link.readStationNumber()

        if activity:
            # print ">SERVER"
            return True

    def submitTransfer(self, transfer):
        self._transfers.submit(transfer)
        return transfer

    def submitTransferReadDeviceInformation(self):
        return self.submitTransfer(SAIATransferReadDeviceInformation(self))

    def submitTransferDiscoverNodes(self):
        return self.submitTransfer(SAIATransferDiscoverNodes(self))

    def __repr__(self):
        return '%s(%d)' % (self.host, self.lid)

    def dump(self):
        self.memory.dump()


class SAIAServers(object):
    def __init__(self, node):
        assert node.__class__.__name__=='SAIANode'
        self._node=node
        self._servers=[]
        self._indexByLid={}
        self._indexByHost={}
        self._currentServer=0

    @property
    def node(self):
        return self._node

    @property
    def logger(self):
        return self.node.logger

    def getFromHost(self, host):
        try:
            return self._indexByHost[host]
        except:
            pass

    def getFromLid(self, lid):
        try:
            return self._indexByLid[int(lid)]
        except:
            pass

    def get(self, key):
        server=self.getFromHost(key)
        if server is None:
            server=self.getFromLid(key)
        return server

    def __getitem__(self, key):
        return self.get(key)

    def all(self):
        return self._servers

    def declare(self, host, lid=None, port=SAIAServer.UDP_DEFAULT_PORT, mapfile=None):
        server=self.getFromHost(host)
        if server is None and not self.node.isIpAddressLocal(host):
            server=SAIAServer(self.node, host, lid, mapfile=mapfile)
            self._servers.append(server)
            self._indexByHost[host]=server
            self.logger.info('server(%s:%d:%s) declared' % (host, port, lid))
        return server

    def declareRange(self, ip, count, lid=None, port=SAIAServer.UDP_DEFAULT_PORT):
        servers=[]
        try:
            ip=ipaddress.ip_address(unicode(ip))
            for n in range(count):
                server=self.declare(str(ip), lid=lid, port=port)
                servers.append(server)
                ip+=1
                if lid:
                    lid+=1
        except:
            self.logger.exception('declareRange')
        return servers

    def manager(self):
        activity=False

        if self._servers:
            count=min(8, len(self._servers))
            while count>0:
                count-=1
                try:
                    server=self._servers[self._currentServer]
                    self._currentServer+=1

                    try:
                        if server.manager():
                            activity=True
                    except:
                        self.logger.exception('manager')
                except:
                    self._currentServer=0
                    break

        if activity:
            return True

    def count(self):
        return len(self._servers)

    def refresh(self):
        for server in self._servers:
            server.refresh()

    def dump(self):
        for server in self._servers:
            server.dump()

    def assignServerLid(self, server, lid):
        s=self.getFromLid(lid)
        if s and s!=server:
            self.logger.error('duplicate server lid %d' % lid)
            return

        try:
            del self._indexByLid[server.lid]
        except:
            pass

        try:
            if lid>=0 and lid<255:
                self._indexByLid[lid]=server
                server._lid=lid
                self.logger.info('Assign server %s with lid %d' % (server.host, lid))
                return True
        except:
            pass

    def mount(self, server):
        """
        create object variable (.deviceName) for better interactive usage with interpreter autocompletion
        """
        try:
            name=server.deviceName
            if name:
                name=name.strip()
                # TODO: name to variable cleaning
                name=name.replace(' ', '_')

                if not hasattr(self, name):
                    setattr(self, name, server)
                    self.logger.info('Server %s mounted as servers.%s object' % (server.host, name))
        except:
            pass


if __name__ == "__main__":
    pass
