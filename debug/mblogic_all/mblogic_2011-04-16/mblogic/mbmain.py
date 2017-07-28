#!/usr/bin/python
##############################################################################
# Project: 	MBLogic
# Module: 	MBMain.py
# Purpose: 	Automation Control System.
# Language:	Python 2.5
# Date:		19-Mar-2008.
# File Version:	16-Mar-2011.
# Author:	M. Griffin.
# Copyright:	2008 - 2011 - Michael Griffin       <m.os.griffin@gmail.com>
#
# This file is part of MBLogic.
# MBLogic is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# MBLogic is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with MBLogic. If not, see <http://www.gnu.org/licenses/>.
#
# Important:	WHEN EDITING THIS FILE, USE TABS TO INDENT - NOT SPACES!
##############################################################################


############################################################

# These should be in the standard Python library.
import signal
import time
import sys


_twistfailmsg = """\n\nFatal Error - Could not import twisted libraries. 
Check to see that you have twisted installed.\n
"""
_twistepollmsg = """\nOptional epoll reactor not available.
"""

# Check to see if twisted is installed. This is an additional library that
# is not part of the standard Python install.
# First we try importing the epoll reactor. This is optional, so if it
# isn't present, we print a message but continue on anyway. The epoll
# reactor option improves performance, but it isn't available on
# some platforms.
try:
	from twisted.internet import epollreactor
	epollreactor.install()
except:
	print(_twistepollmsg)

# Now, we try importing the rest of twisted. If the rest of
# Twisted is not available, we can't continue.
try:
	from twisted.internet import reactor
	from twisted.internet import task
	from twisted.web import static, server
	from twisted.internet.error import CannotListenError
	from twisted.spread import pb
except:
	print(_twistfailmsg)
	sys.exit()


# These are application modules.
from comsconfig import ComsConfig
import MBServer
import MBClient
from sysmon import SysStatus

import MBStartServers
import MBMonitorMem
import PLCRun
from mbplc import PLCComp, PLCIOManage
import GenServer

############################################################

# Messages for printing to the console.
_Msgs = {'shutdown' : 'Shutdown scheduled in %s seconds.',
	'remoteterm' : '\n\tOperator terminated system remotely at %s\n',
	'remoterestart' : '\n\tOperator restarted system remotely at %s\n',
	'keyboardterm' : '\n\tOperator terminated system from keyboard at %s\n',
	'starting' : '\n\nStarting MBLogic.',
	'noservers' : 'No servers configured to start.',
	'unrecognisedprotocol' : 'Unrecognised server protocol type: %s',
	'startmbtcpclient' : 'Starting ModbusTCP clients...',
	'notcpclients' : 'No TCP clients configured to start.',
	'nofaultmonitor' : 'No monitored faults configured.',
	'badsoftlogicio' : 'Bad or missing soft logic IO configuration. Soft logic system will not be started.',
	'startsoftlogic' : 'Soft logic system started.',
	'softlogicerror' : 'Soft logic program errors found. Soft logic system not started.',
	'serverrunning' : '\n\tServer %s running at %s ...\n',
	'systemstopped' : 'System stopped.'
}


############################################################

_SOFTWARENAME = 'MBLogic'
_VERSION = '16-Apr-2011'


# Set the software name and version.
SysStatus.SysStatus.SetSoftwareInfo(_SOFTWARENAME, _VERSION)

# Start time.
StartTime = time.time()
SysStatus.SysStatus.SetStartTime(StartTime)

############################################################

class ShutdownRecord:
	"""This keeps track of the reason for a shutdown."""
	def __init__(self):
		self._RestartReq = False
		self._ShutdownTime = None

	def SetRestart(self):
		self._RestartReq = True
	def IsRestart(self):
		return self._RestartReq

	# The shutdown delay time is done.
	def DelayDone(self):
		if self._ShutdownTime == None:
			self._ShutdownTime = time.time()
			return False
		else:
			return (time.time() - self._ShutdownTime) >= 4.0

ShutdownReason = ShutdownRecord()

# This allows for a delayed shut down.
def ShutDownHandler():
	# Check to see if the generic clients have all stopped yet.
	# If any are still running, we wait and check again later.
	# Once a set delay time has passed however, we give up waiting.
	if ((GenServer.GenClientLanucher.ShutdownMonitor() != 0) and
		(not ShutdownReason.DelayDone())):
		reactor.callLater(0.5, ShutDownHandler)

	else:
		# This forces the termination of any remaining generic clients.
		GenServer.GenClientLanucher.TerminateAll()
		reactor.stop()


# This handles requests to shut down the system.
def ShutDownRequest():
	# This requests all generic clients to shut down.
	GenServer.GenericServer.SetCmdStopAll()
	shutdowndelay = 1.0
	reactor.callLater(shutdowndelay, ShutDownHandler)
	print(_Msgs['shutdown'] % shutdowndelay)


# This is for shut down requests coming via the web interface.
def RemoteShutDownRequest():
	print(_Msgs['remoteterm'] % time.ctime())
	ShutDownRequest()


# This is for restart requests coming via the web interface.
def RemoteRestartRequest():
	print(_Msgs['remoterestart'] % time.ctime())
	ShutdownReason.SetRestart()
	ShutDownRequest()


# Register the shutdown request handler with the user interface.
SysStatus.SysStatus.SetShutDownReq(RemoteShutDownRequest)

# Register the restart request handler with the user interface.
SysStatus.SysStatus.SetRestartReq(RemoteRestartRequest)


# Signal handler to shut down system cleanly.
def SigHandler(signum, frame):
	print(_Msgs['keyboardterm'] % time.ctime())
	ShutDownRequest()


# Initialise the signal handler.
signal.signal(signal.SIGINT, SigHandler)


############################################################

print(_Msgs['starting'])


# Get the server ID name so we can report it.
ServerIDName = ComsConfig.ConfigServer.GetServerIDName()


# Get the list of server configurations.
ServerList = ComsConfig.ConfigServer.GetServerList()

# Get the list of client configurations.
TCPClientList = ComsConfig.ConfigClient.GetTCPClientList()

# Get the list of generic clients.
GenClientList = ComsConfig.ConfigClient.GetGenClientList()

# Get the expanded register map offsets and whether they are enabled for Modbus.
ExpDTParams = ComsConfig.ConfigServer.GetExpDTParams()
ExpDTOffsets = ExpDTParams['mbuidoffset']
ExpDTUIDEnabled = ExpDTParams['mbaddrexp']

# Set the expanded register map options.
MBServer.ModbusServer.SetExpandedDTAddressing(ExpDTOffsets, ExpDTUIDEnabled)

#####


#####


# Start up the servers.
if (len(ServerList) <= 0):
	print(_Msgs['noservers'])

for ServerInstance in ServerList:
	if ServerInstance.ConfigOK():
		ProtocolType = ServerInstance.GetProtocolType().lower()
		# Modbus TCP server.
		if (ProtocolType == 'modbustcp'):
			MBStartServers.ModbusTCP(ServerInstance)

		# Modbus-like REST web service.
		elif (ProtocolType == 'mbrest'):
			MBStartServers.MBRest(ServerInstance)

		# HMI web service.
		elif (ProtocolType == 'mbhmi'):
			MBStartServers.MBHMI(ServerInstance)

		# HMI web service - read-only restricted version.
		elif (ProtocolType == 'rhmi'):
			MBStartServers.MBRestrictedHMI(ServerInstance)

		# HMI web service - ERP version.
		elif (ProtocolType == 'erp'):
			MBStartServers.MBERP(ServerInstance)
			
		# Web based help pages.
		elif (ProtocolType == 'help'):
			MBStartServers.UserHelpServer(ServerInstance)

		# System status web server. 
		elif (ProtocolType == 'status'):
			MBStartServers.Status(ServerInstance)

		# Server for generic clients.
		elif (ProtocolType == 'generic'):
			MBStartServers.Generic(ServerInstance, GenClientList)

		# We don't know what the server type is.
		else:
			print(_Msgs['unrecognisedprotocol'] % ProtocolType)


#####


# Start up the Modbus TCP clients.
if (len(TCPClientList) > 0):
	print(_Msgs['startmbtcpclient'])
	for ClientInstance in TCPClientList:
		# Get the connection information.
		host, port = ClientInstance.GetHostInfo()
		# Start up the client.
		reactor.connectTCP(host, port, MBClient.ModbusClientFactory(ClientInstance))
else:
	print(_Msgs['notcpclients'])

#####

# Get the dictionary of fault monitoring addresses.
FaultResetTable = ComsConfig.ConfigClient.GetFaultResetTable()
# Are there any valid faults configured?
if (len(FaultResetTable) > 0):
	FaultMon = MBMonitorMem.CyclicMemMonitor(65535 - 256, FaultResetTable)
	FaultMonTask = task.LoopingCall(FaultMon.ScanFaultResetCoils)
	FaultMonTask.start(1.0)		# Call cyclically.
else:
	print(_Msgs['nofaultmonitor'])


#####

# PLC Soft Logic System.

# Load and verify the IO configuration.
PLCConfigOK = PLCIOManage.PLCIO.LoadIOConfig()

if not PLCConfigOK:
	print(_Msgs['badsoftlogicio'])


# Give the soft logic system a handle to the Twisted reactor we are using 
# so it schedule it's own timing.
PLCRun.PLCSystem.SetReactor(reactor)
# Start the scanning. The scan framework runs whether or not the actual program does.
PLCRun.PLCSystem.RunPLCScan()

# If the soft logic IO is OK, try to start the PLC program.
if (PLCConfigOK):
	PLCCompileOK = PLCComp.PLCLogic.LoadCompileAndRun()
	if PLCCompileOK:
		print(_Msgs['startsoftlogic'])
	else:
		print(_Msgs['softlogicerror'])



#####

print(_Msgs['serverrunning'] % (ServerIDName, time.ctime(StartTime)))

# Start up servers and clients.
reactor.run()

#####

# System is shut down.
print(_Msgs['systemstopped'])

# Check if this is a restart.
if ShutdownReason.IsRestart():
	sys.exit(119)

#####

