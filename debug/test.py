import time
from digimat.saia import SAIANode

node=SAIANode()
node.memory.disableOnTheFlyItemCreation()

node.flags.declareRange(5, 3, 1)
# s=node.registerServer('127.0.0.1')
# s=node.registerServer('192.168.0.45')

node.start()

while True:
    try:
        time.sleep(1.0)
        node.server.dump()
    except:
        break

node.stop()
