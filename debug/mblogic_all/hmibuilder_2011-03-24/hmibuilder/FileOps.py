##############################################################################
# Project: 	MBLogic
# Module: 	FileOps.py
# Purpose: 	File I/O handling and parsing.
# Language:	Python 2.5
# Date:		16-Jan-2011.
# Version:	19-Jan-2011.
# Author:	M. Griffin.
# Copyright:	2011 - Michael Griffin       <m.os.griffin@gmail.com>
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


import ConfigParser
import itertools

import ErrorMsgs

##############################################################################

# Error handling exception classes.

class HMIConfigError(Exception):
	"""Error reading or decoding HMI config file.
	"""
	def __init__(self, errmsg):
		self.errmsg = errmsg


##############################################################################
class HMITags:
	"""Read in the HMI configuration.
	"""

	########################################################
	def __init__(self, configfilename):
		"""Parameters: configfilename (string) = The name of the 
		hmi configuration file.
		"""

		self._ConfigFileName = configfilename

		self._ConfigParser = ConfigParser.ConfigParser()

		# This is necessary to prevent ConfigParser from forcing
		# option names to lower case. 
		self._ConfigParser.optionxform = lambda x: x

		# List of all the standard HMI tags.
		self._TagList = []

		self._EventTags = []
		self._AlarmTags = []
		self._EventZones = []
		self._AlarmZones = []

		# Read in the configuration file.
		self.ReadConfigFile()

	########################################################
	def ReadConfigFile(self):
		"""Use the parser object to read a configuration file from disk.
		Results are stored in a class variable. 
		"""

		errfile = {'filename' : self._ConfigFileName}

		# Read in the configuration file for parsing.
		try:
			filename = self._ConfigParser.read(self._ConfigFileName)
			# The parser should have returned the name of the requested file. 
			# Could not read the file.
			if (filename[0] != self._ConfigFileName):
				raise HMIConfigError(ErrorMsgs.Msg.GetMessage('badhmiconfigread', errfile))
		# Error when parsing the file.
		except ConfigParser.ParsingError, parserr:
			raise HMIConfigError(ErrorMsgs.Msg.GetMessage('badhmiconfigparse', errfile))
		# A general unspecified error.
		except:
			raise HMIConfigError(ErrorMsgs.Msg.GetMessage('badhmiconfigload', errfile))


		# Get the basic information from the configuration.
		allsectionlist = self._ConfigParser.sections()

		# Filter out the sections we handle separately.
		standardsections = ('&events', '&alarms', '&erplist')
		# This uses set arithmetic.
		self._TagList = list(set(allsectionlist) - set(standardsections))
		# Sort the tag list.
		self._TagList.sort()

		# Get the event tags and event zones.
		if '&events' in allsectionlist:
			try:
				eventcfg = [x[1].split(',') for x in self._ConfigParser.items('&events') if x[0] != 'base']
				# Get the event tags.
				self._EventTags = [x[0].strip() for x in eventcfg]
				# Get the zones. There may be multiple zones for each tag.
				zones = [x[1:] for x in eventcfg]
				# Flatten the list. Also remove duplicates. 
				zones = list(set(itertools.chain(*zones)))
				# Strip spaces from the beginning and end. 
				self._EventZones = [x.strip() for x in zones]
				# Sort the lists.
				self._EventTags.sort()
				self._EventZones.sort()
			except:
				raise HMIConfigError(ErrorMsgs.Msg.GetMessage('badhmiconfigevents', {}))
				


		# Get the alarm tags and alarm zones.
		if '&alarms' in allsectionlist:
			try:
				alarmcfg = [x[1].split(',') for x in self._ConfigParser.items('&alarms') if x[0] != 'base']
				# Get the alarm tags.
				self._AlarmTags = [x[0].strip() for x in alarmcfg]
				# Get the zones. There may be multiple zones for each tag.
				zones = [x[1:] for x in alarmcfg]
				# Flatten the list. Also remove duplicates. 
				zones = list(set(itertools.chain(*zones)))
				# Strip spaces from the beginning and end. 
				self._AlarmZones = [x.strip() for x in zones]
				# Sort the lists.
				self._AlarmTags.sort()
				self._AlarmZones.sort()
			except:
				raise HMIConfigError(ErrorMsgs.Msg.GetMessage('badhmiconfigalarms', {}))



	########################################################
	def GetTagList(self):
		"""Return the list of HMI tags.
		Returns: (list) = List of HMI tags (config sections).
		"""
		return self._TagList


	########################################################
	def GetEventTagList(self):
		"""Return the list of event tags.
		"""
		return self._EventTags

	########################################################
	def GetEventZoneList(self):
		"""Return the list of event zones.
		"""
		return self._EventZones


	########################################################
	def GetAlarmTagList(self):
		"""Return the list of alarm tags.
		"""
		return self._AlarmTags

	########################################################
	def GetAlarmZoneList(self):
		"""Return the list of alarm zones.
		"""
		return self._AlarmZones


##############################################################################


