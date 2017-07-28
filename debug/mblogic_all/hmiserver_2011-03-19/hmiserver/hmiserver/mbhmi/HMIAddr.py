##############################################################################
# Project: 	MBLogic
# Module: 	HMIAddr.py
# Purpose: 	Handle HMI data operations.
# Language:	Python 2.5
# Date:		20-Sep-2008.
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

import time

##############################################################################
"""
This module handles HMI data operations, and also
implements the special "reserved" tags. 
"""
##############################################################################

class HMIReservedTags:
	"""
	This class implements the special "reserved" tags as defined for
	the MB-HMI protocol.
	"""

	########################################################
	def __init__(self, clientversion, protocolversion):
		"""Parameters: 
		clientversion (string) = Current version of the client page(s).
		protocolversion (string) = Current version of the protocol.
		"""
	
		# These are the names of all the reserved tags.
		self._ReservedTags = ['timeutc', 'timelocal', 'clientversion', 'protocolversion']
		# These are the types of each of the reserved tags.
		self._ReservedTypes = {'timeutc' : 'time', 'timelocal' : 'time', 
			'clientversion' : 'string', 'protocolversion' : 'string'}
		# Current version of the client page(s).
		self._ClientVersion = clientversion
		# Current version of the protocol.
		self._ProtocolVersion = protocolversion

	########################################################
	def GetReservedTagList(self):
		""" Returns a list containing the names of the reserved tags.
		"""
		return self._ReservedTags

	########################################################
	def GetReservedType(self, tagname):
		"""Get the data type of a reserved tag.
		Parameters: tagname (string) - The name of a reserved tag.
		Returns: (string) - The type name or an empty string if 
		the tag is not found.
		"""
		try:
			return self._ReservedTypes[tagname]
		except:
			return ''

	########################################################
	def GetClientVersion(self):
		""" Returns a string with the current client page(s) version.
		"""
		return self._ClientVersion

	########################################################
	def GetProtocolVersion(self):
		""" Returns a string with the current MB-HMI protocol version.
		"""
		return self._ProtocolVersion

	########################################################
	def GetTimeUTC(self):
		""" Returns a floating point number with the current time 
		in UTC (GMT).
		"""
		return time.time()

	########################################################
	def GetTimeLocal(self):
		"""  Returns a floating point number with the current local time. 
		The time for the local in this implementation is the time at the server.
		"""
		return time.mktime(time.localtime())


##############################################################################

class HMIData:
	"""
	This class performs all of the HMI data operations, including reading and
	writing data, events, and alarms. 
	"""

	########################################################
	def __init__(self, datatable, tags, hmitags, eventconfig, alarmconfig):
		""" 
		datatable (object) = An initialised object giving access to the data table.
			The data table may be part of the same program, or it may be
			remotely accessed, in which case the data table object is expected
			to supply the means for communicating with it.
			The required methods are:
			
			1) GetEventStates(eventlist)
				Get the current states of a list of events.
				Params: eventlist (list) - a list of Modbus coil addresses.
				E.g. [23, 100, 52]
			Returns: (dict) - A dictionary where Modbus coils addresses are
				keys, and the states are boolean values.
				E.g. {23 : 0, 100 : 1, 52 : 1}

			2) GetAlarmStates(alarmlist)
				Get the current states of a list of alarms.
				Params: eventlist (list) - a list of Modbus coil addresses.
					E.g. [23, 100, 52]
				Returns: (dict) - A dictionary where Modbus coils addresses are
					keys, and the states are boolean values.
					E.g. {23 : 0, 100 : 1, 52 : 1}

			3) AddressWritable(addrtype):
				This is used to test if the address type is writable.
				Returns 'writeable' if the address type is writable. 
				Returns 'writeprotected' if the address type is not writable.
				Returns 'unknown' if the address type is unknown.

			4) GetDataValues(addrlist):
				Get the current values from the data source.
				Params: addrlist (list) = A list of tuples containing tag name, 
					Modbus address types and memory addresses. 
					E.g. [('PB1', 'coil', 5000), ('PB2', 'coil', 4998), 
					('PumpSpeed', 'holdingreg', 23)]
				Returns: (dict), (dict) = Two dictionary where the keys are the 
					tag names. The first dictionary contains any successful read
					results. The second contains error codes.
					E.g. {'PB1' : 1, 'PumpSpeed' : 1825}, {'PB2' : 'addresserror'}

			5) SetDataValues(newdata):
				Write the changed values to the data destination. This also
				checks to see if register values will fit in a Modbus register,
				and if the register type is writable.
				Params: addrlist (list) - A list of tuples containing tag name, 
					Modbus address types, memory address, and data value. 
					E.g. [('PB1', 'coil', 5000, 0), ('PB2', 'coil', 4998, 1), 
					('PumpSpeed', 'holdingreg', 23, 1800)]
				Returns: (dict) - A dictionary where the keys are the 
					tag names and the values are error codes. If there were no
					errors, the dictionary will be empty.
					E.g. {'PB2' : 'outofrange'}


		tags (dict) = A dictionary with address tags (string) as keys and 
			nested dictionaries containing the address type and the 
			data table addresses as values. The address types will
			depend on the data table type or protocol being used.
			e.g.
			{'PumpSpeedActual': {'addrtype': 'holdingreg', 'minrange': -32768, 
			'maxrange': 32767, 'datatype': 'integer', 'memaddr': 5005, 
			'scalespan': 1.0, 'scaleoffset': 0.0}, 
			'PB1': {'addrtype': 'coil', 'minrange': -32768, 'maxrange': 32767, 
			'datatype': 'boolean', 'memaddr': 0, 
			'scalespan': 1, 'scaleoffset': 0},
			'PL1': {'addrtype': 'coil', 'minrange': -32768, 'maxrange': 32767, 
			'datatype': 'boolean', 'memaddr': 16, 
			'scalespan': 1, 'scaleoffset': 0}}

		hmitags (object) = An object providing access to the reserved tags
			defined in the protocol. This uses a code object, as the values 
			of some tags are not fixed (e.g. current time). 

		eventconfig = A dictionary with data table addresses as keys, and event tags 
			(strings) as values. This provides the relationship between data
			table addresses and events.

		alarmconfig = A dictionary with data table addresses as keys, and alarm tags 
			(strings) as values. This provides the relationship between data
			table addresses and alarms.
		"""


		self._DataTable = datatable
		self._TagDict = tags
		self._HMITags = hmitags
		self._ReservedTags = hmitags.GetReservedTagList()


		# This is from a configuration file. This has the memory 
		# addresses and event and alarm tags.
		self._EventConfig = eventconfig
		self._AlarmConfig = alarmconfig


		# Generate serial numbers for events and alarms. Initialise them 
		# with the current time. The *initial* serial numbers will be the
		# same in this implementation, but they will not stay synchronised
		# over time.
		serialinit = int(time.time())
		self._EventSerial = serialinit
		self._AlarmSerial = serialinit
		self._AlarmHistorySerial = serialinit


		# This are buffers to keep track of events and alarms.
		self._EventBuffer = []
		self._AlarmBuffer = []

		# This is the maximum number of events or alarms a buffer is allowed.
		self._MaxEventBuffer = 1000
		self._MaxAlarmBuffer = 1000

		# This is how many to cut from the buffer at one time.
		self._PurgeEvents = 100
		self._PurgeAlarms = 100

		# This keeps track of which events are in which event zones.
		self._EventZones = self._MakeZoneConfigInfo(self._EventConfig)


		# This is used to keep track of the previous state of each event.
		self._EventStates = {}
		try:
			eventaddr = self._EventConfig.keys()
			for i in eventaddr:
				self._EventStates[i] = 'init'
		except:
			pass	# No events to monitor.


		# This is used to keep track of alarms. 
		self._AlarmTable = {}
		for i in self._AlarmConfig:
			self._AlarmTable[self._AlarmConfig[i]['tag']] =  {'state' : 'inactive', 
				'time' : 0.0, 
				'timeok' : 0.0, 
				'count' : 0,
				'ackclient' : '',
				'_alarmaddr' : i}



		# This keeps track of which alarms are in which alarm zones.
		self._AlarmZones = self._MakeZoneConfigInfo(self._AlarmConfig)


		# This buffer stores the alarm history.
		self._AlarmHistory = []
		# This initialises the serial number for the alarm history.


	########################################################
	def GetAddrTagList(self):
		"""Return a list of the HMI address tag list. This exludes 
		serverid and clientid. It does not include event tags, alarm 
		tags, or zone tags. E.g. ['PumpSpeedActual', 'PL4', 'PL3']
		"""
		# Get a list of all the address tags.
		taglist = self._TagDict.keys()

		# Remove the clientversion and serverid tags.
		try:
			taglist.remove('clientversion')
		except:
			pass
		try:
			taglist.remove('serverid')
		except:
			pass

		# Return the list.
		return taglist


	########################################################
	def _MakeZoneConfigInfo(self, msgconfig):
		"""Construct a dictionary relating message (events or alarms) 
		tags to zones. A "zone" is a group of event or alarm tags.
		Parameters: msgconfig (list) - A list of configurations.
		Returns: (dict) - Dictionary relating zones to tags.
		"""
		# This keeps track of which events are in which message zones.
		# First, make a list of all the zones.
		zonelist = []
		for i in msgconfig:
			zonelist.extend(msgconfig[i]['zonelist'])

		# Now reduce this list down to unique items.
		uniquezones = list(set(zonelist))
		# Convert this into a dictionary. The keys will store the zone
		# names and the values will be lists of tags.
		msgzones = {}
		for i in uniquezones:
			msgzones[i] = []

		# Now, add all the tags to the appropriate locations.
		for i in msgconfig:
			for j in msgconfig[i]['zonelist']:
				msgzones[j].append(msgconfig[i]['tag'])

		return msgzones



	########################################################
	def _RescaleReg(self, regvalue, hmidatatype, 
			minrange, maxrange, scaleoffset, scalespan):
		"""Scale one register value for HMI use.
		Parameters: regvalue (numeric) - The unscaled value.
		hmidatatype (string) - 'integer' or 'float'
		minrange (numeric) - The minimum permitted scaled range.
		maxrange (numeric) - The maximum permitted scaled range.
		scaleoffset (numeric) - The scale offset. (b for y=mx+b)
		scalespan (numeric) - The scale span. (m for y=mx+b)
		"""

		# All numbers are assumed to be signed.
		# Now scale the number to the user defined range.
		# We can avoid some work if the number has unity scaling.
		if ((scaleoffset != 0) or (scalespan != 1)):
			try:
				scaledvalue = (scalespan * regvalue) + scaleoffset
			except:
				return None, 'servererror'
		else:
			scaledvalue = regvalue

		# Next, convert the value to the correct data type.
		try:
			if (hmidatatype == 'integer'):
				scaledvalue = int(scaledvalue)
			elif (hmidatatype == 'float'):
				scaledvalue = float(scaledvalue)
			else:
				return None, 'badtype'
		except:
			return None, 'badtype'


		# Check to see if the value is within the acceptable range.
		if ((scaledvalue < minrange) or (scaledvalue > maxrange)):
			return None, 'outofrange'

		# Return the scaled value.
		return scaledvalue, None


	########################################################
	def _ScaleFromRegisters(self, regdata):
		"""Scale register values for the HMI. This does any necessary
		type conversions then rescales the number to fit into the 
		specified range. 
		Parameters: regdata (dict) - A dictionary containing the values
			to be scaled. {tagname : regvalue}. Only integers and floats 
			are scaled. Other types are ignored. Type data is derived 
			from the tag definition dictionary.
		Returns: Two dictionarys. The first contains the scaled values, plus
			any which did not require scaling because of their type. The
			second contains tags with error codes indicating any errors.
		"""

		scaleddata = {}	# Scaled results.
		errors = {}	# Errors.

		# Loop through with the keys and values. At each test, check for
		# errors. 
		for tagname, regvalue in regdata.items():

			# Get the configuration parameters for this tag.
			hmidatatype = self._TagDict[tagname]['datatype']

			# Only integers and floats need to be scaled.
			if hmidatatype in ['integer', 'float']:

				# Get the remaining configuration parameters.
				minrange = self._TagDict[tagname]['minrange']
				maxrange = self._TagDict[tagname]['maxrange']
				scaleoffset = self._TagDict[tagname]['scaleoffset']
				scalespan = self._TagDict[tagname]['scalespan']

				# Scale the values.
				scaledvalue, errorcode = self._RescaleReg(regvalue, hmidatatype, 
					minrange, maxrange, scaleoffset, scalespan)

				# If there were no errors, store the result. If
				# there were any errors, store the error code.
				if (errorcode == None):
					scaleddata[tagname] = scaledvalue
				else:
					errors[tagname] = errorcode

			else:
				# This data type doesn't need scaling
				scaleddata[tagname] = regvalue

		# Done.
		return scaleddata, errors



	########################################################
	def _ScaleReg(self, tagvalue, hmidatatype, 
		minrange, maxrange, scaleoffset, scalespan):
		"""Scale one hmi data value to store in a register.
		Parameters: tagvalue (numeric) - The unscaled value.
		hmidatatype (string) - 'integer' or 'float'
		minrange (numeric) - The minimum permitted scaled range.
		maxrange (numeric) - The maximum permitted scaled range.
		scaleoffset (numeric) - The scale offset. (b for y=mx+b)
		scalespan (numeric) - The scale span. (m for y=mx+b)
		"""
		# First, convert the value to a number.
		try:
			if (hmidatatype == 'integer'):
				datavalue = int(tagvalue)
			elif (hmidatatype == 'float'):
				datavalue = float(tagvalue)
			else:
				return None, 'badtype'
		except:
			return None, 'badtype'


		# Check to see if the value is within the acceptable range.
		if ((datavalue < minrange) or (datavalue > maxrange)):
			return None, 'outofrange'


		# Now scale the number to fit in the specified range.
		# We can avoid some work if the number has unity scaling.
		if ((scaleoffset != 0) or (scalespan != 1)):
			try:
				scaledvalue = (datavalue - scaleoffset)/scalespan
			except:
				return None, 'servererror'

			# If we've reached this far, there were no errors, 
			# so return the scaled number.
			return scaledvalue, None

		else:	# Return the value as is.
			return datavalue, None




	########################################################
	def _ScaleToRegisters(self, writedata):
		"""Scale numbers to fit into registers. This does any necessary
		type conversions then rescales the number to fit into the 
		specified range. This does not check to see if the resulting value
		will fit in the destination register. It also does not do any type
		conversion which may be required to be compatible with the destination.
		Parameters: writedata (dict) - A dictionary containing the values
			to be scaled. {tagname : tagvalue}. Only integers and floats 
			are scaled. Other types are ignored. Type data is derived 
			from the tag definition dictionary.
		Returns: Two dictionarys. The first contains the scaled values, plus
			any which did not require scaling because of their type. The
			second contains tags with error codes indicating any errors.
		"""

		scaleddata = {}	# Scaled results.
		errors = {}	# Errors.

		# Loop through with the keys and values. At each test, check for
		# errors. 
		for tagname, tagvalue in writedata.items():

			# Get the configuration parameters for this tag.
			hmidatatype = self._TagDict[tagname]['datatype']

			# Check if the data type is one that needs to be scaled.
			if hmidatatype in ['integer', 'float']:
				# Get the remainnig scale parameters.
				minrange = self._TagDict[tagname]['minrange']
				maxrange = self._TagDict[tagname]['maxrange']
				scaleoffset = self._TagDict[tagname]['scaleoffset']
				scalespan = self._TagDict[tagname]['scalespan']

				# Scale the values.
				scaledvalue, errorcode = self._ScaleReg(tagvalue, hmidatatype, 
					minrange, maxrange, scaleoffset, scalespan)
				
				# If there were no errors, store the result. If
				# there were any errors, store the error code.
				if (errorcode == None):
					scaleddata[tagname] = scaledvalue
				else:
					errors[tagname] = errorcode
			else:
				# This datat type doesn't need scaling
				scaleddata[tagname] = tagvalue

		# Done.
		return scaleddata, errors


	########################################################
	def _GetReservedTagValue(self, tagname):
		"""Get the values for a single reserved tag.
		Parameters: tagname (string) = A reserved tag name.
		Returns: The value of the reserved tag, or None
			if not found.
		"""

		# The following handle the "reserved" tags.
		if (tagname == 'timeutc'):
			return self._HMITags.GetTimeUTC()
		elif (tagname == 'timelocal'):
			return self._HMITags.GetTimeLocal()
		elif (tagname == 'clientversion'):
			return self._HMITags.GetClientVersion()
		elif (tagname == 'protocolversion'):
			return self._HMITags.GetProtocolVersion()
		else:
			return None



	########################################################
	def ReadDataTable(self, addrlist):
		""" Given a list of address tags, read the corresponding 
		data table addresses and return the values.
		Params: addrlist (list) = A list of address tags.
		Returns: scaleddata (dict) = A dictionary containing the tags as
				keys and the data as values. If an error occurred,
				the affected key will not appear in this dictionary.
			dataerrors (dict) = A dictionary containing the tags as 
				keys and the error codes as values. If there 
				were no errors, this will be empty.
		"""

		reservedata = {}	# Data results for reserved tags.
		dataerrors = {}		# Combined errors.

		# Now, prepare the data to be read from the data source.
		tagparams = []
		for tagname in addrlist:

			# Get the address type and memory location for this
			# address tag. If it doesn't exist, this is an error
			# that must be reported.
			try:
				addrtype = self._TagDict[tagname]['addrtype']
				datatype = self._TagDict[tagname]['datatype']
				memaddr = self._TagDict[tagname]['memaddr']
				tagparams.append((tagname, addrtype, datatype, memaddr))
			except:
				# Check if this is a special reserved tag.
				if tagname in self._ReservedTags:
					result = self._GetReservedTagValue(tagname)
					if (result == None):
						dataerrors[tagname] = 'addresserror'
					else:
						reservedata[tagname] = result
				else:
					dataerrors[tagname] = 'tagnotfound'
					continue

		# Read the register data. This reads all the data values at once.
		regdata, regerrors = self._DataTable.GetDataValues(tagparams)

		# Scale the registers. This does any scaling required, and ignores
		# any values which do not need to be scaled.
		scaleddata, scaleerrors = self._ScaleFromRegisters(regdata)


		# Combine the results.
		scaleddata.update(reservedata)
		# Combine the errors.
		dataerrors.update(regerrors)
		dataerrors.update(scaleerrors)

		# Return the final results.
		return scaleddata, dataerrors



	########################################################
	def WriteDataTable(self, writedata):
		""" Given a dictionary of address tags and data, write the data
		into the corresponding data table addresses.
		Params: writedata (dict) = A dictionary of address tags and data values.
		Returns: dataerrors (dict) = A dictionary containing the tags as 
				keys and the error codes as values. If there 
				were no errors, this will be empty.
		"""

		dataerrors = {}		# Error codes.

		# First, filter the tag list to check for any reserved tags.
		# Reserved tags are not writable, so if we find any this is an error.
		for tagname in self._ReservedTags:
			reservevalue = writedata.get(tagname, None)
			if (reservevalue != None):
				dataerrors[tagname] = 'writeprotected'
				del writedata[tagname]

		# Check for tags which don't exist.
		existkeys = writedata.keys()
		for tagname in existkeys:
			findvalue = self._TagDict.get(tagname, None)
			if (findvalue == None):
				dataerrors[tagname] = 'tagnotfound'
				del writedata[tagname]

		# Scale the tag values. All tag names should be valid
		# at this point.
		scaledparams, scaleerrors = self._ScaleToRegisters(writedata)


		# Now, assemble the data to be written to the data table.
		tagparams = []
		for tagname in scaledparams:
			addrtype = self._TagDict[tagname]['addrtype']
			datatype = self._TagDict[tagname]['datatype']
			memaddr = self._TagDict[tagname]['memaddr']
			datavalue = scaledparams[tagname]
			tagparams.append((tagname, addrtype, datatype, memaddr, datavalue))


		# Write all the scaled data to the destination.
		writeerrors = self._DataTable.SetDataValues(tagparams)


		# Combine the errors.
		dataerrors.update(scaleerrors)
		dataerrors.update(writeerrors)

		# Return the final errors (if any).
		return dataerrors





	########################################################
	def TestTags(self, checktags, testwritable):
		""" Given a dictionary of address tags and data, test if the tags
		are present, and of the correct type. Return any corresponding 
		errors in the reply. This does not return any actual data.
		Params: checktags (dict) = A dictionary of address tags and data types.
			testwritable (boolean) = If True, it will also test if 
			the tags are writable.
		Returns: dataerrors (dict) = A dictionary containing the tags as 
				keys and the error codes as values. If there 
				were no errors, this will be empty.
		"""

		# Get a list of address tags so we can iterate over it.
		addrlist = checktags.keys()

		# Initialise the errors result.
		dataerrors = {}

		# Go through the list one at a time. Find the corresponding 
		# tag configuration information, and verify it.
		for i in addrlist:

			# Get the data table address type and memory location for this
			# address tag. If it doesn't exist, this is an error
			# that must be reported.
			try:
				addrtype = self._TagDict[i]['addrtype']
				memaddr = self._TagDict[i]['memaddr']
				hmidatatype = self._TagDict[i]['datatype']

				# Get the other configuration parameters for this tag.
				# Even if we dont' use them, we need to check that we
				# won't get a fault if we access them.
				minrange = self._TagDict[i]['minrange']
				maxrange = self._TagDict[i]['maxrange']
				scaleoffset = self._TagDict[i]['scaleoffset']
				scalespan = self._TagDict[i]['scalespan']

			except:
				# Check if this is a special reserved tag. 
				if i in self._ReservedTags:
					addrtype = i
					memaddr = None
					hmidatatype = self._ReservedTags.GetReservedType(i)
				else:
					dataerrors[i] = 'tagnotfound'
					continue


			# Now, compare what the client expects the data type to be to
			# what the configuration is set for. If everything was OK, we
			# discard this tag and continue to the next.
			if (hmidatatype != checktags[i]):
				dataerrors[i] = 'badtype'
			elif testwritable:
				# Now, the tags may need to be tested to see if they are writable.
				writetest = self._DataTable.AddressWritable(addrtype)
				if (writetest == 'writeable'):
					pass	# is writable.
				elif (writetest == 'writeprotected'):
					dataerrors[i] = 'writeprotected'	# Read only.
				else:
					if  (addrtype in self._ReservedTags):
						dataerrors[i] = 'writeprotected'	# Read only.
					else:
						dataerrors[i] = 'servererror'	# Shouldn't get this.

		return dataerrors


	########################################################
	def InitMessages(self):
		"""Initialise the messages last state dictionaries. This should 
		be done after everything is started up, but before the first
		event messages are processed.
		Parameters: None.
		Returns: Nothing.
		Modifies the events last state dictionaries.
		"""

		# Events.
		messagekeys = self._EventStates.keys()
		# The keys are data table addresses. If we can't contact
		# the server, then we start without initialising anything.
		# This is necessary for cases where the data table is running in 
		# a different server rather than local to the HMI system.
		try:
			currentevents = self._DataTable.GetEventStates(messagekeys)
		except:
			currentevents = {}

		# Get the current data table value and use it to
		# initialise the last state.
		for evaddr, evstate in currentevents.items():
			self._EventStates[evaddr] = int(evstate)


	########################################################
	def _GetMessages(self, clientresponse, messagebuffer, zoneconfig, tagtype):
		"""Check the history buffers for any new events or alarms to send. 
		The client will send a serial number. Send any message that is 
		more recent than that, up to a maximum.
		Parameters: 
			clientresponse (dict) - dictionary holding the client
				response with a serial number and a maximum number of
				messages. E.g. {'serial' : 12345, 'max' : 50}
			messagebuffer (list) - A list containing the messages. 
			zoneconfig (dict) - A dictionary with the zone configuration.
			tagtype (string) - 'alarm' or 'event'.
		Returns: (list) - A list of dictionaries with each dictionary containing 
			the information defined for that type of message (event or alarm).
			The list elements are in chronological order, with the oldest
			messages first, and the newest ones last.
			(dict) - a dictionary containing any errors.
		""" 

		# Errors for messages.
		dataerrors = {}

		# The client isn't asking for any, so just return.
		if (clientresponse == {}):
			return [], dataerrors

		# Get the client request serial number, the maximum number 
		# of records the client wants, and the list of zones.
		try:
			clientserial = int(clientresponse['serial'])
			clientmax = int(clientresponse['max'])
			zonelist = clientresponse['zones']
		except:
			return [], dataerrors		# The client request was invalid.


	
		# Go through the list of zones and create a list of tags.
		messagetags = []
		for i in zonelist:
			try:
				messagetags.extend(zoneconfig[i])
			except:
				dataerrors[i] = 'tagnotfound'

		# Now, get rid of the duplicates from the list.
		messagetags = list(set(messagetags))


		# This is where we will store the messages to return.
		responsebuffer = []

		# Now, check if there are any messages in the buffer to get.
		bufflength = len(messagebuffer)
		if (bufflength < 1):
			return [], dataerrors


		# The message buffers are in chronological (and therefore serial number)
		# order. Go through the buffer in reverse, looking for serial numbers 
		# which are newer (larger) than the client reference and which are in
		# the list of tags the client wants to see. Stop if we get more 
		# messages than the client requested.
		i = bufflength - 1
		msgcount = 0
		while ((i >= 0) and (msgcount < clientmax)):
			serialnumber = messagebuffer[i]['serial']
			# Check if the message qualifies according to serial number and tag name.
			if (serialnumber > clientserial) and (messagebuffer[i][tagtype] in messagetags):
				responsebuffer.append(messagebuffer[i])
				# Decrement the buffer index position.
				i -= 1
				# Increment the count for how many messages we found.
				msgcount += 1
			else:
				break


		# Now the response buffer is in reverse order, so we need to
		# reverse it again to return to normal order.
		responsebuffer.reverse()
		
		# Return the final response.
		return responsebuffer, dataerrors



	########################################################
	def GetEvents(self, clientresponse):
		"""Check the event buffer for any new events to send. The client
		will send a serial number. Send any message that is more recent
		than that, up to a maximum.
		Parameters: clientresponse (dict) - dictionary holding the client
			response with a serial number, maximum number of events,  and zones. 
			E.g. {'serial' : 12345, 'max' : 50, 'zones' : ['zone1', 'zone2']}
		Returns: A list of event dictionaries with each dictionary containing, 
			serial number, event tag, timestamp and current state. 
			e.g. {"timestamp": 1223094615.0, "serial": 1223094619, 
				"event": "PumpStopped", "state": 1}
			The list elements are in chronological order, with the oldest
			events first, and the newest ones last.
		""" 

		return self._GetMessages(clientresponse, self._EventBuffer, 
				self._EventZones, 'event')




	########################################################
	def UpdateEvents(self):
		"""Scan the monitored addresses in the data table for new events.
		Append these to the event buffer together with a serial number and
		time stamp.
		Parameters: None.
		Returns: None.
		"""

		# Look for new events.
		# Generate a time stamp to use for each new message.
		timestamp = time.time()
		# Make a list of valid keys.
		messagekeys = self._EventConfig.keys()

		# Get the current event states.
		currentevents = self._DataTable.GetEventStates(messagekeys)

		# Check each event to see if it has changed.
		for evaddr, evstate in currentevents.items():
			newvalue = int(evstate)

			# Check if a new event has occured.
			if (newvalue != self._EventStates[evaddr]):
				# Create a new message and put it in the pending buffer.
				# For events, we look for any change of state.
				# Increment message serial number.
				self._EventSerial += 1
				self._EventBuffer.append({'serial' : self._EventSerial,  
						'event' : self._EventConfig[evaddr]['tag'], 
						'timestamp' : timestamp,
						'value' : newvalue})
					
				# Record the old state.
				self._EventStates[evaddr] = newvalue


		# Now, check if the message buffer is getting too long. If so, we 
		# need to start discarding old messages even if the client hasn't
		# seen them yet. We don't want to fill up the server with messages.
		if (len(self._EventBuffer) > self._MaxEventBuffer):
			self._EventBuffer = self._EventBuffer[self._PurgeEvents :]



	########################################################
	def GetAlarms(self, zonelist):
		"""Reply with the current state of any alarms.
		Parameters: zonelist (list) - List of alarm zone tag names.
		Returns: (dict) - Dictionary containing any active alarms.
			(dict) - Dictionary containing any errors.
		""" 
		# Errors.
		dataerrors = {}

		# Go through the list of zones and create a list of tags.
		alarmtags = []
		for i in zonelist:
			try:
				alarmtags.extend(self._AlarmZones[i])
			except:
				dataerrors[i] = 'tagnotfound'
				
		# Now, get rid of the duplicates from the list.
		alarmtags = list(set(alarmtags))

		# Go through the list of alarms tags and get any active alarms.
		activealarms = {}
		for i in alarmtags:
			if (self._AlarmTable[i]['state'] != 'inactive'):
				activealarms[i] = {'state' : self._AlarmTable[i]['state'], 
				'time' : self._AlarmTable[i]['time'], 
				'timeok' : self._AlarmTable[i]['timeok'], 
				'count' : self._AlarmTable[i]['count']}

		return activealarms, dataerrors

	########################################################
	def _AddToAlarmHistory(self, alarmtag):
		"""Add an alarm record to the alarm history.
		Parameters: alarmtag (string) - An alarm tag key to the alarm table.
		"""
		# Add it to the alarm history.
		self._AlarmHistory.append({'serial' : self._AlarmHistorySerial,  
				'alarm' : alarmtag, 
				'state' : 'inactive', 
				'time' : self._AlarmTable[alarmtag]['time'], 
				'timeok' : self._AlarmTable[alarmtag]['timeok'], 
				'count' : self._AlarmTable[alarmtag]['count'],
				'ackclient' : self._AlarmTable[alarmtag]['ackclient']})


		# Increment the alarm history serial number.
		self._AlarmHistorySerial += 1

		# Now, check if the message buffer is getting too long. If so, we 
		# need to start discarding old messages even if the client hasn't
		# seen them yet. We don't want to fill up the server with messages.
		if (len(self._AlarmHistory) > self._MaxAlarmBuffer):
			self._AlarmHistory = self._AlarmHistory[self._PurgeAlarms :]


	########################################################
	def UpdateAlarms(self):
		"""Go through the alarm table and update the state of all the
		alarms. No parameters, and no return values.
		"""
		# Generate a time stamp to use for each new message.
		timestamp = time.time()

		# The keys are data table addresses.
		messagekeys = self._AlarmConfig.keys()

		# Get the current state of the alarms.
		alarmstates = self._DataTable.GetAlarmStates(messagekeys)

		# Now, go through the alarm table.
		for i in self._AlarmTable:

			# Get the current alarm value from the data table.
			alarmaddr = self._AlarmTable[i]['_alarmaddr']

			# Check the current data table value to see if
			# the fault condition is present.
			if alarmstates[alarmaddr]:
				# The alarm has just become active.
				if (self._AlarmTable[i]['state'] == 'inactive'):
					self._AlarmTable[i]['state'] = 'alarm'
					self._AlarmTable[i]['time'] = timestamp
					self._AlarmTable[i]['timeok'] = 0.0
					self._AlarmTable[i]['count'] += 1
				# The alarm has become re-activated.
				elif (self._AlarmTable[i]['state'] in ['ok', 'ackok']):
					self._AlarmTable[i]['state'] = 'alarm'
					self._AlarmTable[i]['timeok'] = 0.0
					self._AlarmTable[i]['count'] += 1

			# The fault condition is gone.
			else:
				# The alarm condition has gone, but it has not been acknowledged.
				if (self._AlarmTable[i]['state'] == 'alarm'):
					self._AlarmTable[i]['state'] = 'ok'
					self._AlarmTable[i]['timeok'] = timestamp

				# The alarm condition has just now gone, and it has 
				# been previously acknowledged.
				elif (self._AlarmTable[i]['state'] == 'ackalarm'):
					self._AlarmTable[i]['timeok'] = timestamp
					# Add it to the alarm history.
					self._AddToAlarmHistory(i)

					# Reset the alarm values.
					self._AlarmTable[i]['state'] = 'inactive'
					self._AlarmTable[i]['time'] = 0.0
					self._AlarmTable[i]['timeok'] = 0.0
					self._AlarmTable[i]['count'] =0

				# The alarm condition had previously gone, but it has 
				# just now been acknowledged.
				elif (self._AlarmTable[i]['state'] == 'ackok'):
					# Add it to the alarm history.
					self._AddToAlarmHistory(i)

					# Reset the alarm values.
					self._AlarmTable[i]['state'] = 'inactive'
					self._AlarmTable[i]['time'] = 0.0
					self._AlarmTable[i]['timeok'] = 0.0
					self._AlarmTable[i]['count'] =0


	########################################################
	def AckAlarms(self, clientack, clientid):
		"""Receive client alarm acknowldge requests, and apply them to
		alarms stored in the alarm table.
		Parameters: clientack (list) - List with client alarm 
			acknowledge messages. These consist of the
			alarm tags being acknowledged.
			clientid (string) - The client id string.
		Returns: Nothing. Acts on the alarm table and alarm history.
		"""

		# Go through the list of acknowledgements, and acknowledge any
		# alarms which are currently active and not already acknowledged.
		for i in clientack:
			if (i in self._AlarmTable):
				# In alarm state, but acknowledged.
				if (self._AlarmTable[i]['state'] == 'alarm'):
					self._AlarmTable[i]['state'] = 'ackalarm'
					self._AlarmTable[i]['ackclient'] = clientid
				# State was OK, but not acknowledged yet.
				if (self._AlarmTable[i]['state'] == 'ok'):
					self._AlarmTable[i]['state'] = 'ackok'
					self._AlarmTable[i]['ackclient'] = clientid



	########################################################
	def GetAlarmHistory(self, clientresponse):
		"""Check the alarm history buffer for any new alarm history to send. 
		The client will send a serial number. Send any message that is 
		more recent than that, up to a maximum.
		Parameters: clientresponse (dict) - dictionary holding the client
			response with a serial number, maximum number of alarms, and zones. 
			E.g. {'serial' : 12345, 'max' : 50, 'zones' : ['zone1', 'zone2']}
		Returns: A list of alarm history dictionaries with each dictionary 
			containing, serial number, alarm tag, timestamp and data
			value. 
			The list elements are in chronological order, with the oldest
			alarms first, and the newest ones last.
		""" 
		return self._GetMessages(clientresponse, self._AlarmHistory, 
				self._AlarmZones, 'alarm')


##############################################################################

