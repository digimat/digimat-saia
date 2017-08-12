import time
from digimat.saia import SAIANode

node=SAIANode()
# node.memory.disableOnTheFlyItemCreation()

server=node.registerServer('127.0.0.1')
r=server.registers[0]

r.value=5.0


node.start()

while True:
    try:
        # node.dump()
        print r
        print "value", r.value
        print "float32", r.float32
        print "ffp", r.ffp
        print

        time.sleep(2.0)
    except:
        break

node.stop()
