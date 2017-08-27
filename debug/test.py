from digimat.saia import SAIANode


# class Device(object):
    # def __init__(self, node):
        # self._server=
        # self.onInit()

    # @property
    # def server(self):
        # return self._server

    # def onInit(self):
        # pass




node=SAIANode()
# node.memory.disableOnTheFlyItemCreation()
r=node.registers[0]

# server=node.servers.declare('127.0.0.1')
# r=server.registers[0]
# r.value=5.0




node.stop()
node.start()

while node.isRunning():
    try:
        node.dump()
        node.sleep(2.0)
    except:
        break

# node.stop()
