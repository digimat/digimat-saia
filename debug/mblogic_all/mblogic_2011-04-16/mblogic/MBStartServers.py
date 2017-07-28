##############################################################################
# Project: 	MBLogic
# Module: 	MBStartServers.py
# Purpose: 	Start the various configured servers.
# Language:	Python 2.5
# Date:		19-Mar-2008.
# Ver.:		06-Dec-2010.
# Copyright:	2008 - 2010 - Michael Griffin       <m.os.griffin@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
# Important:	WHEN EDITING THIS FILE, USE TABS TO INDENT - NOT SPACES!
##############################################################################

"""
This is used to start the various configured servers. Each server type has a
defined function which contains the start up logic.

This code was originally located in mbmain.py, but was moved to a separate 
file as the number of server types increased. 
"""
##############################################################################
import sys

from twisted.internet import reactor
from twisted.web import static, server
from twisted.internet.error import CannotListenError
from twisted.spread import pb

import MBServer
import MBWebService
import HMIServer
import HMIData
import StatusServer
import GenServer

############################################################
# Messages for printing to the console.
_Msgs = {
	'startmbtcpserver' : 'Starting ModbusTCP server...',
	'startrestserver' : 'Starting REST web service...',
	'starthmiserver' : 'Starting HMI web service...',
	'startreshmiserver' : 'Starting restricted HMI web service...',
	'starterpserver' : 'Starting ERP web service...',
	'starthelpserver' : 'Starting help system web server...',
	'startstatusserver' : 'Starting system status web server...',
	'startgenericserver' : 'Starting server for generic clients...',
	'listenmsg' : """\n\tFatal Error - cannot listen on port %s.
\tThis port may already be in use by another program.\n\n"""
}


############################################################
def ModbusTCP(ServerInstance):
	"""Modbus TCP server protocol.
	"""
	print(_Msgs['startmbtcpserver'])
	# Add a reference to the config data to allow status tracking.
	# This lets us track things like connection counts.
	MBServer.ModbusServer.SetStatusInfo(ServerInstance)
	# Start up the server.
	try:
		reactor.listenTCP(ServerInstance.GetHostInfo(), MBServer.ModbusServerFactory())
	except CannotListenError:
		# If we can't use this port, then exit.
		print(_Msgs['listenmsg'] % ServerInstance.GetHostInfo())
		sys.exit()


############################################################
def MBRest(ServerInstance):
	"""MBRest protocol. Modbus-like REST web service.
	"""
	print(_Msgs['startrestserver'])
	# Add a reference to the config data to allow status tracking.
	# This lets us track things like connection counts.
	MBWebService.ReportTracker.SetStatusInfo(ServerInstance)
	# Create the web service.
	RestRoot = MBWebService.MBWebRestService()
	RestSite = server.Site(RestRoot)
	# Start up the web service.
	try:
		reactor.listenTCP(ServerInstance.GetHostInfo(), RestSite)
	except CannotListenError:
		# If we can't use this port, then exit.
		print(_Msgs['listenmsg'] % ServerInstance.GetHostInfo())
		sys.exit()


############################################################
def MBHMI(ServerInstance):
	"""Main HMI protocol. HMI web service.
	"""
	print(_Msgs['starthmiserver'])
	# Add a reference to the config data to allow status tracking.
	# This lets us track things like connection counts.
	HMIData.HMIStatus.SetStatusInfo(ServerInstance)
	# Initialise the messaging routines.
	HMIData.Msg.MsgInit()
	# Start up the web service.
	HMIRoot = HMIServer.MBHMIService()
	HMISite = server.Site(HMIRoot)
	try:
		reactor.listenTCP(ServerInstance.GetHostInfo(), HMISite)
	except CannotListenError:
		# If we can't use this port, then exit.
		print(_Msgs['listenmsg'] % ServerInstance.GetHostInfo())
		sys.exit()


############################################################
def MBRestrictedHMI(ServerInstance):
	"""HMI protocol - restricted read-only version. HMI web service.
	"""
	print(_Msgs['startreshmiserver'])
	# Add a reference to the config data to allow status tracking.
	# This lets us track things like connection counts.
	HMIData.RHMIStatus.SetStatusInfo(ServerInstance)
	# Start up the web service.
	ServerRoot = HMIServer.MBHMIRestrictedService()
	ServerSite = server.Site(ServerRoot)
	try:
		reactor.listenTCP(ServerInstance.GetHostInfo(), ServerSite)
	except CannotListenError:
		# If we can't use this port, then exit.
		print(_Msgs['listenmsg'] % ServerInstance.GetHostInfo())
		sys.exit()


############################################################
def MBERP(ServerInstance):
	"""HMI protocol as an ERP protocol. HMI web service.
	"""
	print(_Msgs['starterpserver'])
	# Add a reference to the config data to allow status tracking.
	# This lets us track things like connection counts.
	HMIData.ERPStatus.SetStatusInfo(ServerInstance)
	# Start up the web service.
	ServerRoot = HMIServer.MBHMIERPService()
	ServerSite = server.Site(ServerRoot)
	try:
		reactor.listenTCP(ServerInstance.GetHostInfo(), ServerSite)
	except CannotListenError:
		# If we can't use this port, then exit.
		print(_Msgs['listenmsg'] % ServerInstance.GetHostInfo())
		sys.exit()




############################################################
def UserHelpServer(ServerInstance):
	"""User help server. This serves static web pages created by the user.
	"""
	print(_Msgs['starthelpserver'])
	# Set the root directory for the help system files.
	HelpRoot = static.File('mbhelppages')
	# Start up the server.
	try:
		reactor.listenTCP(ServerInstance.GetHostInfo(), server.Site(HelpRoot))
	except CannotListenError:
		# If we can't use this port, then exit.
		print(_Msgs['listenmsg'] % ServerInstance.GetHostInfo())
		sys.exit()


############################################################
def Status(ServerInstance):
	"""System status web server. The information this server uses is set
		directly from the relevant sub-systems.
	"""
	print(_Msgs['startstatusserver'])
	# Add a reference to the config data to allow status tracking.
	# This lets us track things like connection counts.
	StatusServer.ReportTracker.SetStatusInfo(ServerInstance)
	# Create a server.
	StatusRoot = StatusServer.MBWebStatus()
	StatusSite = server.Site(StatusRoot)
	try:
		reactor.listenTCP(ServerInstance.GetHostInfo(), StatusSite)
	except CannotListenError:
		# If we can't use this port, then exit.
		print(_Msgs['listenmsg'] % ServerInstance.GetHostInfo())
		sys.exit()


############################################################
def Generic(ServerInstance, GenClientList):
	"""Server protocol for handling generic clients.
	"""
	print(_Msgs['startgenericserver'])
	# Add a reference to the config data to allow status tracking.
	# This lets us track things like connection counts.
	GenServer.GenericServer.SetStatusInfo(ServerInstance)
	# This sets the client parameters.
	GenServer.GenericServer.SetClientParams(GenClientList)
	# Start up the server.
	try:
		reactor.listenTCP(ServerInstance.GetHostInfo(), pb.PBServerFactory(GenServer.GenericServer))
	except CannotListenError:
		# If we can't use this port, then exit.
		print(_Msgs['listenmsg'] % ServerInstance.GetHostInfo())
		sys.exit()
	# Start the generic clients (after a delay).
	GenServer.GenericServer.ClientStartWithDelay(1.5)

##############################################################################

