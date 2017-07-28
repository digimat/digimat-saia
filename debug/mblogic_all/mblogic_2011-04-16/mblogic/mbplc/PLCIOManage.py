##############################################################################
# Project: 	MBLogic
# Module: 	PLCIOManage.py
# Purpose: 	Management of soft logic IO interface.
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

import time

from mbsoftlogicck import  DLCkAddrValidate, DLCkLibs, DLCkDataTable

from mbplc import PLCConfigValidate, PLCMemSave
import PLCRun

import MBDataTable

from sysmon import MonUtils

########################################################################
class SoftLogicIO:
	"""This manages the soft logic IO configuration.
	"""

	############################################################
	def __init__(self, datasave):
		"""Initialise the instruction set.
		"""
		self._DataTableSave = datasave

		# Get the time stamp for when we started.
		timestamp = time.time()

		# Create an initial default IO configuration. We give it an empty file name,
		# because we don't want to load the configuration just yet.
		defaultconfig = PLCConfigValidate.ConfigPLCVal('', timestamp, 
			MBDataTable, DLCkAddrValidate.MemSaveable, DLCkAddrValidate.BoolParamType, 
			DLCkAddrValidate.WordParamType, DLCkLibs.WordTableSeq, 
			DLCkDataTable.BoolDataTable, DLCkDataTable.WordDataTable)



		# New and current compiled soft logic configuration data.
		self._PLCCurrentIOConfig = None
		self._PLCNewIOConfig = None

		self._PLCCurrentIOConfigReport = defaultconfig
		self._PLCNewIOConfigReport = defaultconfig

		# General configuration status parameters for IO.
		self._NewIOConfigStatParams = {'starttime' : 0.0, 'signature' : 'NA', 'configstat' : 'error'}
		self._CurrentIOConfigStatParams = {'starttime' : 0.0, 'signature' : 'NA', 'configstat' : 'error'}


		# File name for soft logic IO configuration.
		self._ConfigFileName = 'mblogic.config'


	########################################################
	def _SetConfigStatus(self, timestamp, filesig, configok):
		"""Set the configuration status codes.
		timestamp = Time stamp (as unix time).
		filesig = File hash signature.
		configok = If True, the configuration was OK.
		"""
		if configok:
			configstat = 'ok'
		else:
			configstat = 'error'
		return {'starttime' : timestamp, 'signature' : filesig, 'configstat' : configstat}


	############################################################
	def ReportCurrentIOConfig(self):
		"""Return an object containing the current IO configuration.
		"""
		return self._PLCCurrentIOConfigReport



	############################################################
	def LoadIOConfig(self):
		"""Load a new IO Configuration.
		"""
		# Get the time stamp for when we started.
		timestamp = time.time()

		# Calculate the file signature.
		try:
			filesig = MonUtils.CalcFileSig(self._ConfigFileName)
		except:
			filesig = 'N/A'

		# Load the new configuration.
		self._PLCNewIOConfig = PLCConfigValidate.ConfigPLCVal(self._ConfigFileName, timestamp, 
			MBDataTable, DLCkAddrValidate.MemSaveable, DLCkAddrValidate.BoolParamType, 
			DLCkAddrValidate.WordParamType, DLCkLibs.WordTableSeq, 
			DLCkDataTable.BoolDataTable, DLCkDataTable.WordDataTable)
		self._PLCNewIOConfig.ReadConfigFile()

		# Check if errors are present in the new configuration. The configuration errors
		# are contained in a dictionary of lists. We must therefore examine all of them
		# to check if there are any errors in any of them.
		ConfigOK = not self._PLCNewIOConfig.IsConfigError()

		# Calculate the new status parameters.  
		self._NewIOConfigStatParams = self._SetConfigStatus(timestamp, filesig, ConfigOK)


		# If we don't have anything for the current IO configuration yet, 
		# then use the one we just read, whether it is any good or not.
		if not self._PLCCurrentIOConfig:
			self._PLCCurrentIOConfig = self._PLCNewIOConfig
			PLCRun.PLCSystem.SetCurrentIOConfig(self._PLCCurrentIOConfig)
			self._CurrentIOConfigStatParams = self._NewIOConfigStatParams
			# Set the memory save parameters.
			self._DataTableSave.SetSaveParams(self._PLCCurrentIOConfig.GetMemSaveUpdateRate(), 
				self._PLCCurrentIOConfig.GetMemSaveWordAddr())
			# Set the current scan rate.
			PLCRun.PLCSystem.SetScanRate()

		# If the new PLC IO config is OK, we use it in place of the old one.
		if (not self._PLCNewIOConfig.IsConfigError()):
			self._PLCCurrentIOConfig = self._PLCNewIOConfig
			PLCRun.PLCSystem.SetCurrentIOConfig(self._PLCCurrentIOConfig)
			self._CurrentIOConfigStatParams = self._NewIOConfigStatParams
			# Set the new memory save parameters.
			self._DataTableSave.SetSaveParams(self._PLCCurrentIOConfig.GetMemSaveUpdateRate(), 
				self._PLCCurrentIOConfig.GetMemSaveWordAddr())
			# Set the current scan rate.
			PLCRun.PLCSystem.SetScanRate()


		# Store the status and error information.
		self._PLCCurrentIOConfigReport = self._PLCCurrentIOConfig
		self._PLCNewIOConfigReport = self._PLCNewIOConfig

		return ConfigOK


	############################################################
	def ConfigEdit(self, newconfig):
		"""Check a new soft logic IO configuration, and if it is OK, 
		save it to disk and use it as the current configuration.
		Parameters: newconfig (dict) = The new configuration. 
		Returns: (list) = A list containing any error messages.
		"""

		# Get the time stamp for when we started.
		timestamp = time.time()

		# Load the new configuration.
		self._PLCNewIOConfig = PLCConfigValidate.ConfigPLCVal(self._ConfigFileName, timestamp, 
			MBDataTable, DLCkAddrValidate.MemSaveable, DLCkAddrValidate.BoolParamType, 
			DLCkAddrValidate.WordParamType, DLCkLibs.WordTableSeq, 
			DLCkDataTable.BoolDataTable, DLCkDataTable.WordDataTable)
		self._PLCNewIOConfig.PLCNewIOConfig(newconfig)

		# Check if errors are present in the new configuration. 
		configerrors = self._PLCNewIOConfig.GetConfigErrorsList()
		ConfigOK = not self._PLCNewIOConfig.IsConfigError()

		# Check for errors and return if there are any.
		if not ConfigOK:
			return configerrors


		# Calculate the file signature.
		try:
			filesig = MonUtils.CalcFileSig(self._ConfigFileName)
		except:
			filesig = 'N/A'


		# Calculate the new status parameters.  
		self._NewIOConfigStatParams = self._SetConfigStatus(timestamp, filesig, ConfigOK)


		# If the new PLC IO config is OK, we use it in place of the old one.
		self._PLCCurrentIOConfig = self._PLCNewIOConfig
		PLCRun.PLCSystem.SetCurrentIOConfig(self._PLCCurrentIOConfig)
		self._CurrentIOConfigStatParams = self._NewIOConfigStatParams
		# Set the new memory save parameters.
		self._DataTableSave.SetSaveParams(self._PLCCurrentIOConfig.GetMemSaveUpdateRate(), 
			self._PLCCurrentIOConfig.GetMemSaveWordAddr())
		# Set the current scan rate.
		PLCRun.PLCSystem.SetScanRate()


		# Store the status and error information.
		self._PLCCurrentIOConfigReport = self._PLCCurrentIOConfig
		self._PLCNewIOConfigReport = self._PLCNewIOConfig

		# Everything was OK, so there were no errors to report.
		return configerrors


	########################################################
	def GetNewIOStatParams(self):
		"""Return the soft logic IO status parameters for the new
		configuration.
		"""
		return self._NewIOConfigStatParams

	########################################################
	def GetCurrentIOStatParams(self):
		"""Return the soft logic IO status parameters for the current
		configuration.
		"""
		return self._CurrentIOConfigStatParams


	########################################################
	def GetNewIOConfigReport(self):
		"""Return the soft logic IO configuration parameters for the 
		new configuration.
		"""
		return self._PLCNewIOConfigReport

	########################################################
	def GetCurrentIOConfigReport(self):
		"""Return the soft logic IO configuration parameters for the 
		current configuration.
		"""
		return self._PLCCurrentIOConfigReport


	########################################################
	def GetCurrentPLCProgName(self):
		"""Return the name of the current soft logic program file.
		"""
		return self._PLCCurrentIOConfig.GetPLCProgName()


########################################################################


# Create the soft logic IO control object. This manages loading and
# changeing the soft logic IO configuration.
PLCIO = SoftLogicIO(PLCMemSave.DataTableSave)


