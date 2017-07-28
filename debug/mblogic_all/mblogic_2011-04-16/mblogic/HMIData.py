##############################################################################
# Project: 	MBLogic
# Module: 	HMIData.py
# Purpose: 	Handle data for the MB-HMI protocol.
# Language:	Python 2.5
# Date:		01-Jan-2009.
# Ver.:		30-Dec-2010.
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


############################################################

import time, os
import sqlite3
import xml.dom.minidom

from twisted.internet import reactor
from twisted.enterprise import adbapi

import MBDataTable
from mbprotocols import HMIMsg

from mbhmi import HMIAddr
from mbhmi import HMIConfig
from mbhmi import HMIModbusConfig as HMIConfigvalidator
from mbhmi import HMIDataTable

from sysmon import MonUtils
import MBFileServices


############################################################

# Version of the protocol implemented.
_ProtocolVersion = '2009-12-16'


# Name of the directory and file where the event messages are stored.
_RSSEventMsgFile = os.path.join('hmipages', 'rsseventtexts.js')
_RSSTemplateFile = os.path.join('hmipages', 'rsstemplate.xml')


############################################################

# Error messages.
_Msgs = {'hmiencodingerror' : 'Error encoding MB-HMI response: %s',
		'noerssmesgs' : 'No RSS events messages found.',
		'norsstemplate' : 'No RSS Events template found.',
		'rsslinkfileerr' : 'Error parsing RSS Events template linkfile.',
		'rsstaglisterr' : 'Error parsing RSS Events template taglist.',
		'rsslogofileerr' : 'Error parsing RSS Events template logofile.'
		}


############################################################

class HMIMessages:
	"""This is a container class to hold the HMI configuration for the server.
	"""

	########################################################
	def __init__(self):

		# Name to use for the configuration file.
		self._ConfigFileName = 'mbhmi.config'

		# Use a default server ID until we get another one.
		self._DefaultServerID = 'default server id'

		# This handles encoding and decoding messages. We initialise it with
		# the name we want to use for the HMI server.
		self.HMIServerMsg = HMIMsg.HMIServerMessages(self._DefaultServerID)

		# Initialised the reserved tags handling with the client and protocol versions.
		self.HMIReservedTags = HMIAddr.HMIReservedTags(self._DefaultServerID, _ProtocolVersion)

		# This initialises the low level routines that read and write the actual data table.
		# These routines are protocol specific.
		self._HMIDataTable = HMIDataTable.HMIDataTable(MBDataTable.MemMap)

		# This handles converting MB-HMI tags to Modbus data table addresses.
		self.HMIData = HMIAddr.HMIData(self._HMIDataTable, {}, self.HMIReservedTags, {}, {})


		# This object validates the protocol specific parameters.
		self.HMITagValidator = HMIConfigvalidator.HMIConfigValidator()

		# Create an initial default configuration. We give it an empty file name,
		# because we don't want to load the configuration just yet.
		timestamp = time.time()
		defaultconfig = HMIConfig.HMIConfig('', timestamp, self.HMITagValidator)
		# Reference to current tag configuration object.
		self._HMICurrentTagconfig = defaultconfig
		# Reference to new tag configuration object.
		self._HMINewTagconfig = defaultconfig


		# General configuration status parameters.
		self._NewConfigStatParams = self._SetConfigStatus(time.time(), 'N/A', False)
		self._CurrentConfigStatParams = self._SetConfigStatus(time.time(), 'N/A', False)

		# For server connection stats calculations.
		self._RequestCounter = []

		# For updating the status information.
		self._StatusInfo = None


	########################################################
	def SetStatusInfo(self, statusinfo):
		""" Must call this to add a reference to the configuration 
		information. This allows status information to be
		tracked and reported.
		"""
		self._StatusInfo = statusinfo


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



	########################################################
	def MsgInit(self):
		"""Initialise the configuration. This is done explicitly so that
		the main configuration system can call it when desired.
		"""

		# Get the time stamp for when we started.
		timestamp = time.time()


		# Calculate the file signature.
		try:
			filesig = MonUtils.CalcFileSig(self._ConfigFileName)
		except:
			# File may not exist.
			filesig = 'N/A'

		# Load the HMI tag configuration from disk.
		self._HMINewTagconfig = HMIConfig.HMIConfig(self._ConfigFileName, timestamp, self.HMITagValidator)
		self._HMINewTagconfig.ReadConfigFile()
		# Check if errors are present in the new configuration.
		ConfigOK = len(self._HMINewTagconfig.GetConfigErrors()) == 0

		# Calculate the new status parameters. We manage the status 
		# parameters here rather than in the parser itself because
		# the HMI parser library is shared with other programs. 
		self._NewConfigStatParams = self._SetConfigStatus(timestamp, filesig, ConfigOK)


		# If we don't have anything for the current configuration yet, then use
		# the one we just read, whether it is any good or not.
		if not self._HMICurrentTagconfig:
			self._HMICurrentTagconfig = self._HMINewTagconfig
			self._CurrentConfigStatParams = self._NewConfigStatParams


		# If the new configuration is OK, we use it in place of the old one.
		if not self._HMINewTagconfig.GetConfigErrors():
			self._HMICurrentTagconfig = self._HMINewTagconfig
			self._CurrentConfigStatParams = self._NewConfigStatParams


		# This handles encoding and decoding messages. We initialise it with
		# the name we want to use for the HMI server.
		self.HMIServerMsg = HMIMsg.HMIServerMessages(self._HMICurrentTagconfig.GetServerID())

		# Initialised the reserved tags handling with the client and protocol versions.
		self.HMIReservedTags = HMIAddr.HMIReservedTags(self._HMICurrentTagconfig.GetServerID(), 
								_ProtocolVersion)

		# This handles converting MB-HMI tags to Modbus data table addresses.
		self.HMIData = HMIAddr.HMIData(self._HMIDataTable, 
						self._HMICurrentTagconfig.GetConfigDict(),
						self.HMIReservedTags,
						self._HMICurrentTagconfig.GetEventConfig(),
						self._HMICurrentTagconfig.GetAlarmConfig()
						)

		# This initialises the last (previous) state dictionaries of the 
		# event and alarm handlers. This is required so they don't issue
		# spurious events and alarms on start up. We have to do this whenever 
		# we re-initialise the parameters so we can update the monitored 
		# events list.
		self.HMIData.InitMessages()


	########################################################
	def ConfigEdit(self, newconfig):
		"""Check a new HMI configuration, and if it is OK, save it to
		disk and use it as the current HMI configuration.
		Parameters: newconfig (dict) = The new HMI configuration. 
		Returns: (list) = A list containing any error messages.
		"""

		# Get the time stamp for when we started.
		timestamp = time.time()


		# Create the new HMI tag configuration.
		self._HMINewTagconfig = HMIConfig.HMIConfig(self._ConfigFileName, timestamp, self.HMITagValidator)
		# Pass it the new configuration, and see if there were any errors.
		self._HMINewTagconfig.SetHMIConfig(newconfig)

		# Check if errors are present in the new configuration.
		ConfigOK = len(self._HMINewTagconfig.GetConfigErrors()) == 0

		if not ConfigOK:
			return self._HMINewTagconfig.GetConfigErrors()


		# Calculate the file signature.
		try:
			filesig = MonUtils.CalcFileSig(self._ConfigFileName)
		except:
			# File may not exist.
			filesig = 'N/A'

		# Calculate the new status parameters. We manage the status 
		# parameters here rather than in the parser itself because
		# the HMI parser library is shared with other programs. 
		self._NewConfigStatParams = self._SetConfigStatus(timestamp, filesig, ConfigOK)


		# If the new configuration is OK, we use it in place of the old one.
		self._HMICurrentTagconfig = self._HMINewTagconfig
		self._CurrentConfigStatParams = self._NewConfigStatParams


		# This handles encoding and decoding messages. We initialise it with
		# the name we want to use for the HMI server.
		self.HMIServerMsg = HMIMsg.HMIServerMessages(self._HMICurrentTagconfig.GetServerID())

		# Initialised the reserved tags handling with the client and protocol versions.
		self.HMIReservedTags = HMIAddr.HMIReservedTags(self._HMICurrentTagconfig.GetServerID(), 
								_ProtocolVersion)

		# This handles converting MB-HMI tags to Modbus data table addresses.
		self.HMIData = HMIAddr.HMIData(self._HMIDataTable, 
						self._HMICurrentTagconfig.GetConfigDict(),
						self.HMIReservedTags,
						self._HMICurrentTagconfig.GetEventConfig(),
						self._HMICurrentTagconfig.GetAlarmConfig()
						)

		# Everything was OK, so there were no errors to report.
		return []



	########################################################
	def GetNewHMIInfo(self):
		"""Get the HMI configuration data for a new configuration.
		Returns an object.
		"""
		return self._HMINewTagconfig

	########################################################
	def GetCurrentHMIInfo(self):
		"""Get the HMI configuration data for the current configuration.
		Returns an object.
		"""
		return self._HMICurrentTagconfig

	########################################################
	def ReloadHMIConfig(self):
		"""Reloads the HMI configuration when reloaded.
		"""
		self.MsgInit()
		# Also reload the RSS messages.
		AlarmLogger.LoadRSSMsgs()


	########################################################
	def GetNewStatParams(self):
		"""Return the HMI status parameters for the new
		configuration.
		"""
		return self._NewConfigStatParams

	########################################################
	def GetCurrentStatParams(self):
		"""Return the HMI status parameters for the current
		configuration.
		"""
		return self._CurrentConfigStatParams


############################################################

Msg = HMIMessages()

############################################################



############################################################

class HMIServerStatusInfo:
	"""This handles HMI protocol status information. 
	"""

	########################################################
	def __init__(self):

		# For server connection stats calculations.
		self._RequestCounter = []

		# For updating the status information.
		self._StatusInfo = None


	########################################################
	def IncRequestCounter(self):
		"""Increment the request counter. This keeps track when each
		request was made in order to calculate a request rate in terms of
		requests per unit of time.
		"""
		# TODO: This is for Debian 5.0 compatibility. 
		# This list could be replaced by a deque if we don't need
		# to support anything older than Python 2.6. This would allow us
		# to use the maxlen parameter to automatically manage the deque length.

		# Add a time stamp to the end of the buffer.
		self._RequestCounter.append(time.time())
		# We limit the size of the buffer so it doesn't grow excessively.
		if len(self._RequestCounter) > 25:
			self._RequestCounter.pop(0)

		# Set the request rate in the container.
		self._StatusInfo.SetRequestCounter(self._RequestCounter)


	########################################################
	def SetStatusInfo(self, statusinfo):
		""" Must call this to add a reference to the configuration 
		information. This allows status information to be
		tracked and reported.
		"""
		self._StatusInfo = statusinfo



############################################################


# These handle the status information for all types of HMI protocol servers.
HMIStatus = HMIServerStatusInfo()
RHMIStatus = HMIServerStatusInfo()
ERPStatus = HMIServerStatusInfo()


########################################################
class AlarmEventHandler:
	"""Handle alarm and event updating and logging. The HMI system must be 
	already initialised before we can initialise this. This class will call
	itself repeated on a fixed time basis to update the alarms and events, and
	to log the resulting data. 
	"""

	########################################################
	def __init__(self):
		"""Initialise the alarms and events database.
		"""
		# Name to use for the database file.
		self._dbname = 'alarms.db'
		# How many history messages to retrieve from the database to use in
		# priming the event and alarm history message queues.
		# This is also used for determining how many RSS messages to keep active.
		self._MessageRestore = 50

		# Event messages. This relates the message texts to the keys.
		self._EventMsgs = {}

		# The RSS template file.
		self._RSSTemplate = ''

		# The link to insert into each RSS entry.
		self._RSSLink = ''
		# The list of tags to use to filter the RSS messages. 
		self._RSSTagFilter = []
		# File to use for preview.
		self._LogoFile = ''


		# Set the default serial numbers. Valid serial numbers should be 
		# positive integers. 
		self._AlarmSerial = -1
		self._EventSerial = -1

		# Create the database if it doesn't already exist. We are doing this 
		# with direct SQLite library calls because we want to block everything 
		# else until this is complete.

		# Open (create) the database.
		conn = sqlite3.connect(database=self._dbname, check_same_thread=False, timeout=30)

		# Create a cursor.
		events = conn.cursor()
		alarms = conn.cursor()

		# Create the events table if it doesn't already exist. 
		events.execute("""CREATE TABLE IF NOT EXISTS events (serial INTEGER, timestamp REAL, event TEXT, value INTEGER)""")

		# Repeat for alarm history.
		alarms.execute("""CREATE TABLE IF NOT EXISTS  alarms (serial INTEGER, time REAL, timeok REAL, alarm TEXT, count INTEGER, ackclient TEXT, state TEXT)""")


		# Commit the changes.
		conn.commit()

		# Get the latest serial numbers from the database. 
		result = events.execute('SELECT MAX(serial) FROM events')
		maxevent = result.fetchone()[0]
		if maxevent != None:
			self._EventSerial = maxevent
		else:
			self._EventSerial = 0

		result = alarms.execute('SELECT MAX(serial) FROM alarms')
		maxalarm = result.fetchone()[0]
		if maxalarm != None:
			self._AlarmSerial = maxalarm
		else:
			self._AlarmSerial = 0

		# Set the serial numbers.
		HMIAddr.MsgBuffers.SetMsgSerialNumbers(self._EventSerial, self._AlarmSerial)


		# Get the last set of records to initialise the message buffers.
		result = events.execute('SELECT MAX(rowid) FROM events')
		maxrowid = result.fetchone()[0]
		eventrecs = []
		if maxrowid != None:
			result = events.execute('SELECT * FROM events WHERE rowid > ?', (maxrowid - self._MessageRestore,))
			initrows = result.fetchall()
			if initrows[0] != None:
				eventrecs = initrows


		result = alarms.execute('SELECT MAX(rowid) FROM alarms')
		maxrowid = result.fetchone()[0]
		alarmhistrecs = []
		if maxrowid != None:
			result = alarms.execute('SELECT * FROM alarms WHERE rowid > ?', (maxrowid - self._MessageRestore,))
			initrows = result.fetchall()
			if initrows[0] != None:
				alarmhistrecs = initrows


		# Now we can close the database.
		events.close()
		alarms.close()
		conn.close()


		# Reconstruct the message buffer format for events.
		eventkeys = ['serial', 'timestamp', 'event', 'value']
		eventbuff = map(lambda x: dict(zip(eventkeys, x)), eventrecs)

		# Reconstruct the message buffer format for alarm history.
		alarmkeys = ['serial', 'time', 'timeok', 'alarm', 'count', 'ackclient', 'state']
		alarmhistbuff = map(lambda x: dict(zip(alarmkeys, x)), alarmhistrecs)


		# Restore the saved messages to the in-memory message buffers.
		HMIAddr.MsgBuffers.SetMsgBuffers(eventbuff, alarmhistbuff)

		# The following deferred calls will run when the main program actually starts up.
		# Open the database, but this time using Twisted's deferred methods. 
		self._dbpool = adbapi.ConnectionPool('sqlite3', database=self._dbname, check_same_thread=False, timeout=30)


		# Load the RSS messages. This also gives us the tag filter list.
		self.LoadRSSMsgs()

		# Store the event information for RSS feed data generation.
		self._RSSEvents = [(x[1], x[2]) for x in eventrecs if x[2] in self._RSSTagFilter]


		# Schedule the first call.
		reactor.callLater(1.0, self._AlarmEventUpdate)



	########################################################
	def _AlarmEventUpdate(self):
		"""Update the alarms and events and log them to the database. This 
		schedules itself regularly on a timed basis.
		"""
		# Update the alarm and event states.
		Msg.HMIData.UpdateAlarms()
		Msg.HMIData.UpdateEvents()


		# Get the latest event data.
		eventbuffer, eventerrors = Msg.HMIData.GetEventsNoLimits(self._EventSerial)

		# Get the latest alarm history data.
		alarmhistorybuffer, alarmhisterrors = Msg.HMIData.GetAlarmHistoryNoLimits(self._AlarmSerial)

		# Log any new events.
		for i in eventbuffer:
			erowdata = (i['serial'], i['timestamp'], i['event'], i['value'])
			self._dbpool.runOperation('INSERT INTO events VALUES (?, ?, ?, ?)', erowdata)

		# Find the maximum serial number so we can update it for the next cycle.
		if len(eventbuffer) > 0:
			serial = [i['serial'] for i in eventbuffer]
			self._EventSerial = max(serial)

		# Update the RSS events record.
		self._RSSEvents.extend([(x['timestamp'], x['event']) for x in eventbuffer 
												if x['event'] in self._RSSTagFilter])
		rssbuflen = len(self._RSSEvents)
		if rssbuflen > self._MessageRestore:
			self._RSSEvents = self._RSSEvents[:rssbuflen - self._MessageRestore]


		# Repeat for alarm history.
		for i in alarmhistorybuffer:
			arowdata = (i['serial'], i['time'], i['timeok'], i['alarm'], i['count'], i['ackclient'], i['state'])
			self._dbpool.runOperation('INSERT INTO alarms VALUES (?, ?, ?, ?, ?, ?, ?)', arowdata)


		# Find the maximum serial number so we can update it for the next cycle.
		if len(alarmhistorybuffer) > 0:
			serial = [i['serial'] for i in alarmhistorybuffer]
			self._AlarmSerial = max(serial)


		# Schedule the next call.
		reactor.callLater(1.0, self._AlarmEventUpdate)



	########################################################
	def QueryEvents(self, startime, endtime, events):
		"""Start the query for the events table for logged data.
		Parameters: startime (float) = Start of time period as a POSIX time stamp.
			endtime (float) = End of time period as a POSIX time stamp.
			events (tuple) = A tuple of event tags to search for.
		"""
		# Construct the parameter portion of the query string and the
		# associated parameters.
		querylist = []
		paramlist = []
		if (startime != None) and (endtime != None):
			querylist.append('timestamp BETWEEN (?) AND (?)')
			paramlist.extend([startime, endtime])
		if (events != None):
			querylist.append('event IN (%s)' % ','.join('?' * len(events)))
			paramlist.extend(events)

		# Join the SQL string together.
		if len(querylist) > 0:
			sqlstr = 'SELECT * FROM events WHERE ' + ' AND '.join(querylist)
		else:
			sqlstr = ''

		return self._dbpool.runQuery(sqlstr, tuple(paramlist))



	########################################################
	def QueryAlarmHistory(self, starttime, endtime, starttimeok, endtimeok, 
									startcount, endcount, ackclient, alarms):
		"""Start the query for the events table for logged data.
		All times are POSIX time stamps.
		Parameters: starttime (float) = Start of time period.
			endtime (float) = End of time period.
			starttimeok (float) = Start of time OK period.
			endtimeok (float) = End of time OK period.
			startcount (integer) = Start of count range.
			endcount (integer) = End of count range.
			ackclient (string) = A tuple of Ack client names.
			alarms (tuple) = A tuple of alarm history tags to search for.
		"""

		# Construct the parameter portion of the query string and the
		# associated parameters.
		querylist = []
		paramlist = []
		if (starttime != None) and (endtime != None):
			querylist.append('time BETWEEN (?) AND (?)')
			paramlist.extend([starttime, endtime])
		if (starttimeok != None) and (endtimeok != None):
			querylist.append('timeok BETWEEN (?) AND (?)')
			paramlist.extend([starttimeok, endtimeok])
		if (startcount != None) and (endcount != None):
			querylist.append('count BETWEEN (?) AND (?)')
			paramlist.extend([startcount, endcount])
		if (ackclient != None):
			querylist.append('ackclient IN (%s)' % ','.join('?' * len(ackclient)))
			paramlist.extend(ackclient)
		if (alarms != None):
			querylist.append('alarm IN (%s)' % ','.join('?' * len(alarms)))
			paramlist.extend(alarms)

		# Join the SQL string together.
		if len(querylist) > 0:
			sqlstr = 'SELECT * FROM alarms WHERE ' + ' AND '.join(querylist)
		else:
			sqlstr = ''

		return self._dbpool.runQuery(sqlstr, tuple(paramlist))



	########################################################
	def GetRSSEvents(self):
		"""Return the current RSS events buffer.
		"""
		return self._RSSEvents


	########################################################
	def GetRSSTexts(self):
		"""Return the current RSS text messages dictionay.
		"""
		return self._EventMsgs

	########################################################
	def GetRSSLinkData(self):
		"""Return the link and logo file name read from the template file.
		"""
		return self._RSSLink, self._LogoFile

	########################################################
	def GetRSSTemplate(self):
		"""Return the RSS template string. This is the template which
		is used to create the overall RSS response container.
		"""
		return self._RSSTemplate


	########################################################
	def LoadRSSMsgs(self):
		"""Load the RSS messages from disk. This looks for a specific file name,
		which the user should have used as part of their web app.
		"""

		# Load the event messages. 
		try:
			eventmsgs = MBFileServices.ReadFile(_RSSEventMsgFile)

			# Convert it to a single string.
			eventstr = ''.join(eventmsgs)

			# Now, convert to a dictionary. The original form should have been 
			# a JSON string.
			self._EventMsgs = MonUtils.JSONDecode(eventstr)
		except:
			self._EventMsgs = {}
			print(_Msgs['noerssmesgs'])


		# Load the RSS template file.
		try:
			self._RSSTemplate = ''.join(MBFileServices.ReadFile(_RSSTemplateFile))
		except:
			self._RSSTemplate = ''
			print(_Msgs['norsstemplate'])


		# If we couldn't read the RSS events file, we can't do the rest. 
		if self._RSSTemplate != '':

			# Get the name of the page to use for the link. This is stored as
			# part of the template so it can be customised.
			try:
				templatexml = xml.dom.minidom.parseString(self._RSSTemplate)

				link = templatexml.getElementsByTagName('linkfile')
				self._RSSLink = link[0].childNodes[0].data
			except:
				self._RSSLink = ''
				print(_Msgs['rsslinkfileerr'])


			# Get the RSS tag filter list.
			try:
				tagfilter = templatexml.getElementsByTagName('taglist')
				tagstr = tagfilter[0].childNodes[0].data
				self._RSSTagFilter = map(lambda x: x.strip(), tagstr.split(','))
			except:
				self._RSSTagFilter = []
				print(_Msgs['rsstaglisterr'])


			# Get the logo file name.
			try:
				logo = templatexml.getElementsByTagName('logofile')
				self._LogoFile = logo[0].childNodes[0].data
			except:
				self._LogoFile = ''
				print(_Msgs['rsslogofileerr'])



############################################################
AlarmLogger = AlarmEventHandler()

############################################################



########################################################
def _ERPFilter(readlist, writevalues):
	"""Filter the read and write requests in an HMI message to comply with 
	the ERP server restrictions. Reads and writes are filtered according to 
	the filter lists from the HMI configuration.
	Parameters: readlist (list) = The read command tag list from the message.
			writevalues (dict) = The write command from the message.
	Returns: (list) = The filtered read request.
		(dict) = The filtered write request.
		(dict) = The read error (readerr) component for the updated message.
		(dict) = The write error (writeerr) component for the updated message.
	The read and write errors will have to be combined with whatever other read
	and write errors are encountered in handling the filtered message.
	"""
	# Get the current HMI configuration information.
	hmiconfig = Msg.GetCurrentHMIInfo()
	erpconfig = hmiconfig.GetERPConfig()
	readfilter = erpconfig['read']
	writefilter = erpconfig['write']

	# Get the list of all the valid tags. 
	tagconfig = hmiconfig.GetConfigDict()
	taglist = tagconfig.keys()

	# Find the tags which do not exist.
	readnotexist = set(readlist) - set(taglist)
	writenotexist = set(writevalues.keys()) - set(taglist)
	readnotfound = dict([(x, 'tagnotfound') for x in readnotexist])
	writenotfound = dict([(x, 'tagnotfound') for x in writenotexist])

	# Find the tags which do exist.
	readexist = set(readlist) & set(taglist)
	writeexist = set(writevalues.keys()) & set(taglist)


	# Find the authorised read keys.
	authorisedkeys = set(readfilter) & set(readexist)
	# Find the unauthorised keys.
	unauthorisedkeys = set(readexist) - set(readfilter)

	# Create the filtered read keys.
	filteredread = list(authorisedkeys)
	# Create the error response for unauthorised reads.
	readerrors = dict([(x, 'accessdenied') for x in unauthorisedkeys])
	readerrors.update(readnotfound)


	# Find the authorised write keys.
	authorisedkeys = set(writefilter) & set(writeexist)
	# Find the unauthorised keys.
	unauthorisedkeys = set(writeexist) - set(writefilter)

	# Create the filtered write values.
	filteredwrite = dict([(x, writevalues[x]) for x in authorisedkeys])
	# Create the error response for unauthorised writes.
	writeerrors = dict([(x, 'accessdenied') for x in unauthorisedkeys])
	writeerrors.update(writenotfound)


	return filteredread, filteredwrite, readerrors, writeerrors


########################################################
def _HandleMessage(recvjson, restricted, erpfilter):
	"""Handle a protocol message.
	Parameters: recvjson (string) = The received JSON message.
		restricted (boolean) = If true, write and alarm acknowledge attempts 
			will be filtered out. This is used to implement a read-only version
			of the protocol.
		erpfilter (boolean) = If true, a limited sub-set of the HMI protocol 
			is implemented. All alarm and event related commands are ignored,
			and read and write commands are filtered according to the ERP list 
			parameters in the configuration.
	Only select *ONE* of the restricted or erpfilter options, not both!
	Returns: (string) = The response JSON string.
	"""

	# Decode the message.
	try:
		(clientid, msgid, readlist, readnoclist, writevalues, 
		readablereq, writablereq, eventrequest, alarmrequest, 
		alarmackrequest, 
		alarmhistoryrequest) = Msg.HMIServerMsg.HMIRequest(recvjson)
	except:
		# Couldn't decode the JSON string.
		return HMIMsg.ProtocolErrorMessage()

	# With the "restricted" version, all write attempts are suppressed.
	# Write commands will return an error.
	# Alarm acknowldgements are simply discarded.
	erpreaderrors = {}
	erpwriteerrors = {}
	if restricted:
		alarmackrequest = [];
		writeerrors = dict([(x, 'writeprotected') for x in writevalues.keys()])
		writevalues = {}

	# The ERP filter allows a subset of the Cascadas protocol.
	elif erpfilter:
		readlist, writevalues, erpreaderrors, erpwriteerrors = _ERPFilter(readlist, writevalues)
		readablereq = {}
		writablereq = {}
		eventrequest = []
		alarmrequest = []
		alarmackrequest = []
		alarmhistoryrequest = []


	# Analyse the request and construct a response.
	try:
		# Write the data table.
		if (len(writevalues) > 0):
			writeerrors = Msg.HMIData.WriteDataTable(writevalues)
		else:
			writeerrors = {}

		# For ERP requests, combine the errors from the authorised and 
		# unauthorised requests. 
		if erpfilter:
			erpwriteerrors.update(writeerrors)
			writeerrors = erpwriteerrors

		# Read the data table.
		if (len(readlist) > 0):
			readresult, readerrors = Msg.HMIData.ReadDataTable(readlist)
		else:
			readresult = {}
			readerrors = {}

		# For ERP requests, combine the errors from the authorised and 
		# unauthorised requests. 
		if erpfilter:
			erpreaderrors.update(readerrors)
			readerrors = erpreaderrors

		# We don't support read with NOC.
		readnocresult = {}

		# Test the tags to see if they are readable.
		if (readablereq != {}):
			readableresp = Msg.HMIData.TestTags(readablereq, False)
		else:
			readableresp = {}

		# Test the tags to see if they are writable.
		if (writablereq != {}):
			writableresp = Msg.HMIData.TestTags(writablereq, True)
		else:
			writableresp = {}

		# Events.
		eventbuffer, eventerrors = Msg.HMIData.GetEvents(eventrequest)

		# Alarms.
		alarmresp, alarmerrors = Msg.HMIData.GetAlarms(alarmrequest)

		# Update the alarm acknowledge requests from the client. These
		# only need to be processed as they arrive.
		Msg.HMIData.AckAlarms(alarmackrequest, clientid)

		# Update the alarm history from the records.
		# Construct a response.
		alarmhistorybuffer, alarmhisterrors = Msg.HMIData.GetAlarmHistory(alarmhistoryrequest)

		# Determine if there were any command errors. Since we don't
		# support read with NOC, any attempt at that is a command error.
		if ((writeerrors != {}) or (readerrors != {}) or 
			(len(readnoclist) != 0) or 
			(readableresp != {}) or	(writableresp != {}) or 
			(eventerrors != {}) or 
			(alarmerrors != {}) or 	(alarmhisterrors != {})):
			serverstat = 'commanderror'
		else:
			# If not, then the server status is ok.
			serverstat = 'ok'

	except:
		# We couldn't use the request message, so we need to return a server error.
		return HMIMsg.ServerErrorMessage()


	# The time stampe is UTC (GMT).
	timestamp = time.time()


	# Construct the response.
	try:
		return Msg.HMIServerMsg.HMIResponse(msgid, serverstat, 
				timestamp, readresult, readnocresult, 
				readerrors, writeerrors, 
				readableresp, writableresp,
				eventbuffer, eventerrors, 
				alarmresp, alarmerrors, 
				alarmhistorybuffer, alarmhisterrors)

	except:
		# We couldn't encode a proper response for some reason.
		print(_Msgs['hmiencodingerror'] % time.ctime())
		return HMIMsg.ServerErrorMessage()

##############################################################################

