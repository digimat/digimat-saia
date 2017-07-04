##############################################################################
# Project: 	SBus Library
# Module: 	SBusExtData.py
# Purpose: 	Extended SBus data types.
# Language:	Python 2.5
# Date:		07-Jun-2009.
# Ver:		17-Dec-2009.
# Author:	M. Griffin.
# Copyright:	2009 - Michael Griffin       <m.os.griffin@gmail.com>
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# Important:	WHEN EDITING THIS FILE, USE TABS TO INDENT - NOT SPACES!
##############################################################################

import struct

##############################################################################
"""
Read and write extended data types to a SBus compatible data table. Extended 
data types are register data types other than 32 bit integers. These include:

- Single precision 4 byte floating point.
- Double precision 8 byte floating point (2 registers per number).
- String with 1 character per register.

The parameters and return values for each function are described in terms 
implying a certain data size (e.g. 32 bit float). However, all numeric
values are native Python types. The size refers to the range of values 
permitted when they are stored in the data table. 

"""

##############################################################################
class ExtendedDataTypes:

	########################################################
	def __init__(self, DataTable):
		"""Parameters: DataTable - An SBus data table object 
		providing the following methods:
		
		"""
		self._DataTable = DataTable



	########################################################
	def GetRegFloat32(self, memaddr):
		"""Parameters: 
		memaddr (int) - A register address storing a float 
				(4 byte floating point).
		Returns: (float) A 32 bit float.
		"""
		reg = self._DataTable.GetRegistersInt(memaddr)
		return struct.unpack('@f', struct.pack('@i', reg))[0]


	########################################################
	def SetRegFloat32(self, memaddr, datavalue):
		"""Parameters: 
		memaddr (int) - A register address storing a float 
				(4 byte floating point).
		datavalue - (float) A 32 bit float.
		"""
		# This needs range checking.
		try:
			reg = list(struct.unpack('@i', struct.pack('@f', datavalue)))[0]
		except:
			reg = 0
		# Store the result in a register.
		self._DataTable.SetRegistersInt(memaddr, reg)



	########################################################
	def GetRegFloat64(self, memaddr):
		"""Parameters: 
		memaddr (int) - A register address for
			the first of 2 registers storing a double (8 byte floating point).
		Returns: (float) A 64 bit float.
		"""
		reglist = self._DataTable.GetRegistersIntList(memaddr, 2)
		return struct.unpack('@d', struct.pack('@2i', *reglist))[0]


	########################################################
	def SetRegFloat64(self, memaddr, datavalue):
		"""Parameters: 
		memaddr (int) - A Holding register address for the first of 2 
			registers storing a double (8 byte floating point).
		datavalue - (float) A 64 bit float.
		"""
		# This needs range checking.
		try:
			reglist = list(struct.unpack('@2i', struct.pack('@d', datavalue)))
		except:
			reglist = [0, 0]
		# Store the result in a pair of registers.
		self._DataTable.SetRegistersIntList(memaddr, 2, reglist)



	########################################################
	def GetRegStr(self, memaddr, strlen):
		"""Parameters: 
		memaddr (int) - A register address for the first character 
			in the string. The string is stored with 1 character per
			register.
		strlen (int) - The length (in registers) of the storage area for 
			the string. 
		Returns: (string) A string.
		"""
		reglist = self._DataTable.GetRegistersIntList(memaddr, strlen)
		# Mask off the upper bytes in the register.
		reglim = [x & 0xff for x in reglist]
		return struct.pack('>%sB' % len(reglist), *reglim)



	########################################################
	def SetRegStr(self, memaddr, strlen, datavalue):
		"""Parameters: 
		memaddr (int) - A register address for the first character 
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
		self._DataTable.SetRegistersIntList(memaddr, len(reglist), reglist)



##############################################################################

