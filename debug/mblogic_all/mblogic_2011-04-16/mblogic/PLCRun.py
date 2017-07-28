##############################################################################
# Project: 	MBLogic
# Module: 	PLCRun.py
# Purpose: 	Run time control of the soft logic engine.
# Language:	Python 2.5
# Date:		30-Jan-2009.
# Ver:		10-Aug-2010.
# Author:	M. Griffin.
# Copyright:	2009 - 2010 - Michael Griffin   <m.os.griffin@gmail.com>
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


from mbsoftlogicck import PLCInterp, DLCkDataTable, DLCkLibs
from mbplc import PLCMemSave


########################################################################
class SoftLogicCK:
	"""This class creates the CK soft logic engine to execute PLC programs.
	"""

	############################################################
	def __init__(self, datasave):
		"""Initialise the instruction set.
		"""
		self._DataTableSave = datasave


		# New and current compiled soft logic configuration data.
		self._PLCCurrentIOConfig = None

		
		# The compiled PLC program.
		self._PLCProgram = None

		# Initialise an interpreter with the PLC program plus all the
		# required support libraries. Initially, set the PLC program 
		# to None, and the instruction count to 0.
		self._MainInterp = PLCInterp.PLCInterp(self._PLCProgram, 
			DLCkDataTable.BoolDataTable, DLCkDataTable.WordDataTable, 
			DLCkDataTable.InstrDataTable,
			DLCkLibs.TableOperations, DLCkDataTable.Accumulator,
			DLCkLibs.BinMathLib, DLCkLibs.FloatMathLib, DLCkLibs.BCDMathLib,
			DLCkLibs.WordConversions, DLCkLibs.CounterTimers, DLCkLibs.SystemScan)


		# PLC program exit conditions.
		self._RunScan = False	# If True, then it is OK to run.
		self._ExitCode = ''	# Program exit code.
		self._ExitSubr = ''	# Program exit subroutine.
		self._ExitRung = 0	# Program exit rung number.


		# Twisted "reactor" used to schedule scans.
		self._TwistReactor = None

		# Default soft logic scan rate. This is the delay between scans
		# in seconds.
		self._ScanRate = 0.100

		# Twisted can call ID.
		self._ScanCallID = None



	########################################################
	def SetReactor(self, twistreactor):
		"""This gives the soft logic system access to the Twisted
		"reactor" which is used to perform the program scanning. 
		Parameters: twistreactor (object) = The Twisted reactor.
		"""
		self._TwistReactor = twistreactor 


	########################################################
	def SetCurrentIOConfig(self, ioconfig):
		"""Set the current soft logic IO configuration. 
		Parameters: ioconfig (object) = The current soft logic IO configuration.
		"""
		self._PLCCurrentIOConfig = ioconfig


	########################################################
	def SetPLCProgram(self, plcprog):
		"""Set the current runnable soft logic program.
		Parameters: plcprog (obj) = The current soft logic program in 
			executable form.
		"""
		self._MainInterp.SetPLCProgram(plcprog)


	############################################################
	def SetScanRate(self):
		"""Set the current soft logic scan rate. This fetches the new scan 
		rate parameter from the soft logic IO parameters, and applies limit
		tests to it before setting it as the current scan rate.
		"""

		# Set the new scan rate. We must convert milli-seconds into seconds.
		self._ScanRate = self._PLCCurrentIOConfig.GetScanRate() / 1000.0

		# Make sure we have a valid scan rate. We also limit it to within
		# an arbitrarily set range. 
		if self._ScanRate:
			if (self._ScanRate < 0.010) or (self._ScanRate > 1.0):
				self._ScanRate = 0.100
		else:
			self._ScanRate = 0.100




	############################################################
	def EnableRunScan(self):
		"""Enable the soft logic program scan.
		"""
		self._RunScan = True

	############################################################
	def DisableRunScan(self):
		"""Disable the soft logic program scan.
		"""
		self._RunScan = False


	############################################################
	def _ReadInputs(self):
		"""Update the PLC data tables from the server data table.
		"""
		# Set the boolean input data.
		for i in self._PLCCurrentIOConfig.IOReadBoolList:
			# Get the data from the server data table.
			boolval = i['tableaction'](i['base'], i['qty'])

			# Make a dictionary out of the address keys and values.
			boolinputs = dict(zip(i['logictable'], boolval))
			self._MainInterp.SetBoolData(boolinputs)


		# Set the word input data for native types.
		for i in self._PLCCurrentIOConfig.IOReadWordList:
			# Get the data from the server data table.
			listval = i['tableaction'](i['base'], i['qty'])

			# Make a dictionary out of the address keys and values.
			wordinputs = dict(zip(i['logictable'], listval))
			self._MainInterp.SetWordData(wordinputs)

		# Set the word input data for extended types.
		for i in self._PLCCurrentIOConfig.IOReadExtList:
			# Get the data from the server data table.
			listval = i['tableaction'](i['base'])
			# Set the value.
			self._MainInterp.SetWordData({i['logictable'][0] : listval})


		# Set the word input data for string types.
		for i in self._PLCCurrentIOConfig.IOReadStrList:
			# Get the data from the server data table.
			listval = i['tableaction'](i['base'], i['strlen'])
			# Make a dictionary out of the address keys and values.
			wordinputs = dict(zip(i['logictable'], listval))
			self._MainInterp.SetWordData(wordinputs)


	############################################################
	def _WriteOutputs(self):
		"""Update the server data table from the PLC data tables.
		"""

		# Write the boolean output data.
		for i in self._PLCCurrentIOConfig.IOWriteBoolList:
			# Get the data from the PLC data table.
			booloutputs = self._MainInterp.GetBoolDataList(i['logictable'])
			# Write it to the server data table.
			i['tableaction'](i['base'], i['qty'], booloutputs)


		# Write the word output data for native types.
		for i in self._PLCCurrentIOConfig.IOWriteWordList:
			# Get the data from the PLC data table.
			wordoutputs = self._MainInterp.GetWordDataList(i['logictable'])
			# Write it to the server data table.
			i['tableaction'](i['base'], i['qty'], wordoutputs)

		# Write the word output data for extended types.
		for i in self._PLCCurrentIOConfig.IOWriteExtList:
			# Get the data from the PLC data table.
			wordoutputs = self._MainInterp.GetWordDataList(i['logictable'])
			# Write it to the server data table.
			i['tableaction'](i['base'], wordoutputs[0])

		# Write the word output data for string types.
		for i in self._PLCCurrentIOConfig.IOWriteStrList:
			# Get the data from the PLC data table.
			outputstr = ''.join(self._MainInterp.GetWordDataList(i['logictable']))
			# Write it to the server data table.
			i['tableaction'](i['base'], i['strlen'], outputstr)


	############################################################
	def RunPLCScan(self):
		"""Run one scan of the PLC program. Results are placed directly into
		the server and PLC data tables.
		"""

		# Check the run state for the soft logic module.
		if self._RunScan:

			# Read the inputs for the PLC.
			self._ReadInputs()

			# Run the program scan.
			self._MainInterp.MainLoop()

			# Write the outputs for the PLC.
			self._WriteOutputs()

			# Get the exit code.
			self._ExitCode, self._ExitSubr, self._ExitRung = self._MainInterp.GetExitCode()

			# Check if it exited normally.
			# result = 'normal_end_requested' == self._ExitCode


			# Save the configured data table addresses. This saved the
			# selected data table values to disk.
			self._DataTableSave.UpdateData()


		# Set up the next scan.
		self._ScanCallID = self._TwistReactor.callLater(self._ScanRate, self.RunPLCScan)


	############################################################
	def GetPLCRunStatus(self):
		"""Get current run status about the copy of the soft
		logic program currently running.
		"""
		if self._RunScan:
			runmode = 'running'
		else:
			runmode = 'stopped'

		return {'plcrunmode' : runmode}

	############################################################
	def GetSystemControlData(self):
		"""Gets data from the system control relays and registers
		in the data table. These only need to be fetched for monitoring
		and reporting. The following addresses are monitored and returned
		in a dictionary:
		SC26 - Watchdog timer (watchdog).
		SD10 - The current scan time (scantime).
		SD11 - The minimum scan time since starting (minscan).
		SD12 - The maximum scan time since starting (maxscan).
		"""

		# Get the data table values.
		booloutputs = self._MainInterp.GetBoolData(['SC26'])
		wordoutputs = self._MainInterp.GetWordData(['SD9', 'SD10', 'SD11', 'SD12'])

		plcruninfo = {}
		# Update the system information.
		plcruninfo['watchdog'] = booloutputs['SC26']
		plcruninfo['scancount'] = wordoutputs['SD9']
		plcruninfo['scantime'] = wordoutputs['SD10']
		plcruninfo['minscan'] = wordoutputs['SD11']
		plcruninfo['maxscan'] = wordoutputs['SD12']

		# Update the exit code information.
		plcruninfo['plcexitcode'] = self._ExitCode
		plcruninfo['plcexitsubr'] = self._ExitSubr
		plcruninfo['plcexitrung'] = self._ExitRung

		return plcruninfo


	############################################################
	def ResetScanValues(self):
		"""This resets the soft logic scan counter and the min and max
		scan time values. 
		"""
		self._MainInterp.WarmRestart()



	############################################################
	def GetDataTableValues(self, addrlist):
		"""Get the data table values corresponding to the addresses
		entered by the user in an arbitrary list.
		Parameters: addrlist (list) = A list of data table addresses.
		Returns: (dict) = A dictionary containing the
		addresses and the corresponding values from the data table. If any
		of the requested addresses were invalid, an error message will be
		returned in place of the data.
		"""

		tablevalues = {}	# This will hold the results.
		# Now, go through the list and get each value, while also
		# verifying the address requested.
		for i in addrlist:
			# First see if it's a boolean.
			try:
				val = DLCkDataTable.BoolDataTable[i]
			except:
				# No? Then see if its a word.
				try:
					val = DLCkDataTable.WordDataTable[i]
				except:
					# No? Then the address is invalid.
					val = 'invalid address'

			
			# Add the value we found to the results dictionary.
			tablevalues[i] = val		

		# This will return a dictionary with the results.
		return tablevalues


########################################################################

# Initialise the soft logic system.
PLCSystem = SoftLogicCK(PLCMemSave.DataTableSave)


########################################################################


