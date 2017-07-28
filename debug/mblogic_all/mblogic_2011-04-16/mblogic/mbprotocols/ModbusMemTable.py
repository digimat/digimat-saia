##############################################################################
# Project: 	Modbus Library
# Module: 	ModbusMemTable.py
# Purpose: 	Modbus TCP Server (slave).
# Language:	Python 2.5
# Date:		10-Mar-2008.
# Ver:		20-Jul-2010.
# Author:	M. Griffin.
# Copyright:	2008 - 2010 - Michael Griffin       <m.os.griffin@gmail.com>
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# Important:	WHEN EDITING THIS FILE, USE TABS TO INDENT - NOT SPACES!
##############################################################################

import ModbusDataLib

##############################################################################
"""
This holds the memory map (data table). This is the memory structure 
that contains the addressable data.

Data is stored in four (or two) lists: Coils, Discrete Inputs, Holding 
Registers, and Input Registers. Coils and Discrete Inputs are stored
as boolean values. Holding Registers and Input Registers are stored as
*signed* integers.

The data table can be initialised with two optional parameters, "unified"
and "overlay". If unified is True, the Coils are mapped over the Discrete 
Inputs and they form a single list. Writing to a coil will affect the
correstponding Discrete Input. The same is true for Holding Registers and Input 
Registers. This is refered to as a "unified" data table. 

The "overlay" parameter determines where Coils and Discrete Inputs are stored.
If "overlay" is False, they are stored in one or two boolean lists (depending
upon whether "unified" is True or False). If "overlay" is True, they are packed
into the first 4096 registers (0 to 4095). This means for example that Coil "0"
is bit 0 in Holding Register "0", and Coil "15" is bit 15 in Holding Register "0". 

The default for both parameters is False.

E.g. 
Mem = ModbusMemTable.ModbusMemTable()		# Separate address space, no overlay.
Mem = ModbusMemTable.ModbusMemTable(True, True)	# Unified address space with overlay.

------------------------------------------------------------------------------

Public methods:


The following methods accept and return packed binary strings as data.
The packed binary strings are compatible with Modbus data.

The following methods read data table addresses and return a binary string.
addr = data table address. qty = number of consecutive addresses.
1) GetCoils(addr, qty)
2) GetDiscreteInputs(addr, qty)
3) GetHoldingRegisters(addr, qty)
4) GetInputRegisters(addr, qty)

The following methods write data table addresses with binary strings.
addr = data table address. qty = number of consecutive addresses.
data = a packed binary string containing a series of coils or registers.
5) SetCoils(addr, qty, data)
6) SetDiscreteInputs(addr, qty, data)
7) SetHoldingRegisters(addr, qty, data)
8) SetInputRegisters(addr, qty, data)

------------------------------------------------------------------------------

The following methods are equivalent to those above, but accept and return 
lists instead of packed binary strings. 


Coil and discrete input functions return lists of booleans. 
Register functions return lists of *signed* integers.

9) GetCoilsBoolList(addr, qty)
10) GetDiscreteInputsBoolList(addr, qty)
11) GetHoldingRegistersIntList(addr, qty)
12) GetInputRegistersIntList(addr, qty)

Same as above, but these operation on single boolean values (not lists).

13) GetCoilsBool(addr)
14) GetDiscreteInputsBool(addr)
15) GetHoldingRegistersInt(addr)
16) GetInputRegistersInt(addr)


Coil and discrete input functions accept lists of booleans. 
Register functions accept lists of *signed* integers.

17) SetCoilsBoolList(addr, qty, data)
18) SetDiscreteInputsBoolList(addr, qty, data)
19) SetHoldingRegistersIntList(addr, qty, data)
20) SetInputRegistersIntList(addr, qty, data)

Same as above, but these operation on single integer values (not lists).

21) SetCoilsBool(addr, data)
22) SetDiscreteInputsBool(addr, data)
23) SetHoldingRegistersInt(addr, data)
24) SetInputRegistersInt(addr, data)
------------------------------------------------------------------------------

25) GetMaxAddresses() Returns a tuple containing 4 integers representing the 
	maximum address for the discrete inputs, coils, input registers, and 
	holding registers.


"""
class ModbusMemTable:

	########################################################
	def __init__(self, unified = False, overlay = False):
		"""Create the data tables. These follow the Modbus addressing convention.
		Params: 
		unified (boolean) - If True, then outputs are mapped over inputs. 
			If False, then they are separate.
		overlay (boolean) - If True, then coils and discrete inputs are 
			packed into registers. If False, they are not.
		"""

		# Maximum discrete inputs.
		self._MaxDisInp = 65535
		# Maximum coils.
		self._MaxCoils = 65535
		# Maximum input registers.
		self._MaxInpReg = 65535
		# Maximum holding registers.
		self._MaxHReg = 1048575

		# Initialise the Coils list. 
		self._Coils = [False] * (self._MaxCoils + 1)

		# Discrete Inputs. If the data table is unified, then we just
		# use the same list as the coils, so all parts of the data
		# table are mapped over each other.
		if not unified:
			self._DiscInputs = [False] * (self._MaxDisInp + 1)
		else:
			self._DiscInputs = self._Coils


		# Initialise the Holding Registers list. 
		self._HoldingRegs = [0] * (self._MaxHReg + 1)

		# Inputs Registers. If the data table is unified, then we just
		# use the same list as the Holding Registers, so all parts of the data
		# table are mapped over each other.
		if not unified:
			self._InputRegs = [0] * (self._MaxInpReg + 1)
		else:
			self._InputRegs = self._HoldingRegs


		# If the coils and discretes are overlaid on the registers.
		if overlay:
			self.GetHoldingRegisters = self._GetHoldingRegistersOverlay
			self.SetHoldingRegisters = self._SetHoldingRegistersOverlay
			self.GetInputRegisters = self._GetInputRegistersOverlay
			self.SetInputRegisters = self._SetInputRegistersOverlay
		# If the coils and discretes are separate from the registers.
		else:
			self.GetHoldingRegisters = self._GetHoldingRegisters
			self.SetHoldingRegisters = self._SetHoldingRegisters
			self.GetInputRegisters = self._GetInputRegisters
			self.SetInputRegisters = self._SetInputRegisters


	########################################################
	def GetCoils(self, addr, qty):
		"""Return qty coil values as a packed binary string. 
		If qty is not a multiple of 8, the remainder of the string will 
		be padded with zeros.
		addr (integer) - Coil address.
		qty (integer) - Number of coils desired.
		Returns a packed binary string.
		"""
		return ModbusDataLib.boollist2bin(self._Coils[addr : addr + qty])

	def SetCoils(self, addr, qty, data):
		"""Store the data in a packed binary string to the coils.
		addr (integer) - Coil address.
		qty (integer) - Number of coils to set.
		data (packed binary string) - Data.
		"""
		self._Coils[addr : addr + qty] = ModbusDataLib.bin2boollist(data)[:qty]


	#####
	def GetCoilsBoolList(self, addr, qty):
		"""Same as GetCoils, but returns a list of booleans.
		"""
		return self._Coils[addr : addr + qty]

	def GetCoilsBool(self, addr):
		"""Same as GetCoilsBoolList, but returns a single boolean.
		"""
		return self._Coils[addr]

	def SetCoilsBoolList(self, addr, qty, data):
		"""Same as SetCoils, but accepts a list of booleans as data.
		"""
		self._Coils[addr : addr + qty] = data[:qty]

	def SetCoilsBool(self, addr, data):
		"""Same as SetCoilsBoolList, but accepts a single boolean as data.
		"""
		self._Coils[addr] = data


	########################################################
	def GetDiscreteInputs(self, addr, qty):
		"""Return qty discrete input values as a packed binary string. 
		If qty is not a multiple of 8, the remainder of the string will 
		be padded with zeros.
		addr (integer) - Discrete input address.
		qty (integer) - Number of discrete inputs desired.
		Returns a packed binary string.
		"""
		return ModbusDataLib.boollist2bin(self._DiscInputs[addr : addr + qty])


	def SetDiscreteInputs(self, addr, qty, data):
		""""Store the data in a packed binary string to the discrete inputs.
		addr (integer) - Discrete input address.
		qty (integer) - Number of discrete inputs to set.
		data (packed binary string) - Data.
		"""
		self._DiscInputs[addr : addr + qty] = ModbusDataLib.bin2boollist(data)[:qty]


	#####
	def GetDiscreteInputsBoolList(self, addr, qty):
		"""Same as GetDiscreteInputs, but returns a list of booleans.
		"""
		return self._DiscInputs[addr : addr + qty]

	def GetDiscreteInputsBool(self, addr):
		"""Same as GetDiscreteInputsBoolList, but returns a single booleans.
		"""
		return self._DiscInputs[addr]

	def SetDiscreteInputsBoolList(self, addr, qty, data):
		""""Same as SetDiscreteInputs, but accepts a list of booleans as data.
		"""
		self._DiscInputs[addr : addr + qty] = data[:qty]

	def SetDiscreteInputsBool(self, addr, data):
		""""Same as SetDiscreteInputsBoolList, but accepts a single boolean as data.
		"""
		self._DiscInputs[addr] = data

	########################################################
	def _GetHoldingRegisters(self, addr, qty):
		"""Return qty holding register values as a packed binary string. 
		addr (integer) - Holding register address.
		qty (integer) - Number of holding registers desired.
		Returns a packed binary string.
		"""
		return ModbusDataLib.signedintlist2bin(self._HoldingRegs[addr : addr + qty])

	def _SetHoldingRegisters(self, addr, qty, data):
		"""Store the data in a packed binary string to the holding registers.
		addr (integer) - Holding register address.
		qty (integer) - Number of holding registers to set.
		data (packed binary string) - Data.
		"""
		self._HoldingRegs[addr : addr + qty] = ModbusDataLib.signedbin2intlist(data)[:qty]


	def _GetHoldingRegistersOverlay(self, addr, qty):
		"""Same as GetHoldingRegisters, except for register overlay option.
		The coils appear to be packed into holding registers 0 to 4095.
		"""
		if (addr > 4095):
			return self._GetHoldingRegisters(addr, qty)
		else:
			binstr = ModbusDataLib.boollist2bin(self._Coils[addr * 16 : (addr + qty) * 16])
			return ModbusDataLib.swapbytes(binstr)


	def _SetHoldingRegistersOverlay(self, addr, qty, data):
		"""Same as SetHoldingRegisters, except for register overlay option.
		The coils appear to be packed into holding registers 0 to 4095.
		"""
		if (addr > 4095):
			self._SetHoldingRegisters(addr, qty, data)
		else:
			binstr = ModbusDataLib.swapbytes(data)
			self._Coils[addr * 16 : (addr + qty) * 16] = ModbusDataLib.bin2boollist(binstr)[:qty * 16]



	#####
	def GetHoldingRegistersIntList(self, addr, qty):
		"""Same as GetHoldingRegisters, but returns a list of 
		signed integers.
		"""
		return self._HoldingRegs[addr : addr + qty]

	def GetHoldingRegistersInt(self, addr):
		"""Same as GetHoldingRegistersIntList, but returns a single 
		signed integer.
		"""
		return self._HoldingRegs[addr]

	def SetHoldingRegistersIntList(self, addr, qty, data):
		"""Same as SetHoldingRegisters, but accepts a list of 
		signed integers as data.
		"""
		self._HoldingRegs[addr : addr + qty] = data[:qty]

	def SetHoldingRegistersInt(self, addr, data):
		"""Same as SetHoldingRegistersIntList, but accepts a single 
		signed integer as data.
		"""
		self._HoldingRegs[addr] = data

	########################################################
	def _GetInputRegisters(self, addr, qty):
		"""Return qty input register values as a packed binary string. 
		addr (integer) - Input register address.
		qty (integer) - Number of input registers desired.
		Returns a packed binary string.
		"""
		return ModbusDataLib.signedintlist2bin(self._InputRegs[addr : addr + qty])

	def _SetInputRegisters(self, addr, qty, data):
		"""Store the data in a packed binary string to the input registers.
		addr (integer) - Input register address.
		qty (integer) - Number of input registers to set.
		data (packed binary string) - Data.
		"""
		self._InputRegs[addr : addr + qty] = ModbusDataLib.signedbin2intlist(data)[:qty]

	
	def _GetInputRegistersOverlay(self, addr, qty):
		"""Same as GetInputRegisters, except for register overlay option.
		The discrete inputs appear to be packed into input registers 0 to 4095.
		"""
		if (addr > 4095):
			return self._GetInputRegisters(addr, qty)
		else:
			binstr = ModbusDataLib.boollist2bin(self._DiscInputs[addr * 16 : (addr + qty) * 16])
			return ModbusDataLib.swapbytes(binstr)
			

	def _SetInputRegistersOverlay(self, addr, qty, data):
		"""Same as SetInputRegisters, except for register overlay option.
		The discrete inputs appear to be packed into input registers 0 to 4095.
		"""
		if (addr > 4095):
			self._SetInputRegisters(addr, qty, data)
		else:
			binstr = ModbusDataLib.swapbytes(data)
			self._DiscInputs[addr * 16 : (addr + qty) * 16] = ModbusDataLib.bin2boollist(binstr)[:qty * 16]


	#####
	def GetInputRegistersIntList(self, addr, qty):
		"""Same as GetInputRegisters, but returns a list of 
		signed integers.
		"""
		return self._InputRegs[addr : addr + qty]

	def GetInputRegistersInt(self, addr):
		"""Same as GetInputRegistersIntList, but returns a single 
		signed integer.
		"""
		return self._InputRegs[addr]

	def SetInputRegistersIntList(self, addr, qty, data):
		"""Same as GetInputRegisters, but accepts a list of 
		signed integers as data.
		"""
		self._InputRegs[addr : addr + qty] = data[:qty]

	def SetInputRegistersInt(self, addr, data):
		"""Same as GetInputRegisters, but accepts a single 
		signed integer as data.
		"""
		self._InputRegs[addr] = data

	########################################################
	def GetMaxAddresses(self):
		"""Return the maximum valid address for each of Discrete Inputs,
		Coils, Input Registers, and Holding Registers.
		"""
		return self._MaxDisInp, self._MaxCoils, self._MaxInpReg, self._MaxHReg


############################################################



