##############################################################################
# Project: 	MBLogic
# Module: 	SBusMsg.py
# Purpose: 	Provides SBus-Ethernet base functions.
# Language:	Python 2.6
# Date:		07-Oct-2009.
# Ver.:		09-May-2010.
# Copyright:	2009 - 2010 - Michael Griffin       <m.os.griffin@gmail.com>
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
This module implements constructing messages for the SAIA EtherSBus protocol.

The following commands are supported:
2 - Read Flags
3 - Read Inputs
5 - Read Outputs
6 - Read Registers
11 - Write flags
13 - Write outputs
14 - Write Registers


The message strings being constructed are:


1) Requests from client to server:
Common:
	Length (L)
	Version (B) = Protocol version (always 1).
	Type (B) = Protocol type (always 0).
	Sequence (H) = An incrementing integer.
	Telegram attribute (B) = Indicates this is a request (always 0).
	Destination (B) = Serial station address.

For read operations:
	Command code (B) = Code indictating command (2, 3, 5, 6).
	Count (B) = Number of flags or registers requested - 1.
	Addr (H) = Data table address for start of request.
	CRC (H) = Message CRC

For writing registers:
	Command code (B) = Code indictating command (14).
	Count (B) = Number of registers to write (as bytes + 1).
	Addr (H) = Data table address for start of request.
	CRC (H) = Message CRC

For writing flags, outputs:
	Command code (B) = Code indictating command (11, 13).
	Count (B) = Number of flags or registers to write (as message length + 2).
	Addr (H) = Data table address for start of request.
	FIO count (B) = Number of IO to write (number of IO - 1).
	CRC (H) = Message CRC


2) Response from server to client:

Common:
	Length (L)
	Version (B) = Protocol version (always 1).
	Type (B) = Protocol type (always 0).
	Sequence (H) = An incrementing integer.
	Telegram attribute (B) = Indicates this is a request 
				(1 = response, 2 = ACK/NAK).

For read operations:
	Data (variable length) = Data read. The length depends on the quantity.
	CRC (H) = CRC.

For write operations:
	msgack (H) = 0 for OK, non-zero for error.
	CRC (H) = CRC.


L = 32 bit signed integer integer.
H = 16 bit signed integer.
B = Single byte.
"""

##############################################################################
class ParamError(ValueError):
	"""Used to help raise exceptions for invalid parameters.
	"""
class MessageLengthError(ValueError):
	"""Used to help raise exceptions for message responses of an incorrect
	length which prevent the message from being decoded.
	"""
class CRCError(ValueError):
	"""Used to help raise exceptions for bad CRCs.
	"""


##############################################################################
# Class to assemble or extract data from SBus/UDP client messages.
#
class SBusClientMessages:
	"""
	This class constructs and decodes client messages for the SAIA 
	EtherSBus protocol.
	"""

	def __init__(self):
		pass


	########################################################
	def SBRequest(self, msgsequence, stnaddr, cmdcode, datacount, dataaddr, msgdata = None):
		"""Make an SBus Ethernet client request message.
		Parameters:
			msgsequence (integer) = A sequentialy incrementing integer (0 - 65535).
			stnaddr (integer) = Serial station address (0 - 255). 
			cmdcode (integer) = The SBus command (2, 3, 5, 6, 11, 13, or 14).
			datacount (integer) = Number of addresses to read or write (0 - 255).
			dataaddr (integer) = Data table address to read or write (0 - 65535).
			msgdata (binary string) = The data to write (optional). This must be
				a packed binary string. 
		Returns: (string) = A packed binary string containing the encoded message.
		Invalid parameters (including unsupported command codes) will cause a 
			ParamError exception. Invalid data will also cause an 
			exception to be raised.
		"""


		# Verify the parameters.
		# Check the data count.
		if (datacount < 1):
			raise ParamError, 'Invalid data count'
		# Boolean flags, inputs, and outputs must be no more than 128.
		elif (cmdcode in (2, 3, 5, 11, 13) and (datacount > 128)):
			raise ParamError, 'Invalid data count'
		# Registers must be no more than 32.
		elif (cmdcode in (6, 14) and (datacount > 32)):
			raise ParamError, 'Invalid data count'

		# The other parameters are inherently checked by the packing operation.

		# Read flags or registers. 
		if cmdcode in (2, 3, 5, 6):
			msglength = 16
			msg = struct.pack('>LBBHB BBBH', msglength, 0, 0, msgsequence, 0, 
				stnaddr, cmdcode, datacount - 1, dataaddr)

		# Write flags, outputs. 
		elif cmdcode in (11, 13):
			msglength = 17 + len(msgdata)
			bytecount = len(msgdata) + 2
			fiocount = datacount - 1

			# Check if the number of bits matches the supplied data parameter.
			bytelen, bitremain = divmod(datacount, 8)
			if (bitremain > 0):
				bytelen += 1
			if (bytelen != len(msgdata)):
				raise ParamError, 'Data length mismatch'

			msg = struct.pack('>LBBHB BBBHB %ds' % len(msgdata) ,msglength, 0, 0, msgsequence, 0, 
				stnaddr, cmdcode, bytecount, dataaddr, fiocount, msgdata)

		# Write register. 
		elif (cmdcode == 14):
			msglength = 16 + len(msgdata)
			bytecount = (datacount * 4) + 1

			# Check if the amount of data supplied matches the request parameter.
			if (len(msgdata) != (datacount * 4)):
				raise ParamError, 'Data length mismatch'

			msg = struct.pack('>LBBHB BBBH %ds' % len(msgdata) ,msglength, 0, 0, msgsequence, 0, 
				stnaddr, cmdcode, bytecount, dataaddr, msgdata)

		# Command code is not supported.
		else:
			raise ParamError, 'Command code not supported'

		# Append the CRC and return the message.
		return struct.pack('>%ds H' % len(msg), msg, SBusCRC(msg))



	########################################################
	def SBResponse(self, Message):
		"""Extract the data from a server response message.
		Parameters: Message = This is a string containing the raw binary message as received.
		Returns:
			telegramattr (integer) = The telegram attribute. 
					0 = Request, 1 = response, 2 = ack/nak. This should be 1 for a
					response to a read, and 2 for a response to a write.
			msgsequence (integer) = This should be an echo of the sequence in the request.
			msgdata (string) = A packed binary string with the message data. If the 
				telegramattr was ack/nak, then this will contain the ack/nak code.
				0 = ack. Non-zero = nak (error).
		An invalid message length will cause a MessageLengthError exception.
		A bad CRC will raise a CRCError exception.
		"""

		# Length of complete received response.
		ResponseLen = len(Message)

		# Check if this is too short or too long to decode.
		if (ResponseLen < 11) or (ResponseLen > 255):
			# The message could not be unpacked because the length does not match 
			# any known valid message format.
			raise MessageLengthError, 'Invalid message length.'


		# Unpack the message.
		(msglength, msgversion, msgtype, msgsequence, telegramattr, 
			msgdata, msgcrc) = struct.unpack('>LBBHB %ds H' % (ResponseLen - 11), Message)

		# Calculate the actual CRC.
		calccrc = SBusCRC(Message[0:-2])

		# Verify the CRC.
		if (msgcrc == calccrc):
			return (telegramattr, msgsequence, msgdata)
		else:
			# Bad CRC.
			raise CRCError, 'Bad CRC'


##############################################################################


##############################################################################
# Class to assemble or extract data from SBus/UDP server messages.
#
class SBusServerMessages:
	"""
	This class constructs and decodes server messages for the SAIA 
	EtherSBus protocol.
	"""

	def __init__(self, maxflags, maxinputs, maxoutputs, maxregisters):
		"""Parameters: 
			maxflags (integer) = Highest flags address.
			maxinputs (integer) = Highest inputs address.
			maxoutputs (integer) = Highest outputs address.
			maxregisters (integer) = Highest registers address.
		"""

		# A dictionary is used to hold the address limits. The dictionary key
		# is the SBus function code, and the data is the address limit.
		self._addrlimits = {2 : maxflags, 3 : maxinputs, 5 : maxoutputs,
			6 : maxregisters, 11 : maxflags, 13 : maxoutputs, 14 : maxregisters }

		# A dictionary is used to hold the constants for the protocol addressing range.
		# These are the  maximum number of elements that can be read or written to at one
		# time without exceeding the protocol limit. 
		self._protocollimits = {2 : 128, 3 : 128, 5 : 128, 6 : 32,
					11 : 128, 13 : 128, 14 : 32 }


	########################################################
	def SBResponse(self, msgsequence, cmdcode, acknak, msgdata = None):
		"""Make an SBus Ethernet server response message.
		Parameters:
			msgsequence (integer) = A sequentialy incrementing integer (0 - 65535).
			cmdcode (integer) = The SBus command (2, 3, 5, 6, 11, 13, or 14).
				This is needed to properly construct the response.
			acknak (integer) = The acknowledgement code for writes. 
			msgdata (binary string) = The data to write (optional). This must be
				a packed binary string. 
		Returns: (string) = A packed binary string containing the encoded message.
		A invalid command code will cause a ParamError exception. 
		"""


		# Read data.
		if cmdcode in (2, 3, 5, 6):
			msglength = 11 + len(msgdata)
			msg = struct.pack('>LBBHB %ds' % (len(msgdata)), msglength, 0, 0, msgsequence, 1, msgdata)

		# Write flags, outputs, registers.
		elif cmdcode in (11, 13, 14):
			msg = struct.pack('>LBBHBH', 13, 0, 0, msgsequence, 2, acknak)

		# Command code is not supported.
		else:
			raise ParamError, 'Command code not supported'


		# Append the CRC and return the message.
		return struct.pack('>%ds H' % len(msg), msg, SBusCRC(msg))


	########################################################
	def SBErrorResponse(self, msgsequence):
		"""Construct a generic SBus error response message with a 
			NAK code of "1".
		Parameters: msgsequence (integer) = Message sequence. 
				This must match the value used by the client.
		"""
		msg = struct.pack('>LBBHBH', 13, 0, 0, msgsequence, 2, 1)
		# Append the CRC and return the message.
		return struct.pack('>%ds H' % len(msg), msg, SBusCRC(msg))



	########################################################
	def SBRequest(self, Message):
		"""Extract the data from a client request message.
		Parameters: Message = This is a string containing the raw binary message as received.
		Returns:
			telegramattr (integer) = The telegram attribute. This should always be 0.
			msgsequence (integer) = An number incremented by the client and used to track messages.
			stnaddr (integer) = The serial station address.
			cmdcode (integer) = The command code. This is not verified for supported codes.
			dataaddr (integer) = The data table address requested.
			datacount (integer) = The number of data values requested.
			msgdata (string) = A packed binary string with the message data.
			resultcode (boolean) = (True = OK), (False = Error).
		An invalid message length will raise a MessageLengthError exception. 
		A bad CRC will raise a CRCError exception.
		If the result code is false, datacount and msgdata may not contain valid data.
		"""
		# Length of complete received request.
		RequestLen = len(Message)

		# Check if this is too short or too long to decode.
		if (RequestLen < 16) or (RequestLen > 255):
			# The message could not be unpacked because the length does not match 
			# any known valid message format.
			raise MessageLengthError, 'Invalid message length.'


		# Unpack the message. The "datapackage" may require further unpacking.
		(msglength, msgversion, msgtype, msgsequence, telegramattr, 
			stnaddr, cmdcode, datacount, dataaddr, datapackage, 
				msgcrc) = struct.unpack('>LBBHB BBBH %ds H' % (RequestLen - 16), Message)

		# Calculate the actual CRC.
		calccrc = SBusCRC(Message[0:-2])
		
		# Verify the CRC.
		if (msgcrc != calccrc):
			raise CRCError, 'Bad CRC'


		# For reading, the data count is offset in the message by -1.
		if cmdcode in (2, 3, 5, 6):
			datacount = datacount + 1
			msgdata = datapackage

		# With write flag, input, and output values we want the 
		# FIO count (number of bits) rather than the "data count" (number of words). 
		elif cmdcode in (11, 13):
			datacount, msgdata = struct.unpack('>B %ds' % (len(datapackage) - 1), datapackage)
			datacount = datacount + 1

		# For writing registers, the data count must be and offset -1.
		# converted from bytes to words.
		elif (cmdcode == 14):
			datacount = (datacount - 1) / 4
			msgdata = datapackage

		# We don't know how to handle this command code.
		else:
			return (telegramattr, msgsequence, stnaddr, cmdcode, dataaddr, 0, '\x00', False)


		# Check for errors.
		# Qty of inputs or outputs is out of range.
		if ((datacount < 1) or (datacount > self._protocollimits[cmdcode])):
			return (telegramattr, msgsequence, stnaddr, cmdcode, dataaddr, datacount, msgdata, False)

		# Check if the requested data exceeds the maximum address.
		if ((dataaddr + datacount - 1) > self._addrlimits[cmdcode]):
			return (telegramattr, msgsequence, stnaddr, cmdcode, dataaddr, datacount, msgdata, False)
			

		# Return the final results.
		return (telegramattr, msgsequence, stnaddr, cmdcode, dataaddr, datacount, msgdata, True)



##############################################################################




##############################################################################

# This is the precalculated hash table for CCITT V.41.
SBusCRCTable = [
0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5, 0x60c6, 0x70e7,
0x8108, 0x9129, 0xa14a, 0xb16b, 0xc18c, 0xd1ad, 0xe1ce, 0xf1ef,
0x1231, 0x0210, 0x3273, 0x2252, 0x52b5, 0x4294, 0x72f7, 0x62d6,
0x9339, 0x8318, 0xb37b, 0xa35a, 0xd3bd, 0xc39c, 0xf3ff, 0xe3de,
0x2462, 0x3443, 0x0420, 0x1401, 0x64e6, 0x74c7, 0x44a4, 0x5485,
0xa56a, 0xb54b, 0x8528, 0x9509, 0xe5ee, 0xf5cf, 0xc5ac, 0xd58d,
0x3653, 0x2672, 0x1611, 0x0630, 0x76d7, 0x66f6, 0x5695, 0x46b4,
0xb75b, 0xa77a, 0x9719, 0x8738, 0xf7df, 0xe7fe, 0xd79d, 0xc7bc,
0x48c4, 0x58e5, 0x6886, 0x78a7, 0x0840, 0x1861, 0x2802, 0x3823,
0xc9cc, 0xd9ed, 0xe98e, 0xf9af, 0x8948, 0x9969, 0xa90a, 0xb92b,
0x5af5, 0x4ad4, 0x7ab7, 0x6a96, 0x1a71, 0x0a50, 0x3a33, 0x2a12,
0xdbfd, 0xcbdc, 0xfbbf, 0xeb9e, 0x9b79, 0x8b58, 0xbb3b, 0xab1a,
0x6ca6, 0x7c87, 0x4ce4, 0x5cc5, 0x2c22, 0x3c03, 0x0c60, 0x1c41,
0xedae, 0xfd8f, 0xcdec, 0xddcd, 0xad2a, 0xbd0b, 0x8d68, 0x9d49,
0x7e97, 0x6eb6, 0x5ed5, 0x4ef4, 0x3e13, 0x2e32, 0x1e51, 0x0e70,
0xff9f, 0xefbe, 0xdfdd, 0xcffc, 0xbf1b, 0xaf3a, 0x9f59, 0x8f78,
0x9188, 0x81a9, 0xb1ca, 0xa1eb, 0xd10c, 0xc12d, 0xf14e, 0xe16f,
0x1080, 0x00a1, 0x30c2, 0x20e3, 0x5004, 0x4025, 0x7046, 0x6067,
0x83b9, 0x9398, 0xa3fb, 0xb3da, 0xc33d, 0xd31c, 0xe37f, 0xf35e,
0x02b1, 0x1290, 0x22f3, 0x32d2, 0x4235, 0x5214, 0x6277, 0x7256,
0xb5ea, 0xa5cb, 0x95a8, 0x8589, 0xf56e, 0xe54f, 0xd52c, 0xc50d,
0x34e2, 0x24c3, 0x14a0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
0xa7db, 0xb7fa, 0x8799, 0x97b8, 0xe75f, 0xf77e, 0xc71d, 0xd73c,
0x26d3, 0x36f2, 0x0691, 0x16b0, 0x6657, 0x7676, 0x4615, 0x5634,
0xd94c, 0xc96d, 0xf90e, 0xe92f, 0x99c8, 0x89e9, 0xb98a, 0xa9ab,
0x5844, 0x4865, 0x7806, 0x6827, 0x18c0, 0x08e1, 0x3882, 0x28a3,
0xcb7d, 0xdb5c, 0xeb3f, 0xfb1e, 0x8bf9, 0x9bd8, 0xabbb, 0xbb9a,
0x4a75, 0x5a54, 0x6a37, 0x7a16, 0x0af1, 0x1ad0, 0x2ab3, 0x3a92,
0xfd2e, 0xed0f, 0xdd6c, 0xcd4d, 0xbdaa, 0xad8b, 0x9de8, 0x8dc9,
0x7c26, 0x6c07, 0x5c64, 0x4c45, 0x3ca2, 0x2c83, 0x1ce0, 0x0cc1,
0xef1f, 0xff3e, 0xcf5d, 0xdf7c, 0xaf9b, 0xbfba, 0x8fd9, 0x9ff8,
0x6e17, 0x7e36, 0x4e55, 0x5e74, 0x2e93, 0x3eb2, 0x0ed1, 0x1ef0
]


########################################################
def SBusCRC(inpdata):
	"""Calculate a CCIT V.41 CRC hash function based on the polynomial
		X^16 + X^12 + X^5 + 1 for SAIA S-Bus (initializer = 0x0000)
	Parameters: inpdata (string) = The string to calculate the crc on.
	Return: (integer) = The calculated CRC.
	"""
	# This uses the built-in reduce rather than importing it from functools
	# in order to provide compatiblity with Python 2.5. This may have to be
	# changed in future for Python 3.x
	return reduce(lambda crc, newchar: 
		SBusCRCTable[((crc >> 8) ^ ord(newchar)) & 0xFF] ^ ((crc << 8) & 0xFFFF), 
			inpdata, 0x0000)

##############################################################################


#############################################################
# signedbin2int32list
def signedbin2int32list(binval):
	""" signedbin2intlist
	Accepts a packed binary string and outputs a list of *signed* 
	32 bit integers. 
	E.g. '\x7F\xFF\xFF\xFF\x80\x00\x00\x00' --> [2147483647, -2147483648]
	binval *must* be of a length in bytes which is evenly divisible by 4 
	to convert to integers.
	"""
	return list(struct.unpack('>%dl' % (len(binval) / 4), binval))


#############################################################
# signedint32list2bin
def signedint32list2bin(intlist):
	"""signedintlist2bin
	Accepts a list of *signed* 32 bit integers and outputs a packed 
	binary string. 
	E.g. [2147483647, -2147483648] --> '\x7F\xFF\xFF\xFF\x80\x00\x00\x00'
	"""
	return struct.pack('>%dl' % len(intlist), *intlist)


##############################################################################

