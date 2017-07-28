#!/usr/bin/python
##############################################################################
# Project: 	MBLogic
# Module: 	helpserver.py
# Purpose: 	Serve HTMP help web pages.
# Language:	Python 2.5
# Date:		11-Feb-2011.
# Version:	11-Feb-2011.
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


import SimpleHTTPServer
import SocketServer
import os

"""
Web server for help files.
"""
##############################################################################

def _request_report(ref, result):
	"""This is just used to enable silencing the routine 
	connection logging.
	"""
	pass

# Change into the help file directory. 
os.chdir('helpfiles')

PORT = 8880
Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

# Silence the log messages.
Handler.log_request = _request_report

httpd = SocketServer.TCPServer(("", PORT), Handler)

# Start the server.
httpd.serve_forever()

##############################################################################

