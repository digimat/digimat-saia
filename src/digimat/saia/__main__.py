from __future__ import print_function  # Python 2/3 compatibility
from digimat.saia import SAIANode


print('Starting digimat.saia demo node...')
node=SAIANode()

print('SAIA Node is now running (address %d).' % node.server.lid)
while node.isRunning():
    try:
        node.sleep(3.0)
        node.dump()
    except:
        break

print('SAIA Node halted.')
