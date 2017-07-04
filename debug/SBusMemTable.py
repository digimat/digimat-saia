##############################################################################
# Project: 	SBus Library
# Module: 	SBusMemTable.py
# Purpose: 	SBus Ethernet Server (slave).
# Language:	Python 2.5
# Date:		10-Mar-2008.
# Ver:		21-Nov-2010.
# Author:	M. Griffin.
# Copyright:	2008 - 2010 - Michael Griffin       <m.os.griffin@gmail.com>
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# Important:	WHEN EDITING THIS FILE, USE TABS TO INDENT - NOT SPACES!
##############################################################################

import ModbusDataLib
import SBusMsg

##############################################################################
"""
This holds the memory map (data table). This is the memory structure 
that contains the addressable data.

Data is stored in two lists: Flags and Registers. Inputs and Outputs
simply use the same list as the flags. Flags are boolean values, while
registers are *signed* integers (32 bit).

------------------------------------------------------------------------------

Public methods:


The following methods accept and return packed binary strings as data.
The packed binary strings are compatible with SBus data.

The following methods read data table addresses and return a binary string.
addr = data table address. qty = number of consecutive addresses.
1) GetFlags(addr, qty)
2) GetInputs(addr, qty)
3) GetOutputs(addr, qty)
4) GetRegisters(addr, qty)

The following methods write data table addresses with binary strings.
addr = data table address. qty = number of consecutive addresses.
data = a packed binary string containing a series of coils or registers.
5) SetFlags(addr, qty, data)
6) SetInputs(addr, qty, data)
7) SetOutputs(addr, qty, data)
8) SetRegisters(addr, qty, data)

------------------------------------------------------------------------------

The following methods are equivalent to those above, but accept and return 
lists instead of packed binary strings. 


Coil and discrete input functions return lists of booleans. 
Register functions return lists of *signed* integers.

9) GetFlagsBoolList(addr, qty)
10) GetInputsBoolList(addr, qty)
11) GetOutputsBoolList(addr, qty)
12) GetRegistersIntList(addr, qty)

Same as above, but these operation on single boolean values (not lists).

13) GetFlagsBool(addr)
14) GetInputsBool(addr)
15) GetOutputsBool(addr)
16) GetRegistersInt(addr)


Coil and discrete input functions accept lists of booleans. 
Register functions accept lists of *signed* integers.

17) SetFlagsBoolList(addr, qty, data)
18) SetInputsBoolList(addr, qty, data)
19) SetOutputsBoolList(addr, qty, data)
20) SetRegistersIntList(addr, qty, data)

Same as above, but these operation on single integer values (not lists).

21) SetFlagsBool(addr, data)
22) SetInputsBool(addr, data)
23) SetOutputsBool(addr, data)
24) SetRegistersInt(addr, data)
------------------------------------------------------------------------------

"""
class SBusMemTable:

	########################################################
	def __init__(self):
		"""Create the data tables. These follow the SBus addressing convention.
		"""

		self._MaxMem = 65535			# Maximum SBus address.

		# Initialise the Flags list. 
		# Inputs and outputs simply use the same list as the flags.
		self._Flags = [False] * (self._MaxMem + 1)

		# Initialise the Registers list. 
		self._Registers = [0] * (self._MaxMem + 1)


	########################################################
	def GetFlags(self, addr, qty):
		"""Return qty flags values as a packed binary string. 
		If qty is not a multiple of 8, the remainder of the string will 
		be padded with zeros.
		addr (integer) - Flag address.
		qty (integer) - Number of flags desired.
		Returns a packed binary string.
		"""
		return ModbusDataLib.boollist2bin(self._Flags[addr : addr + qty])


	def SetFlags(self, addr, qty, data):
		"""Store the data in a packed binary string to the flags.
		addr (integer) - Flag address.
		qty (integer) - Number of flags to set.
		data (packed binary string) - Data.
		"""
		self._Flags[addr : addr + qty] = ModbusDataLib.bin2boollist(data)[:qty]


	#####
	def GetFlagsBoolList(self, addr, qty):
		"""Same as GetFlags, but returns a list of booleans.
		"""
		return self._Flags[addr : addr + qty]

	def GetFlagsBool(self, addr):
		"""Same as GetFlagsBoolList, but returns a single boolean.
		"""
		return self._Flags[addr]

	def SetFlagsBoolList(self, addr, qty, data):
		"""Same as SetFlags, but accepts a list of booleans as data.
		"""
		self._Flags[addr : addr + qty] = data[:qty]

	def SetFlagsBool(self, addr, data):
		"""Same as SetFlagsBoolList, but accepts a single boolean as data.
		"""
		self._Flags[addr] = data



	########################################################
	# Input and output addresses are the simply the same as the flags,
	# so we access them using the same functions.

	GetInputs = GetFlags
	SetInputs = SetFlags
	GetInputsBoolList = GetFlagsBoolList
	GetInputsBool = GetFlagsBool
	SetInputsBoolList = SetFlagsBoolList
	SetInputsBool = SetFlagsBool
	  
	GetOutputs = GetFlags
	SetOutputs = SetFlags
	GetOutputsBoolList = GetFlagsBoolList
	GetOutputsBool = GetFlagsBool
	SetOutputsBoolList = SetFlagsBoolList
	SetOutputsBool = SetFlagsBool




	########################################################
	def GetRegisters(self, addr, qty):
		"""Return qty registers values as a packed binary string. 
		addr (integer) - Registers address.
		qty (integer) - Number of registers desired.
		Returns a packed binary string.
		"""
		return SBusMsg.signedint32list2bin(self._Registers[addr : addr + qty])

	def SetRegisters(self, addr, qty, data):
		"""Store the data in a packed binary string to the registers.
		addr (integer) - Registers address.
		qty (integer) - Number of registers to set.
		data (packed binary string) - Data.
		"""
		self._Registers[addr : addr + qty] = SBusMsg.signedbin2int32list(data)[:qty]


	#####
	def GetRegistersIntList(self, addr, qty):
		"""Same as GetRegisters, but returns a list of 
		signed integers.
		"""
		return self._Registers[addr : addr + qty]

	def GetRegistersInt(self, addr):
		"""Same as GetRegistersIntList, but returns a single 
		signed integer.
		"""
		return self._Registers[addr]

	def SetRegistersIntList(self, addr, qty, data):
		"""Same as SetRegisters, but accepts a list of 
		signed integers as data.
		"""
		self._Registers[addr : addr + qty] = data[:qty]

	def SetRegistersInt(self, addr, data):
		"""Same as SetRegistersIntList, but accepts a single 
		signed integer as data.
		"""
		self._Registers[addr] = data


############################################################



