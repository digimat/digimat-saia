##############################################################################
# Project: 	MBLogic
# Module: 	MBFileServices.py
# Purpose: 	File I/O services.
# Language:	Python 2.5
# Date:		02-Oct-2010.
# Version:	25-Nov-2010.
# Author:	M. Griffin.
# Copyright:	2010 - Michael Griffin       <m.os.griffin@gmail.com>
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
This handles common file I/O services such as saving configuration files.
"""
############################################################

import os 
import time

############################################################

def FormatErr(errorcode, filename):
	"""Return an error message associated with the requested error code.
	The specified file name will embedded in the message before being returned.
	Parameters: errorcode (string) = The error code.
		filename (string) = The name of the configuration file. The 
		'temp' or 'back' extensions will be automatically appended as 
		appropriate.
	Returns: (string) = The corresponding error message.
	"""

	ConfigFileErrMsgs = {
	'baderasebackup' : 'Config file error when erasing the old backup file: %s.back.',
	'badtempfileopen' : 'Config file error when opening the new temporary file: %s.temp.',
	'badfilesave' : 'Config file error when writing to the new temporary file: %s.temp.',
	'badoldfilerename' : 'Config file error when renaming the old file to the back up name: %s.back.',
	'badnewfilerename' : 'Config file error when renaming the temporary file to the configuration file name: %s.'
	}

	return ConfigFileErrMsgs[errorcode] % filename


############################################################
def SaveConfigFile(filename, parser, headermessage):
	"""Save a configuration file. This is performed as follows:
	1) Remove the current backup file.
	2) Save the data to a temporary file ("filename.temp"). This replaces 
		any existing temporary file.
	3) Rename the current file to the backup name ("filename.back").
	4) Rename the temporary file to the specified file name.
	This process does not do an atomic rename because this feature is not
	supported in MS Windows.

	Parameters: filename (string) = The configuration file name.
		parser (object) = The ConfigParser object containing the configuration.
		headermessage (string) = This is inserted into the file header message
			which is automatically added to the beginning of each file. This
			should be a short text string indicating the type of configuration
			(e.g. 'HMI')
	Returns: (string) = An error code, or 'ok' if no errors. The error codes are:
		baderasebackup - Error when erasing the old backup file.
		badtempfileopen - Error when opening the new temporary file.
		badfilesave - Error when writing to the new temporary file.
		badoldfilerename - Error when renaming the old file to the back up name.
		badnewfilerename - Error when renaming the temporary file to the configuration file name.
	"""

	fileheader = '# %s configuration file. Auto-generated on %s\n\n' % (headermessage, time.ctime())

	tempfilename = filename + '.temp'
	backupfilename = filename + '.back'

	# Save the file.
	# Remove the old backup file. The file may not exist, so
	# we have to be prepared to skipt this step.
	if os.path.exists(backupfilename):
		try:
			# First, remove any existing backup file.
			os.remove(backupfilename)
		except:
			return 'baderasebackup'

	# Open the new output file with a temporary name. This should
	# also remove any existing temporary file.
	try:
		outfile = open(tempfilename, 'w')
	except:
		return 'badtempfileopen'


	# Write out the new parser file to the temporary name.
	try:
		# We also write out a header with a descriptive comment. 
		outfile.write(fileheader)
		# Then the parser data.
		parser.write(outfile)
		outfile.flush()
		os.fsync(outfile.fileno())
		outfile.close()
	except:
		return 'badfilesave'

	# Rename the existing file (if it exists) to the backup name.
	if os.path.exists(filename):
		try:
			os.rename(filename, backupfilename)
		except:
			return 'badoldfilerename'

	# Rename the temporary file to the proper file name.
	try:
		os.rename(tempfilename, filename)
	except:
		return 'badnewfilerename'


	return 'ok'


############################################################
def ListHMIFiles(pagdir):
	"""Read a list of HTML and XHTML files in the HMI directory and
	store them for later display.
	Parameters: pagdir (string) = Name of HMI directory.
	"""
	# Get a list of all the files, and split them into name and extenstion.
	allfiles = map(os.path.splitext, os.listdir(pagdir))
	# Filter out all files which are not HTML or XHTML.
	webpages = filter(lambda y: y[1].lower() in ('.html','.xhtml'), allfiles)
	# Reassemble the file names back together.
	return map(lambda (fname, ext): '%s%s' % (fname, ext), webpages)


############################################################
def ReadFile(filepath):
	"""Read a file from disk and return the contents as a list of strings.
	Parameters: filepath (string) = Name of file (including path).
	Returns (list) = List of strings. The list is empty if the file was
		not found (it may not have been created by the user).
	"""
	# Open the input file as read-only.
	try:
		infile = open(filepath, 'r')
		content = infile.readlines()
	except:
		return None
	finally:
		infile.close()

	return content


##############################################################################

