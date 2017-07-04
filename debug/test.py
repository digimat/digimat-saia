import time
from digimat.saia import SAIAClient

c=SAIAClient()

for a in range(1,200):
    s=c.registerServer(a, '213.200.228.190')
    s.memory.flags[1]

c.start()
time.sleep(30.0)
c.stop()
