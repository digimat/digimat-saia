from digimat.saia import SAIANode
import time

node=SAIANode(250, port=5051)
f=node.flags[0]
f.value=1

while True:
    try:
        print node.dump()
        time.sleep(1.0)
    except:
        break

node.stop()



