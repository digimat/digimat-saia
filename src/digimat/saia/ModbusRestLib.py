##############################################################################
# Project:  Modbus Library
# Module:   ModbusRestLib.py
# Purpose:  Encode and decode modbus message data for MBRest protocol.
# Language: Python 2.5
# Date:     10-Mar-2008.
# Version:  23-Jul-2010.
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
This module implements functions from the old ModbusDataStrLib which are
used by the MBRest web service protocol. That protocol is deprecated and
will eventually be removed. This module will be removed at some future date,
and should NOT BE USED for any purpose.

See the ModbusDataLib for list oriented functions which encode and decode
Modbus data.


Public Functions:
=================


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


"""
#############################################################

import binascii


############################################################################################

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
    return ''.join([binhexinvert[data[i: i + 8]] for i in range(0, len(data), 8)])


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
    '\x00': '00000000', '\x01': '10000000', '\x02': '01000000', '\x03': '11000000',
    '\x04': '00100000', '\x05': '10100000', '\x06': '01100000', '\x07': '11100000',
    '\x08': '00010000', '\x09': '10010000', '\x0A': '01010000', '\x0B': '11010000',
    '\x0C': '00110000', '\x0D': '10110000', '\x0E': '01110000', '\x0F': '11110000',
    '\x10': '00001000', '\x11': '10001000', '\x12': '01001000', '\x13': '11001000',
    '\x14': '00101000', '\x15': '10101000', '\x16': '01101000', '\x17': '11101000',
    '\x18': '00011000', '\x19': '10011000', '\x1A': '01011000', '\x1B': '11011000',
    '\x1C': '00111000', '\x1D': '10111000', '\x1E': '01111000', '\x1F': '11111000',
    '\x20': '00000100', '\x21': '10000100', '\x22': '01000100', '\x23': '11000100',
    '\x24': '00100100', '\x25': '10100100', '\x26': '01100100', '\x27': '11100100',
    '\x28': '00010100', '\x29': '10010100', '\x2A': '01010100', '\x2B': '11010100',
    '\x2C': '00110100', '\x2D': '10110100', '\x2E': '01110100', '\x2F': '11110100',
    '\x30': '00001100', '\x31': '10001100', '\x32': '01001100', '\x33': '11001100',
    '\x34': '00101100', '\x35': '10101100', '\x36': '01101100', '\x37': '11101100',
    '\x38': '00011100', '\x39': '10011100', '\x3A': '01011100', '\x3B': '11011100',
    '\x3C': '00111100', '\x3D': '10111100', '\x3E': '01111100', '\x3F': '11111100',
    '\x40': '00000010', '\x41': '10000010', '\x42': '01000010', '\x43': '11000010',
    '\x44': '00100010', '\x45': '10100010', '\x46': '01100010', '\x47': '11100010',
    '\x48': '00010010', '\x49': '10010010', '\x4A': '01010010', '\x4B': '11010010',
    '\x4C': '00110010', '\x4D': '10110010', '\x4E': '01110010', '\x4F': '11110010',
    '\x50': '00001010', '\x51': '10001010', '\x52': '01001010', '\x53': '11001010',
    '\x54': '00101010', '\x55': '10101010', '\x56': '01101010', '\x57': '11101010',
    '\x58': '00011010', '\x59': '10011010', '\x5A': '01011010', '\x5B': '11011010',
    '\x5C': '00111010', '\x5D': '10111010', '\x5E': '01111010', '\x5F': '11111010',
    '\x60': '00000110', '\x61': '10000110', '\x62': '01000110', '\x63': '11000110',
    '\x64': '00100110', '\x65': '10100110', '\x66': '01100110', '\x67': '11100110',
    '\x68': '00010110', '\x69': '10010110', '\x6A': '01010110', '\x6B': '11010110',
    '\x6C': '00110110', '\x6D': '10110110', '\x6E': '01110110', '\x6F': '11110110',
    '\x70': '00001110', '\x71': '10001110', '\x72': '01001110', '\x73': '11001110',
    '\x74': '00101110', '\x75': '10101110', '\x76': '01101110', '\x77': '11101110',
    '\x78': '00011110', '\x79': '10011110', '\x7A': '01011110', '\x7B': '11011110',
    '\x7C': '00111110', '\x7D': '10111110', '\x7E': '01111110', '\x7F': '11111110',
    '\x80': '00000001', '\x81': '10000001', '\x82': '01000001', '\x83': '11000001',
    '\x84': '00100001', '\x85': '10100001', '\x86': '01100001', '\x87': '11100001',
    '\x88': '00010001', '\x89': '10010001', '\x8A': '01010001', '\x8B': '11010001',
    '\x8C': '00110001', '\x8D': '10110001', '\x8E': '01110001', '\x8F': '11110001',
    '\x90': '00001001', '\x91': '10001001', '\x92': '01001001', '\x93': '11001001',
    '\x94': '00101001', '\x95': '10101001', '\x96': '01101001', '\x97': '11101001',
    '\x98': '00011001', '\x99': '10011001', '\x9A': '01011001', '\x9B': '11011001',
    '\x9C': '00111001', '\x9D': '10111001', '\x9E': '01111001', '\x9F': '11111001',
    '\xA0': '00000101', '\xA1': '10000101', '\xA2': '01000101', '\xA3': '11000101',
    '\xA4': '00100101', '\xA5': '10100101', '\xA6': '01100101', '\xA7': '11100101',
    '\xA8': '00010101', '\xA9': '10010101', '\xAA': '01010101', '\xAB': '11010101',
    '\xAC': '00110101', '\xAD': '10110101', '\xAE': '01110101', '\xAF': '11110101',
    '\xB0': '00001101', '\xB1': '10001101', '\xB2': '01001101', '\xB3': '11001101',
    '\xB4': '00101101', '\xB5': '10101101', '\xB6': '01101101', '\xB7': '11101101',
    '\xB8': '00011101', '\xB9': '10011101', '\xBA': '01011101', '\xBB': '11011101',
    '\xBC': '00111101', '\xBD': '10111101', '\xBE': '01111101', '\xBF': '11111101',
    '\xC0': '00000011', '\xC1': '10000011', '\xC2': '01000011', '\xC3': '11000011',
    '\xC4': '00100011', '\xC5': '10100011', '\xC6': '01100011', '\xC7': '11100011',
    '\xC8': '00010011', '\xC9': '10010011', '\xCA': '01010011', '\xCB': '11010011',
    '\xCC': '00110011', '\xCD': '10110011', '\xCE': '01110011', '\xCF': '11110011',
    '\xD0': '00001011', '\xD1': '10001011', '\xD2': '01001011', '\xD3': '11001011',
    '\xD4': '00101011', '\xD5': '10101011', '\xD6': '01101011', '\xD7': '11101011',
    '\xD8': '00011011', '\xD9': '10011011', '\xDA': '01011011', '\xDB': '11011011',
    '\xDC': '00111011', '\xDD': '10111011', '\xDE': '01111011', '\xDF': '11111011',
    '\xE0': '00000111', '\xE1': '10000111', '\xE2': '01000111', '\xE3': '11000111',
    '\xE4': '00100111', '\xE5': '10100111', '\xE6': '01100111', '\xE7': '11100111',
    '\xE8': '00010111', '\xE9': '10010111', '\xEA': '01010111', '\xEB': '11010111',
    '\xEC': '00110111', '\xED': '10110111', '\xEE': '01110111', '\xEF': '11110111',
    '\xF0': '00001111', '\xF1': '10001111', '\xF2': '01001111', '\xF3': '11001111',
    '\xF4': '00101111', '\xF5': '10101111', '\xF6': '01101111', '\xF7': '11101111',
    '\xF8': '00011111', '\xF9': '10011111', '\xFA': '01011111', '\xFB': '11011111',
    '\xFC': '00111111', '\xFD': '10111111', '\xFE': '01111111', '\xFF': '11111111'
}


#############################################################
# Create a new dictionary by inverting hexbininvert.
#
def MakeBinHex():
    return dict([(j, i) for i, j in hexbininvert.items()])
    # return dict([(j, i) for i, j in hexbininvert.iteritems()])


binhexinvert = MakeBinHex()
