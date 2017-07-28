#!/usr/bin/python
##############################################################################
# Project: 	hmiservermbs
# Module: 	hmiservermbs.py
# Purpose: 	HMI Server with Modbus Server.
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

############################################################

# Name of this program.
_SOFTNAME = 'HMIServerMBS'

# Version of this server.
_VERSION = '17-Mar-2011'

# Help string for command line help.
_HelpStr = """
%s, %s

This program provides a simple combination HMI http server and field device
Modbus/TCP server (slave). A field device such as a PLC can communicate
with this program using the Modbus/TCP protocol with the field device acting
as a client (master). Data from the field device is stored in a data table
where it is available to be read by the web browser using the HMI protocol.

Communications parameters are set using the following command line parameters.
Any parameters which are not specified will use their default values. 
These include:

-p Port number of HMI web server. The default is 8082.
-r Port number of Modbus/TCP server. The default is 502.

Examples: (Linux)

./hmiservermbs.py -p 8082 -r 8600

./hmiservermbs.py -p 8082 -r 502

Examples: (MS Windows)

c:\python26\python hmiservermbs.py -p 8082 -r 8600

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

from mbprotocols import ModbusTCPLib
from mbprotocols import ModbusMemTable
from mbprotocols import ModbusDataLib

from mbhmi import HMIDataTable

import HMIServerCommon
import StatusReporter
import ModbusStatusReportMsg


# These are for the Modbus protocol.
from mbhmi import HMIModbusConfig as HMIConfigvalidator


############################################################

class ModbusAsyncServer(asyncore.dispatcher):
	"""This listens for new Modbus/TCP connection requests, and when
	a new connection is made it starts up a handler for it
	to run asynchronously.
	"""

	########################################################
	def __init__(self, port):
		try:
			asyncore.dispatcher.__init__(self)
			self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
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

			
		# Try listening to port.
		try:
			self.listen(5)
		except:
			print('Failed listening to port: %d. Exiting...' % port)
			sys.exit()

		print('Modbus/TCP server running on port %d...' % port)

	########################################################
	def __del__(self):
		self.close()

	########################################################
	def handle_accept(self):
		NewSocket, Address = self.accept()
		print('Connected from %s  %d' % Address)
		ModbusSocketHandler(NewSocket)

############################################################


############################################################
# 
class ModbusSocketHandler(asyncore.dispatcher_with_send):
	"""An instance of this class is started up for each connection.
	"""

	########################################################
	def handle_read(self):

		try:
			ReceivedData = self.recv(8192)
		except:
			ReceivedData = None

		if ReceivedData: 

			# Decode message. 'RequestData' may mean either number of coils or sent data, depending
			# upon the function code being received. For functions 15 and 16, it is a tuple containing
			# data and quantity.
			try:
				TransID, UnitID, FunctionCode, Start, Qty, RequestData, ExceptionCode = \
						MBServerMSg.MBRequest(ReceivedData)

			# We can't decode this message at all, so just drop the request and stop here.
			# Can't decode the message, because the length is invalid.
			except ModbusTCPLib.MessageLengthError:
				print('Server %d - Invalid message length. %s' % (CmdOpts.GetFieldPort(), time.ctime()))
				TransID, UnitID, FunctionCode, Start, Qty, RequestData, ExceptionCode = self._GetDefaultData()

			except:
				TransID, UnitID, FunctionCode, Start, Qty, RequestData, ExceptionCode = self._GetDefaultData()


			# Log the incoming messages for reporting purposes.
			StatusReporter.Report.AddFieldRequest(ModbusStatusReportMsg.ModbusServerFieldRequest(TransID, \
					UnitID, FunctionCode, Start, Qty, RequestData))


			ReplyData = ''
			MsgData = [0]
			# Decode messages. If we get an error in reading/writing memory or in constructing messages,
			# we will consider this to be a Modbus exception.
			try:
				if FunctionCode == 1:		# Read coils.
					MsgData = MemMap.GetCoils(Start, Qty)
					ReplyData = MBServerMSg.MBResponse(TransID, UnitID, FunctionCode, Start, MsgData)

				elif FunctionCode == 2:		# Read discrete inputs.
					MsgData = MemMap.GetDiscreteInputs(Start, Qty)
					ReplyData = MBServerMSg.MBResponse(TransID, UnitID, FunctionCode, Start, MsgData)

				elif FunctionCode == 3:		# Read holding registers.
					MsgData = MemMap.GetHoldingRegisters(Start, Qty)
					ReplyData = MBServerMSg.MBResponse(TransID, UnitID, FunctionCode, Start, MsgData)

				elif FunctionCode == 4:		# Read input registers.
					MsgData = MemMap.GetInputRegisters(Start, Qty)
					ReplyData = MBServerMSg.MBResponse(TransID, UnitID, FunctionCode, Start, MsgData)

				elif FunctionCode == 5:		# Write single coil. RequestData contains data.
					MemMap.SetCoils(Start, 1, RequestData)
					ReplyData = MBServerMSg.MBResponse(TransID, UnitID, FunctionCode, Start, RequestData)

				elif FunctionCode == 6:		# Write single holding register. RequestData contains data.
					MemMap.SetHoldingRegisters(Start, 1, RequestData)
					ReplyData = MBServerMSg.MBResponse(TransID, UnitID, FunctionCode, Start, RequestData)

				elif FunctionCode == 15:	# Write multiple coils.	
					MemMap.SetCoils(Start, Qty, RequestData)
					ReplyData = MBServerMSg.MBResponse(TransID, UnitID, FunctionCode, \
							Start, ModbusDataLib.Int2BinStr(Qty))

				elif FunctionCode == 16:	# Write multiple holding registers. 
					MemMap.SetHoldingRegisters(Start, Qty, RequestData)
					ReplyData = MBServerMSg.MBResponse(TransID, UnitID, FunctionCode, \
							Start, ModbusDataLib.Int2BinStr(Qty))

				elif FunctionCode > 127:	# Modbus exception.
					ReplyData = MBServerMSg.MBErrorResponse(TransID, UnitID, FunctionCode, ExceptionCode)
				else:
					print('Server %d - Unsupported function call' % CmdOpts.GetFieldPort())
					ReplyData = MBServerMSg.MBErrorResponse(TransID, UnitID, FunctionCode + 128, 1)

			except:
				# Modbus exception 4. An error has occured in reading or writing a memory location.
				ReplyData = MBServerMSg.MBErrorResponse(TransID, UnitID, FunctionCode + 128, 4)


			# Send the reply.
			try:
				self.send(ReplyData)
			except:
				# If we have an error here, there's not much we can do about it.
				print('Server %d - Could not reply to request.' % CmdOpts.GetFieldPort())


			# Log the response messages for reporting purposes.
			StatusReporter.Report.AddFieldResponse(ModbusStatusReportMsg.ModbusServerFieldResponse(TransID, \
						FunctionCode, MsgData, RequestData, Qty, ExceptionCode))

		else: 
			self.close()

	########################################################
	def handle_close(self):
		try:
			peername = self.getpeername()
		except:
			peername = ('unknown peer', 0)
		print('Disconnected from %s  %d' % peername)


	########################################################
	def _GetDefaultData(self):
		"""Return default data to use when a message cannot be decoded. This 
		does not provide useful data, but they are place holders for message
		reporting, etc. 
		"""
		TransID = 0
		UnitID = 0
		FunctionCode = 0
		Start = 0
		Qty = 0
		RequestData = ''
		ExceptionCode = 0

		return TransID, UnitID, FunctionCode, Start, Qty, RequestData, ExceptionCode


############################################################





#############################################################################

# Signal handler.
def SigHandler(signum, frame):
	print('\nOperator terminated server at %s\n' % time.ctime())
	asyncore.close_all()


# Initialise the signal handler.
signal.signal(signal.SIGINT, SigHandler)


# Get the command line parameter options.
CmdOpts = HMIServerCommon.GetOptionsServer(502, _HelpStr)

############################################################

# Initialise a memory data table to hold the data.
# This uses a unified address space for all data types.
# We don't overlay coils and registers. We don't use expanded registers.
MemMap = ModbusMemTable.ModbusMemTable(unified = True, overlay = False, expandedregs = False)

# Initialise the data table access routines.
DataTable = HMIDataTable.HMIDataTable(MemMap)

maxcoils, maxdiscretes, maxholdingreg, maxinputreg = MemMap.GetMaxAddresses()
MBServerMSg = ModbusTCPLib.MBTCPServerMessages(maxcoils, maxdiscretes, maxholdingreg, maxinputreg)

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
ModbusAsyncServer(CmdOpts.GetFieldPort())

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


