##############################################################################
# Project: 	MBLogic
# Module: 	DLCkLibs.py
# Purpose: 	Common class and function libraries for a DL Click-like PLC.
# Language:	Python 2.5
# Date:		26-May-2008.
# Ver:		09-Jun-2009.
# Author:	M. Griffin.
# Copyright:	2008 - 2009 - Michael Griffin   <m.os.griffin@gmail.com>
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

import math

import DLCkCounterTimer
import DLCkDataTable
import DLCkTableInstr
import DLCkMath


##############################################################################

# Get a list of consecutive word addresses.
def WordTableSeq(tableaddr, datalen):
	"""Given a starting address and a data length, return a list of data
	table addresses which match these parameters.
	Parameters: 
	tableaddr: (string) - Word data table address label. 
	datalen: (integer) - Number of registers. 
	Returns: (list) - An ordered list of data table addresses which meet
		the criteria.
	"""
	startindex = DLCkDataTable.WordAddrIndex[tableaddr]
	return DLCkDataTable.WordAddrList[startindex : startindex + datalen + 1]

##############################################################################
# Data table operations.
TableOperations = DLCkTableInstr.TableOps(DLCkDataTable.BoolDataTable, 
	DLCkDataTable.BoolAddrList, DLCkDataTable.BoolAddrIndex,
	DLCkDataTable.WordDataTable, DLCkDataTable.WordAddrList,
	DLCkDataTable.WordAddrIndex)

##############################################################################

# Library for math functions.
MathLib = DLCkMath.MathOps(math)

# Decimal math equation compiler.
DecMathComp = DLCkMath.DecMathCompiler(MathLib)

# Hexadecimal math equation compiler.
HexMathComp = DLCkMath.HexMathCompiler(MathLib)



# Define the standard math libraries.
BinMathLib = MathLib
FloatMathLib = None
BCDMathLib = None

# Miscellaneous word conversions.
WordConversions = None


##############################################################################

# Counters and timers.

CounterTimers = DLCkCounterTimer.DLCkCounterTimer(
	DLCkDataTable.CounterAddrList, DLCkDataTable.CounterDataList, 
	DLCkDataTable.TimerAddrList, DLCkDataTable.TimerDataList, 
	DLCkDataTable.BoolDataTable, DLCkDataTable.WordDataTable)

##############################################################################

# Scan overhead.
SystemFlags = DLCkCounterTimer.ScanSPFlags(DLCkDataTable.BoolDataTable, DLCkDataTable.WordDataTable)


##############################################################################

class SystemOverhead:
	"""Run any system updates that must happen between logic scans.
	This includes updating timers and system flags.
	"""
	def __init__(self, timers, scanflags):
		"""Parameters: timers (object) - An object including a call to 
			update the timers.
		scanflags (object) - An object including a call to update the
			system flags.
		"""
		self._Timers = timers
		self._ScanFlags = scanflags

	def ScanUpdate(self):
		"""This should be called once per scan to update the timers,
		system flags, and any other actions required between logic scans
		for the specific PLC model being emulated.
		"""
		self._Timers.UpdateTimers()
		self._ScanFlags.UpdateSPRelays()

	def WarmStart(self):
		"""This is used to reset the scan flags for a "warm start". It
		should be called whenever the PLC program has been reloaded while
		the system was running. It is not needed for a "cold start" (when
		the system is completely restarted).
		"""
		self._ScanFlags.ResetSPCounters()



SystemScan = SystemOverhead(CounterTimers, SystemFlags)

##############################################################################

