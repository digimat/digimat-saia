##############################################################################
# Project:  Modbus Library
# Module:   ModbusExtData.py
# Purpose:  Extended Modbus data types.
# Language: Python 2.5
# Date:     07-Jun-2009.
# Ver:      17-Jun-2009.
# Author:   M. Griffin.
# Copyright:    2009 - Michael Griffin       <m.os.griffin@gmail.com>
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# Important:    WHEN EDITING THIS FILE, USE TABS TO INDENT - NOT SPACES!
##############################################################################

from __future__ import division
import struct

##############################################################################
"""
Read and write extended data types to a Modbus compatible data table. Extended
data types are data types that are stored in more than one register. These include:

- 32 bit signed integers.
- Single precision 4 byte floating point.
- Double precision 8 byte floating point.
- String with 2 characters per register.
- String with 1 character per register.

The parameters and return values for each function are described in terms
implying a certain data size (e.g. 32 bit integer). However, all numeric
values are native Python types. The size refers to the range of values
permitted when they are stored in the data table.

"""


##############################################################################
class ExtendedDataTypes:

    ########################################################
    def __init__(self, DataTable):
        """Parameters: DataTable - A Modbus data table object
        providing the following methods:

        """
        self._DataTable = DataTable

    ########################################################
    def GetHRegInt32(self, memaddr):
        """Parameters:
        memaddr (int) - A Holding register address for
            the first of 2 registers storing an integer.
        Returns: (int) A 32 bit signed integer.
        """
        reglist = self._DataTable.GetHoldingRegistersIntList(memaddr, 2)
        return struct.unpack('@i', struct.pack('@2h', *reglist))[0]

    ########################################################
    def GetInpRegInt32(self, memaddr):
        """Parameters:
        memaddr (int) - An Input register address for
            the first of 2 registers storing an integer.
        Returns: (int) A 32 bit signed integer.
        """
        reglist = self._DataTable.GetInputRegistersIntList(memaddr, 2)
        return struct.unpack('@i', struct.pack('@2h', *reglist))[0]

    ########################################################
    def SetHRegInt32(self, memaddr, datavalue):
        """Parameters:
        memaddr (int) - A Holding register address for
            the first of 2 registers storing an integer.
        datavalue (int) - A 32 bit signed integer.
        """
        # Store the result in a pair of registers.
        reglist = list(struct.unpack('@2h', struct.pack('@i', datavalue)))
        self._DataTable.SetHoldingRegistersIntList(memaddr, 2, reglist)

    ########################################################
    def SetInpRegInt32(self, memaddr, datavalue):
        """Parameters:
        memaddr (int) - An Input register address for
            the first of 2 registers storing an integer.
        datavalue (int) - A 32 bit signed integer.
        """
        # Store the result in a pair of registers.
        reglist = list(struct.unpack('@2h', struct.pack('@i', datavalue)))
        self._DataTable.SetInputRegistersIntList(memaddr, 2, reglist)

    ########################################################
    def GetHRegFloat32(self, memaddr):
        """Parameters:
        memaddr (int) - A Holding register address for the first of 2
            registers storing a float (4 byte floating point).
        Returns: (float) A 32 bit float.
        """
        reglist = self._DataTable.GetHoldingRegistersIntList(memaddr, 2)
        return struct.unpack('@f', struct.pack('@2h', *reglist))[0]

    ########################################################
    def GetInpRegFloat32(self, memaddr):
        """Parameters: memaddr (int) - An Input register address for
            the first of 2 registers storing a float (4 byte floating point).
        Returns: (float) A 32 bit float.
        """
        reglist = self._DataTable.GetInputRegistersIntList(memaddr, 2)
        return struct.unpack('@f', struct.pack('@2h', *reglist))[0]

    ########################################################
    def SetHRegFloat32(self, memaddr, datavalue):
        """Parameters:
        memaddr (int) - A Holding register address for the first of 2
            registers storing a float (4 byte floating point).
        datavalue - (float) A 32 bit float.
        """
        # This needs range checking.
        try:
            reglist = list(struct.unpack('@2h', struct.pack('@f', datavalue)))
        except:
            reglist = [0, 0]
        # Store the result in a pair of registers.
        self._DataTable.SetHoldingRegistersIntList(memaddr, 2, reglist)

    ########################################################
    def SetInpRegFloat32(self, memaddr, datavalue):
        """Parameters:
        memaddr (int) - An Input register address for the first of 2
            registers storing a float (4 byte floating point).
        datavalue - (float) A 32 bit float.
        """
        # This needs range checking.
        try:
            reglist = list(struct.unpack('@2h', struct.pack('@f', datavalue)))
        except:
            reglist = [0, 0]
        # Store the result in a pair of registers.
        self._DataTable.SetInputRegistersIntList(memaddr, 2, reglist)

    ########################################################
    def GetHRegFloat64(self, memaddr):
        """Parameters:
        memaddr (int) - A Holding register address for
            the first of 4 registers storing a double (8 byte floating point).
        Returns: (float) A 64 bit float.
        """
        reglist = self._DataTable.GetHoldingRegistersIntList(memaddr, 4)
        return struct.unpack('@d', struct.pack('@4h', *reglist))[0]

    ########################################################
    def GetInpRegFloat64(self, memaddr):
        """Parameters:
        memaddr (int) - An Input register address for
            the first of 4 registers storing a double (8 byte floating point).
        Returns: (float) A 64 bit float.
        """
        reglist = self._DataTable.GetInputRegistersIntList(memaddr, 4)
        return struct.unpack('@d', struct.pack('@4h', *reglist))[0]

    ########################################################
    def SetHRegFloat64(self, memaddr, datavalue):
        """Parameters:
        memaddr (int) - A Holding register address for the first of 4
            registers storing a double (8 byte floating point).
        datavalue - (float) A 64 bit float.
        """
        # This needs range checking.
        try:
            reglist = list(struct.unpack('@4h', struct.pack('@d', datavalue)))
        except:
            reglist = [0, 0, 0, 0]
        # Store the result in a pair of registers.
        self._DataTable.SetHoldingRegistersIntList(memaddr, 4, reglist)

    ########################################################
    def SetInpRegFloat64(self, memaddr, datavalue):
        """Parameters:
        memaddr (int) - An Input register address for the first of 4
            registers storing a double (8 byte floating point).
        datavalue - (float) A 64 bit float.
        """
        # This needs range checking.
        try:
            reglist = list(struct.unpack('@4h', struct.pack('@d', datavalue)))
        except:
            reglist = [0, 0, 0, 0]
        # Store the result in a pair of registers.
        self._DataTable.SetInputRegistersIntList(memaddr, 4, reglist)

    ########################################################
    def GetHRegStr8(self, memaddr, strlen):
        """Parameters:
        memaddr (int) - A Holding register address for the first character
            in the string. The string is stored with 2 characters per
            register, with the first character in the lower byte.
        strlen (int) - The length (in registers) of the storage area for
            the string.
        Returns: (string) A string.
        """
        reglist = self._DataTable.GetHoldingRegistersIntList(memaddr, strlen)
        return struct.pack('>%sH' % len(reglist), *reglist)

    ########################################################
    def GetInpRegStr8(self, memaddr, strlen):
        """Parameters:
        memaddr (int) - An Input register address for the first character
            in the string. The string is stored with 2 characters per
            register, with the first character in the lower byte.
        strlen (int) - The length (in registers) of the storage area for
            the string.
        Returns: (string) A string.
        """
        reglist = self._DataTable.GetInputRegistersIntList(memaddr, strlen)
        return struct.pack('>%sH' % len(reglist), *reglist)

    ########################################################
    def SetHRegStr8(self, memaddr, strlen, datavalue):
        """Parameters:
        mema
            register, with the first character in the lower byte.
        strlen (int) - The length (in registers) of the storage area for the
            string. The string data will be padded with 0 or truncated to fit.
        datavalue - (string) A string.
        """
        # Compensate for 2 characters per register.
        reglen = strlen * 2
        # Pad or truncate the string to the full specified length.
        if (len(datavalue) < reglen):
            datavalue = '%s%s' % (datavalue, '\x00' * (reglen - len(datavalue)))
        elif (len(datavalue) > reglen):
            datavalue = datavalue[:reglen]
        # If the string is of an odd length, pad it out to an even length.
        if ((len(datavalue) % 2) != 0):
            datavalue = '%s\x00' % datavalue
        reglist = list(struct.unpack('>%sh' % (len(datavalue) // 2), datavalue))
        self._DataTable.SetHoldingRegistersIntList(memaddr, len(reglist), reglist)

    ########################################################
    def SetInpRegStr8(self, memaddr, strlen, datavalue):
        """Parameters:
        memaddr (int) - An Input register address for the first character
            in the string. The string is stored with 2 characters per
            register, with the first character in the lower byte.
        strlen (int) - The length (in registers) of the storage area for the
            string. The string data will be padded with 0 or truncated to fit.
        datavalue - (string) A string.
        """
        # Compensate for 2 characters per register.
        reglen = strlen * 2
        # Pad or truncate the string to the full specified length.
        if (len(datavalue) < reglen):
            datavalue = '%s%s' % (datavalue, '\x00' * (reglen - len(datavalue)))
        elif (len(datavalue) > reglen):
            datavalue = datavalue[:reglen]
        # If the string is of an odd length, pad it out to an even length.
        if ((len(datavalue) % 2) != 0):
            datavalue = '%s\x00' % datavalue
        reglist = list(struct.unpack('>%sh' % (len(datavalue) // 2), datavalue))
        self._DataTable.SetInputRegistersIntList(memaddr, len(reglist), reglist)

    ########################################################
    def GetHRegStr16(self, memaddr, strlen):
        """Parameters:
        memaddr (int) - A Holding register address for the first character
            in the string. The string is stored with 1 character per
            register.
        strlen (int) - The length (in registers) of the storage area for
            the string.
        Returns: (string) A string.
        """
        reglist = self._DataTable.GetHoldingRegistersIntList(memaddr, strlen)
        # Mask off the upper byte in the register.
        reglim = [x & 0xff for x in reglist]
        return struct.pack('>%sB' % len(reglist), *reglim)

    ########################################################
    def GetInpRegStr16(self, memaddr, strlen):
        """Parameters:
        memaddr (int) - An Input register address for the first character
            in the string. The string is stored with 1 character per
            register.
        strlen (int) - The length (in registers) of the storage area for
            the string.
        Returns: (string) A string.
        """
        reglist = self._DataTable.GetInputRegistersIntList(memaddr, strlen)
        return struct.pack('>%sB' % len(reglist), *reglist)

    ########################################################
    def SetHRegStr16(self, memaddr, strlen, datavalue):
        """Parameters:
        memaddr (int) - A Holding register address for the first character
            in the string. The string is stored with 1 character per
            register.
        strlen (int) - The length (in registers) of the storage area for the
            string. The string data will be padded with 0 or truncated to fit.
        datavalue - (string) A string.
        """
        # Pad or truncate the string to the full specified length.
        if (len(datavalue) < strlen):
            datavalue = '%s%s' % (datavalue, '\x00' * (strlen - len(datavalue)))
        elif (len(datavalue) > strlen):
            datavalue = datavalue[:strlen]
        reglist = list(struct.unpack('>%sb' % len(datavalue), datavalue))
        self._DataTable.SetHoldingRegistersIntList(memaddr, len(reglist), reglist)

    ########################################################
    def SetInpRegStr16(self, memaddr, strlen, datavalue):
        """Parameters:
        memaddr (int) - An Input register address for the first character
            in the string. The string is stored with 1 character per
            register.
        strlen (int) - The length (in registers) of the storage area for the
            string. The string data will be padded with 0 or truncated to fit.
        datavalue - (string) A string.
        """
        # Pad or truncate the string to the full specified length.
        if (len(datavalue) < strlen):
            datavalue = '%s%s' % (datavalue, '\x00' * (strlen - len(datavalue)))
        elif (len(datavalue) > strlen):
            datavalue = datavalue[:strlen]
        reglist = list(struct.unpack('>%sb' % len(datavalue), datavalue))
        self._DataTable.SetInputRegistersIntList(memaddr, len(reglist), reglist)
