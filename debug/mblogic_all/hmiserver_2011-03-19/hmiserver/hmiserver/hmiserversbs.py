#!/usr/bin/python
##############################################################################
# Project: 	hmiserversbs
# Module: 	hmiserversbs.py
# Purpose: 	HMI Server with SBus Server (derived from Modbus version).
# Language:	Python 2.5
# Date:		08-Mar-2008.
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
_SOFTNAME = 'HMIServerSBS'

# Version of this server.
_VERSION = '17-Mar-2011'

# Help string for command line help.
_HelpStr = """
%s, %s

This program provides a simple combination HMI http server and field device
SBus Ethernet server (slave). A field device such as a PLC can communicate
with this program using the SBus Ethernet protocol with the field device acting
as a client (master). Data from the field device is stored in a data table
where it is available to be read by the web browser using the HMI protocol.

Communications parameters are set using the following command line parameters.
Any parameters which are not specified will use their default values. 
These include:

-p Port number of HMI web server. The default is 8082.
-r Port number of SBus server. The default is 5050.

Examples: (Linux)

./hmiserversbs.py -p 8082 -r 5050

./hmiserversbs.py -p 8082 -r 5555

Examples: (MS Windows)

c:\python26\python hmiserversbs.py -p 8082 -r 5050

Author: Michael Griffin
Copyright 2008 - 2010 Michael Griffin. This is free software. You may 
redistribute copies of it under the terms of the GNU General Public License
<http://www.gnu.org/licenses/gpl.html>. There is NO WARRANTY, to the
extent permitted by law.

""" % (_SOFTNAME, _VERSION)

############################################################

import sys
import signal
import time

import asyncore
import socket
import collections

from mbprotocols import SBusMsg
from mbprotocols import SBusMemTable

from mbhmi import HMISBusDataTable

import HMIServerCommon
import StatusReporter
import SBusStatusReportMsg


# These are for the SBus protocol.
from mbhmi import HMISBusConfig as HMIConfigvalidator



############################################################

class SBusAsyncServer(asyncore.dispatcher):
	"""This listens for new SBus connection requests, and when
	a new connection is made it starts up a handler for it
	to run asynchronously.
	"""

	########################################################
	def __init__(self, port):

		self._port = port
		# This is used to queue up writes.
		self._WriteQueue = collections.deque()

		try:
			asyncore.dispatcher.__init__(self)
			self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
		except:
			print('Failed to create socket for port: %d. Exiting...' % port)
			sys.exit()

		# If we exit and then try to restart the server again immediately,
		# sometimes we cannot bind to the port until a short period of time
		# has passed. In this case, we will sleep, and try again later. If
		# we still don't succeed after several attempts, we will give up.
		bindcount = 10
		while True:
			try:
				self.bind(('', port))
				break	# Succeeded, so we can exit this loop.
			except:
				if (bindcount > 0):
					print('Failed to bind to socket for port: %d. Will retry in 30 seconds...' % port)
					bindcount -= 1
					time.sleep(30)
				else:
					print('Failed to bind to socket for port: %d. Exiting...' % port)
					sys.exit()

		# Announce the server is running.
		print('SBus server running on port %d...' % self._port)


	########################################################
	def __del__(self):
		self.close()


	########################################################
	def writable(self):
		"""Called by asyncore. Returns True if there is data to write.
		"""
		return len(self._WriteQueue) > 0


	########################################################
	def handle_write(self):
		"""Called by asyncore. Called to write data.
		"""
		recvdata, recvaddr = self._WriteQueue.popleft()
		self.sendto(recvdata, recvaddr)


	########################################################
	def handle_connect(self):
		"""Called by asyncore. Called when the first message arrives.
		We need this to avoid errors, but it doesn't do anything
		useful at this time.
		"""
		pass


	########################################################
	def handle_read(self):
		"""Called by asyncore. Called to read data.
		"""
		recvdata, recvaddr = self.recvfrom(4096)
		if recvdata:
			respdata = SBusMessageHandler(recvdata)
			self._WriteQueue.append((respdata, recvaddr))


############################################################


############################################################
def GetDefaultData():
	""" Return default data for cases where a message cannot be decoded.
	"""
	TelegramAttr = 0
	MsgSequence = 0
	StnAddr = 0
	CmdCode = 0
	DataAddr = 0
	DataCount = 0
	MsgData = ''
	ResultCode = False

	return TelegramAttr, MsgSequence, StnAddr, CmdCode, DataAddr, DataCount, MsgData, ResultCode

############################################################
def SBusMessageHandler(ReceivedData):
	"""Called to handle a single SBus message. This decodes the message, 
	reads from or writes to the data table, and then encodes the response.
	Requests and responses are also logged in the logging system.
	Parameters: ReceivedData (string) = A packed binary string containing
		the SBus request message.
	Returns: (string) = A packed binary string containing the SBus
		response message.
	"""
	# Decode message. 
	try:
		TelegramAttr, MsgSequence, StnAddr, CmdCode, DataAddr, DataCount, MsgData, ResultCode = \
			SBServerMSg.SBRequest(ReceivedData)
	# We can't decode this message at all, so just drop the request and stop here.
	# Can't decode the message, because the length is invalid.
	except SBusMsg.MessageLengthError:
		print('Server %d - Invalid message length. %s' % (CmdOpts.GetFieldPort(), time.ctime()))
		TelegramAttr, MsgSequence, StnAddr, CmdCode, DataAddr, DataCount, MsgData, ResultCode = \
			GetDefaultData()
	# Message had a CRC error.
	except SBusMsg.CRCError:
		print('Server %d - Bad CRC. %s' % (CmdOpts.GetFieldPort(), time.ctime()))
		TelegramAttr, MsgSequence, StnAddr, CmdCode, DataAddr, DataCount, MsgData, ResultCode = \
			GetDefaultData()
	# All other errors.
	except:
		print('Server %d - Request could not be decoded. %s' % (CmdOpts.GetFieldPort(), time.ctime()))
		TelegramAttr, MsgSequence, StnAddr, CmdCode, DataAddr, DataCount, MsgData, ResultCode = \
			GetDefaultData()


	# Log the incoming messages for reporting purposes.
	StatusReporter.Report.AddFieldRequest(SBusStatusReportMsg.SBusServerFieldRequest(TelegramAttr, \
				MsgSequence, StnAddr, CmdCode, DataAddr, DataCount, MsgData))

	ReplyData = ''
	AckNak = 0

	# Handle the command, but only if we were able to properly decode the request.
	if (ResultCode):

		# Decode messages. If we get an error in reading/writing memory or in constructing messages,
		# we will consider this to be an error.
		try:

			if CmdCode == 2:	# Read Flags.
				MsgData = MemMap.GetFlags(DataAddr, DataCount)
				ReplyData = SBServerMSg.SBResponse(MsgSequence, CmdCode, 0, MsgData)

			elif CmdCode == 3:	# Read Inputs.
				MsgData = MemMap.GetInputs(DataAddr, DataCount)
				ReplyData = SBServerMSg.SBResponse(MsgSequence, CmdCode, 0, MsgData)

			elif CmdCode == 5:	# Read Outputs.
				MsgData = MemMap.GetOutputs(DataAddr, DataCount)
				ReplyData = SBServerMSg.SBResponse(MsgSequence, CmdCode, 0, MsgData)

			elif CmdCode == 6:	# Read Registers.
				MsgData = MemMap.GetRegisters(DataAddr, DataCount)
				ReplyData = SBServerMSg.SBResponse(MsgSequence, CmdCode, 0, MsgData)

			elif CmdCode == 11:	# Write flags.
				MemMap.SetFlags(DataAddr, DataCount, MsgData)
				ReplyData = SBServerMSg.SBResponse(MsgSequence, CmdCode, 0, '')

			elif CmdCode == 13:	# Write outputs.
				MemMap.SetOutputs(DataAddr, DataCount, MsgData)
				ReplyData = SBServerMSg.SBResponse(MsgSequence, CmdCode, 0, '')

			elif CmdCode == 14:	# Write Registers.
				MemMap.SetRegisters(DataAddr, DataCount, MsgData)
				ReplyData = SBServerMSg.SBResponse(MsgSequence, CmdCode, 0, '')

			else:
				print('Server %d - Unsupported command code' % CmdOpts.GetFieldPort())
				ReplyData = SBServerMSg.SBErrorResponse(MsgSequence)
				AckNak = 1

		except:
			# An error has occured in reading or writing a memory location.
			ReplyData = SBServerMSg.SBErrorResponse(MsgSequence)
			AckNak = 1

	# The message was bad, so we return a NAK response. 
	else:
		ReplyData = SBServerMSg.SBErrorResponse(MsgSequence)
		AckNak = 1


	# Log the response messages for reporting purposes.
	StatusReporter.Report.AddFieldResponse(SBusStatusReportMsg.SBusServerFieldResponse(MsgSequence, \
					CmdCode, MsgData, AckNak))

	# Return the result
	return ReplyData


#############################################################################

# Signal handler.
def SigHandler(signum, frame):
	print('\nOperator terminated server at %s\n' % time.ctime())
	asyncore.close_all()


# Initialise the signal handler.
signal.signal(signal.SIGINT, SigHandler)


# Get the command line parameter options.
CmdOpts = HMIServerCommon.GetOptionsServer(5050, _HelpStr)

############################################################

# Initialise a memory data table to hold the data.
MemMap = SBusMemTable.SBusMemTable()

# Initialise the data table access routines.
DataTable = HMISBusDataTable.HMIDataTable(MemMap)

# SBus message construction. We will use a large data table for
# all addresses. 
SBServerMSg = SBusMsg.SBusServerMessages(65535, 65535, 65535, 65535)

# Configure the HTTP headers with software name and version.
HMIServerCommon.HeaderStrContainer.ConfigHeader(_SOFTNAME, _VERSION)

# Store the system parameters for display on the monitoring pages. Also, set
# a flag to indicate this program version is a server. This is used for 
# controlling display parameters for the static versions of the web pages.
StatusReporter.Report.SetSysParams(_SOFTNAME, _VERSION, True)
# Store the command line start up parameters for display on the monitoring pages.
StatusReporter.Report.SetCommandServerParams(CmdOpts.GetHMIPort(), CmdOpts.GetFieldPort())

# Load the HMI tag configuration.
HMIServerCommon.HMIConf.SetConfigParams(HMIConfigvalidator, DataTable)
HMIServerCommon.HMIConf.LoadHMIConfig()

# Update the list of available HMI files.
HMIServerCommon.ReadHMIFiles()

# Initialise the field device server using the selected port.
SBusAsyncServer(CmdOpts.GetFieldPort())

# Set the server status to OK. This never really changes.
StatusReporter.Report.SetCommsStatusOK()

# Initialise the HMI server using the selected port.
HMIServerCommon.HMIAsyncServer(CmdOpts.GetHMIPort())


# Print a welcome message.
print('\n%s version: %s' % (_SOFTNAME, _VERSION))
print('Started on %s with HMI port %d' % (time.ctime(), CmdOpts.GetHMIPort()))

# Start the server listening. This runs forever.
try:
	asyncore.loop()
except:
	print('Program terminated unexpectedly.')

############################################################


