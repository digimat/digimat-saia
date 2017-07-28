##############################################################################
# Project: 	MBLogic
# Module: 	MBClient.py
# Purpose: 	Modbus TCP Server (slave).
# Language:	Python 2.5
# Date:		19-Mar-2008.
# Version:	23-Jul-2010.
# Author:	M. Griffin.
# Copyright:	2008 - 2010 - Michael Griffin       <m.os.griffin@gmail.com>
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

"""
Implements the Modbus/TCP client protocol for the Twisted framework. 

Classes:

ModbusClientProtocol - This inherets from the Twisted protocol class. It
is used by the ModbusClientFactory class to receive and transmit messages.
Its methods should not be called outside if this module.

ModbusClientFactory - This is used to create a Modbus/TCP client. Once created,
it runs autonomously on a timed basis and polls the configured server. It must be
initialised with a reference to an object containing all the client information
(client connection object). The client connection object contains all the address
and polling information required to operate the client.

There is a hard coded start-up delay when the client first starts.


ModbusClientFactory is intended to be called from the part of the program which 
starts up all the clients by being passed to TWisted reactor.connectTCP. As many
clients as desired may be started provided they each have their own client
connection objects.

E.g. 
reactor.connectTCP(host, port, MBClient.ModbusClientFactory(ClientInstance))


It automatically handles reconnecting when a connection is lost, using an
exponential back-off algorithm. 

"""

##############################################################################

from twisted.internet import protocol, reactor

import MBDataTable
from mbprotocols import ModbusTCPLib
from mbprotocols import ModbusDataLib

##############################################################################


########################################################
def WriteFaultToDT(FaultCode, containerinfo):
	"""Write a communications or connection fault to the data table.
	Parameters: FaultCode (string) - The fault code to record. This will be 
		converted to an integer before writing it to the data table registers.
	containerinfo (object) = The container object. This is used to convert the
		fault code to an integer and to obtain the fault addresses.
	"""
	# Get the container address info.
	FaultCoilAddr, FaultInpAddr, FaultHoldingRegAddr, FaultInpRegAddr, freset = containerinfo.GetFaultAddresses()

	regvalue = containerinfo.FaultCodeToInt(FaultCode)

	# Update the memory table with the exception.
	MBDataTable.MemMap.SetCoilsBool(FaultCoilAddr, True)
	MBDataTable.MemMap.SetDiscreteInputsBool(FaultInpAddr, True)
	MBDataTable.MemMap.SetHoldingRegistersInt(FaultHoldingRegAddr, regvalue)
	MBDataTable.MemMap.SetInputRegistersInt(FaultInpRegAddr, regvalue)

##############################################################################
#
class ModbusClientProtocol(protocol.Protocol):
	"""Implements the Modbus/TCP client protocol for the Twisted Framework.
	"""

	########################################################
	def __init__(self, connection):
		"""Parameters: connection - This is a client connection container object 
		which is used to store all the connection configuration 
		information. This is a complex object which is created as part
		of the configuration process. It contains all the information
		the client needs to run and poll remote servers.
		"""
		self._ConnectionInfo = connection
		# ID code used to track reactor.callLater schedules.
		self.CallID = None
		# ID code used to track reactor.callLater schedules.
		self.RetryCallID = None
		# If True, we are at the end of the command list.
		self.EndofCommandList = False

		# Client message creation.
		self._MBClientMsg = ModbusTCPLib.MBTCPClientMessages()

		# Transaction ID sent and expected.
		self._TransID = 0
		# Unit ID
		self._UnitID = 1
		
		self._CmdName = 'default'
		self._FunctionCode = 0
		self._AddrRequested = 0
		self._QuantityRequested = 0
		self._MemAddr = 0


		# Get the fault addresses. However, if the configuration 
		# is invalid, these will be default vaules and not usable.
		self._FaultInpAddr, self._FaultCoilAddr, self._FaultInpRegAddr, \
			self._FaultHoldingRegAddr, self._FaultResetAddr \
			= self._ConnectionInfo.GetFaultAddresses()

		# Limit on the number of consecutive transaction ID errors before
		# reporting a fault.
		self._TIDLimit = 3
		# Counter for transaction ID error filtering.
		self._TIDError = 0

	########################################################
	#
	def NextRequest(self):
		"""Increment the command list and execute the next command.
		This includes constructing the next message. 
		"""

		# Transaction ID is incremented for each request to check message integrity.
		# It must not exceed the maximum for an 16 bit unsigned int though.
		self._TransID += 1
		if (self._TransID > 65535):
			self._TransID = 1


		# Get the parameters for this command.
		self._CmdName, self._FunctionCode, self._AddrRequested, self._QuantityRequested, \
			self._MemAddr, self._UnitID, EndofList = self._ConnectionInfo.NextCommand()

		# Get message data appropriate for the function being executed.
		if self._FunctionCode in (1, 2, 3, 4):
			MsgData = ''			# No message data is sent for a read.
		elif (self._FunctionCode == 5):
			CoilData = MBDataTable.MemMap.GetCoilsBool(self._MemAddr)
			if CoilData:
				MsgData = ModbusDataLib.coilvalue(1)	# Special format for function 5
			else:
				MsgData = ModbusDataLib.coilvalue(0)	# Special format for function 5
		elif self._FunctionCode in (6, 16):
			MsgData = MBDataTable.MemMap.GetHoldingRegisters(self._MemAddr, self._QuantityRequested)
		elif (self._FunctionCode == 15):
			MsgData = MBDataTable.MemMap.GetCoils(self._MemAddr, self._QuantityRequested)
		else:
			return '', True		# Invalid function code.


		# Create and return message.
		try:
			Message = self._MBClientMsg.MBRequest(self._TransID, self._UnitID, self._FunctionCode, 
					self._AddrRequested, self._QuantityRequested, MsgData)
		except:
			Message = ''

		return	Message, EndofList


	########################################################
	#
	def HandleReply(self, ServerReply):
		"""Handle the data from the server reply message.
		Parameters: ServerReply - This is the raw binary Modbus message response.
		"""
		
		try:
			# Extract the information from the Modbus reply.
			TransID, FunctionCode, Addr, Qty, MsgData, ExCode = self._MBClientMsg.MBResponse(ServerReply)
		except:
			# Something is wrong with the message, and we can't decode it.
			TransID = 0
			FunctionCode = 0
			Addr = 0
			Qty = 0
			MsgData = ''
			ExCode = 0
			


		# Check if the transaction ID matches what we sent.
		if (TransID == self._TransID):
			self._TIDError = 0

			try:
				if FunctionCode == 1:		# Read coils.
					MBDataTable.MemMap.SetCoils(self._MemAddr, self._QuantityRequested, MsgData)
					self._ConnectionInfo.SetCmdStatusOk(self._CmdName)

				elif FunctionCode == 2:		# Read discrete inputs.
					MBDataTable.MemMap.SetDiscreteInputs(self._MemAddr, self._QuantityRequested, MsgData)
					self._ConnectionInfo.SetCmdStatusOk(self._CmdName)

				elif FunctionCode == 3:		# Read holding registers.
					MBDataTable.MemMap.SetHoldingRegisters(self._MemAddr, self._QuantityRequested, MsgData)
					self._ConnectionInfo.SetCmdStatusOk(self._CmdName)

				elif FunctionCode == 4:		# Read input registers.
					MBDataTable.MemMap.SetInputRegisters(self._MemAddr, self._QuantityRequested, MsgData)
					self._ConnectionInfo.SetCmdStatusOk(self._CmdName)

				elif FunctionCode == 5:		# Write single coil.
					# MsgData in ('\x00\x00', '\xFF\x00')
					self._ConnectionInfo.SetCmdStatusOk(self._CmdName)

				elif FunctionCode == 6:		# Write single holding register.
					#  len(MsgData) == 2
					self._ConnectionInfo.SetCmdStatusOk(self._CmdName)

				elif FunctionCode == 15:	# Write multiple coils.
					self._ConnectionInfo.SetCmdStatusOk(self._CmdName)

				elif FunctionCode == 16:	# Write multiple holding registers.
					self._ConnectionInfo.SetCmdStatusOk(self._CmdName)

				elif FunctionCode > 127:	# Modbus exception.
					# Write the fault information into the configured data table addresses.
					# This includes the Modbus exception.
					faultcode = self._ConnectionInfo.ModbusExceptionToFaultCode(ExCode)
					# Write it to the data table.
					WriteFaultToDT(faultcode, self._ConnectionInfo)
					# Record the current message status.
					self._ConnectionInfo.SetCmdStatus(self._CmdName, faultcode)

				else:
					# We shouldn't get here unless there is a bug.
					print('Client Error - Unsupported function call.')
			except:
				# We shouldn't get here unless there is a bug.
				print('Client Error - Data table fault.')



		else:	# Bad TID
			# Check if too many consecutive TID errors. This allows the occasional bad
			# message without triggering a fault each time.
			if (self._TIDError > self._TIDLimit):
				# Write the fault information into the configured data table addresses.
				# Update the memory table with the error.
				WriteFaultToDT('badtid', self._ConnectionInfo)
				# Record the current message status. (not a Modbus error code).
				self._ConnectionInfo.SetCmdStatus(self._CmdName, 'badtid')
			else:
				self._TIDError += 1



	########################################################
	#
	def dataReceived(self, ServerReply):
		"""Called automatically when the server replies.
		 Parameters: ServerReply - This is the raw binary Modbus 
		 	message response.
		"""
		# Cancel the pending "retry" call.
		if (self.RetryCallID.cancelled != 1):
			self.RetryCallID.cancel()

		# Reply from server.
		self.HandleReply(ServerReply)

		# Record the current status.
		self._ConnectionInfo.SetConStatusRunning()

		# Set up the next data poll.
		if not self.EndofCommandList:
			# Time delay between individual commands in the list.
			delaytime = self._ConnectionInfo.GetCommandTime()
		else:
			# Time delay between sets of commands.
			delaytime = self._ConnectionInfo.GetRepeatTime()

		self.CallID = reactor.callLater(delaytime, self.sendMessage)

	
	########################################################
	# 
	def sendMessage(self):
		"""Called to send a message. The call is set up by an initial 
		"callLater" delayed call, and then subsequently after each 
		server reply. There is also an additional delayed call which is 
		set up after each message is sent. If the server does not reply, 
		then this second call will ensure that another request is sent.
		"""
		# Get the next command in the list.
		RequestMsg, self.EndofCommandList = self.NextRequest()

		# Set up a retry in case the server doesn't reply.
		delaytime = self._ConnectionInfo.GetRetryTime()
		self.RetryCallID = reactor.callLater(delaytime, self.SendTimeOut)

		if (RequestMsg != ''):
			self.transport.write(RequestMsg)	# Send the message!
		else:
			# We shouldn't get here unless there is a bug
			# in the software.
			if (self.RetryCallID.cancelled != 1):
				self.RetryCallID.cancel()
			self.transport.loseConnection()


	########################################################
	#
	def SendTimeOut(self):
		"""Called in the event of a time out. The call is set up by a 
		"callLater" in sendMessage. This function simply closes the 
		connection (and does some fault reporting). The protocol factory 
		class then automatically takes care of trying to re-establish a 
		new connection. This should only get triggered in the event that 
		the host accepts the connection, but fails to reply to a request.
		"""

		# Set status report.
		self._ConnectionInfo.SetConStatusFaulted()
		# Report the fault information to the data table.
		WriteFaultToDT('timeout', self._ConnectionInfo)
		# Record the current message status. (not a Modbus error code).
		self._ConnectionInfo.SetCmdStatus(self._CmdName, 'timeout')

		# Close the connection.
		self.transport.loseConnection()



############################################################
#
class ModbusClientFactory(protocol.ReconnectingClientFactory):
	"""Factory class for Modbus client. The methods are the standard
	Twisted methods. Twisted expects methods with these names to be 
	here, so don't change them to something else.
	"""

	########################################################
	def __init__(self, connection):
		"""Parameters: connection - This is a client connection container 
		object hich is used to store all the connection configuration 
		information. This is a complex object which is created as part
		of the configuration process. It contains all the information
		the client needs to run and poll remote servers.
		"""
		self._ConnectionInfo = connection

		# Get the fault addresses. However, if the configuration 
		# is invalid, these will be default vaules and not usable.
		self._FaultInpAddr, self._FaultCoilAddr, self._FaultInpRegAddr, \
			self._FaultHoldingRegAddr, self._FaultResetAddr \
			= self._ConnectionInfo.GetFaultAddresses()

	########################################################
	def startedConnecting(self, connector):
		print('Started to connect outgoing client %s' % self._ConnectionInfo.GetConnectionName())

	########################################################
	def buildProtocol(self, addr):
		print('Connected outgoing client %s.' % self._ConnectionInfo.GetConnectionName())
		self.resetDelay()
		ModbusClient = ModbusClientProtocol(self._ConnectionInfo)
		reactor.callLater(1.5, ModbusClient.sendMessage)
		# Record the current status.
		self._ConnectionInfo.SetConStatusStarting()
		return ModbusClient

	########################################################
	def clientConnectionLost(self, connector, reason):
		msgstr = 'Lost connection on outgoing client %s.'
		print(msgstr %  (self._ConnectionInfo.GetConnectionName()))
		# Record the current status.
		self._ConnectionInfo.SetConStatusFaulted()
		# Report the information to the data table.
		WriteFaultToDT('connection', self._ConnectionInfo)
		protocol.ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

	########################################################
	def clientConnectionFailed(self, connector, reason):
		msgstr = 'Connection failed on outgoing client %s.'
		print(msgstr %  (self._ConnectionInfo.GetConnectionName()))
		# Record the current status.
		self._ConnectionInfo.SetConStatusFaulted()
		# Report the information to the data table.
		WriteFaultToDT('connection', self._ConnectionInfo)
		protocol.ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

############################################################


