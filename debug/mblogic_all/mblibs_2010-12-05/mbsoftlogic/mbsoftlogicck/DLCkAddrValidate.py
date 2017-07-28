##############################################################################
# Project: 	MBLogic
# Module: 	DLCkAddrValidate.py
# Purpose: 	Define address validators for a Click-like PLC.
# Language:	Python 2.5
# Date:		31-Oct-2007.
# Ver:		23-Aug-2010.
# Author:	M. Griffin.
# Copyright:	2008 - 2010 - Michael Griffin   <m.os.griffin@gmail.com>
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
This module defines the address validator functions for the compiler 
for a DL Click-like PLC. This needs to be customised for each model of PLC being 
emulated.
"""

############################################################

import re

import DLCkDataTable

##############################################################################

# These are the error messages to be passed to the compiler.
ValErrorMsgs = {
'missingparam' : 'One or more expected parameters is missing.',
'invaliddestreg' : 'The destination register type is invalid.',
'invaliddestaddr' : 'The destination register address is invalid.',
'invalidoneshot' : 'The one-shot parameter is invalid.',
'invalidtype' : 'One or more parameters is of an incorrect type.',
'invalidrange' : 'A pair of range parameters are incorrect.',
'incompatible' : 'A set of parameters are incompatible with each other.',
'notexpected' : 'A parameter was present where none was expected.'
}

##############################################################################


# This is used as an accessor function for the word validators.
_PLCWordTable = "PLC_DataWord['%s']"

# This is used to get strings from text registers.
_RegStrings = "PLC_WordAccessors.GetRegString('%s', '%s')"

##############################################################################


# 1) Address format validators
# Define a series of regular expressions to validate the parameters.
# Each string defines the range for one type of address.
# These are for the basic individual types.

## Bit parameters.
_X = 'X[1-9]$|X[1-9][0-9]$|X[1-9][0-9]{2}$|X1[0-9]{3}$|X2000$'		# X1 to X2000
_Y = 'Y[1-9]$|Y[1-9][0-9]$|Y[1-9][0-9]{2}$|Y1[0-9]{3}$|Y2000$'		# Y1 to Y2000
_C = 'C[1-9]$|C[1-9][0-9]$|C[1-9][0-9]{2}$|C1[0-9]{3}$|C2000$'		# C1 to C2000
_T = 'T[1-9]$|T[1-9][0-9]$|T[1-4][0-9]{2}$|T500'			# T1 to T500
_CT = 'CT[1-9]$|CT[1-9][0-9]$|CT1[0-9]{2}$|CT2[0-4][0-9]$|CT250$'	# CT1 to CT250
_SC = 'SC[1-9]$|SC[1-9][0-9]$|SC[1-9][0-9]{2}$|SC1000$'			# SC1 to SC1000

# Word parameters.
_XD = 'XD[1-9]$|XD[1-9][0-9]$|XD1[0-1][0-9]$|XD12[0-5]$'		# XD1 to XD125
_YD = 'YD[1-9]$|YD[1-9][0-9]$|YD1[0-1][0-9]$|YD12[0-5]$'		# YD1 to YD125
_DS = 'DS[1-9]$|DS[1-9][0-9]$|DS[1-9][0-9]{2}$|DS[1-9][0-9]{3}$|DS10000$'	# DS1 to DS10000
_DD = 'DD[1-9]$|DD[1-9][0-9]$|DD[1-9][0-9]{2}$|DD1[0-9]{3}$|DD2000$'	# DD1 to DD2000
_DH = 'DH[1-9]$|DH[1-9][0-9]$|DH[1-9][0-9]{2}$|DH1[0-9]{3}$|DH2000$'	# DH1 to DH2000
_DF = 'DF[1-9]$|DF[1-9][0-9]$|DF[1-9][0-9]{2}$|DF1[0-9]{3}$|DF2000$'	# DF1 to DF2000
_TD = 'TD[1-9]$|TD[1-9][0-9]$|TD[1-4][0-9]{2}$|TD500'			# TD1 to TD500
_CTD = 'CTD[1-9]$|CTD[1-9][0-9]$|CTD1[0-9]{2}$|CTD2[0-4][0-9]$|CTD250$'	# CTD1 to CTD250
_SD = 'SD[1-9]$|SD[1-9][0-9]$|SD[1-9][0-9]{2}$|SD1000$'			# SD1 to SD1000
_TXT = 'TXT[1-9]$|TXT[1-9][0-9]$|TXT[1-9][0-9]{2}$|TXT[1-9][0-9]{3}$|TXT10000$'	# TXT1 to TXT10000

# These are an address extension in addition to XD and YD.
_XS = 'XS[1-9]$|XS[1-9][0-9]$|XS1[0-1][0-9]$|XS12[0-5]$'		# XS1 to XS125
_YS = 'YS[1-9]$|YS[1-9][0-9]$|YS1[0-1][0-9]$|YS12[0-5]$'		# YS1 to YS125

# Pointers. E.g. DD[DS1]
_DSPtr = 'DS\[DS[1-9]\]$|DS\[DS[1-9][0-9]\]$|DS\[DS[1-9][0-9]{2}\]$|DS\[DS[1-9][0-9]{3}\]$|DS\[DS10000\]$'
_DDPtr = 'DD\[DS[1-9]\]$|DD\[DS[1-9][0-9]\]$|DD\[DS[1-9][0-9]{2}\]$|DD\[DS[1-9][0-9]{3}\]$|DD\[DS10000\]$'
_DFPtr = 'DF\[DS[1-9]\]$|DF\[DS[1-9][0-9]\]$|DF\[DS[1-9][0-9]{2}\]$|DF\[DS[1-9][0-9]{3}\]$|DF\[DS10000\]$'
_DHPtr = 'DH\[DS[1-9]\]$|DH\[DS[1-9][0-9]\]$|DH\[DS[1-9][0-9]{2}\]$|DH\[DS[1-9][0-9]{3}\]$|DH\[DS10000\]$'


# Constants.
# Signed integer.
_KInt = """[+-]?[0-9]{1,4}$|[+-]?[0-2][0-9]{4}$|[+-]?3[0-1][0-9]{3}$|
[+-]?32[0-6][0-9]{2}$|[+-]?327[0-5][0-9]$|[+-]?3276[0-7]$|-32768$"""

# Positive signed integer.
_KIntPlus = """[+]?[0-9]{1,4}$|[+]?[0-2][0-9]{4}$|[+]?3[0-1][0-9]{3}$|
[+]?32[0-6][0-9]{2}$|[+]?327[0-5][0-9]$|[+]?3276[0-7]$|-32768$"""

# Unsigned hexadecimal integer.
_KHex = '[0-9a-fA-F]{1,4}h$'

# Signed double integer.
_KDInt = """[+-]?[0-1]?[0-9]{1,9}$|[+-]?20[0-9]{8}$|
[+-]?21[0-3][0-9]{7}$|[+-]?214[0-6][0-9]{6}$|[+-]?2147[0-3][0-9]{5}$|
[+-]?21474[0-7][0-9]{4}$|[+-]?214748[0-2][0-9]{3}$|[+-]?2147483[0-5][0-9]{2}$|
[+-]?21474836[0-3][0-9]$|[+-]?214748364[0-7]$|-2147483648$"""

# Floating point. The maximum is 1.9e307
_KF = '[+-]?[0-9]{1,37}\.[0-9]{1,37}$|[+-]?[0-9]\.[0-9]{1,37}[Ee][+-]([0-2]?[0-9]?[0-9]|30[0-7])$'

# Base definition for text constants.
_KTxtBase = '[0-9a-zA-Z\`\~\!\@\#\$\%\^\&\*\(\)\_\-\+\=\[\]\{\}\\\|\;\:\<\>\,\.\/\?]'
# String of 7 bit visible ASCII characters.
_KTxtStr = '"%s%s+"' % (_KTxtBase, _KTxtBase)
# Single character of 7 bit visible ASCII.
_KTxtChar = '"%s"' % _KTxtBase

# Time base for timers.
_KTimeBase = 'ms$|sec$|min$|hour$|day$'

# Subroutine name.
_Subroutine = '[a-zA-Z][a-zA-Z0-9]{0,23}$'


## 

### Bit address for X
Re_X = re.compile('%s' % _X)

### Bit address for Y
Re_Y = re.compile('%s' % _Y)

### Bit address for C
Re_C = re.compile('%s' % _C)

### Bit address for T
Re_T = re.compile('%s' % _T)

### Bit address for CT
Re_CT = re.compile('%s' % _CT)

### Bit address for SC
Re_SC = re.compile('%s' % _SC)

### Bit address for X, Y, C, T, CT, or SC.
Re_X_Y_C_T_CT_SC = re.compile('%s|%s|%s|%s|%s|%s' % (_X, _Y, _C, _T, _CT, _SC))

### Bit address for Y or C.
Re_Y_C = re.compile('%s|%s' % (_Y, _C))

### Bit address for Y, C or SC.
Re_Y_C_SC = re.compile('%s|%s|%s' % (_Y, _C, _SC))

### Bit address for CT. Also used to check counter numbers.
Re_CT = re.compile('%s' % _CT)

### Bit address for T. Also used to check timer numbers.
Re_T = re.compile('%s' % _T)


### Word address for XD.
Re_XD = re.compile(_XD)

### Word address for YD.
Re_YD = re.compile(_YD)

### Word address for XS.
Re_XS = re.compile(_XS)

### Word address for YS.
Re_YS = re.compile(_YS)

### Word address for DS.
Re_DS = re.compile(_DS)

### Word address for DD.
Re_DD = re.compile(_DD)

### Word address for DF.
Re_DF = re.compile(_DF)

### Word address for DH.
Re_DH = re.compile(_DH)

### Word address for TD.
Re_TD = re.compile(_TD)

### Word address for CTD.
Re_CTD = re.compile(_CTD)

### Word address for SD.
Re_SD = re.compile(_SD)

### Word address for TXT.
Re_TXT = re.compile(_TXT)

###

### Integer constant.
Re_KInt = re.compile(_KInt)

### Positive integer constant.
Re_KIntPlus = re.compile(_KIntPlus)

### Double integer constant.
Re_KDInt = re.compile(_KDInt)

### Floating point constant.
Re_KF = re.compile(_KF)

### Hex constant.
Re_KHex = re.compile(_KHex)

### Text string constant.
Re_KTxtStr = re.compile(_KTxtStr)

### Text character constant.
Re_KTxtChar = re.compile(_KTxtChar)

###

### Timer time base.
Re_KTimeBase = re.compile(_KTimeBase)

### Subroutine name.
Re_Subroutine = re.compile(_Subroutine)

###

### DS pointer address.
Re_DSPtr = re.compile(_DSPtr)

### DD pointer address.
Re_DDPtr = re.compile(_DDPtr)

### DF pointer address.
Re_DFPtr = re.compile(_DFPtr)

### DH pointer address.
Re_DHPtr = re.compile(_DHPtr)


############################################################
# Word parameters require more checking as not all data types are
# compatible with each other. In addition, some are constants rather
# than actual addresses.


#####################
# Doesn't catch pointers or constants!
_RegMatch = {
'DS' : (Re_DS, 'DS'),
'DD' : (Re_DD, 'DD'),
'DF' : (Re_DF, 'DF'),
'DH' : (Re_DH, 'DH'),
'TD' : (Re_TD, 'TD'),
'CT' : (Re_CTD, 'CTD'),
'SD' : (Re_SD, 'SD'),
'XD' : (Re_XD, 'XD'),
'YD' : (Re_YD, 'YD'),
'XS' : (Re_XS, 'XS'),
'YS' : (Re_YS, 'YS'),
'TX' : (Re_TXT, 'TXT')
}

def WordParamType(param):
	"""Compare a parameter, and see if it matches a known word type. 
	It also verifies the address range.
	param (string) = The parameter to be checked.
	Returns (string) = A code indicating the address type, or None if no 
		matches are found.
	"""

	# First see if it is a register type we recognise from the first two 
	# characters. If it is, we can take a short cut to reduce the number of
	# compares required to find a match.
	try:
		prefix = param[0:2]
		if (_RegMatch[prefix][0].match(param) != None):
			return _RegMatch[prefix][1]
	except:
		# If we didn't find a match, we fall back to searching for a 
		# match by comparing one at a time. 
		pass

	# Next, try constants and pointers using normal if/elif tests.
	if (Re_DS.match(param) != None):
		return 'DS'
	elif (Re_DD.match(param) != None):
		return 'DD'
	elif (Re_DF.match(param) != None):
		return 'DF'
	elif (Re_DH.match(param) != None):
		return 'DH'
	elif (Re_TD.match(param) != None):
		return 'TD'
	elif (Re_CTD.match(param) != None):
		return 'CTD'
	elif (Re_SD.match(param) != None):
		return 'SD'
	elif (Re_XD.match(param) != None):
		return 'XD'
	elif (Re_YD.match(param) != None):
		return 'YD'
	elif (Re_XS.match(param) != None):
		return 'XS'
	elif (Re_YS.match(param) != None):
		return 'YS'
	elif (Re_TXT.match(param) != None):
		return 'TXT'
	elif (Re_KInt.match(param) != None):
		return 'KInt'
	elif (Re_KDInt.match(param) != None):
		return 'KDInt'
	elif (Re_KF.match(param) != None):
		return 'KF'
	elif (Re_KHex.match(param) != None):
		return 'KHex'
	elif (Re_KTxtStr.match(param) != None):
		return 'KTxtStr'
	elif (Re_KTxtChar.match(param) != None):
		return 'KTxtChar'
	elif (Re_DSPtr.match(param) != None):
		return 'DSPtr'
	elif (Re_DDPtr.match(param) != None):
		return 'DDPtr'
	elif (Re_DFPtr.match(param) != None):
		return 'DFPtr'
	elif (Re_DHPtr.match(param) != None):
		return 'DHPtr'
	else:
		return None


#####################
# We don't include 'CT' because it conflicts with 'C'.
_BoolMatch = {
'X' : (Re_X, 'X'),
'Y' : (Re_Y, 'Y'),
'C' : (Re_C, 'C'),
'T' : (Re_T, 'T'),
'S' : (Re_SC, 'SC')
}

def BoolParamType(param):
	"""Compare a parameter, and see if it matches a known boolean type. 
	It also verifies the address range.
	param (string) = The parameter to be checked.
	Returns (string) = A code indicating the address type, or None if no 
		matches are found.
	"""
	# Get the first character of the address to narrow down the type.
	# This is used to reduce the number of compares required to find a match.
	try:
		prefix = param[0]
	except:
		return None


	# First see if it is a boolean type we recognise. If it is,
	# we can take a short cut.
	try:
		if (_BoolMatch[prefix][0].match(param) != None):
			return _BoolMatch[prefix][1]
	except:
		pass

	# Now, see if it was a counter ('CT') type. 
	# This collides with internal coils 'C'.
	if (Re_CT.match(param) != None):
		return 'CT'
	else:
		 return None


############################################################

# This defines the valid data ranges for different data types.
# key : (min value, max value) For char, this is min and max string length.
_DataRanges = {
'bool' : (False, True),
'int' : (-32768, 32767),
'pint' : (0, 32767),
'dint' : (-2147483648, 2147483647),
'pdint' : (0, 2147483647),
'uint' : (0, 65535),
'float' : (-1.9e307, 1.9e307),
'char' : (1, 256)
}

# This defines the characteristics of different register, pointer, and constant
# types. This is how we find the size and sign of data, and whether a register
# is writable. 
# key : (datatype, storagetype, writableregister, signed)
_RegDataTypeDef = {
'DS' : ('int', 'reg', True, 'signed'),
'DD' : ('dint', 'reg', True, 'signed'),
'DH' : ('uint', 'reg', True, 'unsigned'),
'DF' : ('float', 'reg', True, 'signed'),
'XD' : ('uint', 'reg', False, 'unsigned'),
'YD' : ('uint', 'reg', True, 'unsigned'),
'XS' : ('int', 'reg', False, 'signed'),
'YS' : ('int', 'reg', True, 'signed'),
'TD' : ('pint', 'reg', True, 'signed'),
'CTD' : ('pdint', 'reg', True, 'signed'),
'SD' : ('int', 'reg', False, 'signed'),
'TXT' : ('char', 'reg', True, 'char'),
'KInt' : ('int', 'const', False, 'signed'),
'KDInt' : ('dint', 'const', False, 'signed'),
'KF' : ('float', 'const', False, 'signed'),
'KHex' : ('uint', 'const', False, 'unsigned'),
'KTxtChar' : ('char', 'tconst', False, 'char'),
'KTxtStr' : ('char', 'tconst', False, 'char'),
'DSPtr' : ('int', 'ptr', True, 'signed'),
'DDPtr' : ('dint', 'ptr', True, 'signed'),
'DFPtr' : ('float', 'ptr', True, 'signed'),
'DHPtr' : ('uint', 'ptr', True, 'unsigned'),
'TXTPtr' : ('char', 'ptr', True, 'char')
}


#####################
def IsRegType(paramtype):
	"""Returns True if paramtype is a register type code.
	Parameters: paramtype (string) = A word data type from RegDataTypeDef.
	Return: (boolean) = True if this is a register (and not a constant or
		pointer.
	"""
	return (_RegDataTypeDef[paramtype][1] == 'reg')

#####################
def IsPtrType(paramtype):
	"""Returns True if paramtype is a pointer type code.
	Parameters: paramtype (string) = A word data type from RegDataTypeDef.
	Return: (boolean) = True if this is a pointer (and not a constant or
		direct register.
	"""
	return (_RegDataTypeDef[paramtype][1] == 'ptr')


#####################
def IsNumericConstType(paramtype):
	"""Returns True if paramtype is a numeric constant type code.
	Parameters: paramtype (string) = A word data type from RegDataTypeDef.
	Return: (boolean) = True if this is a numeric constant.
	"""
	return (_RegDataTypeDef[paramtype][1] == 'const')


#####################
def IsUnsigned(paramtype):
	"""Returns True if paramtype is an unsigned register type code. 
	Parameters: paramtype (string) = A word data type from RegDataTypeDef.
	Return: (boolean) = True if parameter is an unsigned register type code.
	"""
	return (_RegDataTypeDef[paramtype][0] == 'uint')


#####################
def IsNumericReg(paramtype):
	"""Returns True if paramtype is a numeric register type code. 
	Parameters: paramtype (string) = A word data type from RegDataTypeDef.
	Return: (boolean) = True if parameter is a numeric register type code.
	"""
	return ((_RegDataTypeDef[paramtype][1] == 'reg') and
			(_RegDataTypeDef[paramtype][3] in ['signed', 'unsigned']))



#####################
def IsTextConstType(paramtype):
	"""Returns True if paramtype is a text constant type code.
	Parameters: paramtype (string) = A word data type from RegDataTypeDef.
	Return: (boolean) = True if this is a text (character or string) constant.
	"""
	return (_RegDataTypeDef[paramtype][1] == 'tconst')


#####################
def IsTxtReg(paramtype):
	"""Returns True if paramtype is a text register type code. 
	Parameters: paramtype (string) = A word data type from RegDataTypeDef.
	Return: (boolean) = True if parameter is a text register type code.
	"""
	return ((_RegDataTypeDef[paramtype][1] == 'reg') and
			(_RegDataTypeDef[paramtype][3] == 'char'))



#####################
def IsCharType(paramtype):
	"""Returns True if paramtype is a single character type code.
	Parameters: paramtype (string) = A word data type from RegDataTypeDef.
	Return: (boolean) = True if this is a constant (and not a pointer or
		direct register.
	"""
	return (paramtype == 'KTxtChar')


#####################
def IsStringConstType(paramtype):
	"""Returns True if paramtype is a string constant type code.
	Parameters: paramtype (string) = A word data type from RegDataTypeDef.
	Return: (boolean) = True if this is a string constant (multiple characters).
	"""
	return (paramtype == 'KTxtStr')


#####################
def RegIsWritable(paramtype):
	"""Returns True if paramtype is a writable register type code. 
	Parameters: paramtype (string) = A word data type from RegDataTypeDef.
	Return: (boolean) = True if this is a register and writable.
	"""
	return _RegDataTypeDef[paramtype][2]


############################################################

# Destinations for unchecked data:
# key = Destination.
# value = source.
# These are guaranteed to be compatible.
# For other constants, do a range limit check on the actual data
# to see if it is compatible.
_CompatMatrix = {
'DS' : ['DS', 'XS', 'YS', 'TD', 'SD', 'KInt'],
'DD' : ['DS', 'DD', 'XS', 'YS', 'TD', 'CTD', 'SD', 'KInt', 'KDInt', 'KHex'],
'DH' : ['DH', 'XD', 'YD', 'KHex'],
'DF' : ['DF', 'KF'],
'YD' : ['DH', 'XD', 'YD', 'KHex'],
'YS' : ['DS', 'XS', 'YS', 'TD', 'SD', 'KInt'],
'TD' : ['TD'],
'CTD' : ['TD', 'CTD', 'KHex'],
'TXT' : ['TXT', 'KTxtChar']
}


#####################
def RegWrtCompatible(sourcetype, desttype):
	"""Return True if the destination type code is compatible with the
	source type code. 'Compatible' means the source is of the same basic
	type (signed integer, float, etc.) and is guaranteed to fit within
	the destination. This does a static check, and so only checks for
	what can be known at compile time. The destination register must also
	be writable. 
	Parameters: sourcetype (string) = Type code for the data source.
		desttype (string) = Type code for the data destination.
	Returns: (boolean) = True if the source is compatible with the
		destination and the destination is writable. 
	"""
	try:
		return (sourcetype in _CompatMatrix[desttype])
	except:
		return False


#####################
def RegCompareCompatible(param1, param2):
	"""Return True if the two types code are compatible with each other. 
	'Compatible' means both are either signed numeric, unsigned numeric,
	or character. This does a static check, and so only checks for what 
	can be known at compile time. 
	Parameters: param1 (string) = Type code for the first parameter.
		param2 (string) = Type code for the second parameter.
	Returns: (boolean) = True if the two parameters are compatible with
		each other. 
	"""
	try:
		return (_RegDataTypeDef[param1][3] == _RegDataTypeDef[param2][3])
	except:
		return False

#####################
def RegRunTimeCompatible(sourcetype, desttype):
	"""Return True if the destination type code is potentially compatible 
	with the source type code if the parameters are checked at rung time. 
	'Compatible' means the source is of the same basic
	type (signed integer, float, etc.) and is guaranteed to fit within
	the destination. This is intended for run-time checking. 
	The destination register must also be writable. 
	Parameters: sourcetype (string) = Type code for the data source.
		desttype (string) = Type code for the data destination.
	Returns: (boolean) = True if the source is compatible with the
		destination and the destination is writable. 
	"""

	# Get the destination register definitions, and also check if we recognise this
	# register type.
	try:
		destdatatype, deststoragetype, destwritableregister, destsigntype = _RegDataTypeDef[desttype]
	except:
		return False

	# Check if the destination is either a writable register or a pointer.
	if not (destwritableregister or deststoragetype == 'ptr'):
		return False

	# Get the source register definitions, and also check if we recognise this
	# register type.
	try:
		srcdatatype, srcstoragetype, srcwritableregister, srcsigntype = _RegDataTypeDef[sourcetype]
	except:
		return False

	# We already tested above if the destination is writable, so we don't 
	# have to check that again.

	# Text to numeric is not allowed.
	if (srcdatatype == 'char') and (srcdatatype != 'char'):
		return False

	# Everything else is allowed.
	return True


############################################################

#####################
def _FormatParam(paramtype, paramval):
	"""Format a parameter according to whether it is a register or a constant.
	If it is a register, return it in the form "PLC_DataWord['DS1']". If it
	is a constant, return it in the form "99". This is used by other functions
	to format their parameters correctly.
	Parameters: paramtype (string) = A data type key according to RegDataTypeDef.
		paramval (string) = The parameter to be formatted.
	Return: (string) = The formatted parameter.
	"""
	if (_RegDataTypeDef[paramtype][1] == 'reg'):
		return _PLCWordTable % paramval
	else:
		return '%s' % paramval



#####################
def RewriteHexConstant(hexstring):
	"""Rewrite a hex constant to be compatible with Python syntax.
	Parameters: hexstring (string) = The hex constant in PLC notation.
	Returns (string) = The hex constant in Python notation. If the string is
	zero or one characters in length, a hex string of 0x0 is returned.
	"""
	if (len(hexstring) > 1):
		return '0x%s' % hexstring[:len(hexstring)-1]
	else:
		return '0x0'

#####################
def _RegisterBlockLength(startaddr, endaddr):
	"""Calculate the number of registers in a block, given starting and ending 
	address labels.
	startaddr (string) - Starting address label.
	endaddr (string) - Ending address label.
	Returns the number of registers in the block.
	"""
	startindex = DLCkDataTable.WordAddrIndex[startaddr]
	endindex = DLCkDataTable.WordAddrIndex[endaddr]

	if (endindex > startindex):
		return endindex - startindex
	else:
		return startindex - endindex

#####################
def _RegisterSpan(startaddr, endaddr):
	"""Determines the distance between the end address and the start address.
	If endaddr is higher than startaddr, the return value will be positive,
	If startaddr is higher, it will be negative. 
	It does not check if they are of the same type.
	startaddr (string) = Address lable.
	endaddr (string) = Address lable.
	Returns (integer) = The distance between end and start.
	"""
	startindex = DLCkDataTable.WordAddrIndex[startaddr]
	endindex = DLCkDataTable.WordAddrIndex[endaddr]

	return endindex - startindex

	
#####################
def RegisterOffset(startaddr, offset):
	"""Calculate a register address, given an address label and an integer offset.
	startaddr (string) - Starting address label.
	offset (integer) - The offset from the starting address.
	Returns (string) the address label at the offset, or None if the
		new address is not the same type as the startaddr.
	"""
	# Calculate the new address from the offset.
	try:
		startindex = DLCkDataTable.WordAddrIndex[startaddr]
		newaddr = DLCkDataTable.WordAddrList[startindex + offset]
	except:
		return None

	# Get the type of address used by the start and new addresses.
	starttype = WordParamType(startaddr)
	newtype = WordParamType(newaddr)

	# Check if they are both the same type.
	if (starttype == newtype):
		return newaddr
	else:
		return None

############################################################
def _BoolSpan(startaddr, endaddr):
	"""Determines the distance between the end address and the start address.
	If endaddr is higher than startaddr, the return value will be positive,
	If startaddr is higher, it will be negative. 
	It does not check if they are of the same type.
	startaddr (string) = Address lable.
	endaddr (string) = Address lable.
	Returns (integer) = The distance between end and start.
	"""
	# Find the starting and ending indexes of the data table
	# addresses. We need this as we deal with them as an ordered sequence.
	startindex = DLCkDataTable.BoolAddrIndex[startaddr]
	endindex = DLCkDataTable.BoolAddrIndex[endaddr]

	return (endindex - startindex)

############################################################
def _RegStrSpan(regparam, strparam):
	"""Given a text register address and a string constant, calculate the
	address of register corresponding to the end of the string.
	regparam (string) = The label of the starting text register address.
	strparam (string) = A string constant.
	Returns (string) = The register address corresponding to the end
		of the string, or None if an error occurred.
	"""

	# Strip out the text from the enclosing quotes.
	paramtext = strparam[1:len(strparam) - 1]

	# Check if the ending destination address is valid. This is calculated 
	# from the amount of data to be copied.
	return RegisterOffset(regparam, len(paramtext) - 1)


############################################################
def RangeLimit(regtype, value):
	"""Determines if a value is within range to fit within a 
		specified writable register type.
	regtype (string) = Register type code for destination.
	value (any value) = Value to compare
	Returns (boolean) True if within range and the register is writable.
	"""

	# Get the register definitions, and also check if we recognise this
	# register type.
	try:
		datatype, storagetype, writableregister, signtype = _RegDataTypeDef[regtype]
	except:
		return False

	# Get the min and max values.
	minval, maxval = _DataRanges[datatype]

	# Determine if it is a writable register.
	if (storagetype not in ['reg', 'ptr']) or (not writableregister):
		return False

	# For numeric types, check the max and min values.
	if (datatype != 'char'):
		return (value >= minval) and (value <= maxval)
	# For strings, check the length.
	else:
		return (len(value) >= minval) and (len(value) <= maxval)



############################################################
def ConvertConstant(consttype, regtype, valuestr):
	"""Convert a string containing a numeric constant
	to a number of the correct type for a register type. 
	Parameters: 
	consttype (string) = Type code of constant.
	regtype (string) = Desired register type code for constant.
	valuestr (string) = String containing constant to be converted.
	Returns (tuple) = (True, numeric value of constant).
	If consttype or regtype was not recognised, or if valuestr could 
		not be converted, it returns (False, 0).
	"""

	try:
		# First, convert the string to a number.
		if (consttype in ['KInt', 'KDInt']):
			value = int(valuestr)
		elif (consttype == 'KHex'):
			value = int(valuestr, 16)	# Base 16.
		elif (consttype == 'KF'):
			value = float(valuestr)
		else:
			return False, 0

		# Now, convert the number to the expected type.
		if (_RegDataTypeDef[regtype][0] in ['int', 'dint', 'uint', 'pint', 'pdint']):
			return True, int(value)
		elif (_RegDataTypeDef[regtype][0] == 'float'):
			return True, float(value)
		else:
			return False, 0
	except:
		return False, 0


############################################################
def ConvertRegType(sourcetype, desttype, value):
	"""Converts the type of a value to be compatible with a specified 
		register type. The value is assumed to be within range
		for the destination register. This will handle both signed
		and unsigned types.
	sourcetype (string) = Source register type code.
	desttype (string) = Destination register type code.
	value (any value) = Value to compare
	Returns (value) The correct parameter type, or None if error.
	"""

	try:

		# Convert unsigned to signed. This gives us a common type.
		if (_RegDataTypeDef[sourcetype][0] == 'uint') and (value > 32767):
			value = value - 65536

		# Now convert the types.
		# Convert to integer.
		if (_RegDataTypeDef[desttype][0] in ['int', 'dint', 'pint', 'pdint', 'uint']):
			value = int(value)

		# Convert to float.
		elif (_RegDataTypeDef[desttype][0] == 'float'):
			value = float(value)

		# Convert to string.
		elif (_RegDataTypeDef[desttype][0] == 'char'):
			value = str(value)

		# We don't know how to handle this.
		else:
			return None

		# Convert signed to unsigned if necessary.
		if (_RegDataTypeDef[desttype][0] == 'uint') and (value < 0):
			value = int(value + 65536)

		# Return the result.
		return value

	except:

		return None



############################################################
def ConvertRegTypeNoSign(desttype, value):
	"""Converts the type of a value to be compatible with a specified 
		register type. The value is assumed to be within range
		for the destination register. 
	This is similar to ConvertRegType, but it does not convert between signed
		and unsigned data types (integer, double integer, float) or string. 
		The calling routine must make sure for itself that the data source
		and definitions are of compatible types.
	desttype (string) = Destination register type code.
	value (any value) = Value to compare
	Returns (value) The correct parameter type, or None if error.
	"""

	try:
		# Convert to integer.
		if (_RegDataTypeDef[desttype][0] in ['int', 'dint', 'pint', 'pdint', 'uint']):
			value = int(value)

		# Convert to float.
		elif (_RegDataTypeDef[desttype][0] == 'float'):
			value = float(value)

		# Convert to string.
		elif (_RegDataTypeDef[desttype][0] == 'char'):
			value = str(value)

		# We don't know how to handle this.
		else:
			return None

		# Return the result.
		return value

	except:
		return None




############################################################
def MemSaveable(saveaddr):
	"""
	Params: saveaddr (string) - A valid word address label.
		permitted types are:'DS', 'DD', 'DH', 'DF', 'TXT'
	Returns: True if the address is a valid word parameter
	and it is one of the addresses which is permitted to be
	saved and restored.
	"""
	return WordParamType(saveaddr) in ['DS', 'DD', 'DH', 'DF', 'TXT']


############################################################
def OneShotParam(inparam):
	"""Returns True if the parameter is valid for a one shot parameter.
	Parameters: inparam (string) = '0' or '1'.
	Returns: (boolean) = True if '0' or '1'.
	"""
	return inparam in ['0', '1']


############################################################
# Define validator functions for addresses.
# Combine the regular expressions according to what various types of 
# instruction expect. 


#####################
def NoParams(inparam):
	"""Expects there to be no parameters.
	Returns parameters and True if the parameters were OK.
	inparam: {}
	Returns : True, {}, {}, []
	"""
	if (inparam != {}):
		inparam['errors'] = '%s' % ValErrorMsgs['notexpected']
		return False, inparam, inparam, []

	return True, inparam, inparam, []


#####################
def AcceptAny(inparam):
	""" Expects one parameters of type string. May be an empty string.
	Returns parameters and True (always).
	inparam: {'inparam1' : 'ABCdefg'}
	Returns : True, {'inparam1' : 'ABCdefg'}, {'inparam1' : 'ABCdefg'}, ['ABCdefg']
	"""
	# Make an ordered list of all possible input parameter values.
	maxparams = len(inparam)
	instrparamlist = ['inparam%s' % pcounter for pcounter in range(1, maxparams + 1)]

	# Now extract whatever parameters are present.
	plist = [inparam.get(x, '') for x in instrparamlist]
	# Create a list of parameters.
	paramlist = [x for x in plist if x != '']

	try:
		inparam1 = inparam['inparam1']
	except:
		errormsg = {}
		errormsg['errors'] = '%s' % ValErrorMsgs['missingparam']
		return False, errormsg, inparam, []

	return True, inparam, inparam, paramlist


#####################
def CommentStr(inparam):
	""" Expects one parameters of type string. May be an empty string.
	Returns parameters consolidated into a single string and True (always).
	inparam: {'inparam1' : 'ABCdefg', 'inparam2' : 'HIjk'}
	Returns : True, {'inparam1' : 'ABCdefg HIjk'}, {'inparam1' : 'ABCdefg HIjk'},
			['ABCdefg', 'HIjk']
	"""
	# Make an ordered list of all possible input parameter values.
	maxparams = len(inparam)
	instrparamlist = ['inparam%s' % pcounter for pcounter in range(1, maxparams + 1)]

	# Now extract whatever parameters are present.
	paramlist = [inparam.get(x, '') for x in instrparamlist]

	# Convert the list into a single string.
	paramstr = ' '.join(paramlist)

	# Make this the parameter. Strip off the leading space which join 
	# added in the process of making a single string.
	inparam1 = {'inparam1' : paramstr.lstrip()}

	return True, inparam1, inparam1, paramlist




#####################
def IntConstant(inparam):
	""" Expects one parameter of type integer constant.
	Returns parameters and True if the parameters were OK.
	inparam: {'inparam1' : '32'}
	Returns : True, {'inparam1' : '32'}, {'inparam1' : '32'}, ['32']
	"""
	try:
		inparam1 = inparam['inparam1']
	except:
		errormsg = {}
		errormsg['errors'] = '%s' % ValErrorMsgs['missingparam']
		return False, errormsg, inparam, []

	# Check if the type is correct.
	if (Re_KInt.match(inparam1) == None):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidtype']
		return False, inparam, inparam, [inparam1]

	return True, inparam, inparam, [inparam1]



#####################
def BoolC_C(inparam):
	""" Expects two boolean parameters of type 'C'. 
	Returns parameters and True if the parameters were OK.
	inparam: {'inparam1' : 'C1', 'inparam2' : 'C5'}
	Returns : True, {'inparam1' : 'C1', 'inparam2' : 'C5'}, 
		{'inparam1' : 'C1', 'inparam2' : 'C5'}, ['C1', 'C5']
	"""
	try:
		inparam1 = inparam['inparam1']
		inparam2 = inparam['inparam2']
	except:
		errormsg = {}
		errormsg['errors'] = '%s' % ValErrorMsgs['missingparam']
		return False, errormsg, inparam

	paramlist = [inparam1, inparam2]

	# Check if the type is correct.
	if ((Re_C.match(inparam1) == None) or (Re_C.match(inparam2) == None)):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidtype']
		return False, inparam, inparam, paramlist


	return True, inparam, inparam, paramlist


#####################
def BoolXYCTCTSC(inparam):
	"""Expects one boolean parameter of types X, Y, C, T, CT, or SC.
	Returns parameters and True if the parameters were OK.
	inparam: {'inparam1' : 'X1'}
	Returns : True, {'inparam1' : 'X1'}, {'inparam1' : 'X1'}, ['X1']
	"""
	try:
		inparam1 = inparam['inparam1']
	except:
		errormsg = {}
		errormsg['errors'] = '%s' % ValErrorMsgs['missingparam']
		return False, errormsg, inparam, []

	# Check if the type is correct.
	if (Re_X_Y_C_T_CT_SC.match(inparam1) == None):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidtype']
		return False, inparam, inparam, [inparam1]


	return True, inparam, inparam, [inparam1]


#####################
def BoolYC(inparam):
	"""Expects one boolean parameter of types Y or C.
	Returns parameters and True if the parameters were OK.
	inparam: {'inparam1' : 'Y1'}
	Returns : True, {'inparam1' : 'Y1'}, {'inparam1' : 'Y1'}, ['Y1']
	"""
	try:
		inparam1 = inparam['inparam1']
	except:
		errormsg = {}
		errormsg['errors'] = '%s' % ValErrorMsgs['missingparam']
		return False, errormsg, inparam, []

	# Check if the type is correct.
	if (Re_Y_C.match(inparam1) == None):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidtype']
		return False, inparam, inparam, [inparam1]

	return True, inparam, inparam, [inparam1]


#####################
def BoolYCSC(inparam):
	"""Expects one boolean parameter of types Y, C, or SC.
	Returns parameters and True if the parameters were OK.
	inparam: {'inparam1' : 'Y1'}
	Returns : True, {'inparam1' : 'Y1'}, {'inparam1' : 'Y1'}, ['Y1']
	"""
	try:
		inparam1 = inparam['inparam1']
	except:
		errormsg = {}
		errormsg['errors'] = '%s' % ValErrorMsgs['missingparam']
		return False, errormsg, inparam, []

	# Check if the type is correct.
	if (Re_Y_C_SC.match(inparam1) == None):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidtype']
		return False, inparam, inparam, [inparam1]

	return True, inparam, inparam, [inparam1]


#####################
def BoolYC_YC(inparam):
	"""Expects two boolean parameter of types Y or C.
	Returns parameters and True if the parameters were OK.
	inparam: {'inparam1' : 'Y1', 'inparam2' : 'Y5'}
	Returns : True, {'inparam1' : 'Y1', 'inparam2' : 'Y5'}, 
		{'inparam1' : 'Y1', 'inparam2' : 'Y5'}, ['Y1', 'Y5']
	"""
	try:
		inparam1 = inparam['inparam1']
		inparam2 = inparam['inparam2']
	except:
		errormsg = {}
		errormsg['errors'] = '%s' % ValErrorMsgs['missingparam']
		return False, errormsg, inparam, []

	paramlist = [inparam1, inparam2]

	# Find out what type the parameters are.
	paramtype1 = BoolParamType(inparam1)
	paramtype2 = BoolParamType(inparam2)

	# Check if they are the same.
	if (paramtype1 != paramtype2):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidtype']
		return False, inparam, inparam, paramlist

	# Check if they are of the correct type.
	if (paramtype1 not in ['Y', 'C']):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidtype']
		return False, inparam, inparam, paramlist

	# Check if the second parameter is a higher address than the first parameter.
	if (_BoolSpan(inparam1, inparam2) < 0):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidrange']
		return False, inparam, inparam, paramlist

	result = {}
	result['inparam1'] = '%s' % inparam1
	result['inparam2'] = '%s' % inparam2

	return True, result, inparam, paramlist


#####################
def SubrParam(inparam):
	"""Expects one string parameter corresponding to a valid subroutine name
	Returns parameters and True if the parameters were OK.
	inparam: {'inparam1' : 'Subroutine1'}
	Returns : True, {'inparam1' : 'Subroutine1'}, {'inparam1' : 'Subroutine1'}, 
			['Subroutine1']
	"""
	try:
		inparam1 = inparam['inparam1']
	except:
		errormsg = {}
		errormsg['errors'] = '%s' % ValErrorMsgs['missingparam']
		return False, errormsg, inparam, []

	if (Re_Subroutine.match(inparam1) == None):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidtype']
		return False, inparam, inparam, [inparam1]


	return True, inparam, inparam, [inparam1]


#####################
def CounterWord(inparam):
	"""Expects two word parameters. The first is of type CT. 
	The second is of types DS, DD, Int or DInt.
	Returns accessors and True if the parameters were OK.
	inparam: {'inparam1' : 'CT1', 'inparam2' : 'DS1'}
	Returns : True, {'inparam1' : 'CT1', 'inparam2' : PLC_WordTable['DS1']}, 
		{'inparam1' : 'CT1', 'inparam2' : 'DS1'}, ['CT1', 'DS1']
	"""
	try:
		inparam1 = inparam['inparam1']
		inparam2 = inparam['inparam2']
	except:
		errormsg = {}
		errormsg['errors'] = '%s' % ValErrorMsgs['missingparam']
		return False, errormsg, inparam, []

	paramlist = [inparam1, inparam2]

	# The first parameter must be a counter.
	if (not (Re_CT.match(inparam1) != None)):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidtype']
		return False, inparam, inparam, paramlist

	# The second parameter must be either a word or constant of certain types.
	paramtype2 = WordParamType(inparam2)
	if paramtype2 not in ['DS', 'DD', 'KInt', 'KDInt']:
		inparam['errors'] = '%s' % ValErrorMsgs['invalidtype']
		return False, inparam, inparam, paramlist


	# Both paramters are valid.
	result = {}
	result['inparam1'] = '%s' % inparam1

	# Format the parameter according to whether it is a register or constant.
	result['inparam2'] = _FormatParam(paramtype2, inparam2)


	return True, result, inparam, paramlist


#####################
def TimerWord(inparam):
	"""Expects three parameters. The first is of type T. The second is of 
	type DS or Int. The third is a timer time base code.
	Returns accessors and True if the parameters were OK.
	inparam: {'inparam1' : 'T1', 'inparam2' : 'DS1', 'inparam3' : 'ms'}
	Returns : True, {'inparam1' : 'T1', 'inparam2' : PLC_WordTable['DS1'], 'inparam3' : 'ms'}, 
		{'inparam1' : 'T1', 'inparam2' : 'DS1', 'inparam3' : 'ms'}, ['T1', 'DS1', 'ms']
	"""
	try:
		inparam1 = inparam['inparam1']
		inparam2 = inparam['inparam2']
		inparam3 = inparam['inparam3']
	except:
		errormsg = {}
		errormsg['errors'] = '%s' % ValErrorMsgs['missingparam']
		return False, errormsg, inparam, []

	paramlist = [inparam1, inparam2, inparam3]

	# The first parameter must be a timer.
	if (not (Re_T.match(inparam1) != None)):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidtype']
		return False, inparam, inparam, paramlist

	# The second parameter must be either a word or constant of certain types.
	paramtype2 = WordParamType(inparam2)
	if paramtype2 not in ['DS', 'KInt']:
		inparam['errors'] = '%s' % ValErrorMsgs['invalidtype']
		return False, inparam, inparam, paramlist

	# The third parameter must be a timer time base code.
	if (not (Re_KTimeBase.match(inparam3) != None)):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidtype']
		return False, inparam, inparam, paramlist


	# All paramters are valid.
	result = {}
	result['inparam1'] = '%s' % inparam1
	result['inparam3'] = '%s' % inparam3

	# Format the parameter according to whether it is a register or constant.
	result['inparam2'] = _FormatParam(paramtype2, inparam2)

	return True, result, inparam, paramlist



#####################
def WordDS(inparam):
	"""Expects one parameters of type DS or a constant of type Int.
	inparam: {'inparam1' : 'DS1'}
	Returns : True, {'inparam1' : PLC_WordTable['DS1']}, {'inparam1' : 'DS1'}, ['DS1']
	"""
	try:
		inparam1 = inparam['inparam1']
	except:
		errormsg = {}
		errormsg['errors'] = '%s' % ValErrorMsgs['missingparam']
		return False, errormsg, inparam, []

	# Check the word parameter.
	# First, check if it is a DS word.
	if (Re_DS.match(inparam1) != None):
		return True, {'inparam1' : _PLCWordTable % inparam1}, inparam, [inparam1]

	# Next, check if it is an integer constant.
	elif (Re_KInt.match(inparam1) != None):
		return True, {'inparam1' : '%s' % inparam1}, inparam, [inparam1]
	else:
		inparam['errors'] = '%s' % ValErrorMsgs['invalidtype']
		return False, inparam, inparam, [inparam1]


#####################
def ForParams(inparam):
	"""Expects one parameters of type DS or a constant of type Int.
	There is also a second optional parameter to create a one-shot if '1', or
	not if '0' or not present.
	inparam: {'inparam1' : 'DS1', 'inparam2' : '1'}
	Returns : True, {'inparam1' : PLC_WordTable['DS1'], 'inparam2' : '1'}, 
			{'inparam1' : 'DS1', 'inparam2' : '1'}, ['DS1', '1']
	"""
	try:
		inparam1 = inparam['inparam1']
	except:
		errormsg = {}
		errormsg['errors'] = '%s' % ValErrorMsgs['missingparam']
		return False, errormsg, inparam, []

	# The second parameter is optional, and defaults to '0'
	try:
		inparam2 = inparam['inparam2']	# One-shot selection.
	except:
		inparam2 = '0'
		inparam['inparam2'] = inparam2

	paramlist = [inparam1, inparam2]

	result = {}
	# Check if the one-shot parameter is a 0 or 1.
	if (not OneShotParam(inparam2)):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidoneshot']
		return False, inparam, inparam, paramlist


	# Check the word parameter.
	# First, check if it is a DS word.
	if (Re_DS.match(inparam1) != None):
		result['inparam1'] = _PLCWordTable % inparam1
	# Next, check if it is a positive integer constant.
	elif (Re_KIntPlus.match(inparam1) != None):
		result['inparam1'] = '%s' % inparam1
	else:
		inparam['errors'] = '%s' % ValErrorMsgs['invalidtype']
		return False, inparam, inparam, paramlist

	# Include the second parameter.
	result['inparam2'] = '%s' % inparam2

	# Parameters were OK.
	return True, result, inparam, paramlist



#####################
def CompareWordWord(inparam):
	"""Expects two word parameters of types DS, DD, DF, DH, TD, CTD, SD, 
	Int, DInt, Float or TXT. The two parameters must be compatible types. 
	Returns accessors and True if the parameters were OK.
	inparam: {'inparam1' : 'DS1', 'inparam2' : '45'}
	Returns : True, {'inparam1' : PLC_WordTable['DS1'], 'inparam2' : '45'}, 
			{'inparam1' : 'DS1', 'inparam2' : '45'}, ['DS1', '45']
	"""
	try:
		inparam1 = inparam['inparam1']
		inparam2 = inparam['inparam2']
	except:
		errormsg = {}
		errormsg['errors'] = '%s' % ValErrorMsgs['missingparam']
		return False, errormsg, inparam, []

	paramlist = [inparam1, inparam2]

	# See if the parameters are of a valid type and range.
	paramtype1 = WordParamType(inparam1)
	paramtype2 = WordParamType(inparam2)

	if ((paramtype1 == None) or (paramtype2 == None)):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidtype']
		return False, inparam, inparam, paramlist

	# Now, check to see if the two types are compatible.
	if not RegCompareCompatible(paramtype1, paramtype2):
		inparam['errors'] = '%s' % ValErrorMsgs['incompatible']
		return False, inparam, inparam, paramlist

	# If either parameter is a hex constant, rewrite it to be 
	# compatible with Python syntax.
	if (paramtype1 == 'KHex'):
		inparam1 = RewriteHexConstant(inparam1)
	if (paramtype2 == 'KHex'):
		inparam2 = RewriteHexConstant(inparam2)

	# If either parameter is a text string constant, and the other
	# parameter is a text register, we must get a string of
	# text registers to compare it with.

	result = {}

	# Both paramters are valid and compatible with each other.
	if ((paramtype1 == 'TXT') and (paramtype2 == 'KTxtStr')):

		# Get the text register address label corresponding to the
		# end of the input string.
		sourceend = _RegStrSpan(inparam1, inparam2)

		if (sourceend == None):
			inparam['errors'] = '%s' % ValErrorMsgs['invaliddestaddr']
			return False, inparam, inparam, paramlist
		else:
			result['inparam1'] = _RegStrings % (inparam1, sourceend)
	else:
		# Format the parameter according to whether it is a register or constant.
		result['inparam1'] = _FormatParam(paramtype1, inparam1)


	if ((paramtype1 == 'KTxtStr') and (paramtype2 == 'TXT')):

		# Get the text register address label corresponding to the
		# end of the input string.
		sourceend = _RegStrSpan(inparam2, inparam1)

		if (sourceend == None):
			inparam['errors'] = '%s' % ValErrorMsgs['invaliddestaddr']
			return False, inparam, inparam, paramlist
		else:
			result['inparam2'] = _RegStrings % (inparam2, sourceend)

	else:
		# Format the parameter according to whether it is a register or constant.
		result['inparam2'] = _FormatParam(paramtype2, inparam2)


	return True, result, inparam, paramlist


#####################
def CopyBlock(inparam):
	"""Expects three register parameters. The first parameters are the source 
	and must be of the same types. The last is the destination, and must be 
	compatible with the source.
	There is also a fourth optional parameter to create a one-shot if '1', or
	not if '0' or not present.
	Returns addresses and True if the parameters were OK.
	inparam: {'inparam1' : 'DS1', 'inparam2' : 'DS2', 'inparam3' : 'DS9', 'inparam4' : '0'}
	Returns : True, {'inparam1' : 'DS1', 'inparam2' : 'DS2', 'inparam3' : 'DS9', 
		'inparam4' : '0', 'sourcetype' : 'DS', 'desttype' : 'DS'}, 
		{'inparam1' : 'DS1', 'inparam2' : 'DS2', 'inparam3' : 'DS9', 'inparam4' : '0'},
		['DS1', 'DS2', 'DS9', '0']
	"""
	try:
		inparam1 = inparam['inparam1']	# Source start addr.
		inparam2 = inparam['inparam2']	# Source end addr.
		inparam3 = inparam['inparam3']	# Destination start addr.
	except:
		errormsg = {}
		errormsg['errors'] = '%s' % ValErrorMsgs['missingparam']
		return False, errormsg, inparam, []

	# The fourth parameter is optional, and defaults to '0'
	try:
		inparam4 = inparam['inparam4']	# One-shot selection.
	except:
		inparam4 = '0'
		inparam['inparam4'] = inparam4

	paramlist = [inparam1, inparam2, inparam3, inparam4]


	# See if the parameters are of a valid type and range.
	paramtype1 = WordParamType(inparam1)
	paramtype2 = WordParamType(inparam2)
	paramtype3 = WordParamType(inparam3)

	if ((paramtype1 == None) or (paramtype2 == None) or (paramtype3 == None)):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidtype']
		return False, inparam, inparam, paramlist


	# Check if the start and end of the source range are of the same type.
	if (paramtype1 != paramtype2):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidrange']
		return False, inparam, inparam, paramlist

	# Check if they are registers and are writable.
	if not (IsRegType(paramtype1) and RegIsWritable(paramtype3)):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidtype']
		return False, inparam, inparam, paramlist

	# Check if the one shot parameter is a 0 or 1.
	if (not OneShotParam(inparam4)):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidoneshot']
		return False, inparam, inparam, paramlist

	# Check if the ending destination address is valid. This is calculated 
	# from the amount of data to be copied.
	regblocksize = _RegisterBlockLength(inparam1, inparam2)
	destinationend = RegisterOffset(inparam3, regblocksize)
	if (destinationend == None):
		inparam['errors'] = '%s' % ValErrorMsgs['invaliddestaddr']
		return False, inparam, inparam, paramlist


	# All paramters are valid.
	result = {}
	result['inparam1'] = '%s' % inparam1
	result['inparam2'] = '%s' % inparam2
	result['inparam3'] = '%s' % inparam3
	result['inparam4'] = '%s' % inparam4

	# The source and destination types are necessary to determine
	# how to range check the data.
	result['sourcetype'] = '%s' % paramtype1
	result['desttype'] = '%s' % paramtype3

	return True, result, inparam, paramlist


#####################
def CopyFill(inparam):
	"""Expects three register parameters. The first parameter is the source.
	The second two are the destination and must be of the same types. 
	There is also a fourth optional parameter to create a one-shot if '1', or
	not if '0' or not present.
	Returns addresses and True if the parameters were OK.
	inparam: {'inparam1' : 'DS1', 'inparam2' : 'DS2', 'inparam3' : 'DS9', 'inparam4' : '0'}
	Returns : True, {'inparam1' : 'DS1', 'inparam2' : 'DS2', 'inparam3' : 'DS9', 
			'inparam4' : '0', 'inparam4' : '0', 'desttype' : 'DS'}, 
			{'inparam1' : 'DS1', 'inparam2' : 'DS2', 'inparam3' : 'DS9', 
			'inparam4' : '0'}, ['DS1', 'DS2', 'DS9', '0']
	"""
	try:
		inparam1 = inparam['inparam1']
		inparam2 = inparam['inparam2']
		inparam3 = inparam['inparam3']
	except:
		errormsg = {}
		errormsg['errors'] = '%s' % ValErrorMsgs['missingparam']
		return False, errormsg, inparam, []

	# The fourth parameter is optional, and defaults to '0'
	try:
		inparam4 = inparam['inparam4']	# One-shot selection.
	except:
		inparam4 = '0'
		inparam['inparam4'] = inparam4

	paramlist = [inparam1, inparam2, inparam3, inparam4]

	# See if the parameters are of a valid type and range.
	paramtype1 = WordParamType(inparam1)
	paramtype2 = WordParamType(inparam2)
	paramtype3 = WordParamType(inparam3)

	if ((paramtype1 == None) or (paramtype2 == None) or (paramtype3 == None)):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidtype']
		return False, inparam, inparam, paramlist

	# If the first parameter is a hex constant, rewrite it to be compatible
	# with Python syntax.
	if (paramtype1 == 'KHex'):
		inparam1 = RewriteHexConstant(inparam1)

	# Make sure the first parameter is not text string, as we can handle
	# only single characters.
	if (paramtype1 == 'KTxtStr'):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidtype']
		return False, inparam, inparam, paramlist

	# Check if the start and end of the destination range are of the same type.
	if (paramtype2 != paramtype3):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidrange']
		return False, inparam, inparam, paramlist

	# Check if the destinations are writable registers.
	if (not RegIsWritable(paramtype3)):
		inparam['errors'] = '%s' % ValErrorMsgs['invaliddestreg']
		return False, inparam, inparam, paramlist

	# Check if the source address is compatible with the destination.
	if not RegCompareCompatible(paramtype1, paramtype3):
		inparam['errors'] = '%s' % ValErrorMsgs['incompatible']
		return False, inparam, inparam, paramlist

	# Check if the one shot parameter is a 0 or 1.
	if (not OneShotParam(inparam4)):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidoneshot']
		return False, inparam, inparam, paramlist


	# All paramters are valid.
	result = {}
	# Format the parameter according to whether it is a register or constant.
	result['inparam1'] = _FormatParam(paramtype1, inparam1)


	result['inparam2'] = '%s' % inparam2
	result['inparam3'] = '%s' % inparam3
	result['inparam4'] = '%s' % inparam4
	result['desttype'] = '%s' % paramtype2

	return True, result, inparam, paramlist
		
#####################
def CopySingle(inparam):
	"""Expects three parameters. The first is a word parameters of types DS, DD, DF, 
	DH, TD, CTD, SD, TXT Int, DInt, Float, or Text. The second parameter must be a register.
	The two word parameters need not be compatible types. 
	There is also a third optional parameter to create a one-shot if '1', or
	not if '0' or not present.
	Returns address labels and True if the parameters were OK.
	inparam: {'inparam1' : '45', 'inparam2' : 'DS1', 'inparam3' : '0'}
	Returns : True, {'inparam1' : '45', 'inparam2' : "PLC_WordTable['DS1']", 
		'inparam3' : '0', 'sourcetype' : 'KInt', 'desttype' : 'DS'}, 
		{'inparam1' : '45', 'inparam2' : 'DS1', 'inparam3' : '0'},
		['45', 'DS1', '0']
	"""
	try:
		inparam1 = inparam['inparam1']
		inparam2 = inparam['inparam2']
	except:
		errormsg = {}
		errormsg['errors'] = '%s' % ValErrorMsgs['missingparam']
		return False, errormsg, inparam, []

	# The third parameter is optional, and defaults to '0'
	try:
		inparam3 = inparam['inparam3']	# One-shot selection.
	except:
		inparam3 = '0'
		inparam['inparam3'] = inparam3

	paramlist = [inparam1, inparam2, inparam3]

	# See if the parameters are of a valid type and range.
	paramtype1 = WordParamType(inparam1)
	paramtype2 = WordParamType(inparam2)

	if ((paramtype1 == None) or (paramtype2 == None)):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidtype']
		return False, inparam, inparam, paramlist

	# If the first parameter is a hex constant, rewrite it to be compatible
	# with Python syntax.
	if (paramtype1 == 'KHex'):
		inparam1 = RewriteHexConstant(inparam1)


	# Now, check if the parameters are compatible.
	if not RegRunTimeCompatible(paramtype1, paramtype2):

		inparam['errors'] = '%s' % ValErrorMsgs['invaliddestreg']
		return False, inparam, inparam, paramlist


	result = {}
	# The first parameters must be an address labels or constant.
	if (IsRegType(paramtype1) or IsPtrType(paramtype1)):
		result['inparam1'] = "'%s'" % inparam1	# Note the extra enclosed quotes.
	else:
		result['inparam1'] = '%s' % inparam1
	# The second parameter must be an address label.
	result['inparam2'] = '%s' % inparam2

	# Check if the one-shot parameter is a 0 or 1.
	if (not OneShotParam(inparam3)):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidoneshot']
		return False, inparam, inparam, paramlist


	# Generate additional parameters indicating source and destination types.
	# These are needed to handle pointers.
	result['sourcetype'] = paramtype1
	result['desttype'] = paramtype2
	result['inparam3'] = '%s' % inparam3

	return True, result, inparam, paramlist



####################
def CopySingleNoOns(inparam):
	"""Copy a single register without using a one shot. This is a wrapper which
	calls "CopySingleReg", but only if the one shot parameter is missing
	or set to 0. 
	"""
	# The third parameter is optional, and defaults to '0'.
	try:
		inparam3 = inparam['inparam3']	# One-shot selection.
	except:
		inparam3 = '0'

	# Check to see if the one shot parameter is turned off.
	if (inparam3 != '0'):
		errormsg = {}
		errormsg['errors'] = '%s' % ValErrorMsgs['missingparam']
		return False, errormsg, inparam, []


	# Call the regular routine.
	return CopySingleReg(inparam)


	
#####################
def CopySingleReg(inparam):
	"""This does a check for special cases where a constant or register can be 
	copied without having to do any run time checks. This is allowed if the
	source is a constant which can be checked, or both the source and destination
	are registers of the same type. This is a special case for CopySingle.
	Expects three parameters. The first is a word parameters of types DS, DD, DF, 
	DH, TD, CTD, SD, TXT, Int, DInt, or Float. The second parameter must be a register.
	If the first parameter is a register, the second must be a register of the same type.
	If the first parameter is a constant, the second must be a register of a compatible type. 
	There is also a third optional parameter to create a one-shot if '1', or
	not if '0' or not present. Pointers are not allowed.
	Returns address labels and True if the parameters were OK.
	inparam: {'inparam1' : '45', 'inparam2' : 'DS1', 'inparam3' : '0'}
	Returns : True, {'inparam1' : '45', 'inparam2' : "PLC_WordTable['DS1']", 
		'inparam3' : '0', 'sourcetype' : 'KInt', 'desttype' : 'DS'}, 
		{'inparam1' : '45', 'inparam2' : 'DS1', 'inparam3' : '0'},
		['45', 'DS1', '0']
	"""
	try:
		inparam1 = inparam['inparam1']
		inparam2 = inparam['inparam2']
	except:
		errormsg = {}
		errormsg['errors'] = '%s' % ValErrorMsgs['missingparam']
		return False, errormsg, inparam, []

	# The third parameter is optional, and defaults to '0'
	try:
		inparam3 = inparam['inparam3']	# One-shot selection.
	except:
		inparam3 = '0'
		inparam['inparam3'] = inparam3

	paramlist = [inparam1, inparam2, inparam3]

	# See if the parameters are of a valid type and range.
	paramtype1 = WordParamType(inparam1)
	paramtype2 = WordParamType(inparam2)

	if ((paramtype1 == None) or (paramtype2 == None)):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidtype']
		return False, inparam, inparam, paramlist

	# If the first parameter is a hex constant, rewrite it to be compatible
	# with Python syntax.
	if (paramtype1 == 'KHex'):
		inparam1 = RewriteHexConstant(inparam1)
	

	# Now, we need to check if the source and destination are compatible
	# enough that we can skip any run time checks.
	if (not RegWrtCompatible(paramtype1, paramtype2)):

		# If the first parameter is a numeric constant and the 
		# destination a numeric register, we need to convert it to a 
		# number so we can range check it. The type must match the destination.
		if IsNumericConstType(paramtype1) and IsNumericReg(paramtype2):
			convertok, inparam1 = ConvertConstant(paramtype1, paramtype2, inparam1)
			# Did it convert to numeric OK?
			if not convertok:
				inparam['errors'] = '%s' % ValErrorMsgs['invalidtype']
				return False, inparam, inparam, paramlist

			# Check if the numeric constant is within range for this register type.
			if (not RangeLimit(paramtype2, inparam1)):
				inparam['errors'] = '%s' % ValErrorMsgs['incompatible']
				return False, inparam, inparam, paramlist

		# Numeric constants can be stored directly in text registers provided
		# they can be converted to a single character ("0" to "9") - with double quotes!
		elif IsNumericConstType(paramtype1) and IsTxtReg(paramtype2):
			# Convert to string. Note that we have to surround it 
			# with double quote characters so that it output as a quoted string.
			inparam1 = '"%s"' % str(inparam1)
			# Is it exactly 1 character long (plus 2 double quote characters)?
			if (len(inparam1) != 3):
				inparam['errors'] = '%s' % ValErrorMsgs['invalidtype']
				return False, inparam, inparam, paramlist


		# If the first parameter is a character constant, make sure it is compatible
		# with the destination register.
		elif (IsTextConstType(paramtype1) and not (paramtype2 =='TXT' )):
			inparam['errors'] = '%s' % ValErrorMsgs['incompatible']
			return False, inparam, inparam, paramlist

		# We don't know how to handle this.
		else:
			inparam['errors'] = '%s' % ValErrorMsgs['incompatible']
			return False, inparam, inparam, paramlist
			


	# All tests have passed, so output the parameters.

	result = {}
	# The first parameter must be an address label or constant.
	# Format the parameter according to whether it is a register or constant.
	result['inparam1'] = _FormatParam(paramtype1, inparam1)

	# The second parameter must be an address label.
	result['inparam2'] = '%s' % inparam2

	# Check if the one-shot parameter is a 0 or 1.
	if (not OneShotParam(inparam3)):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidoneshot']
		return False, inparam, inparam, paramlist


	# Generate additional parameters indicating source and destination types.
	# These are needed to handle pointers.
	result['sourcetype'] = paramtype1
	result['desttype'] = paramtype2
	result['inparam3'] = '%s' % inparam3

	return True, result, inparam, paramlist


#####################
def CopyPack(inparam):
	"""Expects three parameters. The first two must be a source bit 
	addresses range of no more than 16 addresses. 
	The third must be a register of type YD or DH.
	There is also a fourth optional parameter to create a one-shot if '1', or
	not if '0' or not present.
	Returns addresses and accessors and True if the parameters were OK.
	inparam: {'inparam1' : 'X1', 'inparam2' : 'X8', 'inparam3' : 'YD1'}
	Returns : True, {'inparam1' : 'X1',  'inparam2' : 'X8', 'inparam3' : "PLC_WordTable['YD1']"}, 
		{'inparam1' : 'X1', 'inparam2' : 'X8', 'inparam3' : 'YD1'}, ['X1', 'X8', 'YD1', '0']
	"""
	try:
		inparam1 = inparam['inparam1']
		inparam2 = inparam['inparam2']
		inparam3 = inparam['inparam3']
	except:
		errormsg = {}
		errormsg['errors'] = '%s' % ValErrorMsgs['missingparam']
		return False, errormsg, inparam, []

	# The fourth parameter is optional, and defaults to '0'
	try:
		inparam4 = inparam['inparam4']	# One-shot selection.
	except:
		inparam4 = '0'
		inparam['inparam4'] = inparam4

	paramlist = [inparam1, inparam2, inparam3, inparam4]

	# Check if the boolean parameters are OK.
	paramtype1 = BoolParamType(inparam1)
	paramtype2 = BoolParamType(inparam2)

	# If None was returnd, the parameter wasn't boolean.
	if (paramtype1 == None) or (paramtype2 == None):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidtype']
		return False, inparam, inparam, paramlist

	# Both boolean addresses must be of the same type.
	if (paramtype1 != paramtype2):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidrange']
		return False, inparam, inparam, paramlist


	# Check if the second parameter is a higher address than the first parameter,
	# and that they are no more than 16 bits apart.
	paramspan = _BoolSpan(inparam1, inparam2)
	if (paramspan < 0) or (paramspan >= 16):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidrange']
		return False, inparam, inparam, paramlist

	# See if the parameters are of a valid type and range.
	paramtype3 = WordParamType(inparam3)

	if (paramtype3 == None):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidtype']
		return False, inparam, inparam, paramlist

	# Check to make sure the register address is of the correct type.
	if paramtype3 not in ['YD', 'DH']:
		inparam['errors'] = '%s' % ValErrorMsgs['invaliddestreg']
		return False, inparam, inparam, paramlist


	# Check if the one-shot parameter is a 0 or 1.
	if (not OneShotParam(inparam4)):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidoneshot']
		return False, inparam, inparam, paramlist

	# Return the result.
	result = {}
	# All paramters are valid.
	result['inparam1'] = '%s' % inparam1
	result['inparam2'] = '%s' % inparam2
	result['inparam3'] = '%s' % inparam3
	result['inparam4'] = '%s' % inparam4

	return True, result, inparam, paramlist



#####################
def CopyUnpack(inparam):
	"""Expects three parameters. The first must be a register of type DH.
	The second and third must be destination bit addresses range of no more 
	than 16 addresses. 
	There is also a fourth optional parameter to create a one-shot if '1', or
	not if '0' or not present.
	Returns addresses and accessors and True if the parameters were OK.
	inparam: {'inparam1' : 'DH1', 'inparam2' : 'X1', 'inparam3' : 'X9'}
	Returns : True, {'inparam1' : "PLC_WordTable['DH1']",  'inparam2' : 'X1', 'inparam3' : 'X9'}, 
		{'inparam1' : 'DH1', 'inparam2' : 'X1', 'inparam3' : 'X9'}, ['DH1', 'X1', 'X9', '0']
	"""
	try:
		inparam1 = inparam['inparam1']
		inparam2 = inparam['inparam2']
		inparam3 = inparam['inparam3']
	except:
		errormsg = {}
		errormsg['errors'] = '%s' % ValErrorMsgs['missingparam']
		return False, errormsg, inparam, []

	# The fourth parameter is optional, and defaults to '0'
	try:
		inparam4 = inparam['inparam4']	# One-shot selection.
	except:
		inparam4 = '0'
		inparam['inparam4'] = inparam4

	paramlist = [inparam1, inparam2, inparam3, inparam4]


	# Check if the boolean parameters are OK.
	paramtype2 = BoolParamType(inparam2)
	paramtype3 = BoolParamType(inparam3)

	if (paramtype2 not in ['Y', 'C']):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidtype']
		return False, inparam, inparam, paramlist

	# Both boolean addresses must be of the same type.
	if (paramtype2 != paramtype3):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidrange']
		return False, inparam, inparam, paramlist

	# Check if the second parameter is a higher address than the first parameter,
	# and that they are no more than 16 bits apart.
	paramspan = _BoolSpan(inparam2, inparam3)
	if (paramspan < 0) or (paramspan >= 16):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidrange']
		return False, inparam, inparam, paramlist


	# See if the word parameters is of a valid type and range.
	paramtype1 = WordParamType(inparam1)

	if (paramtype1 == None):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidtype']
		return False, inparam, inparam, paramlist

	# Check to make sure the register address is of the correct type.
	if paramtype1 not in ['DH']:
		inparam['errors'] = '%s' % ValErrorMsgs['invalidtype']
		return False, inparam, inparam, paramlist


	# Check if the one-shot parameter is a 0 or 1.
	if (not OneShotParam(inparam4)):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidoneshot']
		return False, inparam, inparam, paramlist


	# Return the result.
	result = {}
	# All paramters are valid.
	result['inparam1'] = '%s' % inparam1
	result['inparam2'] = '%s' % inparam2
	result['inparam3'] = '%s' % inparam3
	result['inparam4'] = '%s' % inparam4

	return True, result, inparam, paramlist



#####################
def Search(inparam):
	"""Expects 5 parameters. The first is the value to search for and must be
	a data register or constant. The second and third are the range to search in
	and must be data registers. The fourth is the value found and must be a data
	register. The fifth is a control bit ('C').
	There is also a sixth optional parameter to create a one-shot if '1', or
	not if '0' or not present.
	Returns addresses or accessors and True if the parameters were OK.
	inparam: {'inparam1' : 'DS1', 'inparam2' : 'DS2', 'inparam3' : 'DS9', 
		'inparam4' : 'DS10', 'inparam5' : 'C1'}
	Returns : True, {'inparam1' : PLC_WordTable['DS1', 'inparam2' : 'DS2', 'inparam3' : 'DS9', 
		'inparam4' : 'DS10', 'inparam5' : 'C1'}, 
		{'inparam1' : 'DS1', 'inparam2' : 'DS2', 'inparam3' : 'DS9', 
		'inparam4' : 'DS10', 'inparam5' : 'C1'}, ['DS1', 'DS2', 'DS9', 'DS10', 'C1', '0']
	"""
	try:
		inparam1 = inparam['inparam1']	# Search value
		inparam2 = inparam['inparam2']	# Start of search range.
		inparam3 = inparam['inparam3']	# End of search range.
		inparam4 = inparam['inparam4']	# Result register.
		inparam5 = inparam['inparam5']	# Result boolean.
	except:
		errormsg = {}
		errormsg['errors'] = '%s' % ValErrorMsgs['missingparam']
		return False, errormsg, inparam, []

	# The sixth parameter is optional, and defaults to '0'
	try:
		inparam6 = inparam['inparam6']	# One-shot selection.
	except:
		inparam6 = '0'
		inparam['inparam6'] = inparam6

	paramlist = [inparam1, inparam2, inparam3, inparam4, inparam5, inparam6]

	# See if the parameters are of a valid type and range.
	paramtype1 = WordParamType(inparam1)
	paramtype2 = WordParamType(inparam2)
	paramtype3 = WordParamType(inparam3)
	paramtype4 = WordParamType(inparam4)

	if ((paramtype1 == None) or (paramtype2 == None) or (paramtype3 == None) or (paramtype4 == None)):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidtype']
		return False, inparam, inparam, paramlist

	# Check if the boolean parameter is OK.
	if (not (Re_C.match(inparam5) != None)):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidtype']
		return False, inparam, inparam, paramlist

	# Check if the start and end of the search range are of the same type.
	if (paramtype2 != paramtype3):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidrange']
		return False, inparam, inparam, paramlist

	# Check if they are data registers.
	if paramtype2 not in ['DS', 'DD', 'DH', 'DF', 'TXT']:
		inparam['errors'] = '%s' % ValErrorMsgs['invalidtype']
		return False, inparam, inparam, paramlist

	# Check if the end address is after the start address.
	if (_RegisterSpan(inparam2, inparam3) < 0):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidrange']
		return False, inparam, inparam, paramlist

	# Check if the destination register will accept signed integer results.
	if (paramtype4 not in ['DS', 'DD']):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidtype']
		return False, inparam, inparam, paramlist

	# Check if the search value is compatible with the range being searched.
	if not RegCompareCompatible(paramtype1, paramtype2):
		inparam['errors'] = '%s' % ValErrorMsgs['incompatible']
		return False, inparam, inparam, paramlist


	# Check if the one-shot parameter is a 0 or 1.
	if (not OneShotParam(inparam6)):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidoneshot']
		return False, inparam, inparam, paramlist


	# All paramters are valid.
	result = {}
	# Format the parameter according to whether it is a register or constant.
	result['inparam1'] = _FormatParam(paramtype1, inparam1)

	# The rest of the parameters all data registers or bits.
	result['inparam2'] = '%s' % inparam2
	result['inparam3'] = '%s' % inparam3
	result['inparam4'] = '%s' % inparam4
	result['inparam5'] = '%s' % inparam5
	result['inparam6'] = '%s' % inparam6
	result['sourcetype'] = paramtype1

	return True, result, inparam, paramlist


#####################
def SumRegisters(inparam):
	"""Expects three register parameters and one register type parameter. 
	The first two parameters are the source and must be of the same types. 
	The third is the destination, and must be compatible with the source.
	There is also a fourth optional parameter to create a one-shot if '1', or
	not if '0' or not present.
	Returns addresses and True if the parameters were OK.
	inparam: {'inparam1' : 'DS1', 'inparam2' : 'DS10', 'inparam3' : 'DS20', 'inparam4' : '0'}
	Returns : True, {'inparam1' : 'DS1', 'inparam2' : 'DS10', 'inparam3' : 'DS20', 
		'inparam4' : '0', 'desttype' : 'DS'}, 
		{'inparam1' : 'DS1', 'inparam2' : 'DS10', 'inparam3' : 'DS20', 'inparam4' : '0'},
		['DS1', 'DS10', 'DS20', '0']
	"""
	try:
		inparam1 = inparam['inparam1']	# Source start addr.
		inparam2 = inparam['inparam2']	# Source end addr.
		inparam3 = inparam['inparam3']	# Destination addr.
	except:
		errormsg = {}
		errormsg['errors'] = '%s' % ValErrorMsgs['missingparam']
		return False, errormsg, inparam, []

	# The fourth parameter is optional, and defaults to '0'
	try:
		inparam4 = inparam['inparam4']	# One-shot selection.
	except:
		inparam4 = '0'
		inparam['inparam4'] = inparam4

	paramlist = [inparam1, inparam2, inparam3, inparam4]

	# See if the parameters are of a valid type and range.
	paramtype1 = WordParamType(inparam1)
	paramtype2 = WordParamType(inparam2)
	paramtype3 = WordParamType(inparam3)

	if ((paramtype1 == None) or (paramtype2 == None) or (paramtype3 == None)):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidtype']
		return False, inparam, inparam, paramlist

	# Check if the start and end of the source range are of the same type.
	if (paramtype1 != paramtype2):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidrange']
		return False, inparam, inparam, paramlist

	# Check if the register types are OK. Unsigned registers are not to be
	# mixed with signed or floating point registers.
	if (paramtype1 in ['DS', 'DD', 'DF']) and (paramtype3 in ['DS', 'DD', 'DF']):
		pass
	elif (paramtype1 == 'DH') and (paramtype3 == 'DH'):
		pass
	else:
		inparam['errors'] = '%s' % ValErrorMsgs['invalidtype']
		return False, inparam, inparam, paramlist


	# Check if the one shot parameter is a 0 or 1.
	if (not OneShotParam(inparam4)):
		inparam['errors'] = '%s' % ValErrorMsgs['invalidoneshot']
		return False, inparam, inparam, paramlist


	# All paramters are valid.
	result = {}
	result['inparam1'] = '%s' % inparam1
	result['inparam2'] = '%s' % inparam2
	result['inparam3'] = '%s' % inparam3
	result['inparam4'] = '%s' % inparam4

	# The destination types are necessary to determine
	# how to range check the data.
	result['desttype'] = '%s' % paramtype3

	return True, result, inparam, paramlist


##############################################################################


