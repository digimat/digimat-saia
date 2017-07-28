##############################################################################
# Project: 	MBLogic
# Module: 	StatusServer.py
# Purpose: 	Reports and controls status of system.
# Language:	Python 2.5
# Date:		25-Apr-2008.
# Version:	20-Dec-2010.
# Author:	M. Griffin.
# Copyright:	2008 - 2010 - Michael Griffin       <m.os.griffin@gmail.com>
# Modified by: Juan Pomares <pomaresj@gmail.com>
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
"""
This module is used to implement a web based monitoring system for MBLogic.
This includes a set of HTML help pages, plus main status and client details
HTML pages. 

Certain web page names are hard coded into the program (see below).

"""

 
############################################################

import time

from twisted.web import resource

from sysmon import StaticWeb, HMIStat, CommStat, PLCRunStat, PLCProgram, \
	SysStatus, ConfigReload, DataMonitor, PlatformStats

############################################################


# The data pages.
StatusPages = 'statuspages'

# The dynamically generated data.
StatusDataDir = 'statdata'

# Soft logic program source.
ProgDataDir = 'progsource'


##############################################################################


# This relates the request file name to the data handler. These files
# contain dynamic data which is requested by each page.
_StatusHandlers = {

	# System status.
	'sysstatus.js' : SysStatus.SysStatusDataResponse,
	'syssummary.js' : SysStatus.SysSummaryDataResponse,
	'syscontrol.js' : SysStatus.SysControlResponse,

	# These are special versions for MSIE. These output static data.
	'sysstatusmsie.js' : SysStatus.SysStatusDataResponseMSIE,
	'syssummarymsie.js' : SysStatus.SysSummaryDataResponseMSIE,
	

	# Comms data.
	'commserversummary.js' : CommStat.ServerCommsSummaryResponse,
	'commserverstatdata.js' : CommStat.CommServerDataResponse,
	'commclientsummary.js' : CommStat.ClientCommsSummaryResponse,

	'commclientcurrentconfig.js' : CommStat.CurrentClientConfigResponse,

	'commsmonitor.js' : CommStat.CommsMonitorResponse,
	'commsexpdtable.js' : CommStat.CommsExpDTResponse,
	'commslogs.js' : CommStat.CommsLogsResponse,
	'commconfigerrors.js' : CommStat.CommsConfigErrorResponse,

	# HMI web page data
	'hmiwebpageinfo.js' : CommStat.HMIFileInfoResponse,

	# HMI data
	'hmisummary.js' : HMIStat.HMISummaryResponse,
	'hmicurrentconfig.js' : HMIStat.HMICurrentDataResponse,
	'hminewconfig.js' : HMIStat.HMINewDataResponse,

	# Soft logic IO.
	'iosummary.js' : PLCRunStat.IOSummaryResponse,
	'iocurrentconfig.js' : PLCRunStat.IOCurrentDataResponse,
	'ionewconfig.js' : PLCRunStat.IONewDataResponse,

	# Soft logic program
	'plcsummary.js' : PLCRunStat.PLCSummaryResponse,
	'plccurrentconfig.js' : PLCRunStat.PLCCurrentDataResponse,
	'plcnewconfig.js' : PLCRunStat.PLCNewDataResponse,
	'plcrundata.js' : PLCRunStat.PLCRunResponse,

	# Soft logic program editing and monitoring.
	'plccurrentsource.js' : PLCProgram.ProgCurrentSourceResponse,
	'plccurrentsig.js' : PLCProgram.ProgCurrentSigResponse,
	'plcnewsource.js' : PLCProgram.ProgNewSourceResponse,
	
	# Soft logic xref.
	'plcinstrxref.js' : PLCRunStat.InstrXRefDataResponse,
	'plcaddrxref.js' : PLCRunStat.AddrXRefDataResponse,
	'plcsubrlist.js' : PLCProgram.SubrListResponse,

	# Data table monitor
	'sldatatable.js' : DataMonitor.SoftLogicDataResponse,
	'sysdatatable.js' : DataMonitor.SysDataTableResponse,
	
	# Platform information.
	'platformstats.js' : PlatformStats.PlatformStatsResponse

}

############################################################
class MBStatusDataHandle(resource.Resource):
	""" Handle data requests for status pages.
	"""


	########################################################
	def getChild(self, name, request):
		""" This is called by Twisted to handle the URL decoding
		and route the request to the appropriate destination.
		"""
		return _StatusHandlers.get(name, StaticWeb.StaticResponse)


##############################################################################

MBStatusData = MBStatusDataHandle()

# This relates the request file name to the data handler. These files require 
# special handling.
_PageHandlers = {
	# These do POST as well as GET.
	'statuscontrol.html' : ConfigReload.StatusControlPageResponse,
	'statusprogram.html' : PLCProgram.ProgSubrResponse,
}


############################################################
class MBWebStatusPagesHandle(resource.Resource):
	""" Handle requests for status pages.
	"""


	########################################################
	def getChild(self, name, request):
		""" This is called by Twisted to handle the URL decoding
		and route the request to the appropriate destination.
		"""
		return _PageHandlers.get(name, StaticWeb.StaticResponse)


##############################################################################

MBWebStatusPages = MBWebStatusPagesHandle()


# This handles programming pages. This part of the path is used to encode the
# part which indicates it is looking for program source code.

############################################################
class WebProgramHandle(resource.Resource):
	""" Handle requests for programming pages.
	"""

	########################################################
	def getChild(self, name, request):
		""" This is called by Twisted to handle the URL decoding
		and route the request to the appropriate destination.
		"""
		return PLCProgram.WebSubrPages


##############################################################################

WebProgramPages = WebProgramHandle()


############################################################
class MBWebStatus(resource.Resource):
	""" Implement a status web page to show and control the system.
	"""


	########################################################
	def getChild(self, name, request):
		""" This is called by Twisted to handle the URL decoding
		and route the request to the appropriate destination.
		"""

		self._args = {}
		self._path = []

		# Get the URL path.
		self._path = request.prepath[:]
		self._path.extend(request.postpath[:])

		# Check if the last element is empty (because it
		# was a '/'). If so, then delete it.
		if (self._path[-1] == ''):
			self._path.pop()

		# Check to see if we are looking for the main entry page. We look
		# for several alternate names.
		if self._path in [['index.html'], ['MBStatusSystem.html'], ['statussystem.html']]:
			# Now, check the user agent string to see if the browser is MSIE (any version).
			# TODO: This is for Debian 5.0 compatibility. 
			# This try/except is to provide backwards compatibility for Debian Stable.
			# requestHeaders is the newer version, and received_headers is deprecated.
			try:
				useragent = request.requestHeaders.getRawHeaders('User-Agent', default='')
			except:
				useragent = request.received_headers.get('user-agent', '')
			useragentstr = ''.join(useragent)
			if useragentstr.find('MSIE') >= 0:
				request.prepath = ['statussystemmsie.html']
			# Otherwise, we point to the new default main status page.
			else:
				request.prepath = ['statussystem.html']
			

		# Increment the request counter for reporting.
		ReportTracker.IncRequestCounter()

		# Any URL at this point is accepted as requesting the root.
		# This is for the static page content.
		if (name == StatusPages):
			return MBWebStatusPages
		# This path handles dynamically generated data.
		elif (name == StatusDataDir):
			return MBStatusData
		else:
			return StaticWeb.StaticResponse



############################################################
class RepCounter:
	""" This handles calculating the server statistics for reporting purposes.
	"""

	########################################################
	def __init__(self):
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
	def IncRequestCounter(self):
		"""Increment the request counter. This keeps track when each
		request was made in order to calculate a request rate in terms of
		requests per unit of time.
		"""
		# Note: This list could be replaced by a deque if we don't need
		# to support anything older than Python 2.6. This would allow us
		# to use the maxlen parameter to automatically manage the deque length.

		# Add a time stamp to the end of the buffer.
		self._RequestCounter.append(time.time())
		# We limit the size of the buffer so it doesn't grow excessively.
		if len(self._RequestCounter) > 25:
			self._RequestCounter.pop(0)

		# Set the request rate in the container.
		self._StatusInfo.SetRequestCounter(self._RequestCounter)

ReportTracker = RepCounter()

##############################################################################



