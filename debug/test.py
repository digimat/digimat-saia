from digimat.saia import SAIANode

node=SAIANode()
# node.memory.disableOnTheFlyItemCreation()
r=node.registers[0]

# server=node.registerServer('127.0.0.1')
# r=server.registers[0]
# r.value=5.0


node.stop()
node.start()

while node.isRunning():
    try:
        node.dump()
        print "value", r.value
        print "float32", r.float32
        print "ffp", r.ffp
        print
        node.sleep(2.0)
    except:
        break

# node.stop()
