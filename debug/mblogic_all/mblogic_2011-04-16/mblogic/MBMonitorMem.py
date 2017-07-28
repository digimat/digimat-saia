##############################################################################
# Project: 	Modbus Library
# Module: 	MonitorMem.py
# Purpose: 	Modbus TCP Server.
# Language:	Python 2.5
# Date:		30-Apr-2008.
# Ver:		11-Jun-2010.
# Author:	M. Griffin.
# Copyright:	2008 - 2010 - Michael Griffin       <m.os.griffin@gmail.com>
#
# This file is part of MBLogic.
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
"""
This module monitors the data table for changes on a cyclic basis. It must be
initialised with the start of the cyclic coil address scan range and a dictionary.
The dictionary is used to associate the scanned addresses with the data table which
need to be reset.

The dictionary keys are coil address, and the data is a tuple of bit and register data.
This should be in the form of:
ResetTable = {ResetCoil : (DiscreteInput, Coil, InputRegister, HoldingRegister)}

There are as many dictionary entries as there are client faults configurations. 
If there are no client fault configurations, an empty dictionary is returned.

Public Methods: ScanFaultResetCoils() This needs to be called on a regular basis
(normally by using Twisted task.LoopingCall). When called, it checks to see if any
coils in that range are set. If they are set, it looks them up in the dictionary,
resets the associated data table addresses, and then resets the monitored coils. 

FaultPresent() This returns true if at least one fault coild is set. This may
be used to monitor the state of any client which sets a fault coil.

"""


##############################################################################
import MBDataTable

##############################################################################
class CyclicMemMonitor:

	########################################################
	def __init__(self, ScanAddr, FaultResetTable):
		""" 
		Parameters: ScanAddr - The start of the cyclic coil address scan range.
		FaultResetTable - A dictionary used to relate fault reset bits to 
			the associated fault storage addresses. The keys are coil 
			address, and the data is a tuple of bit and register data.
		"""
		# Save the fault reset table.
		self._FaultTriggers = FaultResetTable
		# Create a set of keys.
		self._FaultKeys = self._FaultTriggers.keys()
		# Start of coil scanning addresses (first address).
		self._ScanAddr = ScanAddr
		# Number of coils to scan.
		self._ScanSize = 256	# This is fixed.
		# Used for quickly comparing if all faults are off.
		self._CoilsOff = [False] * 256


	########################################################
	def FaultPresent(self):
		"""Returns true if at least one fault coil is set.
		"""
		return any(MBDataTable.MemMap.GetCoilsBoolList(self._ScanAddr, self._ScanSize))

	########################################################
	def ScanFaultResetCoils(self):
		""" Check if any of the configured monitored coils are set.
		If any are set, reset the associated fault coils, inputs
		and registers, and reset the monitored fault coils.
		"""
		# Get the current state of the monitored coils.
		MonCoils = MBDataTable.MemMap.GetCoilsBoolList(self._ScanAddr, self._ScanSize)

		# If they are all off, then return immediately.
		if (MonCoils == self._CoilsOff):
			return

		# If any are on, we need to find out which ones.
		# Go through the configured fault table to find out
		# which clients are associated with which bits.
		for fault in self._FaultKeys:
			try:
				# Check to see if that address is on ('1').
				if (MonCoils[(fault - self._ScanAddr)]):
					# Get the bit and register addresses.
					FaultInpAddr, FaultCoilAddr, FaultInpRegAddr, FaultHoldingRegAddr = \
						self._FaultTriggers[fault]

					# Reset the coils, inputs, and registers.
					MBDataTable.MemMap.SetDiscreteInputsBool(FaultInpAddr, False)
					MBDataTable.MemMap.SetCoilsBool(FaultCoilAddr, False)
					MBDataTable.MemMap.SetInputRegistersInt(FaultInpRegAddr, 0)
					MBDataTable.MemMap.SetHoldingRegistersInt(FaultHoldingRegAddr, 0)
			except:
				print('Fatal error in fault monitor system.')


		# Reset all the coils in the monitored range.
		MBDataTable.MemMap.SetCoilsBoolList(self._ScanAddr, self._ScanSize, self._CoilsOff)


##############################################################################


