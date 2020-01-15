##############################################################################
# Project:  Modbus Library
# Module:   ModbusDataLib.py
#       Based on the earlier ModbusDataStrLib.py
# Purpose:  Encode and decode modbus message data.
# Language: Python 2.5
# Date:     10-Mar-2008.
# Version:  06-Jul-2010.
# Copyright:    2006-2008 - Juan Miguel Taboada Godoy <juanmi@likindoy.org>
# Copyright:    2008 - 2010 - Michael Griffin       <m.os.griffin@gmail.com>
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
# Important:    WHEN EDITING THIS FILE, USE TABS TO INDENT - NOT SPACES!
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



Miscellaneous:
==============

1) coilvalue(state) - If state = 0, it returns '\x00\x00', else it returns
    '\xFF\x00'. This is used for providing the correct parameter values
    required by Modbus function 5 (write single coil).


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

from __future__ import division

import struct
import array
# from builtins import bytes

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

    boollist = []
    chararray=list(struct.unpack('%dB' % len(binval), binval))

    # Split the string into a list of characters.
    # chararray = list(binval)
    # Python2/3 difference : chararray is a int array (3) and a chr array (2)
    # Python3: [boollist.extend(boolhexlist[chr(i)]) for i in chararray]
    # Python2: [boollist.extend(boolhexlist[i]) for i in chararray]

    # Next, look up the boolean equivalents and add them to the output list.
    for c in chararray:
        boollist.extend(boolhexlist[chr(c)])

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
        return ''.join([boolhexlistinvert[tuple(boollist[i: i + 8])] for i in range(0, len(boollist), 8)])

    # If we had an error, then try again after padding it.
    except:

        # Check if the list needs to be padded out to a multiple of 8.
        if ((len(boollist) % 8) != 0):
            boolinput = []
            boolinput.extend(boollist)
            boolinput.extend([False] * (8 - len(boollist) % 8))
        else:
            boolinput = boollist
        return ''.join([boolhexlistinvert[tuple(boolinput[i: i + 8])] for i in range(0, len(boolinput), 8)])


#############################################################
# bin2intlist
def bin2intlist(binval):
    """ bin2intlist
    Accepts a packed binary string and outputs a list of *unsigned*
    16 bit integers. E.g. '\xF1\x23\x12\xD9' --> [61731, 4825]
    binval *must* be an even number of bytes to convert to integers.
    """
    return list(struct.unpack('>%dH' % (len(binval) // 2), binval))


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
    return list(struct.unpack('>%dh' % (len(binval) // 2), binval))


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
# Create a dictionary for converting packed binary strings to boolean lists.
# This is for the list oriented conversions.
boolhexlist = {
    '\x00': [False, False, False, False, False, False, False, False],
    '\x01': [True, False, False, False, False, False, False, False],
    '\x02': [False, True, False, False, False, False, False, False],
    '\x03': [True, True, False, False, False, False, False, False],
    '\x04': [False, False, True, False, False, False, False, False],
    '\x05': [True, False, True, False, False, False, False, False],
    '\x06': [False, True, True, False, False, False, False, False],
    '\x07': [True, True, True, False, False, False, False, False],
    '\x08': [False, False, False, True, False, False, False, False],
    '\x09': [True, False, False, True, False, False, False, False],
    '\x0A': [False, True, False, True, False, False, False, False],
    '\x0B': [True, True, False, True, False, False, False, False],
    '\x0C': [False, False, True, True, False, False, False, False],
    '\x0D': [True, False, True, True, False, False, False, False],
    '\x0E': [False, True, True, True, False, False, False, False],
    '\x0F': [True, True, True, True, False, False, False, False],
    '\x10': [False, False, False, False, True, False, False, False],
    '\x11': [True, False, False, False, True, False, False, False],
    '\x12': [False, True, False, False, True, False, False, False],
    '\x13': [True, True, False, False, True, False, False, False],
    '\x14': [False, False, True, False, True, False, False, False],
    '\x15': [True, False, True, False, True, False, False, False],
    '\x16': [False, True, True, False, True, False, False, False],
    '\x17': [True, True, True, False, True, False, False, False],
    '\x18': [False, False, False, True, True, False, False, False],
    '\x19': [True, False, False, True, True, False, False, False],
    '\x1A': [False, True, False, True, True, False, False, False],
    '\x1B': [True, True, False, True, True, False, False, False],
    '\x1C': [False, False, True, True, True, False, False, False],
    '\x1D': [True, False, True, True, True, False, False, False],
    '\x1E': [False, True, True, True, True, False, False, False],
    '\x1F': [True, True, True, True, True, False, False, False],
    '\x20': [False, False, False, False, False, True, False, False],
    '\x21': [True, False, False, False, False, True, False, False],
    '\x22': [False, True, False, False, False, True, False, False],
    '\x23': [True, True, False, False, False, True, False, False],
    '\x24': [False, False, True, False, False, True, False, False],
    '\x25': [True, False, True, False, False, True, False, False],
    '\x26': [False, True, True, False, False, True, False, False],
    '\x27': [True, True, True, False, False, True, False, False],
    '\x28': [False, False, False, True, False, True, False, False],
    '\x29': [True, False, False, True, False, True, False, False],
    '\x2A': [False, True, False, True, False, True, False, False],
    '\x2B': [True, True, False, True, False, True, False, False],
    '\x2C': [False, False, True, True, False, True, False, False],
    '\x2D': [True, False, True, True, False, True, False, False],
    '\x2E': [False, True, True, True, False, True, False, False],
    '\x2F': [True, True, True, True, False, True, False, False],
    '\x30': [False, False, False, False, True, True, False, False],
    '\x31': [True, False, False, False, True, True, False, False],
    '\x32': [False, True, False, False, True, True, False, False],
    '\x33': [True, True, False, False, True, True, False, False],
    '\x34': [False, False, True, False, True, True, False, False],
    '\x35': [True, False, True, False, True, True, False, False],
    '\x36': [False, True, True, False, True, True, False, False],
    '\x37': [True, True, True, False, True, True, False, False],
    '\x38': [False, False, False, True, True, True, False, False],
    '\x39': [True, False, False, True, True, True, False, False],
    '\x3A': [False, True, False, True, True, True, False, False],
    '\x3B': [True, True, False, True, True, True, False, False],
    '\x3C': [False, False, True, True, True, True, False, False],
    '\x3D': [True, False, True, True, True, True, False, False],
    '\x3E': [False, True, True, True, True, True, False, False],
    '\x3F': [True, True, True, True, True, True, False, False],
    '\x40': [False, False, False, False, False, False, True, False],
    '\x41': [True, False, False, False, False, False, True, False],
    '\x42': [False, True, False, False, False, False, True, False],
    '\x43': [True, True, False, False, False, False, True, False],
    '\x44': [False, False, True, False, False, False, True, False],
    '\x45': [True, False, True, False, False, False, True, False],
    '\x46': [False, True, True, False, False, False, True, False],
    '\x47': [True, True, True, False, False, False, True, False],
    '\x48': [False, False, False, True, False, False, True, False],
    '\x49': [True, False, False, True, False, False, True, False],
    '\x4A': [False, True, False, True, False, False, True, False],
    '\x4B': [True, True, False, True, False, False, True, False],
    '\x4C': [False, False, True, True, False, False, True, False],
    '\x4D': [True, False, True, True, False, False, True, False],
    '\x4E': [False, True, True, True, False, False, True, False],
    '\x4F': [True, True, True, True, False, False, True, False],
    '\x50': [False, False, False, False, True, False, True, False],
    '\x51': [True, False, False, False, True, False, True, False],
    '\x52': [False, True, False, False, True, False, True, False],
    '\x53': [True, True, False, False, True, False, True, False],
    '\x54': [False, False, True, False, True, False, True, False],
    '\x55': [True, False, True, False, True, False, True, False],
    '\x56': [False, True, True, False, True, False, True, False],
    '\x57': [True, True, True, False, True, False, True, False],
    '\x58': [False, False, False, True, True, False, True, False],
    '\x59': [True, False, False, True, True, False, True, False],
    '\x5A': [False, True, False, True, True, False, True, False],
    '\x5B': [True, True, False, True, True, False, True, False],
    '\x5C': [False, False, True, True, True, False, True, False],
    '\x5D': [True, False, True, True, True, False, True, False],
    '\x5E': [False, True, True, True, True, False, True, False],
    '\x5F': [True, True, True, True, True, False, True, False],
    '\x60': [False, False, False, False, False, True, True, False],
    '\x61': [True, False, False, False, False, True, True, False],
    '\x62': [False, True, False, False, False, True, True, False],
    '\x63': [True, True, False, False, False, True, True, False],
    '\x64': [False, False, True, False, False, True, True, False],
    '\x65': [True, False, True, False, False, True, True, False],
    '\x66': [False, True, True, False, False, True, True, False],
    '\x67': [True, True, True, False, False, True, True, False],
    '\x68': [False, False, False, True, False, True, True, False],
    '\x69': [True, False, False, True, False, True, True, False],
    '\x6A': [False, True, False, True, False, True, True, False],
    '\x6B': [True, True, False, True, False, True, True, False],
    '\x6C': [False, False, True, True, False, True, True, False],
    '\x6D': [True, False, True, True, False, True, True, False],
    '\x6E': [False, True, True, True, False, True, True, False],
    '\x6F': [True, True, True, True, False, True, True, False],
    '\x70': [False, False, False, False, True, True, True, False],
    '\x71': [True, False, False, False, True, True, True, False],
    '\x72': [False, True, False, False, True, True, True, False],
    '\x73': [True, True, False, False, True, True, True, False],
    '\x74': [False, False, True, False, True, True, True, False],
    '\x75': [True, False, True, False, True, True, True, False],
    '\x76': [False, True, True, False, True, True, True, False],
    '\x77': [True, True, True, False, True, True, True, False],
    '\x78': [False, False, False, True, True, True, True, False],
    '\x79': [True, False, False, True, True, True, True, False],
    '\x7A': [False, True, False, True, True, True, True, False],
    '\x7B': [True, True, False, True, True, True, True, False],
    '\x7C': [False, False, True, True, True, True, True, False],
    '\x7D': [True, False, True, True, True, True, True, False],
    '\x7E': [False, True, True, True, True, True, True, False],
    '\x7F': [True, True, True, True, True, True, True, False],
    '\x80': [False, False, False, False, False, False, False, True],
    '\x81': [True, False, False, False, False, False, False, True],
    '\x82': [False, True, False, False, False, False, False, True],
    '\x83': [True, True, False, False, False, False, False, True],
    '\x84': [False, False, True, False, False, False, False, True],
    '\x85': [True, False, True, False, False, False, False, True],
    '\x86': [False, True, True, False, False, False, False, True],
    '\x87': [True, True, True, False, False, False, False, True],
    '\x88': [False, False, False, True, False, False, False, True],
    '\x89': [True, False, False, True, False, False, False, True],
    '\x8A': [False, True, False, True, False, False, False, True],
    '\x8B': [True, True, False, True, False, False, False, True],
    '\x8C': [False, False, True, True, False, False, False, True],
    '\x8D': [True, False, True, True, False, False, False, True],
    '\x8E': [False, True, True, True, False, False, False, True],
    '\x8F': [True, True, True, True, False, False, False, True],
    '\x90': [False, False, False, False, True, False, False, True],
    '\x91': [True, False, False, False, True, False, False, True],
    '\x92': [False, True, False, False, True, False, False, True],
    '\x93': [True, True, False, False, True, False, False, True],
    '\x94': [False, False, True, False, True, False, False, True],
    '\x95': [True, False, True, False, True, False, False, True],
    '\x96': [False, True, True, False, True, False, False, True],
    '\x97': [True, True, True, False, True, False, False, True],
    '\x98': [False, False, False, True, True, False, False, True],
    '\x99': [True, False, False, True, True, False, False, True],
    '\x9A': [False, True, False, True, True, False, False, True],
    '\x9B': [True, True, False, True, True, False, False, True],
    '\x9C': [False, False, True, True, True, False, False, True],
    '\x9D': [True, False, True, True, True, False, False, True],
    '\x9E': [False, True, True, True, True, False, False, True],
    '\x9F': [True, True, True, True, True, False, False, True],
    '\xA0': [False, False, False, False, False, True, False, True],
    '\xA1': [True, False, False, False, False, True, False, True],
    '\xA2': [False, True, False, False, False, True, False, True],
    '\xA3': [True, True, False, False, False, True, False, True],
    '\xA4': [False, False, True, False, False, True, False, True],
    '\xA5': [True, False, True, False, False, True, False, True],
    '\xA6': [False, True, True, False, False, True, False, True],
    '\xA7': [True, True, True, False, False, True, False, True],
    '\xA8': [False, False, False, True, False, True, False, True],
    '\xA9': [True, False, False, True, False, True, False, True],
    '\xAA': [False, True, False, True, False, True, False, True],
    '\xAB': [True, True, False, True, False, True, False, True],
    '\xAC': [False, False, True, True, False, True, False, True],
    '\xAD': [True, False, True, True, False, True, False, True],
    '\xAE': [False, True, True, True, False, True, False, True],
    '\xAF': [True, True, True, True, False, True, False, True],
    '\xB0': [False, False, False, False, True, True, False, True],
    '\xB1': [True, False, False, False, True, True, False, True],
    '\xB2': [False, True, False, False, True, True, False, True],
    '\xB3': [True, True, False, False, True, True, False, True],
    '\xB4': [False, False, True, False, True, True, False, True],
    '\xB5': [True, False, True, False, True, True, False, True],
    '\xB6': [False, True, True, False, True, True, False, True],
    '\xB7': [True, True, True, False, True, True, False, True],
    '\xB8': [False, False, False, True, True, True, False, True],
    '\xB9': [True, False, False, True, True, True, False, True],
    '\xBA': [False, True, False, True, True, True, False, True],
    '\xBB': [True, True, False, True, True, True, False, True],
    '\xBC': [False, False, True, True, True, True, False, True],
    '\xBD': [True, False, True, True, True, True, False, True],
    '\xBE': [False, True, True, True, True, True, False, True],
    '\xBF': [True, True, True, True, True, True, False, True],
    '\xC0': [False, False, False, False, False, False, True, True],
    '\xC1': [True, False, False, False, False, False, True, True],
    '\xC2': [False, True, False, False, False, False, True, True],
    '\xC3': [True, True, False, False, False, False, True, True],
    '\xC4': [False, False, True, False, False, False, True, True],
    '\xC5': [True, False, True, False, False, False, True, True],
    '\xC6': [False, True, True, False, False, False, True, True],
    '\xC7': [True, True, True, False, False, False, True, True],
    '\xC8': [False, False, False, True, False, False, True, True],
    '\xC9': [True, False, False, True, False, False, True, True],
    '\xCA': [False, True, False, True, False, False, True, True],
    '\xCB': [True, True, False, True, False, False, True, True],
    '\xCC': [False, False, True, True, False, False, True, True],
    '\xCD': [True, False, True, True, False, False, True, True],
    '\xCE': [False, True, True, True, False, False, True, True],
    '\xCF': [True, True, True, True, False, False, True, True],
    '\xD0': [False, False, False, False, True, False, True, True],
    '\xD1': [True, False, False, False, True, False, True, True],
    '\xD2': [False, True, False, False, True, False, True, True],
    '\xD3': [True, True, False, False, True, False, True, True],
    '\xD4': [False, False, True, False, True, False, True, True],
    '\xD5': [True, False, True, False, True, False, True, True],
    '\xD6': [False, True, True, False, True, False, True, True],
    '\xD7': [True, True, True, False, True, False, True, True],
    '\xD8': [False, False, False, True, True, False, True, True],
    '\xD9': [True, False, False, True, True, False, True, True],
    '\xDA': [False, True, False, True, True, False, True, True],
    '\xDB': [True, True, False, True, True, False, True, True],
    '\xDC': [False, False, True, True, True, False, True, True],
    '\xDD': [True, False, True, True, True, False, True, True],
    '\xDE': [False, True, True, True, True, False, True, True],
    '\xDF': [True, True, True, True, True, False, True, True],
    '\xE0': [False, False, False, False, False, True, True, True],
    '\xE1': [True, False, False, False, False, True, True, True],
    '\xE2': [False, True, False, False, False, True, True, True],
    '\xE3': [True, True, False, False, False, True, True, True],
    '\xE4': [False, False, True, False, False, True, True, True],
    '\xE5': [True, False, True, False, False, True, True, True],
    '\xE6': [False, True, True, False, False, True, True, True],
    '\xE7': [True, True, True, False, False, True, True, True],
    '\xE8': [False, False, False, True, False, True, True, True],
    '\xE9': [True, False, False, True, False, True, True, True],
    '\xEA': [False, True, False, True, False, True, True, True],
    '\xEB': [True, True, False, True, False, True, True, True],
    '\xEC': [False, False, True, True, False, True, True, True],
    '\xED': [True, False, True, True, False, True, True, True],
    '\xEE': [False, True, True, True, False, True, True, True],
    '\xEF': [True, True, True, True, False, True, True, True],
    '\xF0': [False, False, False, False, True, True, True, True],
    '\xF1': [True, False, False, False, True, True, True, True],
    '\xF2': [False, True, False, False, True, True, True, True],
    '\xF3': [True, True, False, False, True, True, True, True],
    '\xF4': [False, False, True, False, True, True, True, True],
    '\xF5': [True, False, True, False, True, True, True, True],
    '\xF6': [False, True, True, False, True, True, True, True],
    '\xF7': [True, True, True, False, True, True, True, True],
    '\xF8': [False, False, False, True, True, True, True, True],
    '\xF9': [True, False, False, True, True, True, True, True],
    '\xFA': [False, True, False, True, True, True, True, True],
    '\xFB': [True, True, False, True, True, True, True, True],
    '\xFC': [False, False, True, True, True, True, True, True],
    '\xFD': [True, False, True, True, True, True, True, True],
    '\xFE': [False, True, True, True, True, True, True, True],
    '\xFF': [True, True, True, True, True, True, True, True]
}


#############################################################
# Create a new dictionary by inverting hexlist. The keys must be tuples,
# as lists are not hashable.
def MakeBoolHex():
    return dict([(tuple(j), i) for i, j in boolhexlist.items()])


boolhexlistinvert = MakeBoolHex()
