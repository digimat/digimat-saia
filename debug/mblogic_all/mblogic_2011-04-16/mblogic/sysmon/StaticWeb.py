##############################################################################
# Project: 	MBLogic
# Module: 	StaticWeb.py
# Purpose: 	Returns static web content.
# Language:	Python 2.5
# Date:		25-Apr-2008.
# Version:	19-Jul-2010.
# Author:	M. Griffin.
# Copyright:	2008 - 2010 - Michael Griffin       <m.os.griffin@gmail.com>
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
"""

############################################################

import os

from twisted.web import server, resource, static

import MBWebPage

############################################################
# TODO: This is for Debian 5.0 compatibility. 
# This is a temporary measure for use in supporting older versions of 
# Twisted on Debian Stable. 
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


# Root directory for the web server.
StatusRoot = os.path.join('mblogic', 'mbstatuspages')

########################################################
def SendStaticFile(request):
	"""This is used to send a static file. 
	Parameters: request (object) = A Twisted request object.
	Return: Returns a file object or error string. 
	"""
	# Get the file path.
	fplist = []
	fplist.extend(request.prepath[:])
	fplist.extend(request.postpath[:])

	# Combine the list into a single string.
	fpath = reduce(os.path.join, fplist)

	# Look for the requested file.
	f, ctype, flength, ErrorStr = MBWebPage.GetWebPage(StatusRoot, fpath)

	# Send the reply.
	if f:
		# Send the headers.
		request.setHeader('content-type', ctype)
		# Send the page.
		# TODO: This is for Debian 5.0 compatibility. 
		StaticSend(f, flength, request)
		return server.NOT_DONE_YET
	else:
		request.setResponseCode(404)
		return"""
		<html><head><title>404 - No Such Resource</title></head>
		<body><h1>No Such Resource</h1>
		<p>%s</p></body></html>
		""" % ErrorStr


############################################################
class ServiceError(resource.Resource):
	""" Display an error message when attempting to access a
	resource which does not exist.
	"""

	isLeaf = True


	########################################################
	def SetServiceError(self, MessageText):
		""" Set the message to be used when displaying an error condition.
		"""
		# HTML portion of error message.
		self._ErrorStr = """
		<html><head><title>404 - No Such Resource</title></head>
			<body><h1>No Such Resource</h1>
			<p>%s</p></body></html>
		""" % MessageText

	########################################################
	def render(self, request):
		""" This is called by Twisted to handle GET calls.
		"""
		request.setResponseCode(404)
		self._ErrorStr = """
		<html><head><title>404 - No Such Resource</title></head>
			<body><h1>No Such Resource</h1>
			<p></p></body></html>
		"""
		return self._ErrorStr

############################################################

# Create the service error object.
ServiceError = ServiceError()


############################################################
class StaticContent(resource.Resource):
	"""Serve static content such as css, images, etc. This handles any
	content which isn't programmed to be handled by the template system.
	"""

	isLeaf = True	# This is a resource end point.


	########################################################
	# Return the page for a GET. This will handle requests
	# to read data.
	def render_GET(self, request):

		# Get the file path.
		fplist = []
		fplist.extend(request.prepath[:])
		fplist.extend(request.postpath[:])

		# Combine the list into a single string.
		fpath = reduce(os.path.join, fplist)

		# Look for the requested file.
		f, ctype, flength, ErrorStr = MBWebPage.GetWebPage(StatusRoot, fpath)

		# Send the reply.
		if f:
			# Send the headers.
			request.setHeader('content-type', ctype)
			# Send the page.
			# TODO: This is for Debian 5.0 compatibility. 
			StaticSend(f, flength, request)
			return server.NOT_DONE_YET
		else:
			request.setResponseCode(404)
			return"""
			<html><head><title>404 - No Such Resource</title></head>
			<body><h1>No Such Resource</h1>
			<p>%s</p></body></html>
			""" % ErrorStr


	########################################################
	def render_POST(self, request):
		""" Process a POST and return a response. This will handle
		requests to write data.
		"""

		# Return the results.
		return """<HTML>No POST at this time.</HTML>"""

############################################################

# Create a response object.
StaticResponse = StaticContent()



