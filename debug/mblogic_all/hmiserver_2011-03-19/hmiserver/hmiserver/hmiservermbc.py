#!/usr/bin/python
##############################################################################
# Project: 	HMIServer
# Module: 	hmiserver.py
# Purpose: 	Web server for MBServer HMI protocol.
# Language:	Python 2.5
# Date:		20-Mar-2008.
# Ver:		03-Dec-2010.
# Author:	M. Griffin.
# Copyright:	2008 - 2010 - Michael Griffin       <m.os.griffin@gmail.com>
#
# This file is part of HMIServer.
# HMIServer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# HMIServer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with HMIServer. If not, see <http://www.gnu.org/licenses/>.
#
# Important:	WHEN EDITING THIS FILE, USE TABS TO INDENT - NOT SPACES!
##############################################################################

# Name of this program.
_SOFTNAME = 'HMIServerMBC'

# Version of this server.
_VERSION = '17-Mar-2011'

_HelpStr = """
%s, %s

This program provides a simple combination HMI http server and field device
client (master). The field device must use a supported protocol such
as Modbus/TCP. Requests from a web browser are translated into the field
device protocol commands and passed through to a remote server. Replies 
from the remote server are in turn translated and passed back to the web browser.

This server can be started with a variety of command line parameters. 
Any parameters which are not specified will use their default values. 
These include:

-p Port number of HMI web server. The default is 8082.
-h Name or address of remote server. The default is localhost.
-r Port number of remote server. The default is 502.
-u Unit ID of remote server. The default is 1. (This is Modbus specific).
-t Timeout for communications. The default is 5.0 seconds.
-e hElp. (this screen).

Example: "python hmiservermbc.py -p 8080".

Examples: (Linux)

./hmiservermbc.py -p 8082 -h localhost -r 8600 -u 1 -t 5.0

./hmiservermbc.py -p 8082 -h 192.168.10.5 -r 502 -u 1 -t 5.0

Examples: (MS Windows)

c:\python25\python hmiservermbc.py -p 8082 -h localhost -r 8600 -u 1 -t 5.0 

Author: Michael Griffin
Copyright 2008 - 2010 Michael Griffin. This is free software. You may 
redistribute copies of it under the terms of the GNU General Public License
<http://www.gnu.org/licenses/gpl.html>. There is NO WARRANTY, to the
extent permitted by law.

""" % (_SOFTNAME, _VERSION)

############################################################

import signal
import SocketServer
import sys
import time

from mbhmi import HMIDataTable
import HMIServerCommon
import StatusReporter

# These are for the Modbus protocol.
import ModbusClient as DataTableClient
from mbhmi import HMIModbusConfig as HMIConfigvalidator


############################################################


# Signal handler.
def SigHandler(signum, frame):
	print('\nOperator terminated server at %s' % time.ctime())
	sys.exit()


# Initialise the signal handler.
signal.signal(signal.SIGINT, SigHandler)


# Get the command line parameter options.
CmdOpts = HMIServerCommon.GetOptionsClient(502, _HelpStr)


############################################################


# Initialise the client. First get the remote host parameters.
rhost, rport, rtimeout, runitid = CmdOpts.GetRemoteParams()
MBClient = DataTableClient.DataTableAccess(rhost, rport, rtimeout, runitid)
# Initialise the data table access routines.
DataTable = HMIDataTable.HMIDataTable(MBClient)


# Configure the client with the software version.
HMIServerCommon.ClientControl.ConfigVersion(_VERSION)

# Store the system parameters for display on the monitoring pages. Also, set
# a flag to indicate this program version is a client. This is used for 
# controlling display parameters for the static versions of the web pages.
StatusReporter.Report.SetSysParams(_SOFTNAME, _VERSION, False)
# Store the command line start up parameters for display on the monitoring pages.
StatusReporter.Report.SetCommandParams(CmdOpts.GetPort(), rhost, rport, rtimeout, runitid)

# Load the HMI tag configuration.
HMIServerCommon.HMIConf.SetConfigParams(HMIConfigvalidator, DataTable)
HMIServerCommon.HMIConf.LoadHMIConfig()

# Update the list of available HMI files.
HMIServerCommon.ReadHMIFiles()


############################################################
# Define the protocol handler.
Handler = HMIServerCommon.HMIWebRequestHandlerClients

# If we exit and then try to restart the server again immediately,
# sometimes we cannot bind to the port until a short period of time
# has passed. In this case, we will sleep, and try again later. If
# we still don't succeed after several attempts, we will give up.
		
bindcount = 10
while True:
	try:
		httpd = SocketServer.TCPServer(('', CmdOpts.GetPort()), Handler)
		# Save a reference to the server so we can shut it down later.
		HMIServerCommon.ClientControl.SetShutDown(httpd)
		# Succeeded, so we can exit this loop.
		break
	except:
		if (bindcount > 0):
			print('Failed to bind to socket for port: %d. Will retry in 30 seconds...' % CmdOpts.GetPort())
			bindcount -= 1
			time.sleep(30)
		else:
			print('Failed to bind to socket for port: %d. Exiting...' % CmdOpts.GetPort())
			sys.exit()
		
# Print a welcome message.
print('\n%s version: %s' % (_SOFTNAME, _VERSION))
print('Started on %s with HMI port %d' % (time.ctime(), CmdOpts.GetPort()))


# Start up the server.
httpd.serve_forever()

#############################################################################

