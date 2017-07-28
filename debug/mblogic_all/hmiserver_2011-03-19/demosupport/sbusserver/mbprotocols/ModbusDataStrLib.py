##############################################################################
# Project: 	Modbus Library
# Module: 	ModbusDataStrLib.py
# Purpose: 	Encode and decode modbus message data.
# Language:	Python 2.5
# Date:		10-Mar-2008.
# Version:	12-Apr-2009.
# Copyright:	2006-2008 - Juan Miguel Taboada Godoy <juanmi@likindoy.org>
# Copyright:	2008 - 2009 - Michael Griffin       <m.os.griffin@gmail.com>
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
This module implements a number of general utility functions which are useful
when working with the Modbus protocol. These functions manipulate Modbus data
which has been packed into strings.


Public Functions:
=================


List Oriented Functions:
========================

The packed binary strings in all list oriented functions are compatible with 
Modbus messages.

1) bin2boollist(binval): Accepts a packed binary and outputs a list of 
	boolean values. 
	E.g. '\x2F' --> [True, True, True, True, False, True, False, False]

2) boollist2bin(boollist): Accepts a list of boolean values and outputs
	a packed binary string. If the length of the input list is not an even
	multiple of 8, it is padded out with False values to fit.
	E.g. [True, True, True, True, False, True, False, False] --> '\x2F'

3) bin2intlist(binval): Accepts a packed binary string and outputs a list of
	*unsigned* 16 bit integers.
	E.g. '\xF1\x23\x12\xD9' --> [61731, 4825]

4) intlist2bin(intlist): Accepts a list of *unsigned* 16 bit integers and 
	outputs a packed binary string.
	E.g. [61731, 4825] --> '\xF1\x23\x12\xD9'

5) signedbin2intlist(binval): Same as bin2intlist but outputs a list of *signed* 
	integers.
	E.g. '\xF1\x23\x12\xD9' --> [-3805, 4825]

6) signedintlist2bin(intlist): Same as intlist2bin but accepts a list of *signed* 
	integers.
	E.g. [-3805, 4825] --> '\xF1\x23\x12\xD9'


String Oriented Functions:
==========================

The following functions operate on character strings. The packed binary strings
are compatible with Modbus messages.

1) inversorbin(data) - Accepts a string in raw binary format (e.g. '\x2F'), and
	returns an ASCII string of 0 and/or 1 characters. E.g. '11110100'

2) bininversor(data) - The inverse of inversorbin.

3) bin2hex(bin) - Accepts a string in raw binary format. (e.g. '\x2F\x91') and
	returns a string in ASCII hexadecimal. (e.g. '2F91')

4) hex2bin(hexa) - The inverse of bin2hex.


Miscellaneous:
==============

1) coilvalue(state) - If state = 0, it returns '\x00\x00', else it returns
	'\xFF\x00'. This is used for providing the correct parameter values 
	required by Modbus function 5 (write single coil).

2) swapbytes(binval) - Accepts a packed binary string and returns another with the 
	bytes swapped. The input must have an even number of bytes.

3) bitreversebin(data) - Reverses the bit order in each byte of data in a binary string.

4) bin2bitstr(data) - Equivalent to inversorbin, but does not reverse the bit order.

5) bit2binstr(data) - Equivalent to bininversor, but does not reverse the bit order.

6) bytepack(lbyte, hbyte) - Pack two unsigned bytes into a signed integer. 
	Packing is little-endian.
	Parameters: lbyte, hbyte - low and high bytes (0 - 255).
	Returns: A signed 16 bit integer.

7) byteunpack(intval) - Unpacks a signed integer into two unsigned bytes.
	Packing is little-endian.
	Parameters: intval - A signed 16 bit integer.
	Returns: lbyte, hbyte - low and high bytes (0 - 255).


Word and Packed Binary String Conversions:
==========================================

1) Int2BinStr(intdata): Pack a 16 bit integer into a binary string. This may be 
	used where a binary string is expected, but the data is in integer format.
	Parameters: intdata (integer).
	Returns: binary string. 

2) BinStr2Int(strdata): Convert a packed binary string to a 16 bit integer. 
	Parameters: intdata (binary string).
	Returns: integer.

3) SignedInt2BinStrintdata): Same as Int2BinStr but accepts a signed integer
	instead of unsigned.

4) BinStr2SignedInt(strdata): Same as BinStr2Int but returns a signed integer
	instead of unsigned.

"""
#############################################################

import binascii
import struct
import array

############################################################################################

#############################################################
# The following are list oriented functions. These provide the equivalent to
# the string oriented functions, but handle lists instead of strings.

#############################################################
# bin2boollist
def bin2boollist(binval):
	"""bin2boollist
	Accepts a packed binary and outputs a list of boolean values. 
	E.g. '\x2F' --> [True, True, True, True, False, True, False, False]
	"""
	# Split the string into a list of characters.
	chararray = list(binval)
	boollist = []
	# Next, look up the boolean equivalents and add them to the output list.
	[boollist.extend(boolhexlist[i]) for i in chararray]
	return boollist


#############################################################
# boollist2bin
def boollist2bin(boollist):
	"""boollist2bin
	Accepts a list of boolean values and outputs a packed binary string. 
	If the length of the input list is not an even multiple of 8, it
	is padded out with False values to fit.
	E.g. [True, True, True, True, False, True, False, False] --> '\x2F'
	"""
	# Convert the list of boolean values into a list of tuples, with the values
	# grouped together in multiples of 8. Then use a dictionary to convert the 
	# string keys into the packed binary strings.

	# First, try this assuming we have a multiple of 8.
	try:
		return ''.join([boolhexlistinvert[tuple(boollist[i : i + 8])] for i in range(0, len(boollist), 8)])

	# If we had an error, then try again after padding it.
	except:

		# Check if the list needs to be padded out to a multiple of 8.
		if ((len(boollist) % 8) != 0):
			boolinput = []
			boolinput.extend(boollist)
			boolinput.extend([False] * (8 - len(boollist) % 8))
		else:
			boolinput = boollist
		return ''.join([boolhexlistinvert[tuple(boolinput[i : i + 8])] for i in range(0, len(boolinput), 8)])


#############################################################
# bin2intlist
def bin2intlist(binval):
	""" bin2intlist
	Accepts a packed binary string and outputs a list of *unsigned* 
	16 bit integers. E.g. '\xF1\x23\x12\xD9' --> [61731, 4825]
	binval *must* be an even number of bytes to convert to integers.
	"""
	return list(struct.unpack('>%dH' % (len(binval) / 2), binval))


#############################################################
# intlist2bin
def intlist2bin(intlist):
	"""intlist2bin
	Accepts a list of *unsigned* 16 bit integers and outputs a packed 
	binary string. E.g. [61731, 4825] --> '\xF1\x23\x12\xD9'
	"""
	return struct.pack('>%dH' % len(intlist), *intlist)


#############################################################
# signedbin2intlist
def signedbin2intlist(binval):
	""" signedbin2intlist
	Same as bin2intlist but outputs a list of *signed* integers.
	binval *must* be an even number of bytes to convert to integers.
	E.g. '\xF1\x23\x12\xD9' --> [-3805, 4825]
	"""
	return list(struct.unpack('>%dh' % (len(binval) / 2), binval))


#############################################################
# signedintlist2bin
def signedintlist2bin(intlist):
	"""signedintlist2bin
	Same as intlist2bin but accepts a list of *signed* 
	integers. E.g. [-3805, 4825] --> '\xF1\x23\x12\xD9'
	"""
	return struct.pack('>%dh' % len(intlist), *intlist)


##############################################################################

#############################################################
# coilvalue
def coilvalue(state):
	"""coilvalue
	This provides the numeric value used to turn a single coil on or off.
	state = a integer where 0 = off, and any non-zero number = on.
	Returns an integer of value 0x0000 (off) or 0xFF00 (on).
	"""
	if (state == 0):
		return '\x00\x00'
	else:
		return '\xFF\x00'

#############################################################
# swapbytes
def swapbytes(binval):
	"""Accepts a packed binary string and returns another with the 
	bytes swapped. The input must have an even number of bytes.
	"""
	binlistarray = array.array('h')
	binlistarray.fromstring(binval)
	binlistarray.byteswap()
	return binlistarray.tostring()
	

#############################################################
# bitreversebin
def bitreversebin(data):
	"""bitreversebin
	Reverses the bit order in each byte of data in a binary string.
	This uses a 256 element dictionary to do the conversion.
	Parameters:
	data = a string in raw binary format.
	Returns a raw binary string with the bits in each byte reversed.
	E.g. '\x2F' returns '\xF4'.
	"""
	return ''.join([_bitreversebindict[data[i]] for i in range(0, len(data))])

#############################################################
# bytepack.
def bytepack(lbyte, hbyte):
	"""Pack two unsigned bytes into a signed integer.
	Packing is little-endian.
	Parameters: lbyte, hbyte - low and high bytes (0 - 255).
	Returns: A signed 16 bit integer.
	"""
	return struct.unpack('<h', struct.pack('<BB', lbyte, hbyte))[0]
	
#############################################################
# byteunpack.
def byteunpack(intval):
	"""Unpacks a signed integer into two unsigned bytes.
	Packing is little-endian.
	Parameters: intval - A signed 16 bit integer.
	Returns: lbyte, hbyte - low and high bytes (0 - 255).
	"""
	return struct.unpack('<BB', struct.pack('<h', intval))


# The following functions may be used to convert between integers and binary strings.

##############################################################################
# Int2BinSt
def Int2BinStr(intdata):
	""" Int2BinStr: Pack a 16 bit unsigned integer into a binary string. 
	This may be used where a binary string is expected, but the data is in 
	unsigned integer format.
	Parameters: intdata (integer).
	Returns: binary string. 
	"""
	return struct.pack('>H', intdata)

##############################################################################
# BinStr2Int
def BinStr2Int(strdata):
	"""BinStr2Int(strdata): Convert a packed binary string to an 
	unsigned 16 bit integer. 
	Parameters: intdata (binary string).
	Returns: integer.
	"""
	return struct.unpack('>H', strdata)[0]

##############################################################################
# SignedInt2BinSt
def SignedInt2BinStr(intdata):
	""" Int2BinStr: Pack a 16 bit signed integer into a binary string. 
	This may be used where a binary string is expected, but the data is in 
	signed integer format.
	Parameters: intdata (integer).
	Returns: binary string. 
	"""
	return struct.pack('>h', intdata)

##############################################################################
# BinStr2SignedInt
def BinStr2SignedInt(strdata):
	"""BinStr2Int(strdata): Convert a packed binary string to a 
	signed 16 bit integer. 
	Parameters: intdata (binary string).
	Returns: integer.
	"""
	return struct.unpack('>h', strdata)[0]


############################################################################################
# The following functions may be used to convert Modbus binary strings to ASCII strings,
# or visa-versa. ASCII strings are strings of '0' and '1' ASCII characters (for coils and
# discrete inputs) or strings of ASCII hexadecimal characters (for registers).

#############################################################
# inversorbin 
def inversorbin(data):
	"""inversorbin 
	Convert packed binary data to an ASCII string of '0' and '1'
	characters and reverse the bit order for Modbus protocol.
	Parameters: data = a string in raw binary format. E.g. '\x2F'
	Returns an ASCII string of 0 and/or 1 characters. E.g. '11110100'
	"""
	return ''.join([hexbininvert[data[i]] for i in range(0, len(data))])


#############################################################
# bininversor
def bininversor(data):
	"""bininversor
	Inverse operation of inversorbin.
	data = An ASCII string of 0 and/or 1 characters. E.g. '11110100'
		Input data must be in multiples of 8 characters.
	Returns a string in raw binary format. E.g. '\x2F'
	There are no checks for invalid input characters!
	"""
	return ''.join([binhexinvert[data[i : i + 8]] for i in range(0, len(data), 8)])


#############################################################
# bin2bitstr
def bin2bitstr(data):
	"""bin2bitstr
	Convert packed binary strings to  ASCII bit strings *without*
		doing any Modbus bit order reversal.
	Parameters:
	data = a string in raw binary format. E.g. '\x2F'
	Returns an ASCII string of 0 and/or 1 characters. E.g. '11110100'
	There are no checks for invalid input characters! 
	"""
	return ''.join([_bin2bitdict[data[i]] for i in range(0, len(data))])

#############################################################
# bit2binstr
def bit2binstr(data):
	"""bit2binstr
	Convert ASCII bit strings to packed binary strings *without*
		doing any Modbus bit order reversal.
	data = An ASCII string of 0 and/or 1 characters. E.g. '00101111'
		Input data must be in multiples of 8 characters.
	Returns a string in raw binary format. E.g. '\x2F'
	There are no checks for invalid input characters! 
	"""
	return ''.join([_bit2bindict[data[i : i + 8]] for i in range(0, len(data), 8)])



#############################################################
# bin2hex
bin2hex = binascii.hexlify
"""bin2hex(bin)
Convert a string of binary data to a string of hexadecimal characters.
bin = a string in raw binary format. E.g. '\x2F91'
Returns a string in ASCII hexadecimal. E.g. '2F91'
"""


#############################################################
# hex2bin
hex2bin = binascii.unhexlify
"""hex2bin
Inverse operation of bin2hex.
Convert a string of hexadecimal characters to a string of binary data.
hexa = a string in ASCII hexadecimal. E.g. '2F91'
Returns a string in raw binary format. E.g. '\x2F91'
There are no checks for invalid characters! 
"""


############################################################################################


#############################################################
# Dictionaries used as look-up tables for handling 'bit swapping' in
# coil oriented Modbus functions.

#############################################################
# Dictionary used by new version of inversorbin.
# By Michael Griffin on 16-Jan-2008
# Based on the output of the original inversorbin code by 
# Juan Miguel Taboada Godoy
#

hexbininvert = {
'\x00' : '00000000', '\x01' : '10000000', '\x02' : '01000000', '\x03' : '11000000',
'\x04' : '00100000', '\x05' : '10100000', '\x06' : '01100000', '\x07' : '11100000',
'\x08' : '00010000', '\x09' : '10010000', '\x0A' : '01010000', '\x0B' : '11010000',
'\x0C' : '00110000', '\x0D' : '10110000', '\x0E' : '01110000', '\x0F' : '11110000',
'\x10' : '00001000', '\x11' : '10001000', '\x12' : '01001000', '\x13' : '11001000',
'\x14' : '00101000', '\x15' : '10101000', '\x16' : '01101000', '\x17' : '11101000',
'\x18' : '00011000', '\x19' : '10011000', '\x1A' : '01011000', '\x1B' : '11011000',
'\x1C' : '00111000', '\x1D' : '10111000', '\x1E' : '01111000', '\x1F' : '11111000',
'\x20' : '00000100', '\x21' : '10000100', '\x22' : '01000100', '\x23' : '11000100',
'\x24' : '00100100', '\x25' : '10100100', '\x26' : '01100100', '\x27' : '11100100',
'\x28' : '00010100', '\x29' : '10010100', '\x2A' : '01010100', '\x2B' : '11010100',
'\x2C' : '00110100', '\x2D' : '10110100', '\x2E' : '01110100', '\x2F' : '11110100',
'\x30' : '00001100', '\x31' : '10001100', '\x32' : '01001100', '\x33' : '11001100',
'\x34' : '00101100', '\x35' : '10101100', '\x36' : '01101100', '\x37' : '11101100',
'\x38' : '00011100', '\x39' : '10011100', '\x3A' : '01011100', '\x3B' : '11011100',
'\x3C' : '00111100', '\x3D' : '10111100', '\x3E' : '01111100', '\x3F' : '11111100',
'\x40' : '00000010', '\x41' : '10000010', '\x42' : '01000010', '\x43' : '11000010',
'\x44' : '00100010', '\x45' : '10100010', '\x46' : '01100010', '\x47' : '11100010',
'\x48' : '00010010', '\x49' : '10010010', '\x4A' : '01010010', '\x4B' : '11010010',
'\x4C' : '00110010', '\x4D' : '10110010', '\x4E' : '01110010', '\x4F' : '11110010',
'\x50' : '00001010', '\x51' : '10001010', '\x52' : '01001010', '\x53' : '11001010',
'\x54' : '00101010', '\x55' : '10101010', '\x56' : '01101010', '\x57' : '11101010',
'\x58' : '00011010', '\x59' : '10011010', '\x5A' : '01011010', '\x5B' : '11011010',
'\x5C' : '00111010', '\x5D' : '10111010', '\x5E' : '01111010', '\x5F' : '11111010',
'\x60' : '00000110', '\x61' : '10000110', '\x62' : '01000110', '\x63' : '11000110',
'\x64' : '00100110', '\x65' : '10100110', '\x66' : '01100110', '\x67' : '11100110',
'\x68' : '00010110', '\x69' : '10010110', '\x6A' : '01010110', '\x6B' : '11010110',
'\x6C' : '00110110', '\x6D' : '10110110', '\x6E' : '01110110', '\x6F' : '11110110',
'\x70' : '00001110', '\x71' : '10001110', '\x72' : '01001110', '\x73' : '11001110',
'\x74' : '00101110', '\x75' : '10101110', '\x76' : '01101110', '\x77' : '11101110',
'\x78' : '00011110', '\x79' : '10011110', '\x7A' : '01011110', '\x7B' : '11011110',
'\x7C' : '00111110', '\x7D' : '10111110', '\x7E' : '01111110', '\x7F' : '11111110',
'\x80' : '00000001', '\x81' : '10000001', '\x82' : '01000001', '\x83' : '11000001',
'\x84' : '00100001', '\x85' : '10100001', '\x86' : '01100001', '\x87' : '11100001',
'\x88' : '00010001', '\x89' : '10010001', '\x8A' : '01010001', '\x8B' : '11010001',
'\x8C' : '00110001', '\x8D' : '10110001', '\x8E' : '01110001', '\x8F' : '11110001',
'\x90' : '00001001', '\x91' : '10001001', '\x92' : '01001001', '\x93' : '11001001',
'\x94' : '00101001', '\x95' : '10101001', '\x96' : '01101001', '\x97' : '11101001',
'\x98' : '00011001', '\x99' : '10011001', '\x9A' : '01011001', '\x9B' : '11011001',
'\x9C' : '00111001', '\x9D' : '10111001', '\x9E' : '01111001', '\x9F' : '11111001',
'\xA0' : '00000101', '\xA1' : '10000101', '\xA2' : '01000101', '\xA3' : '11000101',
'\xA4' : '00100101', '\xA5' : '10100101', '\xA6' : '01100101', '\xA7' : '11100101',
'\xA8' : '00010101', '\xA9' : '10010101', '\xAA' : '01010101', '\xAB' : '11010101',
'\xAC' : '00110101', '\xAD' : '10110101', '\xAE' : '01110101', '\xAF' : '11110101',
'\xB0' : '00001101', '\xB1' : '10001101', '\xB2' : '01001101', '\xB3' : '11001101',
'\xB4' : '00101101', '\xB5' : '10101101', '\xB6' : '01101101', '\xB7' : '11101101',
'\xB8' : '00011101', '\xB9' : '10011101', '\xBA' : '01011101', '\xBB' : '11011101',
'\xBC' : '00111101', '\xBD' : '10111101', '\xBE' : '01111101', '\xBF' : '11111101',
'\xC0' : '00000011', '\xC1' : '10000011', '\xC2' : '01000011', '\xC3' : '11000011',
'\xC4' : '00100011', '\xC5' : '10100011', '\xC6' : '01100011', '\xC7' : '11100011',
'\xC8' : '00010011', '\xC9' : '10010011', '\xCA' : '01010011', '\xCB' : '11010011',
'\xCC' : '00110011', '\xCD' : '10110011', '\xCE' : '01110011', '\xCF' : '11110011',
'\xD0' : '00001011', '\xD1' : '10001011', '\xD2' : '01001011', '\xD3' : '11001011',
'\xD4' : '00101011', '\xD5' : '10101011', '\xD6' : '01101011', '\xD7' : '11101011',
'\xD8' : '00011011', '\xD9' : '10011011', '\xDA' : '01011011', '\xDB' : '11011011',
'\xDC' : '00111011', '\xDD' : '10111011', '\xDE' : '01111011', '\xDF' : '11111011',
'\xE0' : '00000111', '\xE1' : '10000111', '\xE2' : '01000111', '\xE3' : '11000111',
'\xE4' : '00100111', '\xE5' : '10100111', '\xE6' : '01100111', '\xE7' : '11100111',
'\xE8' : '00010111', '\xE9' : '10010111', '\xEA' : '01010111', '\xEB' : '11010111',
'\xEC' : '00110111', '\xED' : '10110111', '\xEE' : '01110111', '\xEF' : '11110111',
'\xF0' : '00001111', '\xF1' : '10001111', '\xF2' : '01001111', '\xF3' : '11001111',
'\xF4' : '00101111', '\xF5' : '10101111', '\xF6' : '01101111', '\xF7' : '11101111',
'\xF8' : '00011111', '\xF9' : '10011111', '\xFA' : '01011111', '\xFB' : '11011111',
'\xFC' : '00111111', '\xFD' : '10111111', '\xFE' : '01111111', '\xFF' : '11111111'
}


#############################################################
# Create a new dictionary by inverting hexbininvert.
#
def MakeBinHex():
	return dict([(j, i) for i, j in hexbininvert.iteritems()])

binhexinvert = MakeBinHex()

############################################################################################

#############################################################
# Dictionary to do ASCII bit string conversion to binary *without*
# doing any Modbus bit order reversal. 
#
_bin2bitdict = {
'\x00' : '00000000', '\x01' : '00000001', '\x02' : '00000010', '\x03' : '00000011',
'\x04' : '00000100', '\x05' : '00000101', '\x06' : '00000110', '\x07' : '00000111',
'\x08' : '00001000', '\x09' : '00001001', '\x0A' : '00001010', '\x0B' : '00001011',
'\x0C' : '00001100', '\x0D' : '00001101', '\x0E' : '00001110', '\x0F' : '00001111',
'\x10' : '00010000', '\x11' : '00010001', '\x12' : '00010010', '\x13' : '00010011',
'\x14' : '00010100', '\x15' : '00010101', '\x16' : '00010110', '\x17' : '00010111',
'\x18' : '00011000', '\x19' : '00011001', '\x1A' : '00011010', '\x1B' : '00011011',
'\x1C' : '00011100', '\x1D' : '00011101', '\x1E' : '00011110', '\x1F' : '00011111',
'\x20' : '00100000', '\x21' : '00100001', '\x22' : '00100010', '\x23' : '00100011',
'\x24' : '00100100', '\x25' : '00100101', '\x26' : '00100110', '\x27' : '00100111',
'\x28' : '00101000', '\x29' : '00101001', '\x2A' : '00101010', '\x2B' : '00101011',
'\x2C' : '00101100', '\x2D' : '00101101', '\x2E' : '00101110', '\x2F' : '00101111',
'\x30' : '00110000', '\x31' : '00110001', '\x32' : '00110010', '\x33' : '00110011',
'\x34' : '00110100', '\x35' : '00110101', '\x36' : '00110110', '\x37' : '00110111',
'\x38' : '00111000', '\x39' : '00111001', '\x3A' : '00111010', '\x3B' : '00111011',
'\x3C' : '00111100', '\x3D' : '00111101', '\x3E' : '00111110', '\x3F' : '00111111',
'\x40' : '01000000', '\x41' : '01000001', '\x42' : '01000010', '\x43' : '01000011',
'\x44' : '01000100', '\x45' : '01000101', '\x46' : '01000110', '\x47' : '01000111',
'\x48' : '01001000', '\x49' : '01001001', '\x4A' : '01001010', '\x4B' : '01001011',
'\x4C' : '01001100', '\x4D' : '01001101', '\x4E' : '01001110', '\x4F' : '01001111',
'\x50' : '01010000', '\x51' : '01010001', '\x52' : '01010010', '\x53' : '01010011',
'\x54' : '01010100', '\x55' : '01010101', '\x56' : '01010110', '\x57' : '01010111',
'\x58' : '01011000', '\x59' : '01011001', '\x5A' : '01011010', '\x5B' : '01011011',
'\x5C' : '01011100', '\x5D' : '01011101', '\x5E' : '01011110', '\x5F' : '01011111',
'\x60' : '01100000', '\x61' : '01100001', '\x62' : '01100010', '\x63' : '01100011',
'\x64' : '01100100', '\x65' : '01100101', '\x66' : '01100110', '\x67' : '01100111',
'\x68' : '01101000', '\x69' : '01101001', '\x6A' : '01101010', '\x6B' : '01101011',
'\x6C' : '01101100', '\x6D' : '01101101', '\x6E' : '01101110', '\x6F' : '01101111',
'\x70' : '01110000', '\x71' : '01110001', '\x72' : '01110010', '\x73' : '01110011',
'\x74' : '01110100', '\x75' : '01110101', '\x76' : '01110110', '\x77' : '01110111',
'\x78' : '01111000', '\x79' : '01111001', '\x7A' : '01111010', '\x7B' : '01111011',
'\x7C' : '01111100', '\x7D' : '01111101', '\x7E' : '01111110', '\x7F' : '01111111',
'\x80' : '10000000', '\x81' : '10000001', '\x82' : '10000010', '\x83' : '10000011',
'\x84' : '10000100', '\x85' : '10000101', '\x86' : '10000110', '\x87' : '10000111',
'\x88' : '10001000', '\x89' : '10001001', '\x8A' : '10001010', '\x8B' : '10001011',
'\x8C' : '10001100', '\x8D' : '10001101', '\x8E' : '10001110', '\x8F' : '10001111',
'\x90' : '10010000', '\x91' : '10010001', '\x92' : '10010010', '\x93' : '10010011',
'\x94' : '10010100', '\x95' : '10010101', '\x96' : '10010110', '\x97' : '10010111',
'\x98' : '10011000', '\x99' : '10011001', '\x9A' : '10011010', '\x9B' : '10011011',
'\x9C' : '10011100', '\x9D' : '10011101', '\x9E' : '10011110', '\x9F' : '10011111',
'\xA0' : '10100000', '\xA1' : '10100001', '\xA2' : '10100010', '\xA3' : '10100011',
'\xA4' : '10100100', '\xA5' : '10100101', '\xA6' : '10100110', '\xA7' : '10100111',
'\xA8' : '10101000', '\xA9' : '10101001', '\xAA' : '10101010', '\xAB' : '10101011',
'\xAC' : '10101100', '\xAD' : '10101101', '\xAE' : '10101110', '\xAF' : '10101111',
'\xB0' : '10110000', '\xB1' : '10110001', '\xB2' : '10110010', '\xB3' : '10110011',
'\xB4' : '10110100', '\xB5' : '10110101', '\xB6' : '10110110', '\xB7' : '10110111',
'\xB8' : '10111000', '\xB9' : '10111001', '\xBA' : '10111010', '\xBB' : '10111011',
'\xBC' : '10111100', '\xBD' : '10111101', '\xBE' : '10111110', '\xBF' : '10111111',
'\xC0' : '11000000', '\xC1' : '11000001', '\xC2' : '11000010', '\xC3' : '11000011',
'\xC4' : '11000100', '\xC5' : '11000101', '\xC6' : '11000110', '\xC7' : '11000111',
'\xC8' : '11001000', '\xC9' : '11001001', '\xCA' : '11001010', '\xCB' : '11001011',
'\xCC' : '11001100', '\xCD' : '11001101', '\xCE' : '11001110', '\xCF' : '11001111',
'\xD0' : '11010000', '\xD1' : '11010001', '\xD2' : '11010010', '\xD3' : '11010011',
'\xD4' : '11010100', '\xD5' : '11010101', '\xD6' : '11010110', '\xD7' : '11010111',
'\xD8' : '11011000', '\xD9' : '11011001', '\xDA' : '11011010', '\xDB' : '11011011',
'\xDC' : '11011100', '\xDD' : '11011101', '\xDE' : '11011110', '\xDF' : '11011111',
'\xE0' : '11100000', '\xE1' : '11100001', '\xE2' : '11100010', '\xE3' : '11100011',
'\xE4' : '11100100', '\xE5' : '11100101', '\xE6' : '11100110', '\xE7' : '11100111',
'\xE8' : '11101000', '\xE9' : '11101001', '\xEA' : '11101010', '\xEB' : '11101011',
'\xEC' : '11101100', '\xED' : '11101101', '\xEE' : '11101110', '\xEF' : '11101111',
'\xF0' : '11110000', '\xF1' : '11110001', '\xF2' : '11110010', '\xF3' : '11110011',
'\xF4' : '11110100', '\xF5' : '11110101', '\xF6' : '11110110', '\xF7' : '11110111',
'\xF8' : '11111000', '\xF9' : '11111001', '\xFA' : '11111010', '\xFB' : '11111011',
'\xFC' : '11111100', '\xFD' : '11111101', '\xFE' : '11111110', '\xFF' : '11111111'
}

#############################################################
# Create a new dictionary by inverting _bin2bitdict.
#
def MakeBit2Bin():
	return dict([(j, i) for i, j in _bin2bitdict.iteritems()])

_bit2bindict = MakeBit2Bin()



############################################################################################

#############################################################
# Dictionary to do Modbus bit reversal when the data is already
# contained in a binary string.
# This dictionary converts between "un-reversed" bytes (as stored in 
# registers) to "reversed" bytes ready for transmission. This will
# convert data in *both* directions.
#
_bitreversebindict = {
'\x00' : '\x00', '\x01' : '\x80', '\x02' : '\x40', '\x03' : '\xC0',
'\x04' : '\x20', '\x05' : '\xA0', '\x06' : '\x60', '\x07' : '\xE0',
'\x08' : '\x10', '\x09' : '\x90', '\x0A' : '\x50', '\x0B' : '\xD0',
'\x0C' : '\x30', '\x0D' : '\xB0', '\x0E' : '\x70', '\x0F' : '\xF0',
'\x10' : '\x08', '\x11' : '\x88', '\x12' : '\x48', '\x13' : '\xC8',
'\x14' : '\x28', '\x15' : '\xA8', '\x16' : '\x68', '\x17' : '\xE8',
'\x18' : '\x18', '\x19' : '\x98', '\x1A' : '\x58', '\x1B' : '\xD8',
'\x1C' : '\x38', '\x1D' : '\xB8', '\x1E' : '\x78', '\x1F' : '\xF8',
'\x20' : '\x04', '\x21' : '\x84', '\x22' : '\x44', '\x23' : '\xC4',
'\x24' : '\x24', '\x25' : '\xA4', '\x26' : '\x64', '\x27' : '\xE4',
'\x28' : '\x14', '\x29' : '\x94', '\x2A' : '\x54', '\x2B' : '\xD4',
'\x2C' : '\x34', '\x2D' : '\xB4', '\x2E' : '\x74', '\x2F' : '\xF4',
'\x30' : '\x0C', '\x31' : '\x8C', '\x32' : '\x4C', '\x33' : '\xCC',
'\x34' : '\x2C', '\x35' : '\xAC', '\x36' : '\x6C', '\x37' : '\xEC',
'\x38' : '\x1C', '\x39' : '\x9C', '\x3A' : '\x5C', '\x3B' : '\xDC',
'\x3C' : '\x3C', '\x3D' : '\xBC', '\x3E' : '\x7C', '\x3F' : '\xFC',
'\x40' : '\x02', '\x41' : '\x82', '\x42' : '\x42', '\x43' : '\xC2',
'\x44' : '\x22', '\x45' : '\xA2', '\x46' : '\x62', '\x47' : '\xE2',
'\x48' : '\x12', '\x49' : '\x92', '\x4A' : '\x52', '\x4B' : '\xD2',
'\x4C' : '\x32', '\x4D' : '\xB2', '\x4E' : '\x72', '\x4F' : '\xF2',
'\x50' : '\x0A', '\x51' : '\x8A', '\x52' : '\x4A', '\x53' : '\xCA',
'\x54' : '\x2A', '\x55' : '\xAA', '\x56' : '\x6A', '\x57' : '\xEA',
'\x58' : '\x1A', '\x59' : '\x9A', '\x5A' : '\x5A', '\x5B' : '\xDA',
'\x5C' : '\x3A', '\x5D' : '\xBA', '\x5E' : '\x7A', '\x5F' : '\xFA',
'\x60' : '\x06', '\x61' : '\x86', '\x62' : '\x46', '\x63' : '\xC6',
'\x64' : '\x26', '\x65' : '\xA6', '\x66' : '\x66', '\x67' : '\xE6',
'\x68' : '\x16', '\x69' : '\x96', '\x6A' : '\x56', '\x6B' : '\xD6',
'\x6C' : '\x36', '\x6D' : '\xB6', '\x6E' : '\x76', '\x6F' : '\xF6',
'\x70' : '\x0E', '\x71' : '\x8E', '\x72' : '\x4E', '\x73' : '\xCE',
'\x74' : '\x2E', '\x75' : '\xAE', '\x76' : '\x6E', '\x77' : '\xEE',
'\x78' : '\x1E', '\x79' : '\x9E', '\x7A' : '\x5E', '\x7B' : '\xDE',
'\x7C' : '\x3E', '\x7D' : '\xBE', '\x7E' : '\x7E', '\x7F' : '\xFE',
'\x80' : '\x01', '\x81' : '\x81', '\x82' : '\x41', '\x83' : '\xC1',
'\x84' : '\x21', '\x85' : '\xA1', '\x86' : '\x61', '\x87' : '\xE1',
'\x88' : '\x11', '\x89' : '\x91', '\x8A' : '\x51', '\x8B' : '\xD1',
'\x8C' : '\x31', '\x8D' : '\xB1', '\x8E' : '\x71', '\x8F' : '\xF1',
'\x90' : '\x09', '\x91' : '\x89', '\x92' : '\x49', '\x93' : '\xC9',
'\x94' : '\x29', '\x95' : '\xA9', '\x96' : '\x69', '\x97' : '\xE9',
'\x98' : '\x19', '\x99' : '\x99', '\x9A' : '\x59', '\x9B' : '\xD9',
'\x9C' : '\x39', '\x9D' : '\xB9', '\x9E' : '\x79', '\x9F' : '\xF9',
'\xA0' : '\x05', '\xA1' : '\x85', '\xA2' : '\x45', '\xA3' : '\xC5',
'\xA4' : '\x25', '\xA5' : '\xA5', '\xA6' : '\x65', '\xA7' : '\xE5',
'\xA8' : '\x15', '\xA9' : '\x95', '\xAA' : '\x55', '\xAB' : '\xD5',
'\xAC' : '\x35', '\xAD' : '\xB5', '\xAE' : '\x75', '\xAF' : '\xF5',
'\xB0' : '\x0D', '\xB1' : '\x8D', '\xB2' : '\x4D', '\xB3' : '\xCD',
'\xB4' : '\x2D', '\xB5' : '\xAD', '\xB6' : '\x6D', '\xB7' : '\xED',
'\xB8' : '\x1D', '\xB9' : '\x9D', '\xBA' : '\x5D', '\xBB' : '\xDD',
'\xBC' : '\x3D', '\xBD' : '\xBD', '\xBE' : '\x7D', '\xBF' : '\xFD',
'\xC0' : '\x03', '\xC1' : '\x83', '\xC2' : '\x43', '\xC3' : '\xC3',
'\xC4' : '\x23', '\xC5' : '\xA3', '\xC6' : '\x63', '\xC7' : '\xE3',
'\xC8' : '\x13', '\xC9' : '\x93', '\xCA' : '\x53', '\xCB' : '\xD3',
'\xCC' : '\x33', '\xCD' : '\xB3', '\xCE' : '\x73', '\xCF' : '\xF3',
'\xD0' : '\x0B', '\xD1' : '\x8B', '\xD2' : '\x4B', '\xD3' : '\xCB',
'\xD4' : '\x2B', '\xD5' : '\xAB', '\xD6' : '\x6B', '\xD7' : '\xEB',
'\xD8' : '\x1B', '\xD9' : '\x9B', '\xDA' : '\x5B', '\xDB' : '\xDB',
'\xDC' : '\x3B', '\xDD' : '\xBB', '\xDE' : '\x7B', '\xDF' : '\xFB',
'\xE0' : '\x07', '\xE1' : '\x87', '\xE2' : '\x47', '\xE3' : '\xC7',
'\xE4' : '\x27', '\xE5' : '\xA7', '\xE6' : '\x67', '\xE7' : '\xE7',
'\xE8' : '\x17', '\xE9' : '\x97', '\xEA' : '\x57', '\xEB' : '\xD7',
'\xEC' : '\x37', '\xED' : '\xB7', '\xEE' : '\x77', '\xEF' : '\xF7',
'\xF0' : '\x0F', '\xF1' : '\x8F', '\xF2' : '\x4F', '\xF3' : '\xCF',
'\xF4' : '\x2F', '\xF5' : '\xAF', '\xF6' : '\x6F', '\xF7' : '\xEF',
'\xF8' : '\x1F', '\xF9' : '\x9F', '\xFA' : '\x5F', '\xFB' : '\xDF',
'\xFC' : '\x3F', '\xFD' : '\xBF', '\xFE' : '\x7F', '\xFF' : '\xFF'
}

############################################################################################

# Create a dictionary for converting packed binary strings to boolean lists.
# This is for the list oriented conversions.
boolhexlist = {
'\x00' : [False, False, False, False, False, False, False, False],
'\x01' : [True, False, False, False, False, False, False, False],
'\x02' : [False, True, False, False, False, False, False, False],
'\x03' : [True, True, False, False, False, False, False, False],
'\x04' : [False, False, True, False, False, False, False, False],
'\x05' : [True, False, True, False, False, False, False, False],
'\x06' : [False, True, True, False, False, False, False, False],
'\x07' : [True, True, True, False, False, False, False, False],
'\x08' : [False, False, False, True, False, False, False, False],
'\x09' : [True, False, False, True, False, False, False, False],
'\x0A' : [False, True, False, True, False, False, False, False],
'\x0B' : [True, True, False, True, False, False, False, False],
'\x0C' : [False, False, True, True, False, False, False, False],
'\x0D' : [True, False, True, True, False, False, False, False],
'\x0E' : [False, True, True, True, False, False, False, False],
'\x0F' : [True, True, True, True, False, False, False, False],
'\x10' : [False, False, False, False, True, False, False, False],
'\x11' : [True, False, False, False, True, False, False, False],
'\x12' : [False, True, False, False, True, False, False, False],
'\x13' : [True, True, False, False, True, False, False, False],
'\x14' : [False, False, True, False, True, False, False, False],
'\x15' : [True, False, True, False, True, False, False, False],
'\x16' : [False, True, True, False, True, False, False, False],
'\x17' : [True, True, True, False, True, False, False, False],
'\x18' : [False, False, False, True, True, False, False, False],
'\x19' : [True, False, False, True, True, False, False, False],
'\x1A' : [False, True, False, True, True, False, False, False],
'\x1B' : [True, True, False, True, True, False, False, False],
'\x1C' : [False, False, True, True, True, False, False, False],
'\x1D' : [True, False, True, True, True, False, False, False],
'\x1E' : [False, True, True, True, True, False, False, False],
'\x1F' : [True, True, True, True, True, False, False, False],
'\x20' : [False, False, False, False, False, True, False, False],
'\x21' : [True, False, False, False, False, True, False, False],
'\x22' : [False, True, False, False, False, True, False, False],
'\x23' : [True, True, False, False, False, True, False, False],
'\x24' : [False, False, True, False, False, True, False, False],
'\x25' : [True, False, True, False, False, True, False, False],
'\x26' : [False, True, True, False, False, True, False, False],
'\x27' : [True, True, True, False, False, True, False, False],
'\x28' : [False, False, False, True, False, True, False, False],
'\x29' : [True, False, False, True, False, True, False, False],
'\x2A' : [False, True, False, True, False, True, False, False],
'\x2B' : [True, True, False, True, False, True, False, False],
'\x2C' : [False, False, True, True, False, True, False, False],
'\x2D' : [True, False, True, True, False, True, False, False],
'\x2E' : [False, True, True, True, False, True, False, False],
'\x2F' : [True, True, True, True, False, True, False, False],
'\x30' : [False, False, False, False, True, True, False, False],
'\x31' : [True, False, False, False, True, True, False, False],
'\x32' : [False, True, False, False, True, True, False, False],
'\x33' : [True, True, False, False, True, True, False, False],
'\x34' : [False, False, True, False, True, True, False, False],
'\x35' : [True, False, True, False, True, True, False, False],
'\x36' : [False, True, True, False, True, True, False, False],
'\x37' : [True, True, True, False, True, True, False, False],
'\x38' : [False, False, False, True, True, True, False, False],
'\x39' : [True, False, False, True, True, True, False, False],
'\x3A' : [False, True, False, True, True, True, False, False],
'\x3B' : [True, True, False, True, True, True, False, False],
'\x3C' : [False, False, True, True, True, True, False, False],
'\x3D' : [True, False, True, True, True, True, False, False],
'\x3E' : [False, True, True, True, True, True, False, False],
'\x3F' : [True, True, True, True, True, True, False, False],
'\x40' : [False, False, False, False, False, False, True, False],
'\x41' : [True, False, False, False, False, False, True, False],
'\x42' : [False, True, False, False, False, False, True, False],
'\x43' : [True, True, False, False, False, False, True, False],
'\x44' : [False, False, True, False, False, False, True, False],
'\x45' : [True, False, True, False, False, False, True, False],
'\x46' : [False, True, True, False, False, False, True, False],
'\x47' : [True, True, True, False, False, False, True, False],
'\x48' : [False, False, False, True, False, False, True, False],
'\x49' : [True, False, False, True, False, False, True, False],
'\x4A' : [False, True, False, True, False, False, True, False],
'\x4B' : [True, True, False, True, False, False, True, False],
'\x4C' : [False, False, True, True, False, False, True, False],
'\x4D' : [True, False, True, True, False, False, True, False],
'\x4E' : [False, True, True, True, False, False, True, False],
'\x4F' : [True, True, True, True, False, False, True, False],
'\x50' : [False, False, False, False, True, False, True, False],
'\x51' : [True, False, False, False, True, False, True, False],
'\x52' : [False, True, False, False, True, False, True, False],
'\x53' : [True, True, False, False, True, False, True, False],
'\x54' : [False, False, True, False, True, False, True, False],
'\x55' : [True, False, True, False, True, False, True, False],
'\x56' : [False, True, True, False, True, False, True, False],
'\x57' : [True, True, True, False, True, False, True, False],
'\x58' : [False, False, False, True, True, False, True, False],
'\x59' : [True, False, False, True, True, False, True, False],
'\x5A' : [False, True, False, True, True, False, True, False],
'\x5B' : [True, True, False, True, True, False, True, False],
'\x5C' : [False, False, True, True, True, False, True, False],
'\x5D' : [True, False, True, True, True, False, True, False],
'\x5E' : [False, True, True, True, True, False, True, False],
'\x5F' : [True, True, True, True, True, False, True, False],
'\x60' : [False, False, False, False, False, True, True, False],
'\x61' : [True, False, False, False, False, True, True, False],
'\x62' : [False, True, False, False, False, True, True, False],
'\x63' : [True, True, False, False, False, True, True, False],
'\x64' : [False, False, True, False, False, True, True, False],
'\x65' : [True, False, True, False, False, True, True, False],
'\x66' : [False, True, True, False, False, True, True, False],
'\x67' : [True, True, True, False, False, True, True, False],
'\x68' : [False, False, False, True, False, True, True, False],
'\x69' : [True, False, False, True, False, True, True, False],
'\x6A' : [False, True, False, True, False, True, True, False],
'\x6B' : [True, True, False, True, False, True, True, False],
'\x6C' : [False, False, True, True, False, True, True, False],
'\x6D' : [True, False, True, True, False, True, True, False],
'\x6E' : [False, True, True, True, False, True, True, False],
'\x6F' : [True, True, True, True, False, True, True, False],
'\x70' : [False, False, False, False, True, True, True, False],
'\x71' : [True, False, False, False, True, True, True, False],
'\x72' : [False, True, False, False, True, True, True, False],
'\x73' : [True, True, False, False, True, True, True, False],
'\x74' : [False, False, True, False, True, True, True, False],
'\x75' : [True, False, True, False, True, True, True, False],
'\x76' : [False, True, True, False, True, True, True, False],
'\x77' : [True, True, True, False, True, True, True, False],
'\x78' : [False, False, False, True, True, True, True, False],
'\x79' : [True, False, False, True, True, True, True, False],
'\x7A' : [False, True, False, True, True, True, True, False],
'\x7B' : [True, True, False, True, True, True, True, False],
'\x7C' : [False, False, True, True, True, True, True, False],
'\x7D' : [True, False, True, True, True, True, True, False],
'\x7E' : [False, True, True, True, True, True, True, False],
'\x7F' : [True, True, True, True, True, True, True, False],
'\x80' : [False, False, False, False, False, False, False, True],
'\x81' : [True, False, False, False, False, False, False, True],
'\x82' : [False, True, False, False, False, False, False, True],
'\x83' : [True, True, False, False, False, False, False, True],
'\x84' : [False, False, True, False, False, False, False, True],
'\x85' : [True, False, True, False, False, False, False, True],
'\x86' : [False, True, True, False, False, False, False, True],
'\x87' : [True, True, True, False, False, False, False, True],
'\x88' : [False, False, False, True, False, False, False, True],
'\x89' : [True, False, False, True, False, False, False, True],
'\x8A' : [False, True, False, True, False, False, False, True],
'\x8B' : [True, True, False, True, False, False, False, True],
'\x8C' : [False, False, True, True, False, False, False, True],
'\x8D' : [True, False, True, True, False, False, False, True],
'\x8E' : [False, True, True, True, False, False, False, True],
'\x8F' : [True, True, True, True, False, False, False, True],
'\x90' : [False, False, False, False, True, False, False, True],
'\x91' : [True, False, False, False, True, False, False, True],
'\x92' : [False, True, False, False, True, False, False, True],
'\x93' : [True, True, False, False, True, False, False, True],
'\x94' : [False, False, True, False, True, False, False, True],
'\x95' : [True, False, True, False, True, False, False, True],
'\x96' : [False, True, True, False, True, False, False, True],
'\x97' : [True, True, True, False, True, False, False, True],
'\x98' : [False, False, False, True, True, False, False, True],
'\x99' : [True, False, False, True, True, False, False, True],
'\x9A' : [False, True, False, True, True, False, False, True],
'\x9B' : [True, True, False, True, True, False, False, True],
'\x9C' : [False, False, True, True, True, False, False, True],
'\x9D' : [True, False, True, True, True, False, False, True],
'\x9E' : [False, True, True, True, True, False, False, True],
'\x9F' : [True, True, True, True, True, False, False, True],
'\xA0' : [False, False, False, False, False, True, False, True],
'\xA1' : [True, False, False, False, False, True, False, True],
'\xA2' : [False, True, False, False, False, True, False, True],
'\xA3' : [True, True, False, False, False, True, False, True],
'\xA4' : [False, False, True, False, False, True, False, True],
'\xA5' : [True, False, True, False, False, True, False, True],
'\xA6' : [False, True, True, False, False, True, False, True],
'\xA7' : [True, True, True, False, False, True, False, True],
'\xA8' : [False, False, False, True, False, True, False, True],
'\xA9' : [True, False, False, True, False, True, False, True],
'\xAA' : [False, True, False, True, False, True, False, True],
'\xAB' : [True, True, False, True, False, True, False, True],
'\xAC' : [False, False, True, True, False, True, False, True],
'\xAD' : [True, False, True, True, False, True, False, True],
'\xAE' : [False, True, True, True, False, True, False, True],
'\xAF' : [True, True, True, True, False, True, False, True],
'\xB0' : [False, False, False, False, True, True, False, True],
'\xB1' : [True, False, False, False, True, True, False, True],
'\xB2' : [False, True, False, False, True, True, False, True],
'\xB3' : [True, True, False, False, True, True, False, True],
'\xB4' : [False, False, True, False, True, True, False, True],
'\xB5' : [True, False, True, False, True, True, False, True],
'\xB6' : [False, True, True, False, True, True, False, True],
'\xB7' : [True, True, True, False, True, True, False, True],
'\xB8' : [False, False, False, True, True, True, False, True],
'\xB9' : [True, False, False, True, True, True, False, True],
'\xBA' : [False, True, False, True, True, True, False, True],
'\xBB' : [True, True, False, True, True, True, False, True],
'\xBC' : [False, False, True, True, True, True, False, True],
'\xBD' : [True, False, True, True, True, True, False, True],
'\xBE' : [False, True, True, True, True, True, False, True],
'\xBF' : [True, True, True, True, True, True, False, True],
'\xC0' : [False, False, False, False, False, False, True, True],
'\xC1' : [True, False, False, False, False, False, True, True],
'\xC2' : [False, True, False, False, False, False, True, True],
'\xC3' : [True, True, False, False, False, False, True, True],
'\xC4' : [False, False, True, False, False, False, True, True],
'\xC5' : [True, False, True, False, False, False, True, True],
'\xC6' : [False, True, True, False, False, False, True, True],
'\xC7' : [True, True, True, False, False, False, True, True],
'\xC8' : [False, False, False, True, False, False, True, True],
'\xC9' : [True, False, False, True, False, False, True, True],
'\xCA' : [False, True, False, True, False, False, True, True],
'\xCB' : [True, True, False, True, False, False, True, True],
'\xCC' : [False, False, True, True, False, False, True, True],
'\xCD' : [True, False, True, True, False, False, True, True],
'\xCE' : [False, True, True, True, False, False, True, True],
'\xCF' : [True, True, True, True, False, False, True, True],
'\xD0' : [False, False, False, False, True, False, True, True],
'\xD1' : [True, False, False, False, True, False, True, True],
'\xD2' : [False, True, False, False, True, False, True, True],
'\xD3' : [True, True, False, False, True, False, True, True],
'\xD4' : [False, False, True, False, True, False, True, True],
'\xD5' : [True, False, True, False, True, False, True, True],
'\xD6' : [False, True, True, False, True, False, True, True],
'\xD7' : [True, True, True, False, True, False, True, True],
'\xD8' : [False, False, False, True, True, False, True, True],
'\xD9' : [True, False, False, True, True, False, True, True],
'\xDA' : [False, True, False, True, True, False, True, True],
'\xDB' : [True, True, False, True, True, False, True, True],
'\xDC' : [False, False, True, True, True, False, True, True],
'\xDD' : [True, False, True, True, True, False, True, True],
'\xDE' : [False, True, True, True, True, False, True, True],
'\xDF' : [True, True, True, True, True, False, True, True],
'\xE0' : [False, False, False, False, False, True, True, True],
'\xE1' : [True, False, False, False, False, True, True, True],
'\xE2' : [False, True, False, False, False, True, True, True],
'\xE3' : [True, True, False, False, False, True, True, True],
'\xE4' : [False, False, True, False, False, True, True, True],
'\xE5' : [True, False, True, False, False, True, True, True],
'\xE6' : [False, True, True, False, False, True, True, True],
'\xE7' : [True, True, True, False, False, True, True, True],
'\xE8' : [False, False, False, True, False, True, True, True],
'\xE9' : [True, False, False, True, False, True, True, True],
'\xEA' : [False, True, False, True, False, True, True, True],
'\xEB' : [True, True, False, True, False, True, True, True],
'\xEC' : [False, False, True, True, False, True, True, True],
'\xED' : [True, False, True, True, False, True, True, True],
'\xEE' : [False, True, True, True, False, True, True, True],
'\xEF' : [True, True, True, True, False, True, True, True],
'\xF0' : [False, False, False, False, True, True, True, True],
'\xF1' : [True, False, False, False, True, True, True, True],
'\xF2' : [False, True, False, False, True, True, True, True],
'\xF3' : [True, True, False, False, True, True, True, True],
'\xF4' : [False, False, True, False, True, True, True, True],
'\xF5' : [True, False, True, False, True, True, True, True],
'\xF6' : [False, True, True, False, True, True, True, True],
'\xF7' : [True, True, True, False, True, True, True, True],
'\xF8' : [False, False, False, True, True, True, True, True],
'\xF9' : [True, False, False, True, True, True, True, True],
'\xFA' : [False, True, False, True, True, True, True, True],
'\xFB' : [True, True, False, True, True, True, True, True],
'\xFC' : [False, False, True, True, True, True, True, True],
'\xFD' : [True, False, True, True, True, True, True, True],
'\xFE' : [False, True, True, True, True, True, True, True],
'\xFF' : [True, True, True, True, True, True, True, True]
}

#############################################################
# Create a new dictionary by inverting hexlist. The keys must be tuples,
# as lists are not hashable.
def MakeBoolHex():
	return dict([(tuple(j), i) for i, j in boolhexlist.iteritems()])
boolhexlistinvert = MakeBoolHex()


############################################################################################

