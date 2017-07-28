##############################################################################
# Project: 	MBLogic
# Module: 	DLCkMath.py
# Purpose: 	Math functions for a DL Clock-like PLC.
# Language:	Python 2.5
# Date:		11-Nov-2008.
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

import re
import math

import DLCkAddrValidate

##############################################################################

# Error messages for math operations.
_MathErrMsgs = {
	'parentheses' : 'Math error - unbalanced parentheses',
	'illegalchar' : 'Math error - illegal character "%s" in equation',
	'unknownsymb' : 'Math error - unknown symbol %s.',
	'invalidaddr' : 'Math error - invalid address %s.',
	'equacompile' : 'Math error while compiling equation.',
	'equatest' : 'Math error while testing equation.'
}

##############################################################################

class DecMathCompiler:
	"""Compile decimal math expressions into executable Python code. This takes the
	place of the normal address validators used for other instructions.
	"""
	############################################################
	def __init__(self, mathlib):

		# Math library. This is required to perform a test run of
		# the final equation.
		self._Math = mathlib

		# This is used to test the equation when we are done.
		self._TestDataTable = {}

		# PLC decimal math function names, and equivalent math functions.
		self._DecFuncDefs = {
		'SIN(' : 'PLC_BinMathLib.sin(',
		'COS(' : 'PLC_BinMathLib.cos(',
		'TAN(' : 'PLC_BinMathLib.tan(',
		'ASIN(' : 'PLC_BinMathLib.asin(',
		'ACOS(' : 'PLC_BinMathLib.acos(',
		'ATAN(' : 'PLC_BinMathLib.atan(',
		'LOG(' : 'PLC_BinMathLib.log10(',
		'LN(' : 'PLC_BinMathLib.log(',
		'SQRT(' : 'PLC_BinMathLib.sqrt(',
		'RAD(' : 'PLC_BinMathLib.radians(',
		'DEG(' : 'PLC_BinMathLib.degrees('
		}


		# Misc operators and constants.
		self._MiscOpDefs = {
		'PI' : 'PLC_BinMathLib.pi',	# PI constant.
		'MOD' : '%',			# MOD operator.
		'^' : '**'			# Exponent operator.
		}
		

		# List of valid function names.
		self._DecFuncList = self._DecFuncDefs.keys()

		# This defines valid addresses, function names, and some additional symbols for math equations.
		self._DecMathParse = '(' + 'D[DFS][0-9]+|' + \
		'SIN\(|COS\(|TAN\(|ASIN\(|ACOS\(|ATAN\(|LOG\(|LN\(|SQRT\(|RAD\(|DEG\(|' + \
		'PI|MOD|\*|\/|\^|\)| ' + ')'

		self._DecMathConst = '(' + '[+-]?[0-9]+\.[0-9]+Ee][+-][0-9]+|[+-]?[0-9]+\.[0-9]+|[+-]?[0-9]+' + ')'

		self._MathOps = '(' + '\+|\-|\(' + ')'

		# List of characters which are not allowed in equations. Note, '\' is doubled
		# to escape it.
		self._IllegalChars = ['`', '~', '!', '@', '#', '$', '%', '&', '_', '=', 
			'{', '}', '[', ']', '|', '\\', ';', ':', '"', "'", '<', '>', ',', '?']

		# Bad address type. This will match anything that resembles an 
		# address, so this should be applied only after the token has 
		# failed the test for a good address.
		self._BadAddr = re.compile('D[DFS][0-9]+')



	############################################################
	def _ClassifyTokens(self, equlist):
		"""Go through a list of strings, and classify them by type.
		Also, collect a list of addresses used in the equation so
		we can use them in a test at the end.
		Parameters: equlist (list) = The unclassified equation list.
		Returns: (list, list) = A tuple containg the original list with
			further classifications, and a list containing any new
			addresses found.
		"""
		classlist = []
		addrlist = []
		for i in equlist:
			if (i == '') or (i == None) or (i == ' '):
				pass
			# Check addresses.
			elif ((DLCkAddrValidate.Re_DS.match(i) != None) or
				(DLCkAddrValidate.Re_DD.match(i) != None) or
				(DLCkAddrValidate.Re_DF.match(i) != None)):

				classlist.append((DLCkAddrValidate._PLCWordTable % i, 'addr'))
				addrlist.append(i)

			# Check for constants.
			elif ((DLCkAddrValidate.Re_KF.match(i) != None) or
				(DLCkAddrValidate.Re_KInt.match(i) != None) or
				(DLCkAddrValidate.Re_KDInt.match(i) != None)):

				classlist.append((i, 'constant'))

			# This will match anything that looks like an address.
			# It must be applied only after the test for a good
			# address has failed.
			elif (self._BadAddr.match(i) != None):
				classlist.append((i, 'badaddr'))

			# Check for function names.
			elif (i in self._DecFuncList):
				classlist.append((self._DecFuncDefs[i], 'func'))
			# Check for operators.
			elif (i in ['*', '/', '+', '-']):
				classlist.append((i, 'operator'))
			# Check for remaining cases.
			elif (i == 'PI'):
				classlist.append((self._MiscOpDefs['PI'], 'pi'))
			elif (i == 'MOD'):
				classlist.append((self._MiscOpDefs['MOD'], 'mod'))
			elif (i == '^'):
				classlist.append((self._MiscOpDefs['^'], 'exponent'))
			elif (i == ')'):
				classlist.append((i, 'rightbracket'))
			elif (i == '('):
				classlist.append((i, 'leftbracket'))
			else:
				classlist.append((i, 'unknown'))

		return 	classlist, addrlist

	############################################################
	def _SplitLists(self, equlist, splitdef):
		"""Apply additional split rules to an existing list.
		Parameters:
		equlist (list) = The partially split equation list.
		splitdef (string) = The regular expression to apply to
				create additional splits.
		Returns: (list, list) =  A tuple containg the original list with
			further classified splits, and a list containing any new
			addresses found.
		"""
		newlist = []
		addrlist = []
		for i in equlist:
			if (i[1] == 'unknown'):
				# Try to split it a regular expression.
				templist = re.split(splitdef, i[0])
				sublist, addresses = self._ClassifyTokens(templist)
				newlist.extend(sublist)
				addrlist.extend(addresses)
			else:
				newlist.append(i)
		return newlist, addrlist

	############################################################
	def DecMath(self, equation, desttype):
		""" Go through the equation, and split it into individual tokens
		Parameters: equation (string) = The math equation to be parsed 
			and compiled.
		desttype (string) = The destination register type. This
			should be DS, DD, or DF.
		Returns: (string) = The math equation compiled to Python source code.
			(boolean) = True if the equation was OK.
			(string) = An error message.
			(list) = A list of addresses.
		"""


		# We start by doing some simple syntax checks for common problems.
		leftbracket = equation.count('(')
		rightbracket = equation.count(')')
		if (leftbracket != rightbracket):
			return '', False, _MathErrMsgs['parentheses'], []


		# Now look for characters which we know are not permitted at all
		# in equations.
		for i in self._IllegalChars:
			if (equation.find(i) >= 0):
				return '', False, (_MathErrMsgs['illegalchar'] % i), []

		# First, we need to split the equation string up into pieces 
		# corresponding to addresses, constants, functions, etc. We do
		# this using regular expressions. We have to do this in stages,
		# as we otherwise get definition conflicts, resulting in 
		# incorrect splits.

		# First, split it by addresses, functions, and miscellaneous unique symbols.
		eqlist = re.split(self._DecMathParse, equation)
		# Now, go through the list and classify each as an address, or unknown.
		labellist, addrlist = self._ClassifyTokens(eqlist)

		# Next, go through the unclassified ones, and split those by constants.
		constlist, addresses = self._SplitLists(labellist, self._DecMathConst)
		addrlist.extend(addresses)

		# Repeat this for the remaining math symbols.
		opslist, addresses = self._SplitLists(constlist, self._MathOps)
		addrlist.extend(addresses)


		# Make the equation into a single string. While doing this, also
		# go through the list and see if there is anything left which 
		# has not been classified. These will be some form of incorrect syntax.
		testlist = []
		for i in opslist:
			if (i[1] == 'unknown'):
				return '', False, (_MathErrMsgs['unknownsymb'] % i[0]), addrlist
			elif (i[1] == 'badaddr'):
				return '', False, (_MathErrMsgs['invalidaddr'] % i[0]), addrlist
			testlist.append(i[0])

		# Create the equation string. We also insert the correct type conversion
		# which is compatible with the destination register.
		if (desttype in ['DS', 'DD']):
			mathequation = 'int(%s)' % ''.join(testlist)
		else:
			mathequation = 'float(%s)' % ''.join(testlist)

		testequation = 'TestResult = %s' % mathequation

		# Use the list of data table addresses so we can construct a
		# temporary data table to test the equation with.
		Test_DataTable = {}
		for i in addrlist:
			Test_DataTable[i] = 1

		# Dictionary used by PLC program for its working memory.
		plcdict = {
			'PLC_DataWord' : Test_DataTable,	# Word data table.
			'PLC_BinMathLib' : self._Math,		# Binary math library.
			'TestResult' : 0
			}

		# Try compiling the resulting equation, and see if we get any errors.
		try:
			mathobj = compile(testequation, '<plc code>', 'exec')
		except:
			return '', False, _MathErrMsgs['equacompile'], addrlist

		try:
			exec mathobj in plcdict

		except ZeroDivisionError:
			pass	# This is acceptable for testing.
		except ValueError:
			pass	# This is acceptable for testing.
		except:
			return '', False, _MathErrMsgs['equatest'], addrlist

		# Everthing was OK, so return the equation string.
		return mathequation, True, '', addrlist


	#####################
	def MathDecVal(self, inparam):
		"""Validator for decimal math.
		Expects the following parameters:
			One word parameter of types DS, DD, or DF as the destination register.
			One mandatory parameter of 0 or 1 where '1' indicates a one shot is desired.
			An indeterminate number of additional parameters which will be converted into
			a single equation string and compiled into a decimal math statement.
		Returns a destination address, a one-shot parameter, a complete equation string ,
			the original parameters, and True if the parameters were OK. If there were any
			errors, an error message is inserted into the original parameters using the
			'errors' key. Also, a list of addresses is inserted into the original
			parameters using the 'addrlist' key.
		inparam: {'inparam1' : 'DS1', 'inparam2' : '1', 'inparam3' : 'DS10+2'}
		Returns : True, {'inparam1' : 'DS1' , 'inparam2' : '1',  'inparam3' : 'int(PLC_WordTable['DS1']+2)'}, 
			{'inparam1' : 'DS1', 'inparam2' : '1', 'inparam3' : 'DS10+2', 
			'addrlist' : ['DS1', 'DS10']}, ['DS1', '1', 'DS10+2']
		"""

		# The first parameter is the destination address, and the second is the
		# one-shot request. 
		try:
			destination = inparam['inparam1']
			oneshot = inparam['inparam2']
			equtest = inparam['inparam3']	# There must be at least 3 parameters.
		except:
			errormsg = {}
			errormsg['errors'] = '%s' % DLCkAddrValidate.ValErrorMsgs['missingparam']
			return False, errormsg, inparam, []


		# The remaining parameters are to be concatenated into a 
		# single equation string
		equationparams = [inparam.get('inparam%s' % x, '') for x in range(3, len(inparam) + 1)]
		equationparams = ' '.join([x for x in equationparams if x != ''])

		# Parameters as a list.
		paramlist = [destination, oneshot, equationparams]


		# Add the formatted equation into the original parameters.
		inparam['equationparams'] = equationparams

		# Check to see if the destination register is valid.
		desttype = DLCkAddrValidate.WordParamType(destination)
		if desttype not in ['DS', 'DD', 'DF']:
			inparam['errors'] = '%s' % DLCkAddrValidate.ValErrorMsgs['invaliddestreg']
			return False, inparam, inparam, paramlist

		# Check if the one shot parameter is a 0 or 1.
		if (not (oneshot in ['0', '1'])):
			inparam['errors'] = '%s' % DLCkAddrValidate.ValErrorMsgs['invalidoneshot']
			return False, inparam, inparam, paramlist


		# Now, call the decimal math equation compiler. This comes back with a compiled
		# Python equation, a boolean result code, and an error message. The called function
		# will insert any required error messages.
		equation, result, errormsg, addrlist = self.DecMath(equationparams, desttype)

		# Insert the list of addresses into the original parameters. 
		# This has to include the destination address, so we add it to the list.
		addrlist.append(destination)
		inparam['addrlist'] = addrlist

		# Check if there were any errors.
		if not result:
			inparam['errors'] = '%s' % errormsg
			return False, inparam, inparam, paramlist

		# All paramters are valid.
		result = {}
		result['inparam1'] = '%s' % destination
		result['inparam2'] = '%s' % oneshot
		result['inparam3'] = '%s' % equation
		result['desttype'] = '%s' % desttype


		# Return any error message.
		result['errors'] = '%s' % errormsg

		return True, result, inparam, paramlist

##############################################################################


##############################################################################


class HexMathCompiler:
	"""Compile hexadecimal math expressions into executable Python code. This takes the
	place of the normal address validators used for other instructions.
	"""
	############################################################
	def __init__(self, mathlib):

		# Math library. This is required to perform a test run of
		# the final equation.
		self._Math = mathlib

		# This is used to test the equation when we are done.
		self._TestDataTable = {}

		# PLC hexadecimal math function names,a nd equivalent math functions.		
		self._HexFuncDefs = {
		'LSH(' : 'PLC_BinMathLib.lshift(',
		'RSH(' : 'PLC_BinMathLib.rshift(',
		'LRO(' : 'PLC_BinMathLib.lrotate(',
		'RRO(' : 'PLC_BinMathLib.rrotate('
		}

		# Misc operators and constants.
		self._MiscOpDefs = {
		'MOD' : '%',			# MOD operator.
		'AND' : '&',			# AND operator.
		'OR' : '|',			# OR operator.
		'XOR' : '^'			# XOR operator.
		}
		

		# List of valid function names.
		self._HexFuncList = self._HexFuncDefs.keys()

		# This defines valid addresses, function names, and some additional symbols for math equations.
		self._HexMathParse = '(' + 'DH[0-9]+|' + \
		'LSH\(|RSH\(|LRO\(|RRO\(' + \
		'AND|OR|XOR|MOD|\*|\/|\^|\)| ' + ')'

		self._HexMathConst = '(' + '[0-9]+[hH]' + ')'

		self._MathOps = '(' + '\+|\-|\(' + ')'

		# List of characters which are not allowed in equations. Note, '\' is doubled
		# to escape it.
		self._IllegalChars = ['`', '~', '!', '@', '#', '$', '%', '^', '&', '_', '=', 
			'{', '}', '[', ']', '|', '\\', ';', ':', '"', "'", '<', '>', '?']

		# Bad address type. This will match anything that resembles an 
		# address, so this should be applied only after the token has 
		# failed the test for a good address.
		self._BadHexAddr = re.compile('DH[0-9]+')



	############################################################
	def _ClassifyHexTokens(self, equlist):
		"""Go through a list of strings, and classify them by type.
		Also, collect a list of addresses used in the equation so
		we can use them in a test at the end.
		Parameters: equlist (list) = The unclassified equation list.
		Returns: (list, list) = A tuple containg the original list with
			further classifications, and a list containing any new
			addresses found.
		"""
		classlist = []
		addrlist = []
		for i in equlist:
			if (i == '') or (i == None) or (i == ' '):
				pass
			# Check addresses.
			elif (DLCkAddrValidate.Re_DH.match(i) != None):

				classlist.append((DLCkAddrValidate._PLCWordTable % i, 'addr'))
				addrlist.append(i)

			# Check for constants.
			elif (DLCkAddrValidate.Re_KHex.match(i) != None):

				classlist.append((DLCkAddrValidate.RewriteHexConstant(i), 'constant'))

			# This will match anything that looks like an address.
			# It must be applied only after the test for a good
			# address has failed.
			elif (self._BadHexAddr.match(i) != None):
				classlist.append((i, 'badaddr'))

			# Check for function names.
			elif (i in self._HexFuncList):
				classlist.append((self._HexFuncDefs[i], 'func'))
			# Check for operators.
			elif (i in ['*', '/', '+', '-']):
				classlist.append((i, 'operator'))
			elif (i == 'OR'):
				classlist.append((self._MiscOpDefs['OR'], 'or'))
			elif (i == 'AND'):
				classlist.append((self._MiscOpDefs['AND'], 'and'))
			elif (i == 'XOR'):
				classlist.append((self._MiscOpDefs['XOR'], 'xor'))
			elif (i == 'MOD'):
				classlist.append((self._MiscOpDefs['MOD'], 'mod'))
			elif (i == ')'):
				classlist.append((i, 'rightbracket'))
			elif (i == '('):
				classlist.append((i, 'leftbracket'))
			elif (i == ','):
				classlist.append((i, 'comma'))
			else:
				classlist.append((i, 'unknown'))

		return 	classlist, addrlist

	############################################################
	def _SplitHexLists(self, equlist, splitdef):
		"""Apply additional split rules to an existing list.
		Parameters:
		equlist (list) = The partially split equation list.
		splitdef (string) = The regular expression to apply to
				create additional splits.
		Returns: (list, list) =  A tuple containg the original list with
			further classified splits, and a list containing any new
			addresses found.
		"""
		newlist = []
		addrlist = []
		for i in equlist:
			if (i[1] == 'unknown'):
				# Try to split it a regular expression.
				templist = re.split(splitdef, i[0])
				sublist, addresses = self._ClassifyHexTokens(templist)
				newlist.extend(sublist)
				addrlist.extend(addresses)
			else:
				newlist.append(i)
		return newlist, addrlist

	############################################################
	def HexMath(self, equation, desttype):
		""" Go through the equation, and split it into individual tokens
		Parameters: equation (string) = The math equation to be parsed 
			and compiled.
		desttype (string) = The destination register type. This
			should be DH.
		Returns: (string) = The math equation compiled to Python source code.
			(boolean) = True if the equation was OK.
			(string) = An error message.
			(list) = A list of addresses.
		"""


		# We start by doing some simple syntax checks for common problems.
		leftbracket = equation.count('(')
		rightbracket = equation.count(')')
		if (leftbracket != rightbracket):
			return '', False, _MathErrMsgs['parentheses'], []


		# Now look for characters which we know are not permitted at all
		# in equations.
		for i in self._IllegalChars:
			if (equation.find(i) >= 0):
				return '', False, (_MathErrMsgs['illegalchar'] % i), []

		# First, we need to split the equation string up into pieces 
		# corresponding to addresses, constants, functions, etc. We do
		# this using regular expressions. We have to do this in stages,
		# as we otherwise get definition conflicts, resulting in 
		# incorrect splits.

		# First, split it by addresses, functions, and miscellaneous unique symbols.
		eqlist = re.split(self._HexMathParse, equation)
		# Now, go through the list and classify each as an address, or unknown.
		labellist, addrlist = self._ClassifyHexTokens(eqlist)

		# Next, go through the unclassified ones, and split those by constants.
		constlist, addresses = self._SplitHexLists(labellist, self._HexMathConst)
		addrlist.extend(addresses)

		# Repeat this for the remaining math symbols.
		opslist, addresses = self._SplitHexLists(constlist, self._MathOps)
		addrlist.extend(addresses)


		# Make the equation into a single string. While doing this, also
		# go through the list and see if there is anything left which 
		# has not been classified. These will be some form of incorrect syntax.
		testlist = []
		for i in opslist:
			if (i[1] == 'unknown'):
				return '', False, (_MathErrMsgs['unknownsymb'] % i[0]), addrlist
			elif (i[1] == 'badaddr'):
				return '', False, (_MathErrMsgs['invalidaddr'] % i[0]), addrlist
			testlist.append(i[0])

		# Create the equation string. We also insert the correct type conversion
		# which is compatible with the destination register.
		mathequation = 'int(%s)' % ''.join(testlist)

		testequation = 'TestResult = %s' % mathequation

		# Use the list of data table addresses so we can construct a
		# temporary data table to test the equation with.
		Test_DataTable = {}
		for i in addrlist:
			Test_DataTable[i] = 100

		# Dictionary used by PLC program for its working memory.
		plcdict = {
			'PLC_DataWord' : Test_DataTable,	# Word data table.
			'PLC_BinMathLib' : self._Math,		# Binary math library.
			'TestResult' : 0
			}


		# Try compiling the resulting equation, and see if we get any errors.
		try:
			mathobj = compile(testequation, '<plc code>', 'exec')
		except:
			return '', False, _MathErrMsgs['equacompile'], addrlist

		try:
			exec mathobj in plcdict
		except ZeroDivisionError:
			pass	# This is acceptable for testing.
		except ValueError:
			pass	# This is acceptable for testing.
		except:
			return '', False, _MathErrMsgs['equatest'], addrlist

		# Everthing was OK, so return the equation string.
		return mathequation, True, '', addrlist


	#####################
	def MathHexVal(self, inparam):
		"""Validator for hexadecimal math.
		Expects the following parameters:
			One word parameter of types DH as the destination register.
			One mandatory parameter of 0 or 1 where '1' indicates a one shot is desired.
			An indeterminate number of additional parameters which will be converted into
			a single equation string and compiled into a decimal math statement.
		Returns a destination address, a one-shot parameter, a complete equation string, 
			the original parameters, and True if the parameters were OK. Also, a list 
			of addresses is inserted into the original parameters using the 'addrlist' key.
		inparam: {'inparam1' : 'DH1', 'inparam2' : '1' : 'inparam3' : 'DH10+2'}
		Returns : True, {'inparam1' : 'DH1' , 'inparam2' : '1',  'inparam3' : 'int(PLC_WordTable['DH1']+2)'},
			{'inparam1' : 'DH1', 'inparam2' : '1' : 'inparam3' : 'DH10+2', 
			'addrlist' : ['DH1', 'DH10']}, ['DH1', '1', 'DH10+2']
		"""

		# The first parameter is the destination address, and the second is the
		# one-shot request. 
		try:
			destination = inparam['inparam1']
			oneshot = inparam['inparam2']
			equtest = inparam['inparam3']	# There must be at least 3 parameters.
		except:
			errormsg = {}
			errormsg['errors'] = '%s' % DLCkAddrValidate.ValErrorMsgs['missingparam']
			return False, errormsg, inparam, []


		# The remaining parameters are to be concatenated into a 
		# single equation string
		equationparams = [inparam.get('inparam%s' % x, '') for x in range(3, len(inparam) + 1)]
		equationparams = ' '.join([x for x in equationparams if x != ''])

		# Parameters as a list.
		paramlist = [destination, oneshot, equationparams]


		# Check to see if the destination register is valid.
		desttype = DLCkAddrValidate.WordParamType(destination)
		if (desttype != 'DH'):
			inparam['errors'] = '%s' % DLCkAddrValidate.ValErrorMsgs['invaliddestreg']
			return False, inparam, inparam, paramlist

		# Check if the one shot parameter is a 0 or 1.
		if (not (oneshot in ['0', '1'])):
			inparam['errors'] = '%s' % DLCkAddrValidate.ValErrorMsgs['invalidoneshot']
			return False, inparam, inparam, paramlist


		# Add the formatted equation into the original parameters.
		inparam['equationparams'] = equationparams

		# Now, call the hexadecimal math equation compiler. This comes back with a compiled
		# Python equation, a boolean result code, and an error message.
		equation, result, errormsg, addrlist = self.HexMath(equationparams, desttype)

		# Insert the list of addresses into the original parameters. 
		# This has to include the destination address, so we add it to the list.
		addrlist.append(destination)
		inparam['addrlist'] = addrlist

		# Check if there were any errors.
		if not result:
			inparam['errors'] = '%s' % errormsg
			return False, inparam, inparam, paramlist

		# All paramters are valid.
		result = {}
		result['inparam1'] = '%s' % destination
		result['inparam2'] = '%s' % oneshot
		result['inparam3'] = '%s' % equation
		result['desttype'] = '%s' % desttype


		# Return any error message.
		result['errors'] = '%s' % errormsg

		return True, result, inparam, paramlist


##############################################################################

class MathOps:
	"""Math operations.
	"""

	############################################################
	def __init__(self, math):
		"""Parameters: math (object) - This must implement the standard
		math operations required.
		"""
		self.sin = math.sin
		self.cos = math.cos 
		self.tan = math.tan
		self.asin = math.asin
		self.acos = math.acos
		self.atan = math.atan
		self.log10 = math.log10
		self.log = math.log
		self.sqrt = math.sqrt
		self.radians = math.radians
		self.degrees = math.degrees
		self.pi = math.pi


	############################################################
	def RangeError(self, value, desttype):
		"""Check a value to see if it is within the legal range for
		the selected register type.
		Parameters: value (any value) = The number to be checked.
			desttype (string) = DS, DD, or DF
		Returns False if OK, True if a range error has occurred.
		"""
		# We simply use the function from the address validation module,
		# but with a reversed return value and with the input parameters 
		# swapped.
		return not DLCkAddrValidate.RangeLimit(desttype, value)


	############################################################
	def lshift(self, value, amount):
		""" Shift left.
		Parameters: value (integer) = Number to be shifted.
		amount (integer) = Number of bits to shift by.
		"""
		if (amount > 16):
			amount = 16
		return ((value << amount) & 0xFFFF)

	############################################################
	def rshift(self, value, amount):
		""" Shift right.
		Parameters: value (integer) = Number to be shifted.
		amount (integer) = Number of bits to shift by.
		"""
		if (amount > 16):
			amount = 16
		return ((value >> amount) & 0xFFFF)

	############################################################
	def lrotate(self, value, amount):
		""" Rotate left.
		Parameters: value (integer) = Number to be rotated.
		amount (integer) = Number of bits to rotate by.
		"""
		return (((value << (amount % 16)) | (value >> (16 - (amount % 16)))) & 0xFFFF)

	############################################################
	def rrotate(self, value, amount):
		""" Rotate right.
		Parameters: value (integer) = Number to be rotated.
		amount (integer) = Number of bits to rotate by.
		"""
		return (((value << (16 - (amount % 16))) | (value >> (amount % 16))) & 0xFFFF)


##############################################################################



