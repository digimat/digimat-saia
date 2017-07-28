##############################################################################
# Project: 	MBLogic
# Module: 	MBServer.py
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
Implements the Modbus/TCP server protocol for the Twisted framework. Despite
the name of this file, this is not the main entry point for this program!
It is only one of the libraries.

Classes:

ModbusServerHandler - This inherets from the Twisted protocol class. It
is used by the ModbusServerProtocol class to receive and transmit messages.
Its methods should not be called outside if this module. Due to the way
the Twisted servers work, this is a global object and as such only allows
one instance.

ModbusServerProtocol, ModbusServerFactory - These are used to create a Modbus/TCP 
server. Once created, runs autonomously responding to client requests as they arrive. 
It must be initialised with a reference to an object containing all the server information
(server connection object). The server connection object contains all the address
and other information required to operate the server.

ModbusServerFactory is intended to be called from the part of the program which 
starts up all the servers by being passed to TWisted reactor.listenTCP. 

E.g.
MBServer.ModbusServer.SetStatusInfo(ServerInstance)
reactor.listenTCP(ServerInstance.GetHostInfo(), MBServer.ModbusServerFactory())

"""
############################################################
from twisted.internet import protocol

import MBDataTable
from mbprotocols import ModbusTCPLib
from mbprotocols import ModbusDataLib


############################################################
class ExpDTError(ValueError):
	"""Used to help raise exceptions for invalid expanded register map errors.
	"""

############################################################
#
class ModbusServerHandler:
	""" Implements the Modbus/TCP server protocol.
	Methods: HandleRequest - Converts a Modbus server request into a Modbus server reply.
	An initialised memory map object must have been already imported.
	"""

	########################################################
	def __init__(self):
		# Initialise the server message object. Note that the limits here
		# are the Modbus *protocol* limits which are not necessarily the sam
		# as the data table limits (although they must not be greater than
		# the data table limits.
		self._MBServerMsg = ModbusTCPLib.MBTCPServerMessages(65535, 65535, 65535, 65535)

		# Offsets for data table expanded maps.
		self._DTOffsets = {}
		# Enables expanded register maps.
		self._ExpAddressing = False
		# Error message for expanded data table errors.
		self._ExpDTError = 'Modbus/TCP server error - UID not found in expanded register map.'


	########################################################
	def SetStatusInfo(self, statusinfo):
		""" Must call this to add a reference to the configuration 
		information. This allows status information to be
		tracked and reported.
		"""
		self._StatusInfo = statusinfo

	########################################################
	def SetExpandedDTAddressing(self, dtoffsets, enabled):
		"""Set the offsets for data table expanded register map. 
		Parameters: dtoffsets (dict) = A dictionary containing the data table
			offsets used for expanded register maps beyond the normal
			Modbus limits. The keys are unit ID (UID) numbers. The
			values are added to the data table addresses when reading
			or writing expanded maps using the UIDs.
		enabled (boolean) = If true, expanded maps is 
			enabled.
		"""
		self._ExpAddressing = enabled
		self._DTOffsets = dtoffsets
		


	########################################################
	def HandleRequest(self, ReceivedData):
		""" Convert a Modbus server request message into a Modbus 
			server reply message.
		ReceivedData - Binary string with raw request message.
		Returns - Binary string with completed raw reply message. If a 
			server error occurs, an empty string will be returned instead.
		This method handles Modbus protocol functions 1, 2, 3, 4, 5, 6, 15, and 16.
		"""

		# Decode message. 'RequestData' may mean either number of coils or sent data, depending
		# upon the function code being received. For functions 15 and 16, it is a tuple containing
		# data and quantity.
		try:
			TransID, UnitID, FunctionCode, Start, Qty, RequestData, ExceptionCode = \
				self._MBServerMsg.MBRequest(ReceivedData)

		except:
			# Something is wrong with the message, and we can't decode it.
			TransID = 0
			UnitID = 0
			FunctionCode = 0
			Start = 0
			Qty = 0
			RequestData = 0
			ExceptionCode = 0

		try:
			# Read coils. RequestData = quantity.
			if FunctionCode == 1:
				MsgData = MBDataTable.MemMap.GetCoils(Start, Qty)
				ReplyData = self._MBServerMsg.MBResponse(TransID, UnitID, FunctionCode, Start, MsgData)

			# Read discrete inputs.	RequestData = quantity.
			elif FunctionCode == 2:
				MsgData = MBDataTable.MemMap.GetDiscreteInputs(Start, Qty)
				ReplyData = self._MBServerMsg.MBResponse(TransID, UnitID, FunctionCode, Start, MsgData)

			# Read holding registers. RequestData = quantity.
			elif FunctionCode == 3:
				# Get the expanded address.
				if self._ExpAddressing:
					try:
						dtstart = self._DTOffsets[UnitID] + Start
					except:
						raise ExpDTError, self._ExpDTError
				else:
					dtstart = Start

				MsgData = MBDataTable.MemMap.GetHoldingRegisters(dtstart, Qty)
				ReplyData = self._MBServerMsg.MBResponse(TransID, UnitID, FunctionCode, Start, MsgData)

			# Read input registers. RequestData = quantity.
			elif FunctionCode == 4:
				MsgData = MBDataTable.MemMap.GetInputRegisters(Start, Qty)
				ReplyData = self._MBServerMsg.MBResponse(TransID, UnitID, FunctionCode, Start, MsgData)

			# Write single coil. RequestData contains data.
			elif FunctionCode == 5:
				MBDataTable.MemMap.SetCoils(Start, 1, RequestData)
				ReplyData = self._MBServerMsg.MBResponse(TransID, UnitID, FunctionCode, Start, RequestData)

			# Write single holding register. RequestData contains data.
			elif FunctionCode == 6:
				# Get the expanded register maps.
				if self._ExpAddressing:
					try:
						dtstart = self._DTOffsets[UnitID] + Start
					except:
						raise ExpDTError, self._ExpDTError
				else:
					dtstart = Start

				MBDataTable.MemMap.SetHoldingRegisters(dtstart, 1, RequestData)
				ReplyData = self._MBServerMsg.MBResponse(TransID, UnitID, FunctionCode, Start, RequestData)

			# Write multiple coils. RequestData is a tuple.
			elif FunctionCode == 15:
				MBDataTable.MemMap.SetCoils(Start, Qty, RequestData)
				ReplyData = self._MBServerMsg.MBResponse(TransID, UnitID, FunctionCode, \
					Start, ModbusDataLib.Int2BinStr(Qty))

			# Write multiple holding registers. RequestData is a tuple.
			elif FunctionCode == 16:
				# Get the expanded register maps.
				if self._ExpAddressing:
					try:
						dtstart = self._DTOffsets[UnitID] + Start
					except:
						raise ExpDTError, self._ExpDTError
				else:
					dtstart = Start

				MBDataTable.MemMap.SetHoldingRegisters(dtstart, Qty, RequestData)
				ReplyData = self._MBServerMsg.MBResponse(TransID, UnitID, FunctionCode, \
					Start, ModbusDataLib.Int2BinStr(Qty))

			# Modbus exception.
			elif FunctionCode > 127:
				ReplyData = self._MBServerMsg.MBErrorResponse(TransID, UnitID, FunctionCode, ExceptionCode)

			# Something is wrong here and we don't understand the message.
			else:
				ReplyData = self._MBServerMsg.MBErrorResponse(TransID, UnitID, FunctionCode + 128, 1)

		# Extended addressing errors.
		except ExpDTError:
			# Modbus exception 2. The extended UID is not known.
			ReplyData = self._MBServerMsg.MBErrorResponse(TransID, UnitID, FunctionCode + 128, 2)

		except:
			# Modbus exception 4. An error has occured in reading or writing a memory location.
			ReplyData = self._MBServerMsg.MBErrorResponse(TransID, UnitID, FunctionCode + 128, 4)

		# Return the result.
		return ReplyData


	########################################################
	def IncConnectionCount(self):
		"""Increment the connection count.
		"""
		self._StatusInfo.IncConnectionCount()

	########################################################
	def DecConnectionCount(self):
		"""Decrement the connection count.
		"""
		self._StatusInfo.DecConnectionCount()

##############################################################################

# Create a server instance.
ModbusServer = ModbusServerHandler()

############################################################
#
class ModbusServerProtocol(protocol.Protocol):
	""" Implements the Modbus/TCP server protocol for the Twisted Framework.
	"""


	########################################################
	def connectionMade(self):
		"""Client connected.
		"""
		ModbusServer.IncConnectionCount()
		print('Incoming client connected to Modbus TCP server from %s.' 
			% self.transport.getPeer().host)

	########################################################
	def connectionLost(self, reason):
		"""Client disconnected.
		"""
		ModbusServer.DecConnectionCount()
		print('Incoming client connection lost on Modbus TCP server.')

	########################################################
	def dataReceived(self, ReceivedData):
		"""Reply to Modbus requests.
		"""
		ReplyMsg = ModbusServer.HandleRequest(ReceivedData)
		if (ReplyMsg != ''):
			self.transport.write(ReplyMsg)
		else:
			print('Server Error - Unsupported function call on Modbus TCP server.')
			self.transport.loseConnection()


############################################################
#
class ModbusServerFactory(protocol.ServerFactory):
	"""Factory class for Modbus server.
	"""
	protocol = ModbusServerProtocol

############################################################

