##############################################################################
# Project: 	MBLogic
# Module: 	DLCkCounterTimer.py
# Purpose: 	Counters and timers for a DL Click-like PLC.
# Language:	Python 2.5
# Date:		13-Jun-2008.
# Ver:		25-Aug-2010.
# Author:	M. Griffin.
# Copyright:	2008 - 2010 - Michael Griffin   <m.os.griffin@gmail.com>
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

import time


##############################################################################

class CounterContainer:
	def __init__(self, DataAddr):
		self.CounterDataAddr = DataAddr
		self.LastUp = False
		self.LastDown = False
		self.CurrentValue = 0


class TimerContainer:
	def __init__(self, DataAddr):
		self.TimerDataAddr = DataAddr
		self.CurrentValue = 0
		self.TmrType = None
		self.TimeBase = None
		self.TimerState = 'off'
		self.LastRungState = False
		self.StartedAt = 0

	
##############################################################################

# Define counters and timers.
# This takes care of all counter and timer functionality, and must be imported
# into the interpreter to be used.
class DLCkCounterTimer:

	############################################################
	# CounterList
	def __init__(self, CounterAddrList, CounterDataList, 
		TimerAddrList, TimerDataList, BoolDT, WordDT):

		# Make a dictionary of the counter addresses and their associated
		# preset addresse and last logic state. The last state is 
		# used to determine if the logic is changing from false to true 
		# at this invocation.
		self._CTData = {}
		for i in range(len(CounterAddrList)):
			self._CTData[CounterAddrList[i]] = CounterContainer(CounterDataList[i])


		# Make a dictionary of the timer addresses and their associated
		# preset addresse and last logic state. The last state is 
		# used to determine if the logic is changing from false to true 
		# at this invocation.
		self._TData = {}
		for i in range(len(TimerAddrList)):
			self._TData[TimerAddrList[i]] = TimerContainer(TimerDataList[i])

		# List of timers to be updated between program scans. Timers are added 
		# to the list as they are encountered in the program. This is so that
		# only timers that are actually used in the PLC program are checked to
		# see if they need to be updated.
		self._TimerScanList = []


		# Set references to the word and boolean data tables.
		self._BoolDataTable = BoolDT
		self._WordDataTable = WordDT

		# Initialise time for timers.
		self._LastTime = time.time()



	############################################################
	def UpdateTimers(self):
		"""Iterate through the list of active timers, and update the time. 
		This should be called once per scan as part of the general system 
		overhead. Timing is always done using the system time units. The 
		timer instruction function is expected to convert the number to 
		the appropriate units.
		"""
		# Calculate new time interval.
		newtime = time.time()
		for TAddr in self._TimerScanList:
			if (self._TData[TAddr].TimerState == 'timeup'):
				# Time difference since last scan.
				self._TData[TAddr].CurrentValue = newtime - self._TData[TAddr].StartedAt

		self._LastTime = newtime


	############################################################
	def _TimerBase(self, RungState, Reset, TAddr, Preset, Timebase, Ttype):
		"""Call the timer instruction.
		This function servers as a common base for other timer types. 
		RungState (boolean) = The rung logic state when called.
		Reset (boolean) = Timer reset is requested.
		TAddr (string) = The address label of the timer.
		Preset (integer) = The timer preset value.
		Timebase (string) = The timer timebase code.
		Ttype (string) = The type of timer.
		"""

		# Check if this timer is on the scan list. If not, then
		# add it to the list of timers to be scanned. 
		if not TAddr in self._TimerScanList:
			self._TimerScanList.append(TAddr)


		# Get a temporary reference to give us a shorter name.
		Tmr = self._TData[TAddr]

		# Check if reset is selected. This is only for accumulating 
		# on-delay timers.
		if Reset:
			Tmr.TimerState = 'stop'
			Tmr.CurrentValue = 0
			self._WordDataTable[Tmr.TimerDataAddr] = 0
			self._BoolDataTable[TAddr] = False
			Tmr.LastRungState = RungState
			return


		# RungState just turned on.
		if (RungState and (not Tmr.LastRungState)):
			Tmr.LastRungState = True
			# Initialise on-delay timer.
			if (Ttype == 'tmr'):
				Tmr.TimerState = 'timeup'
				Tmr.TimeBase = Timebase
				Tmr.StartedAt = time.time()
			# For an accumulating timer, we must subtract any accumulated
			# time when we restart it.
			elif (Ttype == 'tmra'):
				Tmr.TimerState = 'timeup'
				Tmr.TimeBase = Timebase
				Tmr.StartedAt = time.time() - Tmr.CurrentValue
			# Off-delay timers are simply stopped.
			elif (Ttype == 'tmroff'):
				Tmr.TimerState = 'stop'


		# RungState just turned off.
		elif ((not RungState) and Tmr.LastRungState):
			Tmr.LastRungState = False
			# On-delay
			if (Ttype == 'tmr'):
				Tmr.TimerState = 'stop'
				Tmr.CurrentValue = 0
			# For an accumulating timer, we don't reset the current
			# time value when we stop it.
			if (Ttype == 'tmra'):
				Tmr.TimerState = 'stop'
			# Off delay.
			elif (Ttype == 'tmroff'):
				Tmr.TimerState = 'timeup'
				Tmr.TimeBase = Timebase
				Tmr.StartedAt = time.time()


		# The time must first be converted into the specified timebase.
		if (Timebase == 'ms'):
			timefactor = 1000.0
		elif (Timebase == 'sec'):
			timefactor = 1.0
		elif (Timebase == 'min'):
			timefactor = 0.016666667
		elif (Timebase == 'hour'):
			timefactor = 0.000277778
		else:	# day
			timefactor = 0.000011574

		# Convert the elapsed time to the requested units.
		elapsedtime = int(Tmr.CurrentValue * timefactor)

		# Set the data table value to match the internal count. Make sure
		# we don't exceed the maximum allowed time value.
		if (elapsedtime <= 32767):
			self._WordDataTable[Tmr.TimerDataAddr] = elapsedtime
		else:
			self._WordDataTable[Tmr.TimerDataAddr] = 32767


		# Set the data table value to match the internal count.
		# On-delay and on-delay accumulating timers.
		if (Ttype in ['tmr', 'tmra']):
			self._BoolDataTable[TAddr] = (elapsedtime >= Preset) and RungState
		# Off-delay timers.
		elif (Ttype == 'tmroff'):
			self._BoolDataTable[TAddr] = ((Tmr.TimerState == 'timeup') and (elapsedtime < Preset))



	############################################################
	def TimerTMR(self, state, TAddr, preset, timebase):
		"""Call the TMR timer instruction.
		state (boolean) = The rung logic state when called.
		TAddr (string) = The address label of the timer.
		preset (integer) = The timer preset value.
		timebase (string) = The timer timebase.
		"""
		self._TimerBase(state, False, TAddr, preset, timebase, 'tmr')

	############################################################
	def TimerTMRA(self, state, reset, TAddr, preset, timebase):
		"""Call the TMRA timer instruction.
		state (boolean) = The rung logic state when called.
		reset (boolean) = Reset the timer.
		TAddr (string) = The address label of the timer.
		preset (integer) = The timer preset value.
		timebase (string) = The timer timebase.
		"""
		self._TimerBase(state, reset, TAddr, preset, timebase, 'tmra')

	############################################################
	def TimerTMROFF(self, state, TAddr, preset, timebase):
		"""Call the TMROFF timer instruction.
		state (boolean) = The rung logic state when called.
		TAddr (string) = The address label of the timer.
		preset (integer) = The timer preset value.
		timebase (string) = The timer timebase.
		"""
		self._TimerBase(state, False, TAddr, preset, timebase, 'tmroff')



	############################################################
	def Counter(self, Up, Down, Reset, CTAddr, Preset, CTTypeUp):
		"""Call the counter instruction.
		Up (boolean) = Count up.
		Down (boolean) = Count down.
		Reset (boolean) = Reset the counter.
		CTAddr (string) = The address label of the counter.
		Preset (integer) = The counter preset value.
		CTTypeUp (boolean) = If true, acts as an up counter, else
			acts as a down counter.
		"""

		# Get a temporary reference to give us a shorter name.
		Ctr = self._CTData[CTAddr]


		# Check if reset is selected.
		if Reset:
			self._WordDataTable[Ctr.CounterDataAddr] = 0
			self._BoolDataTable[CTAddr] = False
			Ctr.LastUp = Up
			Ctr.LastDown = Down
			return

		# Up just turned on.
		if (Up and (not Ctr.LastUp)):
			Ctr.LastUp = True
			if (self._WordDataTable[Ctr.CounterDataAddr] < 32767):
				self._WordDataTable[Ctr.CounterDataAddr] += 1

		# Up just turned off.
		elif ((not Up) and Ctr.LastUp):
			Ctr.LastUp = False

		
		# Down just turned on.
		if (Down and (not Ctr.LastDown)):
			Ctr.LastDown = True
			if (self._WordDataTable[Ctr.CounterDataAddr] > -32768):
				self._WordDataTable[Ctr.CounterDataAddr] -= 1

		# Down just turned off.
		elif ((not Down) and Ctr.LastDown):
			Ctr.LastDown = False


		# Is this an up counter, or a down counter?
		if CTTypeUp:
			# Set the data table boolean bit according to the current value.
			self._BoolDataTable[CTAddr] = (self._WordDataTable[Ctr.CounterDataAddr] >= Preset)
		else:
			# Set the data table boolean bit according to the current value.
			self._BoolDataTable[CTAddr] = (self._WordDataTable[Ctr.CounterDataAddr] <= Preset)


##############################################################################


##############################################################################
class ScanSPFlags:
	"""Update the pre-defined special relays.
	"""

	############################################################
	def __init__(self, BoolDataTable, WordDataTable):
		"""Parameters: BoolDataTable (dictionary) = Boolean data table.
		WordDataTable (dictionary) = Word data table.
		"""
		self._BoolDataTable = BoolDataTable
		self._WordDataTable = WordDataTable

		self._FirstScan = True
		self._AlternateScan = False
		self._LastScanTime = 0
		self._MinScanTime = 32767
		self._MaxScanTime = 0
		self._ScanCounter = 0
		self._ScanCountReady = False	# Delay scan measurements for one scan.


	############################################################
	def ResetSPCounters(self):
		"""This may be used to restart the scan counters and first scan
		flag while the system is running.
		"""
		self._FirstScan = True

		self._LastScanTime = 0
		self._MinScanTime = 32767
		self._MaxScanTime = 0
		self._ScanCounter = 0
		self._WordDataTable['SD10'] = 0		# Current scan time
		self._WordDataTable['SD11'] = 32767	# Smallest scan time.
		self._WordDataTable['SD12'] = 0		# Largest scan time.
		self._ScanCountReady = False	# Delay scan measurements for one scan.


	############################################################
	def UpdateSPRelays(self):
		"""Set scan clock flags. 
		"""

		# Used for time based calculations.
		CurrentTime = time.time()
		TimeInSec = int(CurrentTime)		# Current time in seconds.
		TimeInMs = int(CurrentTime * 1000)	# Current time in milliseconds.

		# First scan since start of systems.
		self._BoolDataTable['SC2'] = self._FirstScan

		# SC1	Always ON.
		self._BoolDataTable['SC1'] = True

		# Toggles every other scan.
		self._BoolDataTable['SC3'] = self._AlternateScan
		self._AlternateScan = not self._AlternateScan

		# Clock calculations are in milli-seconds.
		# 10 ms clock - 50% duty cycle.
		self._BoolDataTable['SC4'] = (TimeInMs % 10) < 5
		# 100 ms second clock - 50% duty cycle.
		self._BoolDataTable['SC5'] = (TimeInMs % 100) < 50
		# 500 ms clock - 50% duty cycle.
		self._BoolDataTable['SC6'] = (TimeInMs % 500) < 250
		# 1 sec clock - 50% duty cycle.
		self._BoolDataTable['SC7'] = (TimeInMs % 1000) < 500
		# 1 min clock - 50% duty cycle.
		self._BoolDataTable['SC8'] = (TimeInMs % 60000) < 30000
		# 1 hour clock - 50% duty cycle.
		self._BoolDataTable['SC9'] = (TimeInSec % 3600) < 1800


		# Update the scan counter. This counts the number of scans.
		self._WordDataTable['SD9'] = self._ScanCounter
		self._ScanCounter += 1
		if (self._ScanCounter > 32767):
			self._ScanCounter = 0

		# Measure the scan time
		LatestScanTime = TimeInMs - self._LastScanTime
		self._LastScanTime = TimeInMs

		# Skip these calculations for the first scan.
		if self._ScanCountReady:
			# Time for last scan.
			self._WordDataTable['SD10'] = LatestScanTime

			# Smallest scan time.
			if (LatestScanTime < self._MinScanTime):
				self._MinScanTime = LatestScanTime
				self._WordDataTable['SD11'] = self._MinScanTime


			# Largest scan time.
			if (LatestScanTime > self._MaxScanTime):
				self._MaxScanTime = LatestScanTime
				self._WordDataTable['SD12'] = self._MaxScanTime


		# First scan has occured. This should be the last instruction 
		# in this function.
		self._FirstScan = False

		# We're now ready to measure scan times. This is not the same as
		# "first scan", because we also reset it when we reset the scan counters.
		self._ScanCountReady = True


		# Real time clock.
		rttime = time.localtime(CurrentTime)
		# Year.
		self._WordDataTable['SD20'] = rttime.tm_year
		# Month.
		self._WordDataTable['SD21'] = rttime.tm_mon
		# Day.
		self._WordDataTable['SD22'] = rttime.tm_mday
		# Day of week. This is *not* the same as the Click.
		self._WordDataTable['SD23'] = rttime.tm_wday
		# Hour.
		self._WordDataTable['SD24'] = rttime.tm_hour
		# Minute.
		self._WordDataTable['SD25'] = rttime.tm_min
		# Second.
		self._WordDataTable['SD26'] = rttime.tm_sec




##############################################################################

