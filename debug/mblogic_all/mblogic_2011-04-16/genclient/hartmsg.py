#!/usr/bin/python

##############################################################################
# Project: 	MBLogic
# Module: 	hartmsg.py
# Purpose: 	Provides base functions to create Hart Foundation messages.
# Language:	Python 2.6
# Date:		02-Sep-2010.
# Version:	28-Jan-2011.
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
# Library used for Checksum calculation
import operator

##############################################################################
"""
This module is used for assembling and dissassembling Hart Foundation messages.
Each method either accepts a set of parameters and constructs a valid
Hart serial message ready for transmission, or it takes a Hart
message which has bee received and dissassembles it into its components
so that the contents may be read. 

Functions:
	_ComputeChecksum = Computes a Checksum on the passed in data.
	HartRequestUniqueID = Construct a Hart message to read 
		the slave (device) Unique Identifier.
	HartHandleUniqueID = Extract Revision Level of Hart Command (ProtocolVersion),
		Number of Request Preambles(PreambleSize), and Device Unique Identifier
		(long form address).
	HartRequest = Make a hart foundation client request message.	
	HartResponse = Extract the data from a device response message.

The HART Communications Protocol (Highway Addressable Remote Transducer Protocol)
is an early implementation of Fieldbus, a digital industrial automation protocol.
Its most notable advantage is that it can communicate over legacy 4-20 mA analog
instrumentation wiring, sharing the pair of wires used by the older system.
According to Emerson, due to the huge installed base of 4-20 mA systems throughout
the world, the HART Protocol was one of the most popular industrial protocols today.
HART protocol made a transition protocol for users who were comfortable using the 
legacy 4-20 mA signals, but wanted to implement a smart protocol.
Industries seem to be using Foundation fieldbus (also by Rosemount) more and more
as users become familiar with current technology.
The protocol was developed by Rosemount Inc., built off the Bell 202 early 
communications standard, in the mid-1980s as proprietary digital communication 
protocol for their smart field instruments. Soon it evolved into HART.
In 1986, it was made an open protocol. Since then, the capabilities of the protocol
have been enhanced by successive revisions to the specification.
There are two main operational modes of HART instruments: analog/digital mode,
and multidrop mode.
Peer-to-Peer mode (analog/digital): Here the digital signals are overlayed on the 
4-20 mA loop current. Both the 4-20 mA current and the digital signal are valid
output values from the instrument.The polling address of the instrument is set to 0.
Only one instrument can be put on each instrument cable signal pair.
Multi-drop mode (digital): In this mode only the digital signals are used.
The analog loop current is fixed at 4 mA. In multidrop mode it is possible to have
up to 15 instruments on one signal cable. The polling addresses of the instruments
will be in the range 1-15. Each meter needs to have a unique address.
"""


########################################################
def _ComputeChecksum(Data):
	"""
		Computes a Checksum on the passed in data. The Checksum is composed
		of an XOR of all the bytes starting from the Start Byte and Ending 
		with the last byte of the data field, including those bytes.
		Parameters:
			Data = The data to create a Checksum of. Accepts a string or a
				integer list
		Return:
			Checksum = calculated checksum
	"""
	# Linear Redundancy Check calculation
	return chr(reduce(operator.xor, map(ord, Data)))


########################################################
def HartRequestUniqueID(UnitID):
	"""
		Construct a Hart message to read the slave (device) Unique Identifier.
		Unit ID setting in configuration file is in Short Form/Frame (Rev 4) [0-15, x0-xF], 
		system must use Hart Universal Command 0 to read Unique Identifier 
		in Long Form/Frame (Rev5), 4311744513-274877906943 (2exp38 or 
		0101000001-3FFFFFFFFF in Hex mode).
		Parameters:
			UnitID (integer) = Slave Unit ID (in short frame).
		Return:
			Message = Universal Hart Command 0 message to be used		
	"""

	# Unit ID in string format, with the Primary Master flag
	struid = struct.pack('>B', (UnitID + 128))
	# Message without preamble frame, nor checksum byte
	Content = []
	# Complete protocol frame
	Message = []
	# Set preamble frame (20 bytes), for synchronization and carrier detect.
	PreambleFrame = '\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
	# Frame Delimiter or Start Character, for synchronization and information purposes
	# Master Request (STX), Short Address, 0x02
	StartDelimiter = '\x02'
	#Hart Command Number
	HartCommand = '\x00'
	# Length (in chars) of Data
	DataLength = '\x00'
	# Segment of data to calculate checksum
	Content = StartDelimiter + struid + HartCommand + DataLength
	# Checksum calculation
	Checksum = _ComputeChecksum(Content)
	# Complete Hart protocol message/command
	Message = PreambleFrame + Content + Checksum
	return Message, 23


########################################################
def HartHandleUniqueID(ReplyMsg):
	"""
		Extract Revision Level of Hart Command (ProtocolVersion), Number of Request 
		Preambles(PreambleSize), and Device Unique Identifier (long form address).
		The Unique ID is composed by:
			- Device Manufacturer Code (1 char / byte)
			- Manufacturer Device Type (1 char / byte)
			- Device ID Number ( 3 chars / bytes)
		Parameters:
			ReplyMsg = Hart frame to be evaluated
		Return:
			ProtocolVersion = hart protocol version of device
			PreambleSize = preamble size, configured in device
			LongAddress = Device long address
	"""

	# Data package to be decoded
	MsgData = ''
	# Default values of communications parameters
	ProtocolVersion = 4
	PreambleSize = 20
	LongAddress = '\x0000000000'

	# Decode Hart Foundation frame received
	FunctionCode, MsgData, ExceptionCode = HartResponse(ReplyMsg)
	# Evaluate if length of data is correct and no error
	if (len(MsgData) > 11 and ExceptionCode == 0):
		# Decode the received data, and read communications parameters of Hart device
		# Protocol Version
		ProtocolVersion = MsgData[4]
		# Preamble size (in char - bytes)
		PreambleSize = MsgData[3]
		# Read and process first byte of long address
		# Manufacturer Identification Code - 1 Byte
		MfrIDCode = MsgData[1]
		# Bitwise AND of 6 less significant bits
		MfrIDLSBits = MfrIDCode & 63
		# Manufacture Device Type - 1 Byte
		MfrDevType = MsgData[2]
		# Device Identification Number - 3 Bytes
		DevideIDNumberMSB = MsgData[9]
		DevideIDNumberCB = MsgData[10]
		DevideIDNumberLSB = MsgData[11]
		# Unique Identifier (Long Address) with a Primary Master Flag
		LongAddress = struct.pack('>BBBBB', (MfrIDLSBits + 128), MfrDevType, \
			DevideIDNumberMSB , DevideIDNumberCB, DevideIDNumberLSB)
	# Return device communications parameters		
	return ProtocolVersion, PreambleSize, LongAddress


########################################################
def HartRequest(PreambleSize, UnitID, FunctionCode):
	"""
		Make a Hart client request message.
		This version implement a Secondary Master.
		Data is not required for Hart functions 0, 1, 2 and 3.
		Parameters:
			PreambleSize (integer) = size (in char/bytes) of preamble for this message (slave especific)
			UnitID (hex string) = Unit ID, in long form address.
			FunctionCode (integer) = Function code. If the function code is not supported,
				an empty string will be returned. Invalid data will cause an exception to be raised.
		Return:
			Message = Hart Foundation frame to be send throught serial port.
			Responsesize = Size (in chars) of expected device response, if ok.
	"""

	# Lookup table: Hart Foundation function to expected message size
	# (Minimal size or # of chars for succesfull slave response:
	# Protocol overhead + data without preamble frame)
	function2size = {'0' : 23, '1' : 16, '2' : 19, '3' : 35}

	# Message without preamble frame, nor checksum byte
	Content = []
	# Complete protocol frame
	Message = []
	""" Set preamble frame (5 to 20 bytes) for a command, 
	Used for to synchronization and carrier detect in Hart messages.
	Preamble char = 255 (FF in hex mode)
	"""	
	PreambleFrame = '\xff' * PreambleSize

	# Read equipment (slave) Unique Identifier, Read primary variable,
	# Read current and percent of range, Read all dynamic variables and current
	if FunctionCode in [0, 1, 2, 3]:
		# Frame Delimiter or Start Character, for synchronization and information purposes
		# Master Request (STX), Long Address, 0x82
		StartDelimiter = '\x82'				
		# Hart Command Number
		HartCommand = struct.pack('>B', FunctionCode)
		# Length (in chars) of Data
		DataLength = struct.pack('>B', 0)
		# Segment of data to calculate checksum
		Content = StartDelimiter + UnitID + HartCommand + DataLength
		# Checksum calculation
		Checksum = _ComputeChecksum(Content)
		# Complete Hart protocol message/command
		Message = PreambleFrame + Content + Checksum
		Responsesize = function2size[str(FunctionCode)]
		return Message, Responsesize
	# Function code is not supported.
	else:
		return '', 0


########################################################
def HartResponse(RawMessage):
	"""
		Extract the data from a device response message.
		Parameters: 
			RawMessage = This is a string containing the raw binary message as received.
		Return values: 
			Function (integer) = Function or error code.
			Data = Message data. For a successful request, 
				this is an ASCII string containing the coil or register data. 
				For errors, this is an integer indicating the Hart exception code.
			Exception = if error, is an integer indicating the Hart exception code.
				Otherwise is 0.
			If a message cannot be decoded, it will return 255 for function, an empty
			data string, and an exception code.
	"""

	# Message without preamble frame, nor checksum byte
	ProtocolMessage = []
	# Protocol package, without preamble frame
	Message = []
	# Data package, inside the message		
	DataPackage = []
	# Dictionary of data, to be returned		
	MsgData = []

	# Preamble char = 255 (FF in hex mode)
	PreambleChar = '\xff'
	# Discard the preamble frame from the message
	Index = 0
	while (RawMessage[Index] == PreambleChar):
		Index = Index + 1
	Message = RawMessage[Index:]
	# Length of received response.
	ResponseLen = len(Message)

	# Check if this is too short or too long to decode, according to Hart standard.
	if (ResponseLen < 7) or (ResponseLen > 264):
		# The message could not be unpacked because the length does not match 
		# any known valid message format.
		return 255, '', 8

	# Checksum received value.
	ChecksumReceived = Message[(ResponseLen-1):]
	# Message without the checksum value, nor preamble frame
	ProtocolMessage = Message[:(ResponseLen-1)]
	# Calculate the checksum for received message
	ChecksumComputed = _ComputeChecksum(ProtocolMessage)
	# Evaluate the Checksum
	if (ChecksumReceived != ChecksumComputed):
		return 255, '', 8

	# Extract the start character / frame delimiter
	StartChar = struct.unpack('>B', ProtocolMessage[0:1])[0]
	# If start character is \x06 (6 Decimal), this is a short address response.
	if (StartChar == 6):
		Function = struct.unpack('>B', ProtocolMessage[2:3])[0]
		# This is the data of the message.
		DataPackage = ProtocolMessage[6:]
	# If start character is \x86 (134 Decimal), this is a long address response.
	elif (StartChar == 134):
		Function = struct.unpack('>B', ProtocolMessage[6:7])[0]
		# This is the data of the message.
		DataPackage = ProtocolMessage[10:]
	else:
		pass

	# Length of data segment
	bytes_data = len(DataPackage)
	# Check if data length is the expected for that command.
	if ((Function == 0 and bytes_data < 12) or (Function == 1 and bytes_data != 5)
		or (Function == 2 and bytes_data != 8) or (Function == 3 and bytes_data != 24)):
		# No data passed
		return 255, '', 8
	else:
		# Construct Data Pack.
		MsgData = struct.unpack('>%sB' % len(DataPackage), DataPackage)
		# Return received function, data, and no error code
		return Function, MsgData, 0
