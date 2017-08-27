from digimat.saia import SAIANode

node=SAIANode()
server=node.servers.declare('192.168.0.48', mapfile='./map/pg5.map')
symbols=server.symbols

symbol=symbols.flag('s.com.ipchannel.xbsy')
server.flags.declare(symbol)


node.stop()




