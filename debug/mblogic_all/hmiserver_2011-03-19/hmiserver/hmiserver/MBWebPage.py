##############################################################################
# Project: 	mbserver
# Module: 	MBWebPage.py
# Purpose: 	Modbus Web Service Server.
# Language:	Python 2.5
# Date:		30-Apr-2008.
# Version:	25-Jan-2009.
# Author:	M. Griffin.
# Copyright:	2008 - 2009 - Michael Griffin       <m.os.griffin@gmail.com>
#
# This file is part of MBServer.
# MBServer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# MBServer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with MBServer. If not, see <http://www.gnu.org/licenses/>.
#
# Important:	WHEN EDITING THIS FILE, USE TABS TO INDENT - NOT SPACES!
##############################################################################
"""
Used to read in HTML pages for use by a web server.

Public objects: GetWebPage

"""
import mimetypes
import os
import posixpath


########################################################
def _ContentType(requestedfile):
	"""
	Guess the file type based on the extension. This will be used 
	to decide whether to open the file in text or binary mode.
	"""

	base, ext = posixpath.splitext(requestedfile)

	# This uses the standard MIME types mapping library. If it isn't 
	# found, we check to see if it is xhtml (which might not be in the
	# local mime types library). If the type still is not found, it 
	# defaults to plain text.
	mimetypes.init()
	try:
		ctype = mimetypes.types_map[ext]
	except:
		if (ext.lower() == '.xhtml'):
			ctype = 'application/xhtml+xml'
		else:
			ctype = 'text/plain'

	# We need to augment this information with a set of image
	# types to use for the file mode.
	if (ext in ['.png', '.PNG', '.gif', '.GIF', '.jpeg', '.JPEG', 
		'.jpg', '.JPG']):
		fmode = 'rb'
	else:
		fmode = 'r'

	return fmode, ctype


########################################################
def GetWebPage(siteroot, path):
	"""Parameters:
	siteroot (string) = The path to the directory containing the web pages.
	path (string) = The web page file name.
	Look for the requested file, and return it.
	Returns: f, ctype, flength, ftime, ferror
	f = File-like object. Returns none if error.
	ctype = MIME type of file. Returns empty string if error.
	flength = file length string. Returns empty string if error.
	ftime = file modification time. Returns empty string if error.
	ferror = Error string. Empty string if no error.
	"""

	# Check if requested file exists.
	requestedfile = os.path.join(siteroot, path)

	if not os.path.isfile(requestedfile):
		return None, '', '', '', 'File not found: %s - No such file.' % requestedfile
     
	# Guess the file mode and content type based on the file extension.
	# This probably needs to be tied into a proper library.
	fmode, ctype = _ContentType(requestedfile)

	# Now try to open the file.
        f = None
	try:
		f = open(requestedfile, fmode)
	except IOError:
		return None, '', '', '', 'File not found: %s - Could not open file.' % requestedfile


	# Get the length of the file.
	fs = os.fstat(f.fileno())
	flength = int(fs[6])
	ftime = fs.st_mtime

	# Return the requested file, as well as its type and length.
	return f, ctype, flength, ftime, ''

##############################################################################

