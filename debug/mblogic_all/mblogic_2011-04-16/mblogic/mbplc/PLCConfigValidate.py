##############################################################################
# Project: 	MBLogic
# Module: 	PLCConfigValidate.py
# Purpose: 	Validate the soft logic configuration.
# Language:	Python 2.5
# Date:		30-Jan-2009.
# Ver:		03-Oct-2010.
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

import itertools

import PLCConfig
from mbprotocols import MBAddrTypes



########################################################################
# Error messages.
ErrMsg = {
	'unknownaddr' : 'Soft logic IO config error in %(section)s - unknown address %(paramvalue)s',
	'unknowndtsave' : 'Soft logic IO config error in %(section)s - unknown value %(paramvalue)s',
	'invalidaddr' : 'Soft logic IO config error in %(section)s - unknown address %(paramvalue)s',
}

########################################################
def FormatErr(errkey, section, paramvalue):
	"""Format and return an error message. 
	Parameters:
		errkey (string) = A key to the error message dictionary.
		section (string) = The section name the error occured in.
		paramvalue (string) = The parameter value which is in error.
	Returns (string) = The formatted error message.
	"""
	return (ErrMsg[errkey] % {'section' : section, 'paramvalue' : paramvalue})


########################################################################
class ConfigPLCVal:
	"""This class validates and sets soft logic configurations. This includes 
	setting up the data table scanning actions according to the configuration.
	"""

	############################################################
	def __init__(self, configfile, timestamp, dtaccess, memsaveable, 
			boolparamtype, wordparamtype, wordseq, booldt, worddt):
		"""Validate the soft logic IO configuration parameters.
		Parameters: 
		configfile (string) = The name of the configuration file.
		timestamp (time) = The current time stamp. 
		dtaccess (object) = An object providing data table read and write 
			accessors, including extended data types.
		memsaveable (function) = Returns True if the parameter is a 
			saveable memory address.
		boolparamtype (function) = Returns the type of boolean parameter.
		wordparamtype (function) = Returns True if the parameter is a
			word data table type.
		wordseq (function) = A function returning a list with a 
			sequential list of a subset of the word data table.
			WordTableSeq(tableaddr, datalen)
		booldt (dict) = A reference to the boolean data table. This is
			used to check for the existence of specified addresses.
		worddt (dict) = A reference to the word data table. This is
			used to check for the existence of specified addresses.
		"""

		# Save references to the initialisation parameters.
		self._MemSaveable = memsaveable
		self._BoolParamType = boolparamtype
		self._WordParamType = wordparamtype
		self._WordSeq = wordseq
		self._BoolDataTable = booldt
		self._WordDataTable = worddt


		# Lists to associate PLC addresses with main server addresses.
		self.IOReadBoolList = []
		self.IOReadWordList = []
		self.IOReadExtList = []
		self.IOReadStrList = []
		self.IOWriteBoolList = []
		self.IOWriteWordList = []
		self.IOWriteExtList = []
		self.IOWriteStrList = []

		# IO configuration list for reporting.
		self._IOConfigList = []

		# Configuration errors.
		self._PLCAddrErr = []
		self._MemSaveAddrErr = []
		self._DataTableErr = []
		self._SysTableErr = []
		self._ConfigFileErrors = []

		# This defines the means for defining how to transfer data between the
		# system data table and the soft logic data table.
		# readaction = Method to read data from the data table.
		# readlist = Read operations are added to this list.
		# writeaction = Method to use to write data to the data table.
		# writelist = Write operations are added to this list.
		# softlogictypes = Acceptable soft logic data types.
		# datatype = Data type.
		# datalength = Number of coils or registers for each data element.
		# lengthlimited = If True, the data length is fixed. This is False for strings.

		self._RegisterActions = {
			'coil' : {'readaction' : dtaccess.MemMap.GetCoilsBoolList, 
					'readlist' : self.IOReadBoolList,  
					'writeaction' : dtaccess.MemMap.SetCoilsBoolList, 
					'writelist' : self.IOWriteBoolList,
					'softlogictypes' : ['X', 'Y', 'C'],
					'datatype' : 'boolean',
					'datalength' : 1,
					'lengthlimited' : False},
			'discrete' : {'readaction' : dtaccess.MemMap.GetDiscreteInputsBoolList, 
					'readlist' : self.IOReadBoolList, 
					'writeaction' : dtaccess.MemMap.SetDiscreteInputsBoolList, 
					'writelist' : self.IOWriteBoolList,
					'softlogictypes' : ['X', 'Y', 'C'],
					'datatype' : 'boolean',
					'datalength' : 1,
					'lengthlimited' : False},
			'holdingreg' : {'readaction' : dtaccess.MemMap.GetHoldingRegistersIntList, 
					'readlist' : self.IOReadWordList, 
					'writeaction' : dtaccess.MemMap.SetHoldingRegistersIntList, 
					'writelist' : self.IOWriteWordList,
					'softlogictypes' : ['DS', 'XD', 'YD', 'XS', 'YS'],
					'datatype' : 'word',
					'datalength' : 1,
					'lengthlimited' : False},
			'inputreg' : {'readaction' : dtaccess.MemMap.GetInputRegistersIntList, 
					'readlist' : self.IOReadWordList, 
					'writeaction' : dtaccess.MemMap.SetInputRegistersIntList, 
					'writelist' : self.IOWriteWordList,
					'softlogictypes' : ['DS', 'XD', 'YD', 'XS', 'YS'],
					'datatype' : 'word',
					'datalength' : 1,
					'lengthlimited' : False},
			'holdingreg32' : {'readaction' : dtaccess.MemExtData.GetHRegInt32, 
					'readlist' : self.IOReadExtList, 
					'writeaction' : dtaccess.MemExtData.SetHRegInt32, 
					'writelist' : self.IOWriteExtList,
					'softlogictypes' : ['DD'],
					'datatype' : 'word',
					'datalength' : 2,
					'lengthlimited' : True},
			'inputreg32' : {'readaction' : dtaccess.MemExtData.GetInpRegInt32, 
					'readlist' : self.IOReadExtList, 
					'writeaction' : dtaccess.MemExtData.SetInpRegInt32, 
					'writelist' : self.IOWriteExtList,
					'softlogictypes' : ['DD'],
					'datatype' : 'word',
					'datalength' : 2,
					'lengthlimited' : True},
			'holdingregfloat' : {'readaction' : dtaccess.MemExtData.GetHRegFloat32, 
					'readlist' : self.IOReadExtList, 
					'writeaction' : dtaccess.MemExtData.SetHRegFloat32, 
					'writelist' : self.IOWriteExtList,
					'softlogictypes' : ['DF'],
					'datatype' : 'word',
					'datalength' : 2,
					'lengthlimited' : True},
			'inputregfloat' : {'readaction' : dtaccess.MemExtData.GetInpRegFloat32, 
					'readlist' : self.IOReadExtList, 
					'writeaction' : dtaccess.MemExtData.SetInpRegFloat32, 
					'writelist' : self.IOWriteExtList,
					'softlogictypes' : ['DF'],
					'datatype' : 'word',
					'datalength' : 2,
					'lengthlimited' : True},
			'holdingregdouble' : {'readaction' : dtaccess.MemExtData.GetHRegFloat64, 
					'readlist' : self.IOReadExtList, 
					'writeaction' : dtaccess.MemExtData.SetHRegFloat64, 
					'writelist' : self.IOWriteExtList,
					'softlogictypes' : ['DF'],
					'datatype' : 'word',
					'datalength' : 4,
					'lengthlimited' : True},
			'inputregdouble' : {'readaction' : dtaccess.MemExtData.GetInpRegFloat64, 
					'readlist' : self.IOReadExtList, 
					'writeaction' : dtaccess.MemExtData.SetInpRegFloat64, 
					'writelist' : self.IOWriteExtList,
					'softlogictypes' : ['DF'],
					'datatype' : 'word',
					'datalength' : 4,
					'lengthlimited' : True},
			'holdingregstr8' : {'readaction' : dtaccess.MemExtData.GetHRegStr8, 
					'readlist' : self.IOReadStrList,  
					'writeaction' : dtaccess.MemExtData.SetHRegStr8, 
					'writelist' : self.IOWriteStrList, 
					'softlogictypes' : ['TXT'],
					'datatype' : 'str',
					'datalength' : None,
					'lengthlimited' : True},
			'holdingregstr16' : {'readaction' : dtaccess.MemExtData.GetHRegStr16, 
					'readlist' : self.IOReadStrList,  
					'writeaction' : dtaccess.MemExtData.SetHRegStr16, 
					'writelist' : self.IOWriteStrList, 
					'softlogictypes' : ['TXT'],
					'datatype' : 'str',
					'datalength' : None,
					'lengthlimited' : True},
			'inputregstr8' : {'readaction' : dtaccess.MemExtData.GetInpRegStr8, 
					'readlist' : self.IOReadStrList,  
					'writeaction' : dtaccess.MemExtData.SetInpRegStr8, 
					'writelist' : self.IOWriteStrList, 
					'softlogictypes' : ['TXT'],
					'datatype' : 'str',
					'datalength' : None,
					'lengthlimited' : True},
			'inputregstr16' : {'readaction' : dtaccess.MemExtData.GetInpRegStr16, 
					'readlist' : self.IOReadStrList, 
					'writeaction' : dtaccess.MemExtData.SetInpRegStr16, 
					'writelist' : self.IOWriteStrList, 
					'softlogictypes' : ['TXT'],
					'datatype' : 'str',
					'datalength' : None,
					'lengthlimited' : True}
		}


		# Read in the PLC soft logic configuration.
		self._PLCIOConfig = PLCConfig.PLCConfig(configfile, timestamp)


	########################################################
	def _CheckConfig(self):
		""" Check a complete configuration and update the configuration results. 
		Returns: Nothing
		"""

		# Data file configuration parsing errors.
		self._ConfigFileErrors = self._PLCIOConfig.GetConfigErrors()

		# Check the regular I/O sections.
		self._PLCAddrErr = self._VerifyAddresses(self._PLCIOConfig.GetConfigDict())

		# Check for errors in the memory save parameters.
		self._MemSaveAddrErr = self._VerifyMemSaveAddresses(self._PLCIOConfig.GetMemSaveWordAddr())

		# Update the configuration data, and test for further errors.
		self._DataTableErr, self._SysTableErr = self._ConfigAddrUpdate(self._PLCIOConfig.GetConfigDict())



	########################################################
	def ReadConfigFile(self):
		"""Use the parser object to read a configuration file from disk.
		"""
		self._PLCIOConfig.ReadConfigFile()

		# Check the configuration. The results are stored in the class variables.
		self._CheckConfig()



	########################################################
	def PLCNewIOConfig(self, newconfig):
		""" Validate a new soft logic IO configuration dictionary and 
		store it in the configuration file. 
		Parameters: newconfig (dict) = The new configuration dictionary.
		Returns: (list) = A list containg the errors (if any).
		"""

		self._PLCIOConfig.PLCNewIOConfig(newconfig)


		# Check the configuration. The results are stored in the class variables.
		# This checks for more than just parser errors.
		self._CheckConfig()

		# If all checks are OK (including checks after parsing is done),
		# save the configuration file.
		if not self.IsConfigError():
			self._PLCIOConfig.PLCSaveIOConfig()


		# Return any errors found.
		return self.GetConfigErrorsList()


	############################################################
	def GetSysParams(self):
		"""Return the system parameters.
		"""
		return self._PLCIOConfig.GetSysParams()

	############################################################
	def GetMemSaveUpdateRate(self):
		"""Return the memory save update rate.
		"""
		return self._PLCIOConfig.GetMemSaveUpdateRate()

	############################################################
	def GetMemSaveWordAddr(self):
		"""Return the list with the data table save addresses.
		"""
		return self._PLCIOConfig.GetMemSaveWordAddr()


	############################################################
	def GetMemSaveUpdateStatus(self):
		"""Return the memory save update status.
		"""
		return self._PLCIOConfig.GetMemSaveUpdateStatus()

	############################################################
	def GetMemSaveParams(self):
		"""Return the memory save parameters.
		"""
		return self._PLCIOConfig.GetMemSaveParams()

	############################################################
	def GetConfigDict(self):
		"""Return the configuration parameters.
		"""
		return self._PLCIOConfig.GetConfigDict()


	############################################################
	def GetConfigErrors(self):
		"""Return any configuration errors as a dictionary.
		"""
		return {'addrerr' : self._PLCAddrErr, 
			'memsaveerr' : self._MemSaveAddrErr, 
			'datatableerr' : self._DataTableErr,
			'systableerr' : self._SysTableErr,
			'fileeerr' : self._ConfigFileErrors
			}

	############################################################
	def GetConfigErrorsList(self):
		"""Return any configuration errors as a single list.
		This combines the error dictionary into a single list.
		"""
		configerrors = self.GetConfigErrors().values()
		return list(itertools.chain(*configerrors))



	############################################################
	def IsConfigError(self):
		"""Return True if an error is present.
		"""
		return ((len(self._PLCAddrErr) > 0) or (len(self._MemSaveAddrErr) > 0) or 
			(len(self._DataTableErr) > 0) or (len(self._ConfigFileErrors) > 0) or
			(len(self._SysTableErr) > 0))

	############################################################
	def GetPLCProgName(self):
		"""Return the current soft logic program name.
		Return: (string) - File name of program.
		"""
		return self._PLCIOConfig.GetPLCProgName()

	############################################################
	def GetScanRate(self):
		"""Return the current target soft logic scan rate.
		Return: (float) - Target scan rate in milli-seconds.
		"""
		return self._PLCIOConfig.GetScanRate()

	############################################################
	def GetIOConfig(self):
		"""Return the IO configuration.
		"""
		return self._PLCIOConfig

	############################################################
	def GetIOConfigReport(self):
		"""Return a list with a report of the IO configuration.
		"""
		return self._IOConfigList

	############################################################
	def _VerifyAddrList(self, addrlist, datatable):
		""" Verify that a list of address labels exists
		in the data table.
		Parameters: 
		boollist (list) = List of boolean address labels.
		datatable (dict) = A data table dictionary.
		Returns: (list) = List of addresses which do not exist.
		"""
		# Iterate through the list and attempt to read each one to 
		# find ones that don't exist.
		badaddr = [addr for addr in addrlist if addr not in datatable]

		return badaddr


	############################################################
	def _VerifyAddresses(self, addrconfig):
		"""Verify that a list of address labels exists
		in the data table. This can be used to check the configuration
		which maps the PLC data table to the server data table.
		Parameters: addrconfig (dict) = A dictionary of address 
			configurations to be checked.
		Return: badlabels (list) = A list of address labels which do not
			exist in data table.
		"""

		# Get a list of keys so we can iterate through them all.
		try:
			addrkeys = addrconfig.keys()
		except:
			return None

		# Try reading each address. If the address does not exist, then
		# add that label to the list of bad ones.
		badlabels = []
		for i in addrkeys:
			addrtype = addrconfig[i]['addrtype']
			addrlist = addrconfig[i]['logictable']
			if addrtype in ['coil', 'discrete']:
				badaddr = self._VerifyAddrList(addrlist, self._BoolDataTable)
			else:
				badaddr = self._VerifyAddrList(addrlist, self._WordDataTable)

			# Add any errors to the list of bad addresses.
			if len(badaddr) > 0:
				badlabels.append(FormatErr('unknownaddr', i, badaddr))

		return badlabels


	############################################################
	def _VerifyMemSaveAddresses(self, addrlist):
		"""Verify that a list of address labels consists of only
		addresses which are permitted to be saved and restored. This 
		version is for the data table save configuration. This is done 
		this way to make it compatible with the regular soft logic I/O 
		sections so that it is reported together with it.
		Parameters: addrlist (list) = A list of address configurations 
			to be checked.
		Return: badlabels (list) = A list of address labels which do not
			exist in data table. This is a single element list containing
			a dictionary compatible with the one used for I/O section errors.
		"""
		# Strip out empty strings. These seem to come as an artifact of parsing.
		addrstripped = filter(len, addrlist)
		# Find any addresses that are not memory saveable (or may not exist). 
		badaddr = list(itertools.ifilterfalse(self._MemSaveable, addrstripped))

		# Add any errors to the list of bad addresses.
		badlabels = []
		if badaddr:
			badlabels.append(FormatErr('unknowndtsave', '&logicsave', badaddr))

		return badlabels


	############################################################
	def _CheckBoolParams(self, logictable, softlogictypes):
		"""Validate the boolean soft logic data table parameters.
		Parameters:
		logictable (list) = The list of soft logic addresses to be validated.
		softlogictypes (list) = The list of soft logic address types which
			are permitted. e.g ['X', 'Y', 'C']
		Returns (boolean) = True for OK, False otherwise.
		""" 
		# Get a list of all the valid types in the parameters. Then use
		# a set to get a list of unique values, and then see if they are
		# in the list of valid soft logic types.
		paramtypes = list(set(map(self._BoolParamType, logictable)))
		badvals = [tabletype for tabletype in paramtypes if tabletype not in softlogictypes]

		return len(badvals) == 0

		
	############################################################
	def _CheckWordParams(self, logictable, softlogictypes):
		"""Validate the word soft logic data table parameters.
		Parameters:
		logictable (list) = The list of soft logic addresses to be validated.
		softlogictypes (list) = The list of soft logic address types which
			are permitted. e.g ['DS', 'XS', 'YS']
		Returns (boolean) = True for OK, False otherwise.
		""" 
		# Get a list of all the valid types in the parameters. Then use
		# a set to get a list of unique values, and then see if they are
		# in the list of valid soft logic types.
		paramtypes = list(set(map(self._WordParamType, logictable)))
		badvals = [tabletype for tabletype in paramtypes if tabletype not in softlogictypes]

		return len(badvals) == 0


	############################################################
	def _CheckDataTableAddr(self, memaddr, addrtype, strlen):
		"""Check if the system data table address is valid. This has to 
		take into account data types which occupy multiple addresses.
		Parameters:
		memaddr (integer) = The system data table address.
		addrtype (string) = The address type.
		strlen (integer) = The string length. This is only used if the type is string.
		Returns: (tuple) = Returns True if the address is OK and an integer containing
			the highest address.
		"""
		if (self._RegisterActions[addrtype]['datatype'] != 'str'):
			lastaddr = memaddr + self._RegisterActions[addrtype]['datalength'] - 1
		else:
			lastaddr = memaddr + strlen - 1

		return ((lastaddr >= 0) and (lastaddr <= MBAddrTypes.MaxExtAddrTypes[addrtype])), lastaddr



	############################################################
	def _ConfigAddrUpdate(self, addrconfig):
		"""Set the address configuration. This modifies the
		address lists.
		Parameters: addrconfig (dict) = Dictionary containing the
			address configuration.
		Return (list) = A list of data table errors.
		"""
		LogicTableErr = []
		SysTableErr = []

		# The list of keys is used for reporting purposes.
		addrkeys = addrconfig.keys()
		addrkeys.sort()

		# Iterate through the items.
		for configkeys, configvalues in addrconfig.items():
			addrtype = configvalues['addrtype']
			action = configvalues['action']
			base = configvalues['base']
			strlen = configvalues['strlen']
			logictable = configvalues['logictable']
			addressok = False


			# Determine the read or write action.
			if (action == 'read'):
				keylist = self._RegisterActions[addrtype]['readlist']
				tableaction = self._RegisterActions[addrtype]['readaction']
			elif (action == 'write'):
				keylist = self._RegisterActions[addrtype]['writelist']
				tableaction = self._RegisterActions[addrtype]['writeaction']
			else:
				print('Error - Unrecognised PLC configuration action.')

			# If the data type is string, then the logic table definition
			# needs to be adjusted to a complete list of addresses.
			if (self._RegisterActions[addrtype]['datatype'] == 'str'):
				logictable = self._WordSeq(logictable[0], strlen)

			# Check the address type.
			if (self._RegisterActions[addrtype]['datatype'] == 'boolean'):
				addressok = self._CheckBoolParams(logictable, 
						self._RegisterActions[addrtype]['softlogictypes'])
			elif (self._RegisterActions[addrtype]['datatype'] in ['word', 'str']):
				addressok = self._CheckWordParams(logictable, 
						self._RegisterActions[addrtype]['softlogictypes'])

			# Check the system data table address. This is needed to check for 
			# cases where extended data types extend past the end of memory.
			datatableaddrok, maxaddr = self._CheckDataTableAddr(base, addrtype, strlen)

			if addressok and datatableaddrok:
				# Add the configuration to the appropriate scan list.
				keylist.append({'base' : base, 'strlen' : strlen, 'tableaction' : tableaction,
					'logictable' : logictable, 'qty' : len(logictable)})

				# This list is for reporting purposes. 
				self._IOConfigList.append({'iosection' : addrkeys, 'base' : base, 'strlen' : strlen, 
					'action' : action, 'logictable' : logictable, 
					'addrtype' : addrtype, 'qty' : len(logictable)})
			elif not addressok:
				LogicTableErr.append(FormatErr('unknownaddr', configkeys, logictable))
			elif not datatableaddrok:
				SysTableErr.append(FormatErr('invalidaddr', configkeys, base))

		return LogicTableErr, SysTableErr


########################################################################


