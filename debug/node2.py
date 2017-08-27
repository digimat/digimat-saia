from digimat.saia import SAIANode

node=SAIANode(250)

server=node.servers.declare('192.168.0.252')

server.registers.declareRange(0, 600)

while node.isRunning():
    try:
        node.sleep(3.0)
        node.dump()
    except:
        break
