from digimat.saia import SAIANode

node=SAIANode(250)
node.setMapFileStoragePath('~/Dropbox/python/digimat-saia/debug')

# node.servers.declareRange('192.168.0.48', count=500)

server1=node.servers.declare('192.168.0.48')
server2=node.servers.declare('192.168.0.49')

f1=server1.flags[2010]
f2=server2.flags[2010]

# server1.flags.declareRange(0, 1000)
# server2.flags.declareRange(0, 1000)

# r=server.registers[15]
# r.float32=56.4

# for n in range(1024):
    # server.registers[n]

while node.isRunning():
    try:
        # node.dump()
        node.sleep(3.0)
        # f1.toggle()
        # f2.toggle()
    except:
        break
