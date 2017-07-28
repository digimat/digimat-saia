##############################################################################
# Project: 	MBLogic
# Module: 	PLCStdMem.py
# Purpose: 	Standard PLC memory structures.
# Language:	Python 2.5
# Date:		26-May-2008.
# Ver:		07-Feb-2009
# Author:	M. Griffin.
# Copyright:	2008 - 2009 - Michael Griffin   <m.os.griffin@gmail.com>
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



########################################################

"""
	The following are functions used to create data tables. Each data table 
	is a dictionary holding a single type of data. The dictionary key is the
	address label, and the values are the data table values. 
	Boolean (bit) values are stored in the boolean data table, and word
	values are to be stored in the word table. Special functions will provide
	the means to combine groups of booleans into words, or split words into
	groups of booleans.
"""


########################################################
def GenOctalAddr(start, maxaddr, addrprefix):
	"""Generate a list of PLC octal addresses with an optional prefix.
	start (integer) = start address.
	maxaddr (integer) = maximum value (in decimal).
	addrprefix (string) = characters to use to prefix address (use '' for none).
	"""
	addrstr = addrprefix + '%o'
	return [addrstr % i for i in range(start, maxaddr + 1)]

########################################################
def GenDecimalAddr(start, maxaddr, addrprefix):
	"""Generate a list of PLC decimal addresses with an optional prefix.
	start (integer) = start address.
	maxaddr (integer) = maximum value (in decimal).
	addrprefix (string) = characters to use to prefix address (use '' for none).
	"""
	addrstr = addrprefix + '%d'
	return [addrstr % i for i in range(start, maxaddr + 1)]

########################################################
def GenIECBitAddr(start, maxaddr, addrprefix):
	"""Generate a list of PLC IEC bit addresses with an optional prefix.
	start (integer) = start address.
	maxaddr (integer) = maximum value (in decimal).
	addrprefix (string) = characters to use to prefix address (use '' for none).
	"""
	addrlist = []
	for i in range (start, maxaddr + 1):
		for j in range (8):
			addrlist.append('%s%d.%o' % (addrprefix, i, j))
	return addrlist

########################################################


########################################################
def GenBoolTable(addrlist):
	"""Convert a list of addresses into a dictionary of boolean addresses. The 
	address list provides the keys, and all values are initialised to False.
	addrlist (list) = A list of address keys.
	"""
	return {}.fromkeys(addrlist, False)


########################################################
def GenWordTable(addrlist, initval):
	"""Convert a list of addresses into a dictionary of word addresses. The 
	address list provides the keys, and all values are initialised to 0.
	addrlist (list) = A list of address keys.
	initval (any type) = The value with which to initialise the table.
	"""
	return {}.fromkeys(addrlist, initval)

########################################################
def GenTableIndex(addrlist):
	"""Generate a dictionary that relates the address label to the original address
	list index. This is used to quickly find the start of a sequence of address
	labels in a list for operations where a consecutive series of addresses
	must be found. A linear search is too slow to look up addresses on the list directly. 
	addrlist (list) = The list of address lables in the order as used by 
		the original address list.
	Returns (dict) = A dictionary where the keys are address lables and the
		values are integer list indexes.
	"""
	addrindex = {}
	for i in range(len(addrlist)):
		addrindex[addrlist[i]] = i
	return addrindex

########################################################

