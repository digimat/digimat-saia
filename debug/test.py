import time
from digimat.saia import SAIAClient

c=SAIAClient()

s=c.registerServer('192.168.0.45', 10)
f=s.memory.flags[1]

s.dump()


c.start()
time.sleep(20.0)
c.stop()
