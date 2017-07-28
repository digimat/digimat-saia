##############################################################################
# Project: 	MBLogic
# Module: 	PLCConfig.py
# Purpose: 	Read an soft logic address configuration file.
# Language:	Python 2.5
# Date:		20-Jan-2009.
# Ver.:		02-Oct-2010.
# Copyright:	2009 - 2010 - Michael Griffin       <m.os.griffin@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
# Important:	WHEN EDITING THIS FILE, USE TABS TO INDENT - NOT SPACES!
##############################################################################

import ConfigParser

from mbprotocols import MBAddrTypes
import MBFileServices


##############################################################################


_ErrorMessages = {
'badfile' : 'Bad or missing soft logic config file:',
'noplctype' : 'Bad soft logic config - No PLC type specified.',
'noplcprogname' : 'Bad soft logic config - No program name specified.',
'noscanrate' : 'Bad soft logic config - Scan rate missing or invalid.',
'missingaddrtype' :  'Bad soft logic config - address type missing in section:',
'unsuppaddrtype' : 'Bad soft logic config - unsupported address type in section:',
'badmemaddr' : 'Bad soft logic config - data table address out of range in section:',
'missingmemaddr' : 'Bad soft logic config - data table address missing or non-numeric in section:',
'missingaction' : 'Bad soft logic config - bad action in section:',
'unsuppaction' : 'Bad soft logic config - unsupported action in section:',
'missinglogictable' : 'Soft logic config - logic table spec missing in section:',
'noupdateinterval' : 'Soft logic config - no data table save update interval specified. Default value used instead.',
'missingmemsavetable' : 'Soft logic config - no data table save addresses specified.',
'badstrlen' : 'Bad soft logic config - Bad or missing string length.'
}

class PLCConfig:


	########################################################
	def __init__(self, configname, timestamp):
		"""Parameters: configname (string) - Name of configuration file.
		timestamp (float) - Time when initialised.
		"""

		# List of valid data table address types.
		self._ValidAddrTypes = MBAddrTypes.MaxExtAddrTypes.keys()
		

		# List of valid action types.
		self._ValidActionTypes = ['read', 'write']

		# Error messages. This is referenced like this to make adding
		# other message languages easier later.
		self._ErrorMessages = _ErrorMessages

		# Name of configuration file.
		self._ConfigFileName = configname
		# Time when initialised.
		self._TimeStamp = timestamp

		self._ConfigParser = ConfigParser.ConfigParser()

		# This is necessary to prevent ConfigParser from forcing
		# option names to lower case. 
		self._ConfigParser.optionxform = lambda x: x

		# Dictionary for data tags.
		self._ConfigDict = {}
		# Dictionary for system parameters.
		self._SysParams = {'plcprog' : '', 'scan' : 5000, 'type' : 'ck'}
		# List of configuration errors. Initialise it with an error message.
		self._ConfigErrors = []

		# Dictionary for data table save parameters.
		self._MemSaveParams = {'updateinterval' : -10.0, 'wordaddr' : []}

		# Header string to save in configuration file.
		self._FileHeader = 'Soft Logic IO'


	########################################################
	def GetConfigDict(self):
		"""Returns the configuration dictionary.
		"""
		return self._ConfigDict

	########################################################
	def GetSysParams(self):
		"""Return the dictionary with the system parameters.
		"""
		return self._SysParams

	########################################################
	def GetMemSaveParams(self):
		"""Return the dictionary with the data table save parameters.
		"""
		return self._MemSaveParams

	########################################################
	def GetMemSaveWordAddr(self):
		"""Return the list with the data table save addresses.
		"""
		return self._MemSaveParams['wordaddr']

	########################################################
	def GetMemSaveUpdateRate(self):
		"""Return the data table save minimum update interval.
		"""
		return self._MemSaveParams['updateinterval']

	########################################################
	def GetMemSaveUpdateStatus(self):
		"""Returns True if data table saving is enabled.
		"""
		return (self._MemSaveParams['updateinterval'] >= 0.0)


	########################################################
	def GetConfigErrors(self):
		""" Return a list of configuration error strings.
		"""
		return self._ConfigErrors


	########################################################
	def GetScanRate(self):
		"""Return the target scan rate in milliseconds.
		"""
		if self._SysParams['scan']:
			return self._SysParams['scan']
		else:
			return 5000

	########################################################
	def GetPLCProgName(self):
		"""Return the name of the soft logic program.
		"""
		return self._SysParams['plcprog']


	########################################################
	def _ReportError(self, errormsg):
		""" Report an error to the user, and store the message in
		a buffer for later status reporting.
		Parameters: errormsg (string). The error message.
		"""
		print(errormsg)
		self._ConfigErrors.append(errormsg)



	########################################################
	def _AddrListFormat(self, addrstr):
		"""Parameters: addrstr (string) = A string of comma separated
			values which are to be split into a list. We also strip 
			out any white space, such as spaces and tabs, and also 
			double commas.
		Returns: (list) = A list of strings.
		"""
		# We don't verify the logic table addresses just yet, but we do
		# split them into a list if possible.
		# First though, we need to remove all the white space characters.
		addrstr = addrstr.replace(' ', '')
		addrstr = addrstr.replace('\t', '')
		# Also, check for double commas
		addrstr = addrstr.replace(',,', ',')
		# Now, split into a list.
		return addrstr.split(',')


	########################################################
	def _GetSysParams(self, parser):
		""" Get the system parameters. 
		Parameters: parser - config parser object.
		Returns: A dictionary with the parameters for the section,
			or None if an error occured.
		"""

		# Get the PLC logic engine type.
		try:
			logictype = parser.get('&system', 'type')
		except:
			self._ReportError(self._ErrorMessages['noplctype'])
			logictype =  None

		# Get the PLC program name.
		try:
			plcprog = parser.get('&system', 'plcprog')
		except:
			self._ReportError(self._ErrorMessages['noplcprogname'])
			plcprog =  None

		# Get the scan rate.
		try:
			scanrate = int(parser.get('&system', 'scan'))
		except:
			self._ReportError(self._ErrorMessages['noscanrate'])
			scanrate =  None


		# If all is OK, then return a dictionary with the configuration.
		return {'type' : logictype, 'plcprog' : plcprog, 'scan' : scanrate}


	########################################################
	def _GetMemSaveParams(self, parser):
		""" Get the data table save parameters. 
		Parameters: parser - config parser object.
		Returns: A dictionary with the parameters for the section,
			or default values if an error occured. Since this is an
			optional feature, this is not a hard error.
		"""
		# Get the data save update interval (in seconds).
		try:
			updateinterval = float(parser.get('&logicsave', 'updateinterval'))
		except:
			self._ReportError(self._ErrorMessages['noupdateinterval'])
			updateinterval =  -10.0	# Negative indicates no update.

		# Get the list of PLC word data table addresses. These are the data
		# table addresses which will be saved.
		try:
			logictablestr = parser.get('&logicsave', 'wordaddr')
		except:
			self._ReportError(self._ErrorMessages['missingmemsavetable'])
			logictablestr = ''	# Default is not to monitor any addresses.

		# We don't verify the logic table addresses just yet, but we do
		# split them into a list if possible.
		logictable = self._AddrListFormat(logictablestr)

		# We have all the results, so now pack them into a 
		# dictionary and return them.
		return {'updateinterval' : updateinterval, 'wordaddr' : logictable}



	########################################################
	def _GetIOConfig(self, sectionname, parser):
		""" Get the list of items in an IO section. 
		Parameters: sectionname (string): The name of the section.
		Returns: A dictionary with the parameters for the section,
			or None if an error occured.
		"""

		addrtype = ''
		base = ''
		action = ''
		logictable = ''
		strlen = 0


		# Get the type of address.
		try:
			addrtype = parser.get(sectionname, 'addrtype')
		except:
			self._ReportError('%s %s' % (self._ErrorMessages['missingaddrtype'], sectionname))
			return None

		# Check to see if we recognise the address type.
		if addrtype not in self._ValidAddrTypes:
			self._ReportError('%s %s' % (self._ErrorMessages['unsuppaddrtype'], sectionname))
			return None

		# Get the base data table memory address.
		try:
			base = parser.getint(sectionname, 'base')
		except:
			self._ReportError('%s %s' % (self._ErrorMessages['missingmemaddr'], sectionname))
			return None

		# Check if the data table address is out of range.
		if (base < 0) or (base > MBAddrTypes.MaxExtAddrTypes[addrtype]):
			self._ReportError('%s %s' % (self._ErrorMessages['badmemaddr'], sectionname))
			return None

		# Get the type of action to be performed.
		try:
			action = parser.get(sectionname, 'action')
		except:
			self._ReportError('%s %s' % (self._ErrorMessages['missingaction'], sectionname))
			return None

		# Check to see if we recognise the action type.
		if action not in self._ValidActionTypes:
			self._ReportError('%s %s' % (self._ErrorMessages['unsuppaction'], sectionname))
			return None

		# Get the list of PLC data table addresses.
		try:
			logictablestr = parser.get(sectionname, 'logictable')
		except:
			self._ReportError('%s %s' % (self._ErrorMessages['missinglogictable'], sectionname))
			return None

		# Get the string length, if present.
		# This parameter needs to be optional.
		try:
			strlenstr = parser.get(sectionname, 'strlen')
		except:
			strlenstr = '0'

		# Convert the string length to integer.
		try:
			strlen = int(strlenstr)
		except:
			self._ReportError('%s %s' % (self._ErrorMessages['badstrlen'], sectionname))
			return None


		# We don't verify the logic table addresses just yet, but we do
		# split them into a list if possible.
		logictable = self._AddrListFormat(logictablestr)

		# We've passed all the tests, so now pack them into a 
		# dictionary and return them.
		return {'addrtype' : addrtype, 'base' : base, 'strlen' : strlen,
				'action' : action, 'logictable' : logictable}


	########################################################
	def _CheckConfig(self):
		""" Check a complete configuration and update the configuration results. 
		Returns: Nothing
		"""


		# Get the system parameters.
		self._SysParams = self._GetSysParams(self._ConfigParser)

		# Get the data table save parameters.
		self._MemSaveParams = self._GetMemSaveParams(self._ConfigParser)


		# Now we have to get the remaining sections. These will be user 
		# defined tag names, so we don't know in advance what these will be.
		# Get a list of sections. Each section represents one address tag.
		sectionlist = self._ConfigParser.sections()

		self._ConfigDict = {}
		# Go through the list of sections one at a time.
		for i in sectionlist:
			# Otherwised, assume it is for an address tag.
			if i not in ['&system', '&logicsave']:
				sectionconfig = self._GetIOConfig(i, self._ConfigParser)
				# If it was OK, add it to the overall config dictionary.
				if (sectionconfig != None):
					self._ConfigDict[i] = sectionconfig


	########################################################
	def ReadConfigFile(self):
		"""Use the parser object to read a configuration file from disk.
		"""
		
		# Read in the configuration file.
		try:
			filename = self._ConfigParser.read(self._ConfigFileName)

			# The parser should have returned the name of the requested file. 
			if (filename[0] != self._ConfigFileName):
				self._ReportError('%s %s' % (self._ErrorMessages['badfile'], self._ConfigFileName))
				return
		except ConfigParser.ParsingError, parserr:
			self._ReportError('%s %s  %s' % (self._ErrorMessages['badfile'], self._ConfigFileName, parserr))
			return
		except:
			self._ReportError('%s %s' % (self._ErrorMessages['badfile'], self._ConfigFileName))
			return


		# Check the configuration. The results are stored in the class variables.
		self._CheckConfig()


	########################################################
	def PLCNewIOConfig(self, newconfig):
		""" Validate a new soft logic IO configuration dictionary and 
		store it in the configuration file. 
		Parameters: newconfig (dict) = The new configuration dictionary.
		Returns: Nothing.
		"""

		# Add in the system parameters.
		# Web format: {"plcprog": "plcprog.txt", "type": "ck", "scan": 52}
		try:
			sysparams = newconfig['sysparams'].items()
			section = '&system'
			self._ConfigParser.add_section(section)
			for (option, value) in sysparams:
				self._ConfigParser.set(section, option, str(value))
		except:
			pass

		# Add in the memory save parameters. 
		# Web format: {"wordaddr": ["DD1", "DF2", "DS10"], "updateinterval": 2.1}
		try:
			memsaveparams = newconfig['memsaveparams']
			# The list of addresses must be converted to a string.
			wordaddr = ','.join(memsaveparams['wordaddr'])
			updateinterval = str(memsaveparams['updateinterval'])
			section = '&logicsave'
			self._ConfigParser.add_section(section)
			self._ConfigParser.set(section, 'wordaddr', wordaddr)
			self._ConfigParser.set(section, 'updateinterval', updateinterval)
		except:
			pass


		# The logic IO parameters have a consistent format which looks like this:
		# "PandPOut": {"addrtype": "discrete", "base": 32120, "action": "write", 
		#	"strlen": 0, "logictable": ["Y10", "Y11", "Y12"]},

		# First, convert the "logictable" list to a string.
		logicioconfig = newconfig['logicioconfig']
		for (tag, params) in logicioconfig.items():
			params['logictable'] = ','.join(params['logictable'])

		# Now add these to the parser.
		for (section, params) in logicioconfig.items():
			self._ConfigParser.add_section(section)
			for (option, value) in params.items():
				self._ConfigParser.set(section, option, str(value))



		# Check the configuration. The results are stored in the class variables.
		self._CheckConfig()




	########################################################
	def PLCSaveIOConfig(self):
		"""Store the soft logic IO configuration in the configuration file. 
		It is assumed that a valid configuration is already present by 
		one means or another. 
		Returns: (boolean) = True if the file save was Ok. Any error 
			messages are added to the normal error report and
			can be retrieved that way.
		"""

		# If everything was OK, then save the new configuration.
		fileresult = MBFileServices.SaveConfigFile(self._ConfigFileName, 
				self._ConfigParser, self._FileHeader)

		# Was the file save operation Ok? If not, then convert the 
		# error code into an error message.
		if fileresult != 'ok':
			self._ReportError(MBFileServices.FormatErr(fileresult, self._ConfigFileName))
			return True
		else:
			return False



##############################################################################


