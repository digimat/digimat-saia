##############################################################################
# Project: 	MBLogic
# Module: 	HMIConfig.py
# Purpose: 	Read an MB-HMI address tag configuration file.
# Language:	Python 2.5
# Date:		22-Sep-2008.
# Ver.:		25-Nov-2010.
# Copyright:	2008 - 2010 - Michael Griffin       <m.os.griffin@gmail.com>
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

import re
import ConfigParser

import MBFileServices

##############################################################################


"""This reads the MB-HMI tag configuration file which defines address
tag names, their types, and their data table addresses.
Configuration files are in the typical Unix format of:
[section]
key=value
key=value
etc.

Where:
[section] - This is the 'tag' name. e.g. [PB1]
addrtype= <data table address type>. The valid address types are imported from 
	the configuration validator passed as part of the initialisation. 
memaddr= <data table address>. This must be a valid data table address.
	For Modbus, valid addresses are integers.

If addrtype is boolean, the following are ignored and the correct
data type (boolean) is automatically used.

datatype= <MB-HMI data type>. Valid MB-HMI data type.
range= <min, max>. Two valid integers or floating point values. These are the
	minimum and maximu legal values for this tag.
scale= <offset, span>. Two valid integers or floating point values. These are the
	scale factors applied to this tag according to y = mx + b where b = offset
	and m = span.

strlen= <length. An integer specifying the length of the string.


# Example MB-HMI config file.
[PB1]
addrtype=discrete
memaddr=9

[SOL1]
addrtype = coil
memaddr = 9

[TankLevel]
addrtype = inputreg
memaddr = 5000
datatype = integer
range = 0, 100
scale = 0, 1

[PumpSpeed]
addrtype = holdingreg
memaddr = 5000
datatype = integer
range = -1800, 1800
scale = 0, 1

Presently, errors are reported in the terminal, and any invalid 
definitions are discarded.

The resulting dictionary appears as follows:

{'addrtype' : addrtype, 	# Data table data type.
'memaddr' : memaddr, 		# Data table address.
'datatype' : datatype,		# MB-HMI data table type.
'minrange' : minrange, 		# Minimum value allowed.
'maxrange': maxrange, 		# Maximum value allowed.
'scaleoffset' : scaleoffset, 	# 'b' value in y=mx + b
'scalespan' : scalespan}	# 'm' value in y=mx + b

At present, the permitted data types are:
1) boolean. ['boolean']
2) integer. ['integer']
3) Floating point. ['float']
4) String. - ['string'].


"""

_ErrorMessages = {
'badfile' : 'Bad MB-HMI config file:',
'clientver' : 'Bad MB-HMI config - client version name too long.',
'noclientver' : 'Bad MB-HMI config - could not find client version.',
'serveridname' : 'Bad MB-HMI config - server id name too long.',
'noserverid' : 'Bad MB-HMI config - could not find server id.',
'missingaddrtype' :  'Bad MB-HMI config - address type missing in section:',
'unsuppaddrtype' : 'Bad MB-HMI config - unsupported address type in section:',
'badmemaddr' : 'Bad MB-HMI config - data table address out of range in section:',
'missingmemaddr' : 'Bad MB-HMI config - data table address missing or incorrect in section:',
'missingdatatype' : 'Bad MB-HMI config - data type is missing or incorrect in section:',
'badrange' : 'Bad MB-HMI config - bad range in section:',
'badscale' : 'Bad MB-HMI config - bad scale factors in section:',
'badstring' : 'Bad MB-HMI config - string too long in section:',
'badtag' : 'Bad MB-HMI config - tag name is invalid in section:',
'badbase' : 'Bad MB-HMI config - base address missing or bad: ',
'badmsgnum' : 'Bad MB-HMI config - bad message number index: ',
'badstrlen' : 'Bad MB-HMI config - bad string length: ',
'badparams' : 'Bad MB-HMI config - no parameters found: ',
'unknownparam' : 'Bad MB-HMI config - unknown parameter name: ',
'erpreadmissing' : 'Bad MB-HMI config - missing read parameter in ERP list: ',
'erpwritemissing' : 'Bad MB-HMI config - missing write parameter in ERP list: ',
'baderpreadtag' : 'Bad MB-HMI config - bad read tag in ERP list: ',
'baderpwritetag' : 'Bad MB-HMI config - bad write tag in ERP list: '
}

class HMIConfig:


	########################################################
	def __init__(self, configname, timestamp, configvalidator):
		"""Parameters: 
		configname (string) = Name of configuration file.
		timestamp (float) = Time when initialised.
		
		configvalidator (object) = Validator object for parameters that 
			are protocol specific. This allows the same configuration
			parser to be used for protocols that require different
			parameter types or ranges. This must expose the following methods:


			1) ValidDataTypes() : Return a list of the valid address types. 
				These must include ['boolean', 'integer', 'float']

			2) DefaultIntRange(self) : Returns a tuple containing the maximum 
				and minimum default integers. This provides default values
				in the event they are not specified in the configuration.

			3) TagAddrClass(addrtype) : Classifies the address type as 
				'scale' or 'noscale' to	determine whether they require 
				scaling parameters. 

			4) AddrTypeIsValid(addrtype) : Tests the 'addrtype' parameter.
				Returns True if addrtype is a valid address type.

			5) MemAddrIsValid(memaddr) : Tests the 'memaddr' parameter.
				Returns a boolean flag and the formatted memory address.
				The flag is True if the address is of the correct type and
				within range. The memory address is returned as an integer
				if it could be converted, or None if not.

			6) AlarmEventAddrIsValid(base, memaddr)
				Parameters: base (string) = The base address to be
					converted to integer and added to memaddr.
				memaddr (string) = The alarm or event number
					to be converted to integer and added to base.
				Returns a boolean flag and the formatted alarm or
				event memory address. 
				The flag is True if the address is of the correct type and
				within range. The memory address is returned as an integer
				if it could be converted, or None if not.

			7) AlarmEventUseBase()
				Returns True if the base address is required for alarms
				and events, False otherwise.

		"""

		# Validator object for parameters that are protocol specific.
		self._Validator = configvalidator

		# List of valid data types implemented in this server.
		self._ValidDataTypes = self._Validator.ValidDataTypes()

		# Error messages. This is referenced like this to make adding
		# other message languages easier later.
		self._ErrorMessages = _ErrorMessages

		# Regex to check the tag names.
		self._TagCheck = re.compile('^[a-zA-Z_][0-9a-zA-Z_]*$')


		# Valid parameter names. 
		self._ValidParamNames = ('addrtype', 'memaddr', 'datatype', 'range', 'scale', 'strlen')


		# Name of configuration file.
		self._ConfigFileName = configname
		# Time when initialised.
		self._TimeStamp = timestamp

		# Dictionary for data tags.
		self._ConfigDict = {}
		# Dictionary for server configuration.
		self._ServerConfigDict = {}
		# Dictionary for event tags.
		self._EventConfig = {}
		# Dictionary for alarm tags.
		self._AlarmConfig = {}
		# Dictionary for the ERP tag list.
		self._ERPConfig = {'read' : [], 'write' : []}
		# Number of tags found.
		self._TagCount = 0
		# Server ID string.
		self._ServerID = 'default server id'
		# Client version string.
		self._ClientVersion = 'default client version'


		self._ConfigParser = ConfigParser.ConfigParser()

		# This is necessary to prevent ConfigParser from forcing
		# option names to lower case. 
		self._ConfigParser.optionxform = lambda x: x

		# List of configuration errors.
		self._ConfigErrors = []

		# Header to use when writing out modified configurations.
		self._FileHeader = 'HMI'


	########################################################
	def GetConfigDict(self):
		"""Returns the configuration dictionary.
		"""
		return self._ConfigDict

	########################################################
	def GetTagCount(self):
		"""Returns the tag count.
		"""
		return self._TagCount

	########################################################
	def GetEventConfig(self):
		"""Returns the event configuration.
		"""
		return self._EventConfig

	########################################################
	def GetAlarmConfig(self):
		"""Returns the alarm configuration.
		"""
		return self._AlarmConfig

	########################################################
	def GetERPConfig(self):
		"""Returns the ERP tag list configuration.
		"""
		return self._ERPConfig

	########################################################
	def GetConfigErrors(self):
		""" Return a list of configuration error strings.
		"""
		return self._ConfigErrors

	########################################################
	def GetTimeStamp(self):
		"""Return the initialisation time stamp.
		"""
		return self._TimeStamp

	########################################################
	def GetServerID(self):
		"""Return the server id string.
		"""
		return self._ServerID

	########################################################
	def GetClientVersion(self):
		"""Return the client version string.
		"""
		return self._ClientVersion


	########################################################
	def _ReportError(self, errormsg):
		""" Report an error to the user, and store the message in
		a buffer for later status reporting.
		Parameters: errormsg (string). The error message.
		"""
		# print(errormsg)
		self._ConfigErrors.append(errormsg)

	########################################################
	def _CheckTagName(self, tagname):
		"""Check a tag name to see if it is valid.
		Parameters: tagname (string) - The tag name to check.
		Returns: (boolean) - True if OK, False if bad.
		"""
		# First, check if the tag name is ok.
		# Check if the tag name is too long.
		if (len(tagname) > 100):
			return False

		# Check if the tag name contains only valid characters, does
		# nost start with a number, and has at least one character.
		elif (self._TagCheck.match(tagname) == None):
			return False

		# We assume the tag name is OK.
		else:
			return True


	########################################################
	def _GetClientVersionConfig(self, parser):
		""" Get the client version from a section. 
		Parameters: parser - config parser object.
		Returns: A dictionary with the parameters for the section,
			or None if an error occured.
		"""

		# There is only one section item, so we look for it directly.
		try:
			clientversion = parser.get('clientversion', 'ver')
		except:
			self._ReportError(self._ErrorMessages['noclientver'])
			return None

		# Make sure the string does not exceed the maximum length
		# of a string for the protocol.
		if (len(clientversion) > 256):
			self._ReportError('%s %s' % (self._ErrorMessages['badstring'], 'clientversion'))
			return None

		# If all is OK, then return a dictionary with the configuration.
		self._ClientVersion = clientversion
		return {'clientversion' : clientversion}


	########################################################
	def _GetServerIDConfig(self, parser):
		""" Get the server id from a section. 
		Parameters: parser - config parser object.
		Returns: A dictionary with the parameters for the section,
			or None if an error occured.
		"""

		# There is only one section item, so we look for it directly.
		try:
			serverid = parser.get('serverid', 'id')
		except:
			self._ReportError(self._ErrorMessages['noserverid'])
			return None

		# Make sure the string does not exceed the maximum length
		# of a string for the protocol.
		if (len(serverid) > 256):
			self._ReportError('%s %s' % (self._ErrorMessages['serveridname'], 'serverid'))
			return None

		# If all is OK, then return a dictionary with the configuration.
		self._ServerID = serverid
		return {'serverid' : serverid}


	########################################################
	def _GetMessageTags(self, messageparams, sectionname, base):
		"""Get the parameters for event and alarm configurations.
		Parameters: 
			messageparams (string) = The parameter string containing the
				offset, tag name, and zone list.
			sectionname (string) = The section name. This is used for 
				error reporting.
			base (integer) = Base address for message number. This
				parameter is protocol dependent and may be set
				to zero if not required.
		Returns: The message number and a dictionary with the tag name
			and zone list. Returns None and an empty dictionary if
			an error occurs.
		"""
		# Get the message number.
		try:
			messageindex = messageparams[0]
		except:
			self._ReportError('%s %s: %s' % (self._ErrorMessages['badmsgnum'], 
				sectionname, messageparams))
			return None, {}

		# Check if the message name is valid. If the base address is used for this
		# protocol, it will be automatically added to the message number.
		msgvalid, messagenum = self._Validator.AlarmEventAddrIsValid(messageindex, base)
		if not msgvalid:
			self._ReportError('%s %s: %s' % (self._ErrorMessages['badmsgnum'], 
				sectionname, messageparams))
			return None, {}

		# Get the tag name and zone list.
		try:
			messagelist = messageparams[1].split(',')
			messagetag = messagelist[0]
			zoneraw = messagelist[1:]
			# Strip out the leading and trailing blanks.
			zonelist = [i.strip() for i in zoneraw]
		except:
			self._ReportError('%s %s' % (self._ErrorMessages['badtag'], sectionname))
			return None, {}


		# Add the event/alarm tag to the dictionary. The message
		# number gets added to the base address to give a data 
		# table address.
		return messagenum, {'tag' : messagetag, 'zonelist' : zonelist}


	########################################################
	def _GetEventsAlarms(self, sectionname, parser):
		""" Get the the list of events or alarms from a section. 
		Parameters: sectionname (string): The name of the section.
		sectionitems: The list of section items.
		Returns: A dictionary with the parameters for the section,
			or None if an error occured.
		"""


		# Base address for events/alarms.
		baseadrr = None
		# Dictionary with events/alarms.
		tagdict = {}

		# First we have to get the base address before we process any
		# other tags, as we need it so we can add it to the address 
		# for each tag. The base address may be ignored for some protocols.
		# This is not user configurable.
		if self._Validator.AlarmEventUseBase():
			try:
				baseadrr = parser.get(sectionname, 'base')
			except:
				self._ReportError('%s %s' % (self._ErrorMessages['badbase'], sectionname))
				return None
		else:
			baseadrr = 0	# Default of 0.


		# Now, get a list of the section items. The section name 
		# should be either alarms or events.
		sectionitems = parser.items(sectionname)

		# Now, go through the other items and look for indexes as keys and
		# event/alarm tags as values. The index is an integer offset which gets
		# added to the base address to be used as an address in the data table.
		for j in sectionitems:
			if (j[0] != 'base'):	# We already found base address, so skip it.

				# Get the tag name and zone list.
				messagenum, tagparams = self._GetMessageTags(j, sectionname, baseadrr)
				if (messagenum != None):
					tagdict[messagenum] = tagparams

		# If all is OK, then return a dictionary with the configuration.
		return tagdict


	########################################################
	def _ParseERPTags(self, parser):
		"""Read the list of ERP tags and make sure they match existing tags
		defined elsewhere.
		Parameters: parser: The configuration parser.
		Returns: A dictionary with the parameters for the section,
			or None if an error occured.
		"""
		# Section name.
		sectionname = '&erplist'

		# This is a new optional parameter, so see if it is present. Existing
		# configurations may not have this.
		if not parser.has_section(sectionname):
			readinp = ''
			writeinp = ''
		else:
			# Get the read parameters.
			try:
				readinp = parser.get(sectionname, 'read')
			except:
				self._ReportError('%s %s' % (self._ErrorMessages['erpreadmissing'], sectionname))
				return None

			# Get the write parameters.
			try:
				writeinp = parser.get(sectionname, 'write')
			except:
				self._ReportError('%s %s' % (self._ErrorMessages['erpwritemissing'], sectionname))
				return None


		# Split them into lists.
		readonly = readinp.split(',')
		readwrite = writeinp.split(',')

		# Strip off any leading or trailing blanks. Also filter out any 
		# empty strings.
		erpread = [x.strip() for x in readonly if len(x.strip())]
		erpwrite = [x.strip() for x in readwrite if len(x.strip())]

		# Verify that the tags exist.
		allsectionlist = parser.sections()
		# Filter out the sections we handle separately.
		# This uses set arithmetic.
		sectionset = set(allsectionlist) - set(('&events', '&alarms', '&erplist'))

		# Find tags that don't exist.
		badreadtags = set(erpread) - sectionset
		badwritetags = set(erpwrite) - sectionset

		if len(badreadtags) > 0:
			self._ReportError('%s %s - %s' % 
				(self._ErrorMessages['baderpreadtag'], sectionname, ', '.join(badreadtags)))
			return None

		if len(badwritetags) > 0:
			self._ReportError('%s %s - %s' % 
				(self._ErrorMessages['baderpwritetag'], sectionname, ', '.join(badwritetags)))
			return None

		# Return the tag lists.
		return {'read' : erpread, 'write' : erpwrite}



	########################################################
	def _GetBoolAddrClass(self):
		"""
		"""
		return 'boolean'

	########################################################
	def _GetStrAddrClass(self, parser, sectionname, memaddr):
		"""Get the string address class.
		Parameters: parser (object) = The parser object.
			sectionname (string) = The section name.
			memaddr (any value) = The memory address.
		Return: (string) = The data type or None if error.
			(tuple) = A tuple containing the address and string length 
				or None if error.
		"""
		datatype = 'string'

		# Get the string length. 
		try:
			stringlen = parser.getint(sectionname, 'strlen')
		except:
			self._ReportError('%s %s' % (self._ErrorMessages['badstrlen'], sectionname))
			return None, None

		# For strings, the memory address is a tuple including the length.
		memaddr = (memaddr, stringlen)

		return datatype, memaddr


	########################################################
	def _GetDataType(self, parser, sectionname):
		"""Get the data type.
		Parameters: parser (object) = The parser object.
			sectionname (string) = The section name.
		Return: (string) = The data type. If no data type is found, 
			'integer' will be returned by default. If the datatype 
			is not one of the recognised types, None will be returned.
		"""

		# Get the data type. If one isn't specified, use integer as a default.
		try:
			datatype = parser.get(sectionname, 'datatype')
		except:
			return None

		# Check if the data type is recognised.
		if datatype not in self._ValidDataTypes:
			self._ReportError('%s %s' % (self._ErrorMessages['unsuppaddrtype'], sectionname))
			return None
		else:
			return datatype



	########################################################
	def _GetDataRange(self, parser, sectionname, defaultminrange, defaultmaxrange):
		"""Get the data range paramters.
		Parameters: parser (object) = The parser.
			sectionname (string) = The section name.
			defaultminrange (numeric) = The default minimum range.
			defaultmaxrange (numeric) = The default maximum range.
		Returns: (float) = The minimum range or None if error.
			(float) = The maximum range or None if error.
		"""

		# Get the data range. 
		try:
			datarange = parser.get(sectionname, 'range')
		except:
			datarange = None

		# If a range was specified, extract the data.
		if (datarange != None):
			try:
				datarangelist = datarange.split(',')
				minrange = float(datarangelist[0])
				maxrange = float(datarangelist[1])
			except:
				self._ReportError('%s %s' % (self._ErrorMessages['badrange'], sectionname))
				return None, None
		else:
			# Use the defaults.
			minrange = defaultminrange
			maxrange = defaultmaxrange

		# The minimum must not be greater than the maximum.
		if (minrange > maxrange):
			self._ReportError('%s %s' % (self._ErrorMessages['badrange'], sectionname))
			return None, None

		return minrange, maxrange


	########################################################
	def _GetScaleFactors(self, parser, sectionname, defaultscaleoffset, defaultscalespan):
		"""Get the scale factor parameters.
		Parameters: parser (object) = The parser.
			sectionname (string) = The section name.
			defaultscaleoffset (numeric) = The default offset.
			defaultscalespan (numeric) = The default span.
		Return: (float) = The scale offset.
			(float) = The scale span.
		"""

		# Get the scaling factors. 
		try:
			scale = parser.get(sectionname, 'scale')
		except:
			scale = None

		# If a scale was specified, extract the data.
		if (scale != None):
			try:
				scalelist = scale.split(',')
				scaleoffset = float(scalelist[0])
				scalespan = float(scalelist[1])
			except:
				self._ReportError('%s %s' % (self._ErrorMessages['badscale'], sectionname))
				return None, None
		else:
			# Use the defaults.
			scaleoffset = defaultscaleoffset
			scalespan = defaultscalespan

		return scaleoffset, scalespan



	########################################################
	def _GetSectionItems(self, sectionname, parser):
		""" Get the list of items in a section. The section is 
		assumed to be for normal address tags.
		Parameters: sectionname (string): The name of the section.
		sectionitems: The list of section items.
		Returns: A dictionary with the parameters for the section,
			or None if an error occured.
		"""

		addrtype = None
		memaddr = None
		datatype = None
		maxrange = None
		minrange = None
		scaleoffset = None
		scalespan = None

		# Check if the tag name contains only valid characters, does
		# nost start with a number, has at least one character, and is
		# not too long.
		if not self._CheckTagName(sectionname):
			self._ReportError('%s %s ' % (self._ErrorMessages['badtag'], sectionname))
			return None

		# Check to see if there are any unknown parameters (items). At this point we
		# just want a list of the actual parameter names.
		try:
			paramitems = parser.items(sectionname)
			paramlist = [x[0] for x in paramitems]
		except:
			self._ReportError('%s %s' % (self._ErrorMessages['badparams'], sectionname))
			return None
			

		# Now see if there are any parameters we don't recognise. This is set
		# arithmatic, not subtraction.
		extra = list(set(paramlist) - set(self._ValidParamNames))

		# Any we don't recognise?
		if len(extra):
			self._ReportError('%s %s' % (self._ErrorMessages['unknownparam'], extra))
			return None


		# Get the type of address.
		try:
			addrtype = parser.get(sectionname, 'addrtype')
		except:
			self._ReportError('%s %s' % (self._ErrorMessages['missingaddrtype'], sectionname))
			return None

		# Check to see if we recognise the address type.
		if not self._Validator.AddrTypeIsValid(addrtype):
			self._ReportError('%s %s' % (self._ErrorMessages['unsuppaddrtype'], sectionname))
			return None

		# Get the data table memory address.
		try:
			memaddrparam = parser.get(sectionname, 'memaddr')
		except:
			self._ReportError('%s %s' % (self._ErrorMessages['missingmemaddr'], sectionname))
			return None
		
		# Check if the data table address is out of range.
		memaddrvalid, memaddr = self._Validator.MemAddrIsValid(memaddrparam, addrtype)
		if not memaddrvalid:
			self._ReportError('%s %s' % (self._ErrorMessages['badmemaddr'], sectionname))
			return None


		# Now check the configuration for any special parameters required 
		# by that data type class.
		addrclass = self._Validator.TagAddrClass(addrtype)
		if (addrclass == 'boolean'):
			datatype = self._GetBoolAddrClass()

		# If the data type is scaleable, we need to get the actual data type,
		# range, and scaling factors.
		elif (addrclass == 'scale'):
			datatype = self._GetDataType(parser, sectionname)
			# If no data type is specified, set the default to integer.
			if (datatype == None):
				datatype = 'integer'

			# Get the maximum and minimum integers to use as defaults.
			maxrange, minrange = self._Validator.DefaultIntRange()

			minrange, maxrange = self._GetDataRange(parser, sectionname, minrange, maxrange)
			if (minrange == None):
				return None

			scaleoffset = 0		# Default scale offset.
			scalespan = 1		# Default scale span factor.
			scaleoffset, scalespan = self._GetScaleFactors(parser, sectionname, scaleoffset, scalespan)
			if (scaleoffset == None):
				return None

		# String data.
		elif (addrclass == 'string'):
			datatype, memaddr = self._GetStrAddrClass(parser, sectionname, memaddr)
			if (datatype == None):
				return None

		# The data type might be determined by a source external to this 
		# program (e.g. accessed via a protocol that doesn't use types).
		# In that case the data type must be explicitely specified.
		elif (addrclass == 'external'):
			# Get the data type.
			datatype = self._GetDataType(parser, sectionname)

			# The data type is boolean. We don't need any other parameters.
			if (datatype == 'boolean'):
				pass

			# The data type is integer or float. We need the range and scale factors.
			elif (datatype in ['integer', 'float']):

				# Get the maximum and minimum integers to use as defaults.
				maxrange, minrange = self._Validator.DefaultIntRange()

				minrange, maxrange = self._GetDataRange(parser, sectionname, minrange, maxrange)
				if (minrange == None):
					return None

				scaleoffset = 0		# Default scale offset.
				scalespan = 1		# Default scale span factor.
				scaleoffset, scalespan = self._GetScaleFactors(parser, sectionname, scaleoffset, scalespan)
				if (scaleoffset == None):
					return None	

			# The data type is string. We need to get the string length 
			# and pack it into the memory address as a tuple.
			elif (datatype == 'string'):
				datatype, memaddr = self._GetStrAddrClass(parser, sectionname, memaddr)
				if (datatype == None):
					return None

			# The data type is unknown.
			else:
				self._ReportError('%s %s' % (self._ErrorMessages['missingdatatype'], sectionname))
				return None

		# Unrecognised type. 
		else:
			self._ReportError('%s %s' % (self._ErrorMessages['unsuppaddrtype'], sectionname))
			return None


		# We've passed all the tests, so now pack them into a dictionary and return them.
		return {'addrtype' : addrtype, 'memaddr' : memaddr, 'datatype' : datatype,
			'minrange' : minrange, 'maxrange': maxrange, 
			'scaleoffset' : scaleoffset, 'scalespan' : scalespan}



	########################################################
	def _CheckConfig(self):
		""" Check a complete configuration and update the configuration results. 
		Returns: Nothing
		"""

		# Get the client version configuration.
		sectionconfig = self._GetClientVersionConfig(self._ConfigParser)
		# If it was OK, add it to the overall config dictionary.
		if (sectionconfig == None):
			sectionconfig = {'clientversion' : 'default client version'}
		self._ConfigDict['clientversion'] = sectionconfig


		# Get the server id.
		sectionconfig = self._GetServerIDConfig(self._ConfigParser)
		# If it was OK, add it to the overall config dictionary.
		if (sectionconfig == None):
			sectionconfig = {'serverid' : 'default server id'}
		self._ConfigDict['serverid'] = sectionconfig


		# Get the event configuration.
		msgconfig = self._GetEventsAlarms('&events', self._ConfigParser)
		if (msgconfig != None):
			self._EventConfig = msgconfig

		# Get the alarm configuration.
		msgconfig = self._GetEventsAlarms('&alarms', self._ConfigParser)
		if (msgconfig != None):
			self._AlarmConfig = msgconfig

		# Now we have to get the remaining sections. These will be user 
		# defined tag names, so we don't know in advance what these will be.
		# Get a list of sections. Each section represents one address tag.
		allsectionlist = self._ConfigParser.sections()

		# Filter out the sections we handle separately.
		standardsections = ('clientversion', 'serverid', '&events', '&alarms', '&erplist')
		# This uses set arithmetic.
		sectionlist = list(set(allsectionlist) - set(standardsections))

		# Go through the list of sections one at a time.
		for i in sectionlist:
			sectionconfig = self._GetSectionItems(i, self._ConfigParser)
			# If it was OK, add it to the overall config dictionary.
			if (sectionconfig != None):
				self._ConfigDict[i] = sectionconfig

		# Get the ERP lists. These have to be done last as the validity of the
		# items depends on the other tags existing and being valid.
		erpconfig = self._ParseERPTags(self._ConfigParser)
		if (erpconfig != None):
			self._ERPConfig = erpconfig

		# Now, count how many tags are configured, not including the standard ones.
		self._TagCount = len(self._ConfigDict) - 2



	########################################################
	def ReadConfigFile(self):
		"""Use the parser object to read a configuration file from disk.
		"""

		# Read in the configuration file for parsing.
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
	def _FormatToFile(self, config):
		"""Convert the expanded parameter format used in the program
		to the format used when storing the parameters to disk.
		Parameters: config (dict) = The expanded dictionary format used
			in the program.
		Returns: (dict) = The abreviated format used for disk storage.
		E.g. {'addrtype' : addrtype, 'memaddr' : memaddr, 'datatype' : datatype,
			'minrange' : minrange, 'maxrange': maxrange, 
			'scaleoffset' : scaleoffset, 'scalespan' : scalespan}
		Converts to {'addrtype' : addresstype, 'memaddr' : memaddr, 
				'datatype' : datatype, 'range' : (minrange, maxrange), 
				'scale' : (minrange, maxrange), 'strlen' : unpacked tuple from memaddr)
		"""

		reconfig = {}

		# Filter out the empty data (None).
		filtconfig = dict([(x, y) for x,y in config.items() if y != None])

		try:
			reconfig['addrtype'] = '%s' % filtconfig['addrtype']
		except:
			pass

		try:
			reconfig['datatype'] = '%s' % filtconfig['datatype']
		except:
			pass

		# Memory address may have to be unpacked from a tuple if the datatype is string.
		try:
			memaddr = filtconfig['memaddr']
			if reconfig['datatype'] == 'string':
				reconfig['memaddr'] = '%s' % memaddr[0]
				reconfig['strlen'] = '%s' % memaddr[1]
			else:
				reconfig['memaddr'] = '%s' % memaddr
		except:
			pass



		# Range has to be combined into a single string.
		try:
			reconfig['range'] = '%s, %s' % (filtconfig['minrange'], filtconfig['maxrange'])
		except:
			pass

		# As does scale.
		try:
			reconfig['scale'] = '%s, %s' % (filtconfig['scaleoffset'], filtconfig['scalespan'])
		except:
			pass

		# Return whatever we found. The number of keys will depend on the nature of the data.
		return reconfig


	########################################################
	def SetHMIConfig(self, newconfig):
		""" Validate a new HMI configuration dictionary and store 
		it in the configuration file. 
		Parameters: newconfig (dict) = The new configuration dictionary.
		Returns: (list) = A list of errors. If there were no errors an
			empty list is returned.
		"""

		# Convert the expanded configuration format into the format used in files.

		# Add the HMI tags to the parser.
		for section, config in newconfig['hmitagdata'].items():
			self._ConfigParser.add_section(section)

			# This is the server id
			if section == 'serverid':
				try:
					self._ConfigParser.set(section, 'id', config['serverid'])
				except:
					pass
			# This is the client version.
			elif section == 'clientversion':
				try:
					self._ConfigParser.set(section, 'ver', config['clientversion'])
				except:
					pass
			
			# These are normal tags.
			else:
				# Reformat the data.
				reconfig = self._FormatToFile(config)
				# Add it to the section.
				for option, value in reconfig.items():
					self._ConfigParser.set(section, option, value)


		# Add the alarms to the parser.
		# First we need to reformat the data.
		# Find the "base" parameter by finding the smallest key.
		alarmconfig = newconfig['alarmconfig']
		base = min(map(int, alarmconfig.keys()))

		# Convert this into a list of tuples, with the "base" subracted
		# from the address, and the items as the second element. This should
		# convert each record from something like this:
		# {'32400': {'tag': 'PB1Alarm', 'zonelist': ['zone1', 'zone2']} 
		# to something like this: ('0', 'PB1Alarm, zone1, zone2')
		alarms = [('%s' % (int(x) - base), '%s, %s' % (y['tag'], ', '.join(y['zonelist']))) 
					for (x,y) in alarmconfig.items()]

		# Add these to the parser.
		section = '&alarms'
		self._ConfigParser.add_section(section)
		self._ConfigParser.set(section, 'base', '%s' % base)
		for (option, value) in alarms:
			self._ConfigParser.set(section, option, value)


		# Repeat the same process for events.
		eventconfig = newconfig['eventconfig']
		base = min(map(int, eventconfig.keys()))
		events = [('%s' % (int(x) - base), '%s, %s' % (y['tag'], ', '.join(y['zonelist']))) 
					for (x,y) in eventconfig.items()]
		section = '&events'
		self._ConfigParser.add_section(section)
		self._ConfigParser.set(section, 'base', '%s' % base)
		for (option, value) in events:
			self._ConfigParser.set(section, option, value)

		# Repeat for ERP tag lists.
		erpconfig = newconfig['erplist']
		section = '&erplist'
		self._ConfigParser.add_section(section)
		self._ConfigParser.set(section, 'read', ', '.join(erpconfig['read']))
		self._ConfigParser.set(section, 'write', ', '.join(erpconfig['write']))


		# Check the configuration. The results are stored in the class variables.
		self._CheckConfig()



		# Were there any configuration errors?
		if self._ConfigErrors:
			return self._ConfigErrors

		# If everything was OK, then save the new configuration.
		fileresult = MBFileServices.SaveConfigFile(self._ConfigFileName, 
				self._ConfigParser, self._FileHeader)

		# Was the file save operation Ok? If not, then convert the 
		# error code into an error message.
		if fileresult != 'ok':
			self._ReportError(MBFileServices.FormatErr(fileresult, self._ConfigFileName))


		# Everything was OK if there were no errors.
		return self._ConfigErrors


##############################################################################

