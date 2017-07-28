##############################################################################
# Project: 	MBLogic
# Module: 	HMIServer.py
# Purpose: 	Handle the MB-HMI protocol.
# Language:	Python 2.5
# Date:		01-Jan-2009.
# Ver.:		31-Dec-2010.
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
import datetime

from twisted.web import server, resource, static

from mbprotocols import HMIMsg
from sysmon import MonUtils

import MBWebPage
import HMIData


############################################################

############################################################
# TODO: This is for Debian 5.0 compatibility. 
# This supports older versions of Twisted on Debian Stable. 
def StaticSendOld(f, flength, request):
	"""This is for compatibility with older versions of Twisted.
	"""
	static.FileTransfer(f, flength, request)


def StaticSendNew(f, flength, request):
	"""This is for compatibility with newer versions of Twisted.
	"""
	producer = static.NoRangeStaticProducer(request, f)
	producer.start()

try:
	from twisted.web.static import NoRangeStaticProducer
	StaticSend = StaticSendNew
except:
	StaticSend = StaticSendOld
	


############################################################

# Name of the directory where the web pages are stored.
PageDir = 'hmipages'

# Name of the directory where the standard HMI library files are stored.
HMILibDir = os.path.join('mblogic', 'hmilib')

############################################################

############################################################
class ServiceError(resource.Resource):
	"""Display an error message when attempting to access a
	resource which does not exist.
	"""

	isLeaf = True


	########################################################
	def SetErrorMsg(self, MessageText):
		"""Set the error message to be used when
		displaying an error condition.
		"""
		# HTML portion of error message.
		self._ErrorStr = """
		<html><head><title>404 - No Such Resource</title></head>
			<body><h1>No Such Resource</h1>
			<p>%s</p></body></html>
		""" % MessageText

	########################################################
	def render(self, request):
		"""This is called by Twisted to handle GET calls.
		"""
		request.setResponseCode(404)
		return self._ErrorStr

############################################################

_ServiceError = ServiceError()

############################################################


############################################################
class MakeRSS:
	"""Create an RSS content page.
	"""

	########################################################
	def __init__(self):
		self._rsspage = ''
		self._cachetime = 0.0

	########################################################
	def _makerss(self, host, port):
		"""Assemble a fresh RSS page.
		Parameters: host (string) = The IP host for this server.
			port (string) = The IP port for this server.
		"""
		itemtemplate = """
			<item>
				<title>%(timestamp)s - %(event)s</title>
				<link>%(link)s</link>
				<description>%(text)s</description>
			</item>
"""

		# Get the name of the page to use for the link. This is stored as
		# part of the template so it can be customised.
		userpage, logofile = HMIData.AlarmLogger.GetRSSLinkData()

		# This link is inserted into each RSS item.
		linkurl = 'http://%s:%s/%s' % (host, port, userpage)
		logourl = 'http://%s:%s/%s' % (host, port, logofile)

		# Get the message texts associated with the event keys.
		msgtexts = HMIData.AlarmLogger.GetRSSTexts()

		# Convert the time stamp, and reformat the data as a dictionary.
		# We also add in the text equivalent to the event. If a message is 
		# missing, a blank is substituted.
		rssdata = map(lambda x: {'timestamp' : time.ctime(x[0]), 'event' : x[1], 
				'text' : msgtexts.get(x[1], ''), 'link' : linkurl}, HMIData.AlarmLogger.GetRSSEvents())
		# Reverse the list to put the newest records first.
		rssdata.reverse()
		# Create the RSS items.
		rssitems = str(''.join(map(lambda x: itemtemplate % x, rssdata)))
		# We have to force these items to string as Twisted will not accept unicode.
		rss = {'messages' : str(rssitems), 'logofile' : str(logourl)}


		rssfeed = HMIData.AlarmLogger.GetRSSTemplate() % rss

		return rssfeed


	########################################################
	def GetRSSFeed(self, host, port):
		"""Get the RSS feed page. RSS pages are fed from a cache to avoid
		excessive updates. The cache is updated on a timed basis.
		Parameters: host (string) = The IP host for this server.
			port (string) = The IP port for this server.)
		"""
		# Check to see if the cache must be updated.
		if (time.time() - self._cachetime) > 15.0:
			self._cachetime = time.time()
			self._rsspage = self._makerss(host, port)

		return self._rsspage


_MakeRSSPage = MakeRSS()


############################################################
class ShowRSSResponse(resource.Resource):
	"""Respond with the appropriate RSS protocol response. 
	"""

	isLeaf = True	# This is a resource end point.


	########################################################
	def render_GET(self, request):
		"""Return the page for a GET. This will handle requests
		to read data.
		"""
		# Get the host IP and port for this server.
		ip = request.getHost()

		rssfeed = _MakeRSSPage.GetRSSFeed(ip.host, ip.port)
		return rssfeed


	########################################################
	def render_POST(self, request):
		""" POST is not a valid request.
		"""
		return _ServiceError


############################################################

_ShowRSSResponse = ShowRSSResponse()



########################################################
def _ValidateTimeQuery(timestr):
	"""Validate a time string entered by the user, and convert it to a
	valid time POSIX stamp. The valid string format is as follows:
	'YYYYMMDDHHMMSS'
	Parameters: timestr (string) = The time string entered by the user.
	Returns: (float) = A POSIX time stamp, or None if invalid.
	"""
	# String is the expected length.
	if len(timestr) != 14:
		return None
	# It is all digits.
	if not timestr.isdigit():
		return None

	# Convert to a time tuple
	t = datetime.datetime(int(timestr[0:4]),	# Year
						int(timestr[4:6]),		# Month
						int(timestr[6:8]),		# Day
						int(timestr[8:10]),		# Hour
						int(timestr[10:12]),	# Minute
						int(timestr[12:14]))	# Second

	# Convert to a POSIX time stamp.
	return time.mktime(t.timetuple())



############################################################
class ShowEventsQueryResponse(resource.Resource):
	"""Respond with the appropriate event query response. 
	This provides the ability to query the event database.
	"""

	isLeaf = True	# This is a resource end point.


	########################################################
	def _QueryErr(self, result, request):
		"""
		"""

		_ErrorStr = """
		<html><head><title>404 - Query Error</title></head>
			<body><h1>Query error</h1>
			<p>Query error</p></body></html>
		"""

		request.setResponseCode(404)
		request.write(_ErrorStr)
		request.finish()
		return server.NOT_DONE_YET


	########################################################
	def _ContinueQuery(self, result, request):
		"""Complete the event query. 
		Parameters: result (list) = The list response from the query.
			request: (Twisted request) = The Twisted request passed from the
				original request.
		"""
		request.write(MonUtils.JSONEncode(result))
		request.finish()
		return server.NOT_DONE_YET


	########################################################
	def render_GET(self, request):
		"""Return the page for a GET. This will handle requests
		to read data. This is a sample query:
		http://localhost:8082/aequery/events?timestamp=20101217080000,20101218120059;events=PumpStopped,Tank1Full
		"""

		# Get the request arguements.
		args = request.args
		timestamp = args.get('timestamp', ('', ''))[0]
		events = args.get('events', ('', ''))[0]

		# Validate the time values.
		timeparams = [x.strip() for x in timestamp.split(',') if len(x.strip()) > 0]
		if len(timeparams) == 2:
			try:
				starttime = _ValidateTimeQuery(timeparams[0])
				endtime = _ValidateTimeQuery(timeparams[1])
			except:
				starttime = None
				endtime = None
		else:
			starttime = None
			endtime = None


		eventparams = tuple([x.strip() for x in events.split(',') if len(x.strip()) > 0])
		if len(eventparams) == 0:
			eventparams = None

		query = HMIData.AlarmLogger.QueryEvents(starttime, endtime, eventparams)
		query.addCallback(self._ContinueQuery, request)
		query.addErrback(self._QueryErr, request)

		return server.NOT_DONE_YET



	########################################################
	def render_POST(self, request):
		""" POST is not a valid request.
		"""
		return _ServiceError


############################################################

_ShowEventsQueryResponse = ShowEventsQueryResponse()


############################################################
class ShowAlarmsQueryResponse(resource.Resource):
	"""Respond with the appropriate alarm history query response. 
	This provides the ability to query the alarm history database.
	"""

	isLeaf = True	# This is a resource end point.


	########################################################
	def _QueryErr(self, result, request):
		"""
		"""

		_ErrorStr = """
		<html><head><title>404 - Query Error</title></head>
			<body><h1>Query error</h1>
			<p>Query error</p></body></html>
		"""

		request.setResponseCode(404)
		request.write(_ErrorStr)
		request.finish()
		return server.NOT_DONE_YET


	########################################################
	def _ContinueQuery(self, result, request):
		"""Complete the event query. 
		Parameters: result (list) = The list response from the query.
			request: (Twisted request) = The Twisted request passed from the
				original request.
		"""
		request.write(MonUtils.JSONEncode(result))
		request.finish()
		return server.NOT_DONE_YET


	########################################################
	def render_GET(self, request):
		"""Return the page for a GET. This will handle requests
		to read data.
		http://localhost:8082/aequery/alarmhist?time=20101217080000,20101220120059;alarms=PB1Alarm,PB2Alarm;count=2,4
		"""

		# Get the request arguements.
		args = request.args
		timeval = args.get('time', ('', ''))[0]
		timeok = args.get('timeok', ('', ''))[0]
		countval = args.get('count', ('', ''))[0]
		ackparams = args.get('ackclient', ('', ''))[0]
		alarms = args.get('alarms', ('', ''))[0]

		# Validate the time values.
		timeparams = [x.strip() for x in timeval.split(',') if len(x.strip()) > 0]
		if len(timeparams) == 2:
			try:
				starttime = _ValidateTimeQuery(timeparams[0])
				endtime = _ValidateTimeQuery(timeparams[1])
			except:
				starttime = None
				endtime = None
		else:
			starttime = None
			endtime = None

		# Validate the timeok values.
		timeokparams = [x.strip() for x in timeok.split(',') if len(x.strip()) > 0]
		if len(timeokparams) == 2:
			try:
				starttimeok = _ValidateTimeQuery(timeokparams[0])
				endtimeok = _ValidateTimeQuery(timeokparams[1])
			except:
				starttimeok = None
				endtimeok = None
		else:
			starttimeok = None
			endtimeok = None

		# Validate the time values.
		countparams = [x.strip() for x in countval.split(',') if len(x.strip()) > 0]
		if len(countparams) == 2:
			try:
				startcount = int(countparams[0])
				endcount = int(countparams[1])
			except:
				startcount = None
				endcount = None
		else:
			startcount = None
			endcount = None

		# Validate the ack client params.
		ackclient = tuple([x.strip() for x in ackparams.split(',') if len(x.strip()) > 0])
		if len(ackclient) == 0:
			ackclient = None

		# List of alarms.
		alarmparams = tuple([x.strip() for x in alarms.split(',') if len(x.strip()) > 0])
		if len(alarmparams) == 0:
			alarmparams = None

		query = HMIData.AlarmLogger.QueryAlarmHistory(starttime, endtime, starttimeok, endtimeok, 
									startcount, endcount, ackclient, alarmparams)
		query.addCallback(self._ContinueQuery, request)
		query.addErrback(self._QueryErr, request)

		return server.NOT_DONE_YET




	########################################################
	def render_POST(self, request):
		""" POST is not a valid request.
		"""
		return _ServiceError


############################################################

_ShowAlarmsQueryResponse = ShowAlarmsQueryResponse()



############################################################

def _HandleFileGet(request):
	"""Handle a request for a file.
	"""
	fpath = request.prepath[:][0]	# Extract file name as a string.

	# Look for the requested file.
	f, ctype, flength, ErrorStr = MBWebPage.GetWebPage(PageDir, fpath)

	# Send the reply.
	if f:
		# Send the headers.
		request.setHeader('content-type', ctype)
		# Send the page.
		# TODO: This is for Debian 5.0 compatibility. 
		StaticSend(f, flength, request)
		return server.NOT_DONE_YET


	# Didn't find it? Look for the requested file in the HMI library directory.
	f, ctype, flength, ErrorStr = MBWebPage.GetWebPage(HMILibDir, fpath)

	# Send the reply.
	if f:
		# Send the headers.
		request.setHeader('content-type', ctype)
		# Send the page.
		# TODO: This is for Debian 5.0 compatibility. 
		StaticSend(f, flength, request)
		return server.NOT_DONE_YET


	# Still didn't find it? Return an error.
	request.setResponseCode(404)
	return"""
	<html><head><title>404 - No Such Resource</title></head>
	<body><h1>No Such Resource</h1>
	<p>%s</p></body></html>
	""" % ErrorStr

############################################################



############################################################
class ShowHMIResponse(resource.Resource):
	"""Respond with the appropriate HMI protocol response. A GET should 
	return a file. A POST should use the MB-HMI protocol.
	"""

	isLeaf = True	# This is a resource end point.


	########################################################
	def render_GET(self, request):
		"""Return the page for a GET. This will handle requests
		to read data.
		"""
		return _HandleFileGet(request)


	########################################################
	def render_POST(self, request):
		""" Process a POST and return a response. This will handle
		all the AJAX read and write requests for data.
		"""

		# Update the server rate counter stats for reporting.
		HMIData.HMIStatus.IncRequestCounter()

		# Get the JSON data from the message.
		try:
			recvjson = request.received_headers['cascadas']
		except:
			# The data wasn't found in the headers.
			return HMIMsg.ServerErrorMessage()


		# Analyse the request and construct a response.
		# restricted = False, erpfilter = False
		respjson = HMIData._HandleMessage(recvjson, False, False)

		# Return the JSON response.
		return respjson


############################################################

_ShowHMIResponse = ShowHMIResponse()



############################################################
class ShowRestrictedHMIResponse(resource.Resource):
	"""Respond with the appropriate HMI protocol response. This is for the
	*restricted* HMI server. This allows read-only access to the HMI server.
	This is regulated by a flag which is passed to _HandleMessage.
	A GET should return a file. A POST should use the MB-HMI protocol.
	"""

	isLeaf = True	# This is a resource end point.


	########################################################
	def render_GET(self, request):
		"""Return the page for a GET. This will handle requests
		to read data.
		"""
		return _HandleFileGet(request)


	########################################################
	def render_POST(self, request):
		""" Process a POST and return a response. This will handle
		all the AJAX read and write requests for data.
		"""

		# Update the server rate counter stats for reporting.
		HMIData.RHMIStatus.IncRequestCounter()

		# Get the JSON data from the message.
		try:
			recvjson = request.received_headers['cascadas']
		except:
			# The data wasn't found in the headers.
			return HMIMsg.ServerErrorMessage()


		# Analyse the request and construct a response.
		# restricted = True, erpfilter = False
		respjson = HMIData._HandleMessage(recvjson, True, False)

		# Return the JSON response.
		return respjson


############################################################

_ShowRestrictedHMIResponse = ShowRestrictedHMIResponse()



############################################################
class ShowERPResponse(resource.Resource):
	"""Respond with the appropriate ERP HMI protocol response. This is for the
	*ERP* HMI server. This allows read-write access to the HMI server, but 
	excludes alarms and events, and also filters the tag list.
	GET is not allowed. A POST should use the MB-HMI protocol.
	"""

	isLeaf = True	# This is a resource end point.


	########################################################
	def render_GET(self, request):
		"""GET will result in an error.
		"""

		# Get the current configuration.
		hmiconfig = HMIData.Msg.GetCurrentHMIInfo()
		erpconfig = hmiconfig.GetERPConfig()
		readtags = erpconfig['read']
		writetags = erpconfig['write']

		serverid = hmiconfig.GetServerID()
		clientversion = hmiconfig.GetClientVersion()

		# Get the current values of the tags.
		alltags = readtags[:]
		alltags.extend(writetags)
		tagslist = list(set(alltags))
		readtagsresult, readtagserrors = HMIData.Msg.HMIData.ReadDataTable(tagslist)
		tagtable = map(lambda (x,y): '<tr><td>%s</td><td>%s</td></tr>' % (x,y), readtagsresult.items())


		# HTML web page.
		webstring = """
<html><head>
<title>%(serverid)s</title>
</head>
<body>
<h1>ERP Tag List</h1>
<h2>Server ID</h2>
<p>%(serverid)s</p>
<h2>Client Version</h2>
<p>%(clientversion)s</p>
<h2>Tags Available for Reading:</h2>
<p>%(readtags)s</p>
<h2>Tags Available for Writing:</h2>
<p>%(writetags)s</p>
<h2>Present Values:</h2>
<table  border="1">
<tr> <th>Tag</th> <th>Value</th> </tr>
%(tagtable)s
</table>
</body></html>
"""

		# This must be explicitely forced to type string to avoid errors in 
		# Twisted. This HTML will under some combinations of effects sometimes
		# get turned into unicode, which Twisted does not seem to like.
		msg = str(webstring % {'serverid' : serverid, 'clientversion' : clientversion,
				'readtags' : ', '.join(readtags),  'tagtable' : '\n'.join(tagtable),
				'writetags' : ', '.join(writetags)})

		return msg


	########################################################
	def render_POST(self, request):
		""" Process a POST and return a response. This will handle
		all the AJAX read and write requests for data.
		"""

		# Update the server rate counter stats for reporting.
		HMIData.ERPStatus.IncRequestCounter()

		# Get the JSON data from the content.
		recvjson = request.content.read()

		# No data?
		if len(recvjson) == 0:
			return HMIMsg.ServerErrorMessage()


		# Analyse the request and construct a response.
		# restricted = False, erpfilter = True
		respjson = HMIData._HandleMessage(recvjson, False, True)

		# Return the JSON response.
		return respjson


############################################################

_ShowERPResponse = ShowERPResponse()



############################################################

class AEQService(resource.Resource):
	"""Alarm history and event query web service.
	"""

	########################################################
	#
	def getChild(self, name, request):
		"""This is called by Twisted to handle the URL decoding
		and route the request to the appropriate destination.
		"""

		# Get the URL path.
		self._path = request.prepath[:]
		if (request.postpath != []):
			self._path.extend(request.postpath[:])

		# Is this an alarms query?
		if request.prepath[-1] == 'alarmhist':
			return _ShowAlarmsQueryResponse

		# Is this an events query?
		elif request.prepath[-1] == 'events':
			return _ShowEventsQueryResponse

		# Anything else must be in the site root directory.
		else:
			_ServiceError.SetErrorMsg('Invalid path in URL: %s' % self._path)
			return _ServiceError



############################################################

_AEQService = AEQService()

############################################################

class MBHMIService(resource.Resource):
	"""Implement an HMI web service protocol.
	"""

	########################################################
	#
	def getChild(self, name, request):
		"""This is called by Twisted to handle the URL decoding
		and route the request to the appropriate destination.
		"""

		# Get the URL path.
		self._path = request.prepath[:]
		if (request.postpath != []):
			self._path.extend(request.postpath[:])

		# Is this an RSS feed?
		if request.prepath[0] == 'rss':
			return _ShowRSSResponse

		# Is this an alarm / event data query?
		elif request.prepath[0] == 'aequery':
			return _AEQService

		# Anything else must be in the site root directory.
		elif (len(self._path) != 1):
			_ServiceError.SetErrorMsg('Invalid path in URL: %s' % self._path)
			return _ServiceError

		# Point to the class which displays the web service results.
		return _ShowHMIResponse




############################################################

class MBHMIRestrictedService(resource.Resource):
	"""Implement an HMI web service protocol for read-only access.
	"""

	########################################################
	#
	def getChild(self, name, request):
		"""This is called by Twisted to handle the URL decoding
		and route the request to the appropriate destination.
		"""

		# Get the URL path.
		self._path = request.prepath[:]
		if (request.postpath != []):
			self._path.extend(request.postpath[:])

		# Is this an RSS feed?
		if request.prepath[0] == 'rss':
			return _ShowRSSResponse

		# Is this an alarm / event data query?
		elif request.prepath[0] == 'aequery':
			return _AEQService

		# Check if the path is too long or too short.
		elif (len(self._path) != 1):
			_ServiceError.SetErrorMsg('Invalid path in URL: %s' % self._path)
			return _ServiceError

		# Point to the class which displays the web service results.
		return _ShowRestrictedHMIResponse



############################################################

class MBHMIERPService(resource.Resource):
	"""Implement an HMI web service protocol for ERP systems.
	"""

	########################################################
	#
	def getChild(self, name, request):
		"""This is called by Twisted to handle the URL decoding
		and route the request to the appropriate destination.
		"""

		# Get the URL path.
		self._path = request.prepath[:]
		if (request.postpath != []):
			self._path.extend(request.postpath[:])

		# Check if the path is too long or too short.
		if (len(self._path) != 1):
			_ServiceError.SetErrorMsg('Invalid path in URL: %s' % self._path)
			return _ServiceError

		# Point to the class which displays the web service results.
		return _ShowERPResponse



##############################################################################


