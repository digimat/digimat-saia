from digimat.saia import SAIANode

node=SAIANode(250)


# node.servers.declareRange('192.168.0.48', count=500)

server=node.servers.declare('192.168.0.48')

f=server.flags[2010]

# r=server.registers[15]
# r.float32=56.4

for n in range(512):
    server.registers[n]

while node.isRunning():
    try:
        # node.dump()
        node.sleep(1.0)
        f.toggle()
        print server.deviceName
        print server.deviceType
        print server.buildTime
    except:
        break
