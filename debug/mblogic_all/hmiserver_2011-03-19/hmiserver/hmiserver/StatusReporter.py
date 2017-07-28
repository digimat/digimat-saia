##############################################################################
# Project: 	HMIServer
# Module: 	StatusReporter.py
# Purpose: 	Log events and messages to memory, and create web reports.
# Language:	Python 2.5
# Date:		28-Feb-2009.
# Ver.:		25-Nov-2010.
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

"""This module logs messages and events to memory, and prepares web pages 
to produce reports based on this information.
"""

import time

import MBFileServices

############################################################

class Reporter:

	########################################################
	def _FormatTimeDiff(self, starttime):
		"""
		"""
		try:
			return '%.02f' % ((time.time() - starttime) / 3600.0)
		except:
			return 0

	########################################################
	def _FormatTimeStr(self, timeval):
		"""Format a time value as a string.
		"""
		return time.strftime('%H:%M:%S, %a %d of %b, %Y', time.localtime(timeval))


	########################################################
	def __init__(self):

		self._MaxBuff = 50
		self._HmiRequestBuff = []	# HMI request messages.
		self._HmiResponseBuff = []	# HMI response messages.
		self._FieldRequestBuff = []	# Field device request messages.
		self._FieldResponseBuff = []	# Field device response messages.

		self._StartTime = time.time()
		self._CommsStatus = 'init'
		self._HMIConfig = {}
		self._HMIEventConfig = {}
		self._HMIAlarmConfig = {}
		self._HMIConfigErrors = []

		# Current status.
		self._StatParams = {
		'softname' : '',
		'softversion' : '',
		'starttimeformat' : self._FormatTimeStr(time.time()),
		'starttime' : time.time(),
		'uptime' : '0.0',
		'configok' : 'Undefined',
		'configcolour' : 'statusalert',
		'commsok' : 'Undefined',
		'commscolour' : 'statusalert',
		'port' : '',
		'fport' : '',
		'remotehost' : '',
		'remoteport' : '',
		'unitid' : '',
		'timeout' : 0.0,
		'serverid' : '',
		'hmifilelist' : []
		}

		#  HMI Parameters formatted for a static web page.
		# This will include embedded HTML mark-up.
		# The serverpage and clientpage keys control the visibility of
		# the display tables on the web page for servers and clients
		# respectively.
		self._HMIConfigParamsHTML = {
		'serverid' : '',
		'clientversion' : '',
		'addrtags' : '',
		'events' : '',
		'alarms' : '',
		'configerrors' : '',
		'serverpage' : 'none',
		'clientpage' : 'none'
		}

		#  HMI Parameters. This constains just the data.
		self._HMIConfigParams = {
		'serverid' : '',
		'clientversion' : '',
		'addrtags' : '',
		'events' : '',
		'alarms' : '',
		'configerrors' : ''
		}



	############################################################
	def ListHMIFiles(self, pagdir):
		"""Read a list of HTML and XHTML files in the HMI directory and
		store them for later display.
		Parameters: pagdir (string) = Name of HMI directory.
		"""
		self._StatParams['hmifilelist'] = MBFileServices.ListHMIFiles(pagdir)


	########################################################
	def AddHMIRequest(self, hmirequest):
		"""Add a copy of an HMI request message to the log buffer.
		"""
		self._HmiRequestBuff.append(hmirequest)
		if (len(self._HmiRequestBuff) > self._MaxBuff):
			self._HmiRequestBuff.pop(0)

	########################################################
	def AddHMIResponse(self, hmiresponse):
		"""Add a copy of an HMI response message to the log buffer.
		"""
		self._HmiResponseBuff.append(hmiresponse)
		if (len(self._HmiResponseBuff) > self._MaxBuff):
			self._HmiResponseBuff.pop(0)


	########################################################
	def AddFieldRequest(self, requestmsg):
		"""Add a copy of the field device request message to the log buffer.
		"""
		self._FieldRequestBuff.append(requestmsg)
		if (len(self._FieldRequestBuff) > self._MaxBuff):
			self._FieldRequestBuff.pop(0)

	########################################################
	def AddFieldResponse(self, responsemsg):
		"""Add a copy of the field device response message to the log buffer.
		"""
		self._FieldResponseBuff.append(responsemsg)
		if (len(self._FieldResponseBuff) > self._MaxBuff):
			self._FieldResponseBuff.pop(0)


	########################################################
	def GetHMIMsgs(self):
		""" Return a string containing the HMI messages.
		This string is in reverse order, with the newest messages first.
		When we substitute in the message strings, we have to insert spaces
		in the messages to allow the web page to wrap the lines.
		"""
		msgs = []
		try:
			for i in range(len(self._HmiRequestBuff) - 1, -1, -1):
				msgs.append('<tr><td>%s</td><td>%s</td></tr>' % 
					(str(self._HmiRequestBuff[i]).replace(',"', ', "'), 
					str(self._HmiResponseBuff[i]).replace(',"', ', "')))
		except:
			pass	# If we run into an error, then just accept what we have.
		return ''.join(msgs)

	########################################################
	def GetHMIMsgsList(self):
		"""Return the HMI messages buffers.
		Returns: (dict) = A dictionary containing the request and 
		response lists.
		"""
		return {'req' : self._HmiRequestBuff, 'resp' : self._HmiResponseBuff}



	########################################################
	def GetFieldDeviceMsgs(self):
		""" Return a string containing the field device messages.
		This string is in reverse order, with the newest messages first.
		The field device will be using a protocol such as Modbus/TCP.
		"""
		msgs = []
		try:
			for i in range(len(self._FieldRequestBuff) - 1, -1, -1):
				msgs.append('<tr><td>%s</td><td>%s</td></tr>' % 
					(str(self._FieldRequestBuff[i]), 
					str(self._FieldResponseBuff[i])))
		except:
			pass	# If we run into an error, then just accept what we have.

		return ''.join(msgs)


	########################################################
	def GetFieldDeviceMsgsList(self):
		"""Return the field device messages buffers.
		Returns: (dict) = A dictionary containing the request and 
		response lists.
		"""
		return {'req' : self._FieldRequestBuff, 'resp' : self._FieldResponseBuff}



	########################################################
	def SetSysParams(self, softname, softversion, hmiservertype):
		"""Set the general system parameters for display.
		softname (string) = Name of the software.
		softversion (string) = Version of the software.
		hmiservertype (boolean) = If True, system is a server, else
			system is a client.
		"""
		self._StatParams['softname'] = softname
		self._StatParams['softversion'] = softversion

		if hmiservertype:
			serverpagetype = 'block'
			clientpagetype = 'none'
		else:
			serverpagetype = 'none'
			clientpagetype = 'block'

		self._HMIConfigParamsHTML['serverpage'] = serverpagetype
		self._HMIConfigParamsHTML['clientpage'] = clientpagetype



	########################################################
	def SetCommandParams(self, port, rhost, rport, rtimeout, runitid):
		"""Store the command line start up parameters for display.
		port (integer) = Port for web server.
		rhost (string) = Host IP or name for remote data server.
		rport (integer) =  Port for remote data server.
		rtimeout (float) = Communications time out for remote data server.
		runitid (integer) = Modbus unit ID to use.
		"""
		self._StatParams['port'] = port
		self._StatParams['remotehost'] = rhost
		self._StatParams['remoteport'] = rport
		self._StatParams['timeout'] = rtimeout
		self._StatParams['unitid'] = runitid


	########################################################
	def SetCommandServerParams(self, wport, fport):
		"""Store the command line start up parameters for display.
		wport (integer) = Port for web server.
		fport (integer) =  Port for field device data server.
		"""
		self._StatParams['port'] = wport
		self._StatParams['fport'] = fport


	########################################################
	def GetStatParams(self):
		""" Return the status parameter dictionary. The uptime, and
		comms status are automatically updated as part of this call.
		"""
		# Update the uptime.
		self._StatParams['uptime'] = self._FormatTimeDiff(self._StartTime)

		# Update the communications status.
		if (self._CommsStatus == 'init'):
			self._StatParams['commsok'] = 'Undefined'
			self._StatParams['commscolour'] = 'statusalert'
		elif (self._CommsStatus == 'error'):
			self._StatParams['commsok'] = 'Fault'
			self._StatParams['commscolour'] = 'statusfault'
		elif (self._CommsStatus == 'ok'):
			self._StatParams['commsok'] = 'OK'
			self._StatParams['commscolour'] = 'statusok'
		else:
			self._StatParams['commsok'] = 'Undefined'
			self._StatParams['commscolour'] = 'statusalert'

		return self._StatParams


	########################################################
	def GetStaticParams(self):
		""" Return the status parameter dictionary. The uptime, and
		comms status are automatically updated as part of this call.
		This also returns the HMI configuration. Data is formatted for
		a static web page.
		"""
		staticparams = {}
		# Get the current status parameters.
		statparams = self.GetStatParams()
		# We don't want to affect the original version.
		staticparams.update(statparams)
		# Add in the HMI parameters.
		staticparams.update(self._HMIConfigParamsHTML)

		return staticparams


	########################################################
	def GetHMIConfigParams(self):
		""" Return the HMI configuration parameter dictionary. 
		"""
		return self._HMIConfigParams


	########################################################
	def SetCommsStatusOK(self):
		"""Set the communcations status flag to OK.
		"""
		self._CommsStatus = 'ok'


	########################################################
	def SetCommsStatusError(self):
		"""Set the communcations status flag to Error.
		"""
		self._CommsStatus = 'error'


	########################################################
	def _FormatZones(self, zonelist):
		"""Convert a zone list to a nicely formatted string.
		"""
		zonestr = ''
		for i in zonelist:
			zonestr = '%s %s,' % (zonestr, i)
		return zonestr


	########################################################
	def SetHMIConfig(self, serverid, clientversion, configdict, 
		eventconfig, alarmconfig, errors):
		"""Format the HMI Configuration.
		"""
		# Status summary.
		self._StatParams['serverid'] = serverid

		# Set the report status.
		if not errors:
			self._StatParams['configok'] = 'OK'
			self._StatParams['configcolour'] = 'statusok'
		else:
			self._StatParams['configok'] = 'Errors'
			self._StatParams['configcolour'] = 'statusfault'


		# HMI configuration data used for AJAX interface.
		self._HMIConfigParams['serverid'] = serverid
		self._HMIConfigParams['clientversion'] = clientversion
		self._HMIConfigParams['addrtags'] = configdict
		self._HMIConfigParams['events'] = eventconfig
		self._HMIConfigParams['alarms'] = alarmconfig
		self._HMIConfigParams['configerrors'] = errors



		# Data is re-formatted for static HTML.
		self._HMIConfigParamsHTML['serverid'] = serverid
		self._HMIConfigParamsHTML['clientversion'] = clientversion

		self._HMIConfig = configdict
		self._HMIEventConfig = eventconfig
		self._HMIAlarmConfig = alarmconfig
		self._HMIConfigErrors = errors


		# Format the address tag configuration.
		addrtags = []
		addrhtml = '<td>%(addrtype)s</td><td>%(memaddr)s</td>' + \
			'<td>%(datatype)s</td><td>%(minrange)s</td>' + \
			'<td>%(maxrange)s</td><td>%(scaleoffset)s</td>' + \
			'<td>%(scalespan)s</td></tr>'
		for i in configdict:
			if i not in ['serverid', 'clientversion']:
				addrtags.append(('<tr><td>%s</td>' % i) + (addrhtml % configdict[i]))

		# Sort for display.
		addrtags.sort()

		self._HMIConfigParamsHTML['addrtags'] = ''.join(addrtags)


		# Format the event tags configuration.
		eventtags = []
		for i in eventconfig:
			eventtags.append('<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % 
				(i, eventconfig[i]['tag'], 
				self._FormatZones(eventconfig[i]['zonelist'])))

		# Sort for display.
		eventtags.sort()

		self._HMIConfigParamsHTML['events'] = ''.join(eventtags)

		# Format the alarm tags configuration.
		alarmtags = []
		for i in alarmconfig:
			alarmtags.append('<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % 
				(i, alarmconfig[i]['tag'], 
				self._FormatZones(alarmconfig[i]['zonelist'])))

		# Sort for display.
		alarmtags.sort()

		self._HMIConfigParamsHTML['alarms'] = ''.join(alarmtags)

		# Format the error messages.
		errormsgs = []
		if errors:
			for i in errors:
				errormsgs.append('<tr><td>%s</td></tr>' % str(i))
		else:
			errormsgs.append('<tr><td><strong><em>No errors</em></strong></td></tr>')

		self._HMIConfigParamsHTML['configerrors'] = ''.join(errormsgs)


############################################################

# Create a common report object.
Report = Reporter()

############################################################



############################################################


########################################################
def GetStatCommand(recvdata):
	"""Accept an HTTP header and extract the status system command.
	Parameters: recvdata (string) = The received raw HTTP data.
	Returns: (string) = The command payload as a raw string. Returns an
		empty string if error or no payload found.
	"""
	# Split the block of text into lines
	headerlines = recvdata.splitlines()
	if len(headerlines) > 0:
		# Find the first blank line.
		try:
			blankindex = headerlines.index('')
		except:
			# No blank line found.
			return ''
		# Take everything after the blank line and convert it
		# into a single block of text.
		return ''.join(headerlines[blankindex:])
	else:
		return ''



##############################################################################


