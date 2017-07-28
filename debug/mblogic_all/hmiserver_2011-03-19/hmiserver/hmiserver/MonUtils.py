##############################################################################
# Project: 	MBLogic
# Module: 	MonUtils.py
# Purpose: 	General monitoring utilities.
# Language:	Python 2.5
# Date:		05-Jun-2010.
# Ver.:		05-Jun-2010.
# Copyright:	2010 - Michael Griffin       <m.os.griffin@gmail.com>
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

"""
General utility routines.
"""
############################################################

import hashlib

_jsonerrmsg = """\nWarning - The optimised standard library was not found. 
A pure Python version is being imported instead.\n
"""

try:
	import json
except:
	print(_jsonerrmsg)
	import mbprotocols.py_simplejson as json

############################################################
def CalcFileSig(filename):
	"""Calculate the signature of a file. Returns None if error.
	"""

	# Read in the configuration file as a block so we can calculate a hash signature.
	f = open(filename, 'r')
	if f:
		configdata = f.read(-1)
		f.close()
		confighash = hashlib.md5()
		confighash.update(configdata)
		return confighash.hexdigest()
	else:
		return None


############################################################
def CalcSig(sigdata):
	"""Calculate the signature of a block of text This expects the actual
	data and does not read in a file. Returns None if error.
	"""
	confighash = hashlib.md5()
	confighash.update(sigdata)
	return confighash.hexdigest()

############################################################
def JSONEncode(pydata):
	"""Encode data as JSON. This is done here to allow us to substitute a
	different JSON library in the event that the standard library version
	is not present. This allows for compatibility with Python versions 
	older than 2.6. 
	"""
	return json.dumps(pydata)


############################################################
def JSONDecode(jdata):
	"""Dencode JSON data. This is done here to allow us to substitute a
	different JSON library in the event that the standard library version
	is not present. This allows for compatibility with Python versions 
	older than 2.6. 
	"""
	return json.loads(jdata)

##############################################################################


