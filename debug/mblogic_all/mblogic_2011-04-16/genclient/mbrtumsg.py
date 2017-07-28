#!/usr/bin/python

##############################################################################
# Project: 	MBLogic
# Module: 	mbrtumsg.py
# Purpose: 	Provides base functions to create ModbusRTU messages.
# Language:	Python 2.6
# Date:		04-Aug-2010.
# Version:	26-Jan-2011.
# Author:	J. Pomares.
# Copyright:	2010 - 2011 - Juan Pomares       	<pomaresj@gmail.com>
# Based on code of Michael Griffin <m.os.griffin@gmail.com>
# 
# This file is proposed to be optional part of MBLogic.
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

# Library used for data type handle and conversion
import struct

##############################################################################
"""
This module is used for assembling and dissassembling Modbus/RTU messages.
Each method either accepts a set of parameters and constructs a valid
Modbus/RTU message ready for transmission, or it takes a Modbus/RTU
message which has bee received and dissassembles it into its components
so that the contents may be read. 

Functions:
	_ComputeCRC = Computes a crc16 on the passed in data.
	MBRTURequest = Make a modbus RTU client request message.	
	MBRTUResponse = Extract the data from a server response message.

A Modbus RTU message consists of two parts, a Modbus Application Protocol
header (MBAP), and a Protocol Data Unit (PDU). 

MBAP Header
- Unit ID: (1 byte) This is the Modbus slave address number.

PDU:
- Function code: (1 byte) This is the Modbus function number.
- Data address: (2 bytes) This is the Modbus data address.
- The remainder of the PDU is determined by the function being used.
See the official Modbus RTU specifications for more details.

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
If there is an error in the message, a Modbus/RTU exception code is generated.
Modbus/RTU exception codes are generated in the following order: 1, 3, 2, 4, 8. When
an critical exception is found, processing stops there and the code is returned.

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
Exception Code 8 (All functions): Received modbus frame has an unexpected lenght, or an CRC16 error.
"""

# Bit position to integer conversion lookup table
bin2int = {0:1, 1:2, 2:4, 3:8, 4:16, 5:32, 6:64, 7:128}

# Struct to handle the CRC16 calculation		
crc16table = [0, 49345, 49537, 320, 49921, 960, 640, 49729, 50689, 1728, \
	1920, 51009, 1280, 50625, 50305, 1088, 52225, 3264, 3456, 52545, 3840, 53185, \
	52865, 3648, 2560, 51905, 52097, 2880, 51457, 2496, 2176, 51265, 55297, 6336, \
	6528, 55617, 6912, 56257, 55937, 6720, 7680, 57025, 57217, 8000, 56577, 7616, \
	7296, 56385, 5120, 54465, 54657, 5440, 55041, 6080, 5760, 54849, 53761, 4800, \
	4992, 54081, 4352, 53697, 53377, 4160, 61441, 12480, 12672, 61761, 13056, 62401, \
	62081, 12864, 13824, 63169, 63361, 14144, 62721, 13760, 13440, 62529, 15360, \
	64705, 64897, 15680, 65281, 16320, 16000, 65089, 64001, 15040, 15232, 64321, \
	14592, 63937, 63617, 14400, 10240, 59585, 59777, 10560, 60161, 11200, 10880, \
	59969, 60929, 11968, 12160, 61249, 11520, 60865, 60545, 11328, 58369, 9408, 9600, \
	58689, 9984, 59329, 59009, 9792, 8704, 58049, 58241, 9024, 57601, 8640, 8320, \
	57409, 40961, 24768, 24960, 41281, 25344, 41921, 41601, 25152, 26112, 42689, \
	42881, 26432, 42241, 26048, 25728, 42049, 27648, 44225, 44417, 27968, 44801, \
	28608, 28288, 44609, 43521, 27328, 27520, 43841, 26880, 43457, 43137, 26688, \
	30720, 47297, 47489, 31040, 47873, 31680, 31360, 47681, 48641, 32448, 32640, \
	48961, 32000, 48577, 48257, 31808, 46081, 29888, 30080, 46401, 30464, 47041, \
	46721, 30272, 29184, 45761, 45953, 29504, 45313, 29120, 28800, 45121, 20480, \
	37057, 37249, 20800, 37633, 21440, 21120, 37441, 38401, 22208, 22400, 38721, \
	21760, 38337, 38017, 21568, 39937, 23744, 23936, 40257, 24320, 40897, 40577, \
	24128, 23040, 39617, 39809, 23360, 39169, 22976, 22656, 38977, 34817, 18624, \
	18816, 35137, 19200, 35777, 35457, 19008, 19968, 36545, 36737, 20288, 36097, \
	19904, 19584, 35905, 17408, 33985, 34177, 17728, 34561, 18368, 18048, 34369, \
	33281, 17088, 17280, 33601, 16640, 33217, 32897, 16448]


########################################################
def _ComputeCRC(Data):
	"""
		Computes a crc16 on the passed in data.
		The difference between modbus's	crc16 and a normal crc16
	   is that modbus starts the crc value out at 0xffff.
		Parameters:
			Data = The data to create a crc16. Accepts a string
			or a integer list
   	Return:
 		  	strcrc16 = calculated crc16, in string format
   """
   
	result = []
	crc16 = 0xffff
	pre = lambda x: x
	if isinstance(Data, str): pre = lambda x: ord(x)
	for a in Data:
		crc16 = ((crc16 >> 8) & 0xff) ^ crc16table[(crc16 ^ pre(a)) & 0xff];
	strcrc16 = struct.pack('<H', crc16)
	return strcrc16


########################################################
def MBRTURequest(UnitID, FunctionCode, Addr, Qty, Data = None):
	"""
		Make a modbus RTU client request message.
		Parameters:
			UnitID (integer) = Unit ID.
			FunctionCode (integer) = Function code.
			Addr (integer) = Data address.
			Qty (integer) = Number of addresses to read or write.
			Data (binary string) = Data in Modbus binary string format. Valid data is required for
			functions 5, 6, 15, and 16. For 1, 2, 3, and 4, this parameter is optional.
		If the function code is not supported, an empty string will be returned. Invalid data
		will cause an exception to be raised.
		Returns:
			Message = ModbusRTU frame to be send throught serial port.
			Responsesize = Size (in chars) of expected slave response, if ok.
	"""
	
	# Internal variables
	Content = []
	Message = []
	MsgData = ''
	# Initial Value for CRC16 calculation
	Crc16 = 0xffff
		# Convert Data for write messages with single discrete data (coil).
	if FunctionCode == 5:
		# Verify if there is data
		try:
			Data
		except:
			# No data passed
			return '', 0
		# Construct value if data is integer.
		try:
			int(Data)
			if Data == 0:
				MsgData = '\x00\x00'
			else:
				MsgData = '\xff\x00'					
		except:
			# Construct value if data is boolean.
			if Data == True:
				MsgData = '\xff\x00'
			else:
				MsgData = '\x00\x00'
	# Convert Data for write messages with single word data (16 bits holding register).
	if FunctionCode == 6:
		# Verify if there is data
		try:
			Data
		except:
			# No data passed
			return '', 0
		# Construct value if data is integer.
		try:
			int(Data)
			# Construct Data Value.
			MsgData = struct.pack('>H', Data)
		except:
			# Construct value if data is boolean.
			if Data == True:
				MsgData = '\x00\x01'
			else:
				MsgData = '\x00\x00'			
	# Convert Data for write messages with multiple discrete data (coils).
	if FunctionCode == 15:
		try:
			Data
		except:
			# No data passed
			return '', 0		
		if (len(Data)>0):
			bitindex = 0
			bytedata = 0
			for dataindex in range(0, len(Data)):
				# Construct Data Pack.
				# If data is True or and integer, result is 1, otherwise is 0
				if (Data[dataindex] == True) or (Data[dataindex] > 0):
					bytedata = bytedata + bin2int[bitindex]
				bitindex += 1
				# Validate if current character convertion is finished 
				if (bitindex == 8) or (dataindex == len(Data)-1):
					hexdata = struct.pack('>B', bytedata)
					MsgData = MsgData + hexdata
					bitindex = 0
					bytedata = 0
		else:
			# No data passed
			return '', 0
	# Convert Data for write messages with multiple word data (16 bits holding registers).
	if FunctionCode == 16:
		try:
			Data
		except:
			# No data passed
			return '', 0		
		if (len(Data)>0):
			# Convert each data into a 16-bits word
			for dataindex in range(0, len(Data)):
				# Construct value if data is integer.
				try:
					int(Data[dataindex])
					# Construct Data Pack.
					hexdata = struct.pack('>H', Data[dataindex])
				except:
					# Construct value if data is boolean.
					if Data[dataindex] == True:
						hexdata = '\x00\x01'
					else:
						hexdata = '\x00\x00'			
				# Append new word to data frame
				MsgData = MsgData + hexdata
		else:
			# No data passed
			return '', 0
		# Read coils or discrete inputs.
	if FunctionCode in [1, 2]:
		# Construct message.
		Content = struct.pack('>BBHH', UnitID, FunctionCode, Addr, Qty)
		Crc16 = _ComputeCRC(Content)
		Message = Content+Crc16
		# Size (# of chars) required in slave response if ok
		# Calculate size for expected modbus response (rounded to 8 bits words)
		if (Qty > int(Qty / 8)*8):
			Responsesize = (int(Qty / 8) + 1 + 5)
		else:
			Responsesize = (int(Qty / 8) + 5)
		return Message, Responsesize
	# Read input or holding registers.
	elif FunctionCode in [3, 4]:
		# Construct message.
		Content = struct.pack('>BBHH', UnitID, FunctionCode, Addr, Qty)
		Crc16 = _ComputeCRC(Content)
		Message = Content+Crc16
		# Size (# of chars) required in slave response if ok
		Responsesize = (int(Qty * 2) + 5)
		return Message, Responsesize
	# Write single coil or register.
	elif FunctionCode in [5, 6]:
		# Construct message.
		Content = struct.pack('>BBH', UnitID, FunctionCode, Addr) + MsgData
		Crc16 = _ComputeCRC(Content)
		Message = Content+Crc16
		# Size (# of chars) required in slave response if ok
		Responsesize = 8
		return Message, Responsesize
	# Write multiple coils or registers.
	elif FunctionCode in [15, 16]:
		# Construct message.
		count = len(MsgData)
		# MBAP length parameter is size of PDU plus unitid.
		Content =  struct.pack('>BBHHB', UnitID, FunctionCode, Addr, Qty, len(MsgData)) + MsgData
		Crc16 = _ComputeCRC(Content)
		Message = Content+Crc16
		# Size (# of chars) required in slave response if ok
		Responsesize = 8
		return Message, Responsesize
	# Function code is not supported.
	else:
		return '', 0


########################################################
def MBRTUResponse(Message):
	"""
		Extract the data from a server response message.
		Parameters:
			Message = This is a string containing the raw binary message as received.
		Return values: 
			UnitID = Unit ID of slave (server) device
			FunctionCode (integer) = Function or error code.
			MsgData = Message data. For a successful request, this is a list of boolean values or 16 bits word
			registers, containing the coil or register data. Otherwise is empty.
			ExceptionCode = In case of errors, this is an integer indicating the Modbus exception code.
			Otherwise is 0.
		If a message cannot be decoded, zeros will be returned for all fields.
	"""

	# Internal variables
	ProtocolMessage = []
	MsgData = []
	# Initials Values for CRC16 calculation
	CrcReceived = 0xffff
	CrcComputed = 0xffff
	# Length of complete received response.
	ResponseLen = len(Message)
	# Check if this is too short or too long to decode, according to ModbusRTU standard.
	if (ResponseLen < 5) or (ResponseLen > 256):
		# The message could not be unpacked because the length does not match 
		# any known valid message format.
		return 0, 0, MsgData, 8
	# CRC16 received value.
	CrcReceived = Message[(ResponseLen-2):]
	# Message without the CRC value
	ProtocolMessage = Message[0:(ResponseLen-2)]
	# Calculate the CRC16 for received message
	CrcComputed = _ComputeCRC(ProtocolMessage)
	# Evaluate the CRC
	if not (CrcReceived == CrcComputed):
		# Exception code for Memory Parity Error, used to shown an CRC error in message
		return 0, 0, MsgData, 8
	# Unpack the first part of the message.
	UnitID, FunctionCode = struct.unpack('>BB', ProtocolMessage[0:2])
	# This is the remainder of the message.
	datapackage = ProtocolMessage[2:]
	# Now unpack the data portion of the message.
	# Check if this is a response to a read function for coils or inputs discrete data.
	if (FunctionCode in [1, 2]):
		# Decode the data part of the message.
		try:
			datapackage
		except:
			# No data passed
			return UnitID, FunctionCode, MsgData, 3		
		if (len(datapackage)>0):
			for dataindex in range(1, len(datapackage)):
				# Construct Data Pack.
				intdata = struct.unpack('>B', datapackage[dataindex])[0]
				for bitindex in range(0,8):
					if intdata & (2**bitindex) == 0:
						MsgData.append(False)
					else:
						MsgData.append(True)							
			return UnitID, FunctionCode, MsgData, 0
		else:
			# No data passed
			return UnitID, FunctionCode, MsgData, 3		
	# Check if this is a response to a read function for input or holding registers.
	elif (FunctionCode in [3, 4]):
		# Decode the data part of the message.
		try:
			datapackage
		except:
			# No data passed
			return UnitID, FunctionCode, MsgData, 3		
		if (len(datapackage)>0):
			for dataindex in range(0, ((len(datapackage)-1)/2)):
				# Construct Data Pack.
				strdata = (datapackage[dataindex*2+1:dataindex*2+3])
				MsgData.append(struct.unpack('>H', strdata)[0])
			return UnitID, FunctionCode, MsgData, 0
		else:
			# No data passed
			return UnitID, FunctionCode, MsgData, 3		
	# Check if this is a response to a write function.
	elif (FunctionCode in [5, 6, 15, 16]):
		MsgData = [0,0]
		# Decode the data part of the message.
		MsgData[0], MsgData[1] = struct.unpack('>HH', datapackage)
		if (FunctionCode == 5):
			if (MsgData[1] == 0):
				MsgData[1] = False
			else:
				MsgData[1] = True					
		return UnitID, FunctionCode, MsgData, 0
	# Check if this is an error response.
	elif (FunctionCode > 127):
		# Decode the message. Ignore anything after the first byte.
		ExceptionCode = struct.unpack('>B', datapackage[0])[0]
		return UnitID, FunctionCode, MsgData, ExceptionCode
	# We don't know how to handle this function code.
	else:
		return 0, 0, MsgData, 1
