##############################################################################
# Project: 	MBLogic
# Module: 	PLCInterp.py
# Purpose: 	Interpreter.
# Language:	Python 2.5
# Date:		09-Dec-2007.
# Author:	M. Griffin.
# Copyright:	2007-2009 - Michael Griffin   <m.os.griffin@gmail.com>
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


########################################################################
class PLCExitCode(Exception):
	"""Create a class to allow exiting from the interpreter.
	The user program raises this exception, which is then caught by
	the interpreter.
	"""
	def __init__(self, exitcode):
		self._ExitCode = exitcode
	def __str__(self):
		return self._ExitCode

############################################################
class SubCallStack:
	"""This class is used to track subroutine calls for diagnostic purposes.
	At each subroutine call, the calling function saves the name of the
	current subroutine and the rung number. When the subroutine
	exits, the variable tracking these are restored. If the program exists 
	unexpectedly, a diagnostic routine can read the top of stack to 
	determine what subroutine was being executed when the error 
	occured. 
	"""

	############################################################
	def __init__(self):
		self.CallStack = []

	############################################################
	def PushSub(self, subname, rungnumber):
		"""Save the subroutine name and rung number.
		subname (string) = name of a subroutine.
		rungnumber (string) = rung number.
		"""
		self.CallStack.append((subname, rungnumber))

	############################################################
	def PopSub(self):
		"""Pops (discards) the current subroutine name and
		rung number from the top of the stack.
		"""
		self.CallStack.pop()

	############################################################
	def StackTop(self):
		"""Returns a tuple containing the name of the current subroutine
		and the rung number from the top of the stack.
		"""
		return self.CallStack[-1]


	############################################################
	def StackInit(self, defaultname):
		"""Initialise the call stack with a default name. This should 
		be the name of the main routine. The rung number is automatically
		set to zero.
		"""
		self.CallStack = [(defaultname, 0)]

PLC_SubCallStack = SubCallStack()

############################################################
# Main PLC interpreter.

class PLCInterp:


	########################################################
	def __init__(self, PlcProgram, BoolDT, WordDT, InstrDT, 
			WordAccessors, Accumulator, BinMath, FloatMath, 
			BCDMath, WordConversions, CounterTimers, SystemScan):

		"""PlcProgram (Python code object) = PLC program to execute.
		BoolDT (dictionary) = Boolean data table.
		WordDT (dictionary) = Word data table.
		InstrDT (dictionary) = Instruction data table.
		WordAccessors (class obg) = Accessor functions for pointers, etc.
		Accumulator (class obj) = Accumulator stack.
		BinMath (std library) = Standard binary math library.
		FloatMath (std library) = Standard floating point math library.
		BCDMath (std library) = Standard BCD math library.
		WordConversions (std library) = Standard misc math library.
		CounterTimers (class obj) = Implementation dependent counter and timer functions.
		SystemScan (class obj) = Implementation dependent system scan functions.
		"""

		# Reason for exit from PLC program.
		self._ExitCode = ''

		# The PLC program.
		self._PLCProgram = PlcProgram
		# Boolean data table.
		self._PLC_DataBool = BoolDT
		# Word data table.
		self._PLC_DataWord = WordDT
		self._PLC_InstrDT = InstrDT
		# Special accessor functions for the word data table.
		self._WordAccessors = WordAccessors
		# PLC accumulator.
		self._PLC_Acc = Accumulator
		# Binary math library.
		self._PLC_BinMath = BinMath
		# Floating point math library
		self._PLC_FloatMath = FloatMath
		# BCD math library.
		self._PLC_BCDMath = BCDMath
		# Misc. word conversions.
		self._PLC_WordConversions = WordConversions
		# Counters and timers.
		self._PLC_CounterTimers = CounterTimers
		# System scan overhead functions.
		self._PLC_SystemScan = SystemScan

		# Dictionary used by PLC program for its working memory.
		self._plcdict = {
			'PLC_RUNGNUMBER' : 0,		# Current rung number.
			'PLC_SUBROUTINE' : 'main',	# Current subroutine name.
			'PLC_CALLSTACK' : PLC_SubCallStack,	# Track subroutine calls.
			'PLC_LOGICSTACK' : [], 		# Logic stack.
			'PLC_STACKTOP' : False, 	# Cache of top of logic stack.
			'PLC_WORD' : 0,			# Temp variable for work values.
			'PLC_TEMP1' : 0,		# Temp variable for work values.
			'PLC_TEMP2' : 0,		# Temp variable for work values.
			'PLC_TEMP3' : 0,		# Temp variable for work values.
			'PLC_TEMP4' : 0,		# Temp variable for work values.
			'PLC_ExitCode' : PLCExitCode,		# Raise an exception to exit the PLC program.
			'PLC_InstrDT' : self._PLC_InstrDT,	# Instruction data table.

			'PLC_ACCU' : self._PLC_Acc,	# Word accumulator stack.
			'PLC_DataBool' : self._PLC_DataBool,	# Boolean data table. 
			'PLC_DataWord' : self._PLC_DataWord,	# Word data table.

			'PLC_WordAccessors' : self._WordAccessors,	# For word data table.
			'PLC_BinMathLib' : self._PLC_BinMath,		# Binary math library.
			'PLC_FloatMathLib' : self._PLC_FloatMath,	# Float math library.
			'PLC_BCDMathLib' : self._PLC_BCDMath, 		# BCD math library.
			'PLC_WordConversions' : self._PLC_WordConversions,	# Misc conversions.
			'PLC_CounterTimers' : self._PLC_CounterTimers	# Counters, timers.
			}


	########################################################
	def GetBoolData(self, boollist):
		"""Return a sub-set of the boolean data table.
		boollist (list) = A list of boolean address labels.
		Returns a dictionary.
		"""
		booldata = {}
		for i in boollist:
			booldata[i] = self._PLC_DataBool[i]
		return booldata

	########################################################
	def GetBoolDataList(self, boollist):
		"""Return a sub-set of the boolean data table.
		This works the same as "GetBoolData", except it returns a
		list instead of a dictionary. The list data is returned in the 
		same order as the input parameter list.
		"""
		return [self._PLC_DataBool[i] for i in boollist]

	########################################################
	def SetBoolData(self, booltable):
		"""Update the boolean data table.
		booltable (dictionary) = An updated boolean data table.
		"""
		self._PLC_DataBool.update(booltable)

	########################################################
	def GetWordData(self, wordlist):
		"""Return a sub-set of the word data table.
		wordlist (list) = A list of word address labels.
		Returns a dictionary.
		"""
		worddata = {}
		for i in wordlist:
			worddata[i] = self._PLC_DataWord[i]
		return worddata

	########################################################
	def GetWordDataList(self, wordlist):
		"""Return a sub-set of the word data table.
		This works the same as "GetWordData", except it returns a
		list instead of a dictionary. The list data is returned in the 
		same order as the input parameter list.
		"""
		return [self._PLC_DataWord[i] for i in wordlist]


	########################################################
	def SetWordData(self, wordtable):
		"""Update the word data table.
		wordtable (dictionary) = An updated word data table.
		"""
		self._PLC_DataWord.update(wordtable)


	########################################################
	def GetInstrDataTable(self):
		"""Return the complete instruction data table.
		Returns a dictionary.
		"""
		return self._PLC_InstrDT

	########################################################
	def SetInstrDataTable(self, instrtable):
		"""Update the complete instruction data table.
		instrtable (dictionary) = An updated instruction data table.
		"""
		self._PLC_InstrDT = instrtable


	########################################################
	def GetExitCode(self):
		"""Return the PLC program exit information, including any errors.
		Return (tuple) = Exit code, subroutine name, rung number.
		"""
		return self._ExitCode, self._plcdict['PLC_SUBROUTINE'], self._plcdict['PLC_RUNGNUMBER']


	########################################################
	def SetPLCProgram(self, plcprog):
		"""Set the current soft logic program to be the compiled code 
		object in the parameter.
		Parameter plcprog (code object) = This is the compiled code object
			that is to be run as the soft logic program.
		"""
		self._PLCProgram = plcprog

	########################################################
	def WarmRestart(self):
		"""Reset whatever data structures are necessary when doing a 
		"warm start" (reinitialising the PLC program while running).
		This should be called after loading a new PLC program while 
		running. It is not required for a "cold start".
		"""
		self._PLC_SystemScan.WarmStart()


	########################################################
	def MainLoop(self):
		"""Main execution loop. Execute the PLC program for one scan.
		"""

		# Update the timers and other period functions.
		self._PLC_SystemScan.ScanUpdate()

		# Initialise the diagnostic variables.
		PLC_SubCallStack.StackInit('main')
		self._plcdict['PLC_RUNGNUMBER'] = 0
		self._ExitCode = 'unexpected_end'

		# Execute entire PLC program once.
		try:
			exec self._PLCProgram in self._plcdict

		# We need to catch the normal exit, which is done through
		# an exception.
		except PLCExitCode, ExitCode:
			self._ExitCode = str(ExitCode)

		# Any other errors are trapped here.
		except:
			self._ExitCode = 'exception_error'



############################################################


