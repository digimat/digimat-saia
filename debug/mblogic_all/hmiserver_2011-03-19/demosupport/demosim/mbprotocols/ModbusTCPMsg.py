##############################################################################
# Project: 	MBLogic
# Module: 	ModbusTCPMsg.py
# Purpose: 	Provides ModbusTCP base functions.
# Language:	Python 2.5
# Date:		08-Mar-2008.
# Ver.:		04-Jul-2010.
# Copyright:	2006-2008 - Juan Miguel Taboada Godoy <juanmi@likindoy.org>
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

import struct

##############################################################################
"""
This module is used for assembling and dissassembling Modbus/TCP messages.
Each method either accepts a set of parameters and constructs a valid
Modbus/TCP message ready for transmission, or it takes a Modbus/TCP
message which has bee received and dissassembles it into its components
so that the contents may be read. 

There are two classes. One class (MBTCPServerMessages) is used with servers (slaves),
while the other (MBTCPClientMessages) is used with clients (masters). Neither class
implements that actual transmission or receipt of messages, nor do they implement
a Modbus memory structure for storing data.

Public Classes:
A) MBTCPServerMessages - This must be initialised with 4 integers indicating the 
	maximum number of coils, discrete inputs, holding registers, and input 
	registers. These are used to determine if the address in a client request 
	is out of range.

Public Methods:
For the following: 
TransID, TID = transaction ID (integer), 
UnitID, UID = unit ID (integer), 
FunctionCode, Func = Modbus function code (integer), 
ErrorCode = Modbus error code (integer), 
ExceptionCode = Modbus exception code (integer),
Addr = data table address (integer), 
Qty = Number of consecutive addresses (integer), 
MsgData = data (packed binary string),

A1) MBResponse(TransID, UnitID, FunctionCode, Addr, MsgData) - Construct an server 
	response message. Returns a packed binary string containing message.
A2) MBErrorResponse(TransID, UnitID, ErrorCode, ExceptionCode) - Construct a 
	server error response message. Returns a packed binary string containing message.
A3) MBRequest(Func, Addr, Qty, TID, UID, Message) 
	- Extract the data from a modbus client request message. This handles writes.
	Returns a tuple containing TransID, UnitID, FunctionCode, Address, 
	MsgData, exceptioncode. For functions 15 and 16, MsgData is actually a tuple
	containing (Quantity, MsgData).

Public Classes:
B) MBTCPClientMessages

Public Methods:
For the following:
TransID = Transaction ID (integer)
UnitID = Unit ID (integer)
FunctionCode - Modbus function (integer)
Addr - Data table address (integer)
Qty - Number of consecutive addresses (integer)
MsgData = 'none' - Message data (default of 'none') (packed binary string)
Message - Message data (packed binary string)
B1) MBRequest(TransID, UnitID, FunctionCode, Addr, Qty, MsgData = 'none')
	- Make a modbus client request message. Returns a tuple containing the
	message (packed binary string).
B2) MBResponse(Message) - Extract the data from a server response message.
	Returns a tuple containing the transaction ID (integer), function (integer),
	and data (packed binary string). In the event of an error, function is the
	error code, and data is an integer with the exception code. 

========================================================================

A Modbus TCP message consists of two parts, a Modbus Application Protocol
header (MBAP), and a Protocol Data Unit (PDU). 

MBAP Header
- Transaction ID: (2 bytes) This is set by the client (master) and echoed
	back by the client. This may be any number.
- Protocol: (2 bytes) This must always be zero for Modbus. This is a fixed 
	constant in this library and cannot be changed.
- Length: (2 bytes) This is the length of the message, and is 
	calculated automatically.
- Unit ID: (1 byte) This is used for routing serial Modbus messages through 
	a gateway. The Advantech ADAM 5000 TCP requires this to be set to 1.

PDU:
- Function code: (1 byte) This is the Modbus function number.
- Data address: (2 bytes) This is the Modbus data address.
- The remainder of the PDU is determined by the function being used.
See the official Modbus TCP specifications for more details.

This library supports the following functions:
1	= Read Coils
2	= Read Discrete Inputs
3	= Read Holding Registers
4	= Read Input Registers
5	= Write Single Coil
6	= Write Single Register
15	= Write Multiple Coils
16	= Write Multiple registers


Modbus Exceptions:
If there is an error in the message, a Modbus/TCP exception code is generated.
Modbus/TCP exception codes are generated in the following order: 1, 3, 2, 4. When
an exception is found, processing stops there and the code is returned.

Exceptions are defined as followed:
Exception Code 1 (All functions): Function code is not supported.
Exception Code 2 (functions 1, 2, 3, 4): Start address not OK or Start address + qty outputs not OK.
Exception Code 2 (functions 5, 6): Output address not OK.
Exception Code 2 (functions 15, 16): Start address not OK or start address + qty outputs or registers not OK.
Exception Code 3 (functions 1, 2): Qty of inputs, or outputs is not between 1 and 0x07D0.
Exception Code 3 (functions 3, 4): Qty of registers is not between 1 and 0x07D.
Exception Code 3 (function 5): Output value is not 0x0000 or 0xFF00.
Exception Code 3 (function 6): Register value is not between 0x0000 and 0xFFFF.
Exception Code 3 (functions 15, 16): Qty of outputs or registers is not between 1 and 0x07B0.
Exception Code 4 (All functions):An error has occurred during reading or writing an input, output, 
or register. This exception cannot be detected at this point, and so will not be returned.
"""


##############################################################################
# Class to assemble or extract data from Modbus/TCP server messages.
# This class must be initialised with the maximum permitted addresses for
# coils, discrete inputs, holding registers, and input registers. 
# This is necessary so requests for attempts to access addresses which are
# out of range can be detected and an exception generated.
#
class MBTCPServerMessages:

	########################################################
	def __init__(self, maxcoils, maxdiscretes, maxholdingreg, maxinputreg):
		"""Initialise the limits to the data tables.
		maxcoils (integer) = Highest permitted coil address.
		maxdiscretes (integer) = Highest permitted discrete input address.
		maxholdingreg (integer) = Highest permitted holding register address.
		maxinputreg (integer) = Highest permitted input register address.
		"""

		# A dictionary is used to hold the address limits. The dictionary key
		# is the Modbus function code, and the data is the address limit.
		self._addrlimits = {1 : maxcoils, 2 : maxdiscretes, 3 : maxholdingreg,
		4 : maxinputreg, 5 : maxcoils, 6 : maxholdingreg, 15 : maxcoils, 16 : maxholdingreg }

		# A dictionary is used to hold the constants for the protocol addressing range.
		# These are the  maximum number of elements that can be read or written to at one
		# time without exceeding the protocol limit. Exceeding these limits results in 
		# a Modbus exception 3.
		self._protocollimits = {1 : 0x07D0, 2 : 0x07D0, # Max coils that can be read at once.
					3 : 0x07D, 4 : 0x07D,	# Max registers that can be read at once.
					5 : 0x0, 6 : 0x0,	# N/A for 5 or 6.
					15 : 0x07B0, 		# Max coils that can be written at once.
					16 : 0x07B}		# Max registers that can be written at once.


	########################################################
	def MBResponse(self, TransID, UnitID, FunctionCode, Addr, MsgData):
		"""Construct a Modbus/TCP response message for a read data request.
		TransID (integer) = Transaction ID. This must match the value used by the client.
		UnitID (integer) = Unit ID.
		FunctionCode (integer) = Modbus/TCP function code.
		Addr (integer) = Data table address (requiredOriginal address 
		MsgData (packed binary string) = The data to be returned.
		"""

		# struct parameters are:
		# 1) Format string (calculated using length of data).
		# 2) TransID - Transaction ID.
		# 3) Protocol. This is always 0 for Modbus/TCP.
		# 4) MBAP length parameter is size of PDU plus unitid. (calculated)
		# 5) UnitID - Unit ID.
		# 6) FunctionCode - Modbus function code.
		# 7a) DataLen - Length of data. (calculated). For func 1 to 4
		# 7b) Addr - Original address. For func 5, 6, 15, 16.
		# 8) MsgData - Preconstructed message data.

		if (FunctionCode in [1, 2, 3, 4]):
			DataLen = len(MsgData)		# Length of data.
			return struct.pack('>HHHBBB %ds' % DataLen, TransID, 0, DataLen + 3, 
					UnitID, FunctionCode, DataLen, MsgData)
		else:
			return struct.pack('>HHHBBH2s', TransID, 0, 6, UnitID, FunctionCode, Addr, MsgData)



	########################################################
	# Construct a Modbus/TCP error response message.
	# TransID (integer) = Transaction ID. This must match the value used by the client.
	# UnitID (integer) = Unit ID.
	# ErrorCode (integer) = Modbus/TCP error code.
	# ExceptionCode (integer) = Modbus/TCP exception code.
	def MBErrorResponse(self, TransID, UnitID, ErrorCode, ExceptionCode):
		"""Construct a Modbus/TCP error response message.
		TransID (integer) = Transaction ID. This must match the value used by the client.
		UnitID (integer) = Unit ID.
		ErrorCode (integer) = Modbus/TCP error code.
		ExceptionCode (integer) = Modbus/TCP exception code.
		"""

		# struct parameters are:
		# 1) Format string. An error response is a fixed length of 9 bytes.
		# 2) TransID - Transaction ID.
		# 3) Protocol. This is always 0 for Modbus/TCP.
		# 4) MBAP length parameter is size of PDU plus unitid. (Always 3 for an error)
		# 5) UnitID - Unit ID.
		# 6) ErrorCode - Modbus error code.
		# 7) ExceptionCode - Modbus error code.

		return struct.pack('>HHHBBB', TransID, 0, 3, UnitID, ErrorCode, ExceptionCode)


	########################################################
	#
	def MBRequest(self, Message):
		"""Extract the data from a Modbus/TCP request message.
		Parameters: Message = This is a string containing the raw binary 
					message as received.
		Return values: 
		TransID (integer) = Transaction ID.
		UnitID (integer) = Unit ID.
		Function (integer) = Function or error code.
		Start (integer) = First address in request.
		data = Message data. For functions 1, 2, 3, 4 this is an integer 
			representing the quantity of requested inputs, coils or 
			registers. For 5 or 6, this is a binary string containing
			the coil or register data. For 15 or 16 this is a tuple 
			containing an integer with the number of coils or registers, 
			and a binary string containing the data. In the case of
			exception 1 (unsupported function), this will be a binary 
			string containing zeros.
		exceptioncode (integer) = Modbus exception code. This is 0 if there is no error.
		If a message cannot be decoded, zeros will be returned for all fields.
		"""

		# Check if the message is long enough to begin decoding.
		# If it is too short, it cannot be a meaningful message.
		if (len(Message) <= 10):
			TransID = 0
			UnitID = 0
			Function = 0
			Start = 0
			data = '/x00/x00'
			exceptioncode = 0
			return TransID, UnitID, Function, Start, data, exceptioncode

		MbPDU = Message[10:]	# Get remainder of message.

		# Unpack the first 10 bytes of the message.
		TransID, protocol, length, UnitID, Function, Start = struct.unpack('>HHHBBH', Message[0:10])

		# Get remainder of message.
		MbPDU = Message[10:]

		# Read coils, inputs, or registers..
		if Function in (1, 2, 3, 4):
			
			# Unpack the rest of the message.
			# unpack always returns a tuple, so we need to get size this way.
			(qty,) = struct.unpack('>H', MbPDU)

			exceptioncode = 0	# Default exception code.
			
			# Check for exceptions.
			# Qty of inputs or outputs is out of range.
			if ((qty < 1) or (qty > self._protocollimits[Function])):
				Function = Function + 128	# Create error code.
				exceptioncode = 3		# Exception code.

			# Check if the requested data exceeds the maximum address.
			elif ((Start + qty - 1) > self._addrlimits[Function]):
				Function = Function + 128	# Create error code.
				exceptioncode = 2		# Exception code.

			return TransID, UnitID, Function, Start, qty, exceptioncode


		# Write single coil.
		elif Function == 5:

			# Unpack the rest of the message.
			# unpack always returns a tuple, so we need to get data this way.
			(data,) = struct.unpack('>2s', MbPDU)
			
			exceptioncode = 0	# Default exception code.

			# Check for exceptions.
			# Check if the requested data exceeds the maximum address.
			if (Start > self._addrlimits[Function]):
				Function = Function + 128	# Create error code.
				exceptioncode = 2		# Exception code.
			# For function 5, data value must be one of two possible values.
			elif (data not in ('\x00\x00', '\xFF\x00')):
				Function = Function + 128	# Create error code.
				exceptioncode = 3		# Exception code.

			return TransID, UnitID, Function, Start, data, exceptioncode


		# Write single register.
		elif Function == 6:

			# Unpack the rest of the message.
			# unpack always returns a tuple, so we need to get data this way.
			(data,) = struct.unpack('>2s', MbPDU)
			
			exceptioncode = 0	# Default exception code.

			# Check for exceptions.
			# Check if the requested data exceeds the maximum address.
			if (Start > self._addrlimits[Function]):
				Function = Function + 128	# Create error code.
				exceptioncode = 2		# Exception code.

			# For function 6, data is unpacked into two bytes, so the value *must* 
			# be within the range of 0 to 65535. Therefore, we do not need to check 
			# for exception 3.

			return TransID, UnitID, Function, Start, data, exceptioncode

		# Write multiple coils.
		elif Function == 15:

			# Unpack the rest of the message.
			qty, bytecount, data = struct.unpack('>HB %ds' % (len(MbPDU) - 3), MbPDU)

			exceptioncode = 0	# Default exception code.

			# Check for exceptions.
			# Check if the requested data exceeds the maximum address.
			if ((Start + qty - 1) > self._addrlimits[Function]):
				Function = Function + 128	# Create error code.
				exceptioncode = 2		# Exception code.
			# Qty of outputs, or registers is out of range.
			elif ((qty < 1) or (qty > self._protocollimits[Function])):
				Function = Function + 128	# Create error code.
				exceptioncode = 3		# Exception code.
			# Qty for coils exceeds amount of data sent.
			elif (qty > (len(data) * 8)):
				Function = Function + 128	# Create error code.
				exceptioncode = 3		# Exception code.
			# Qty for coils less than amount of data sent.
			elif (qty < ((len(data) - 1) * 8) + 1):
				Function = Function + 128	# Create error code.
				exceptioncode = 3		# Exception code.

			return TransID, UnitID, Function, Start, (qty, data), exceptioncode

		# Write multiple holding registers.
		elif Function == 16:

			# Unpack the rest of the message.
			qty, bytecount, data = struct.unpack('>HB %ds' % (len(MbPDU) - 3), MbPDU)

			exceptioncode = 0	# Default exception code.

			# Check for exceptions.
			# Check if the requested data exceeds the maximum address.
			if ((Start + qty - 1) > self._addrlimits[Function]):
				Function = Function + 128	# Create error code.
				exceptioncode = 2		# Exception code.
			# Qty of registers is out of protocol range.
			elif ((qty < 1) or (qty > self._protocollimits[Function])):
				Function = Function + 128	# Create error code.
				exceptioncode = 3		# Exception code.
			# Qty for registers does not equal the size of data sent.
			elif ((qty * 2) != len(data)):
				Function = Function + 128	# Create error code.
				exceptioncode = 3		# Exception code.

			return TransID, UnitID, Function, Start, (qty, data), exceptioncode


		# Function is not supported.
		else:
			# This error code needs special treatment in case of bad function
			# codes that are very large.
			Function = (Function & 0xff) | 0x80	# Create error code.
			exceptioncode = 1		# Exception code.
			return TransID, UnitID, Function, 0, '\x00\x00', exceptioncode



##############################################################################
# Class to assemble or extract data from Modbus/TCP client messages.
#
class MBTCPClientMessages:

	def __init__(self):
		pass

	########################################################
	def MBRequest(self, TransID, UnitID, FunctionCode, Addr, Qty, MsgData = None):
		"""Make a modbus client request message.
		Parameters:
		TransID (integer) = Transaction ID.
		UnitID (integer) = Unit ID.
		FunctionCode (integer) = Function code.
		Addr (integer) = Data address.
		Qty (integer) = Number of addresses to read or write.
		MsgData (binary string) = Data in Modbus binary string format. Valid data is required for
			functions 5, 6, 15, and 16. For 1, 2, 3, and 4, this parameter is optional.
		If the function code is not supported, an empty string will be returned. Invalid data
			will cause an exception to be raised.
		"""

		# Read coils or registers. MBAP length is fixed at 6.
		if FunctionCode in (1, 2, 3, 4):
			return struct.pack('>HHHBBHH', TransID, 0, 6, UnitID, 
				FunctionCode, Addr, Qty)

		# Write single coil or register. MBAP length is fixed at 6.
		elif FunctionCode in (5, 6):
			# Construct message.
			return struct.pack('>HHHBBH2s', TransID, 0, 6, UnitID, 
				FunctionCode, Addr, MsgData)

		# Write multiple coils or registers. MBAP length is variable.
		elif FunctionCode in (15, 16):
			# Construct message.
			count = len(MsgData)
			# MBAP length parameter is size of PDU plus unitid.
			return struct.pack('>HHHBBHHB %ds' % count, TransID, 0, count + 7, UnitID, 
				FunctionCode, Addr, Qty, count, MsgData)

		# Function code is not supported.
		else:
			return ''



	########################################################
	def MBResponse(self, Message):
		"""Extract the data from a server response message.
		Parameters: Message = This is a string containing the raw binary message as received.
		Return values: 
		TransID (integer) = Transaction ID.
		Function (integer) = Function or error code.
		Data or Exception Code = Message data. For a successful request, 
			this is an ASCII string containing the coil or register data. 
			For errors, this is an integer indicating the Modbus exception code.
		If a message cannot be decoded, zeros will be returned for all fields.
		"""

		# Length of complete recieved response.
		ResponseLen = len(Message)

		# Check if this is too short or too long to decode.
		if (ResponseLen < 9) or (ResponseLen > 260):
			# The message could not be unpacked because the length does not match 
			# any known valid message format.
			return (0, 0, '0')

		# Unpack the first part of the message.
		TransID, protocol, length, unit_id, funct = struct.unpack('>HHHBB', Message[0:8])
		# This is the remainder of the message.
		datapackage = Message[8:]

		# Now unpack the data portion of the message.
		# Check if this is a response to a read function.		
		if (funct in [1, 2, 3, 4]):
			# Decode the data part of the message.
			bytes_data, MsgData = struct.unpack('>B %ds' % (len(datapackage) - 1), datapackage)
			return  (TransID, funct, MsgData)

		# Check if this is a response to a write function.
		elif (funct in [5, 6, 15, 16]):
			# Decode the data part of the message.
			bytes_data, MsgData = struct.unpack('>H %ds' % (len(datapackage) - 2), datapackage)
			return  (TransID, funct, MsgData)

		# Check if this is an error response.
		elif (funct > 127):
			# Decode the message. Ignore anything after the first byte.
			exceptioncode = struct.unpack('>B', datapackage[0])[0]
			return  (TransID, funct, exceptioncode)

		# We don't know how to handle this function code.
		else:
			return (0, 0, '0')
			

##############################################################################

