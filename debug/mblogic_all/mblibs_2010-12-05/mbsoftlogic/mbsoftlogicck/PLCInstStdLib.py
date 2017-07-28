##############################################################################
# Project: 	MBLogic
# Module: 	PLCInstrStdLib.py
# Purpose: 	Generic soft logic instruction library.
# Language:	Python 2.5
# Date:		18-May-2008.
# Author:	M. Griffin.
# Copyright:	2008 - Michael Griffin   <m.os.griffin@gmail.com>
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


############################################################
# General system instructions.

# Source code comment (convert to a Python comment).
PLCComment = ["#"]

# Start of a new rung.
PLCNetwork = ["PLC_RUNGNUMBER = %(inparam1)s", "PLC_LOGICSTACK = [False]", "PLC_STACKTOP = False"]

############################################################

# Boolean instructions taking a single parameter.

# AND parameter with the logic stack.
PLCAnd = ["PLC_STACKTOP = PLC_STACKTOP and (PLC_DataBool['%(inparam1)s'])"]

# AND NOT parameter with the logic stack.
PLCAndNot = ["PLC_STACKTOP = PLC_STACKTOP and (not PLC_DataBool['%(inparam1)s'])"]

# OR parameter with the logic stack.
PLCOr = ["PLC_STACKTOP = PLC_STACKTOP or PLC_DataBool['%(inparam1)s']"]

# OR NOT parameter with the logic stack.
PLCOrNot = ["PLC_STACKTOP = PLC_STACKTOP or (not PLC_DataBool['%(inparam1)s'])"]

# Output the top of the logic stack to the parameter.
PLCOut = ["PLC_DataBool['%(inparam1)s'] = PLC_STACKTOP"]

# RESET the parameter if the top of the logic stack is true.
PLCOutReset = ["if PLC_STACKTOP: PLC_DataBool['%(inparam1)s'] = False"]

# SET the parameter if the top of the logic stack is true.
PLCOutSet = ["if PLC_STACKTOP: PLC_DataBool['%(inparam1)s'] = True"]

# Push the parameter onto the top of the logic stack.
PLCStr = ["PLC_LOGICSTACK.append(PLC_STACKTOP)", "PLC_STACKTOP = PLC_DataBool['%(inparam1)s']"]

# Not and push the parameter onto the top of the logic stack.
PLCStrNot = ["PLC_LOGICSTACK.append(PLC_STACKTOP)", "PLC_STACKTOP = not PLC_DataBool['%(inparam1)s']"]

# OR all rungs with this address in the program to turn on the coil. This requires
# additional support from the interpreter to work correctly. The address must be
# automatically reset at the start of each scan.
PLCOutOr = PLCOutSet

############################################################
# Boolean instructions taking no parameters.

# AND the top two elements of the logic stack.
PLCAndStr = ["try:", "\tPLC_STACKTOP = PLC_STACKTOP and PLC_LOGICSTACK[-1]", 
	"\tPLC_LOGICSTACK.pop()", "except:", "\tPLC_STACKTOP = False"]

# OR the top two elements of the logic stack.
PLCOrStr = ["try:", "\tPLC_STACKTOP = PLC_STACKTOP or PLC_LOGICSTACK[-1]", 
	"\tPLC_LOGICSTACK.pop()", "except:", "\tPLC_STACKTOP = False"]

# NOT the top of the logic stack.
PLCNot = ["PLC_STACKTOP = (not PLC_STACKTOP)"]

############################################################


# Differentiation instructions. These use the systems private instruction 
# data table to store last state information outside of the normal PLC data tables.

# Store Positive Differentiate. AND the previous state of the parameter with 
# the current state, and PUSH the result onto the logic stack.
PLCDiffStorPD = ["PLC_LOGICSTACK.append(PLC_STACKTOP)", 
	"PLC_STACKTOP = PLC_DataBool['%(inparam1)s'] and not PLC_InstrDT['%(instrindex)s']", 
	"PLC_InstrDT['%(instrindex)s'] = PLC_DataBool['%(inparam1)s']"]


# Store Negative Differentiate. AND the previous state of the parameter with 
# the inverse of the current state, and PUSH the result onto the logic stack.
PLCDiffStorND = ["PLC_LOGICSTACK.append(PLC_STACKTOP)", 
	"PLC_STACKTOP = (not PLC_DataBool['%(inparam1)s']) and PLC_InstrDT['%(instrindex)s']", 
	"PLC_InstrDT['%(instrindex)s'] = PLC_DataBool['%(inparam1)s']"]

# OR Positive Differentiate. AND the previous state of the parameter with 
# the current state, and OR the result with the logic stack.
PLCDiffOrPD = ["PLC_STACKTOP = PLC_STACKTOP or (PLC_DataBool['%(inparam1)s'] and not PLC_InstrDT['%(instrindex)s'])",
	"PLC_InstrDT['%(instrindex)s'] = PLC_DataBool['%(inparam1)s']"]

# OR Negative Differentiate. AND the previous state of the parameter with 
# the inverse of the current state, and OR the result with the logic stack.
PLCDiffOrND = ["PLC_STACKTOP = PLC_STACKTOP or (not PLC_DataBool['%(inparam1)s'] and PLC_InstrDT['%(instrindex)s'])",
	"PLC_InstrDT['%(instrindex)s'] = PLC_DataBool['%(inparam1)s']"]

# AND Positive Differentiate. AND the previous state of the parameter with 
# the current state, and AND the result with the logic stack.
PLCDiffAndPD = ["PLC_STACKTOP = PLC_STACKTOP and (PLC_DataBool['%(inparam1)s'] and not PLC_InstrDT['%(instrindex)s'])",
	"PLC_InstrDT['%(instrindex)s'] = PLC_DataBool['%(inparam1)s']"]

# AND Negative Differentiate. AND the previous state of the parameter with 
# the inverse of the current state, and AND the result with the logic stack.
PLCDiffAndND = ["PLC_STACKTOP = PLC_STACKTOP and (not PLC_DataBool['%(inparam1)s'] and PLC_InstrDT['%(instrindex)s'])",
	"PLC_InstrDT['%(instrindex)s'] = PLC_DataBool['%(inparam1)s']"]

# OUT Positive Differentiate. AND the previous state of the logic stack with
# the inverse of the current state, and output the result to the parameter.
PLCDiffPD = ["PLC_DataBool['%(inparam1)s'] = PLC_STACKTOP and not PLC_InstrDT['%(instrindex)s']",
	"PLC_InstrDT['%(instrindex)s'] = PLC_STACKTOP"]

############################################################
# PLC control instructions.
PLCEnd = ["raise PLC_ExitCode('normal_end_requested')"]
PLCEndCond = ["if PLC_STACKTOP: raise PLC_ExitCode('normal_end_requested')"]
PLCNop = ["# NOP"]
PLCResetWD = ["reset watch dog not implemented"]
PLCStop = ["raise PLC_ExitCode('stop_requested')"]


########################################################################

# Program control.

# Declare a subroutine heading. PLC_RUNGNUMBER has to be set to "global" to make
# the system use the variable from the main program. PLC_STACKTOP is created so
# that we don't get an exception if someone doesn't create a rung first.
PLCSubrDef = ["def PLC_Subroutine_%(inparam1)s():", 
	"\tglobal PLC_RUNGNUMBER", "\tglobal PLC_SUBROUTINE", 
	"\tPLC_RUNGNUMBER = 0", "\tPLC_SUBROUTINE = '%(inparam1)s'",
	"\tPLC_STACKTOP = False"]
# Call a subroutine.
PLCSubrCall = ["if PLC_STACKTOP:", 
	"\tPLC_CALLSTACK.PushSub(PLC_SUBROUTINE, PLC_RUNGNUMBER)", 
	"\tPLC_Subroutine_%(inparam1)s()"]
# Return from a subroutine.
PLCSubrRet = ["PLC_SUBROUTINE, PLC_RUNGNUMBER = PLC_CALLSTACK.StackTop()", 
	"PLC_CALLSTACK.PopSub()", "return"]
# Conditional return from a subroutine.
PLCSubrRetCond = ["if PLC_STACKTOP:", 
	"\tPLC_SUBROUTINE, PLC_RUNGNUMBER = PLC_CALLSTACK.StackTop()", 
	"\tPLC_CALLSTACK.PopSub()", "\treturn"]


########################################################################

# Comparitive Boolean instructions. Compare the values of two words.
# Both values are assumed to be of compatible types.

# Compare two numbers for equality and push the logical result to the top of the logic stack.
PLCCompStrEqu = ["PLC_LOGICSTACK.append(PLC_STACKTOP)", "PLC_STACKTOP = %(inparam1)s == %(inparam2)s"]

# Compare two numbers for not equality and push the logical result to the top of the logic stack.
PLCCompStrNeq = ["PLC_LOGICSTACK.append(PLC_STACKTOP)", "PLC_STACKTOP = %(inparam1)s != %(inparam2)s"]

# Compare two numbers for 1st is GT 2nd, and push the logical result to the top of the logic stack.
PLCCompStrGT = ["PLC_LOGICSTACK.append(PLC_STACKTOP)", "PLC_STACKTOP = %(inparam1)s > %(inparam2)s"]

# Compare two numbers for 1st is GT or EQ 2nd, and push the logical result to the top of the logic stack.
PLCCompStrGE = ["PLC_LOGICSTACK.append(PLC_STACKTOP)", "PLC_STACKTOP = %(inparam1)s >= %(inparam2)s"]

# Compare two numbers for 1st is LT 2nd, and push the logical result to the top of the logic stack.
PLCCompStrLT = ["PLC_LOGICSTACK.append(PLC_STACKTOP)", "PLC_STACKTOP = %(inparam1)s < %(inparam2)s"]

# Compare two numbers for 1st is LT or EQ 2nd, and push the logical result to the top of the logic stack.
PLCCompStrLE = ["PLC_LOGICSTACK.append(PLC_STACKTOP)", "PLC_STACKTOP = %(inparam1)s <= %(inparam2)s"]


# Compare two numbers for equality and OR the result with the logic stack.
PLCCompOrEqu = ["PLC_STACKTOP = PLC_STACKTOP or (%(inparam1)s == %(inparam2)s)"]

# Compare two numbers for not equality and OR the result with the logic stack.
PLCCompOrNeq = ["PLC_STACKTOP = PLC_STACKTOP or (%(inparam1)s != %(inparam2)s)"]

# Compare two numbers for 1st is GT 2nd, and OR the result with the logic stack.
PLCCompOrGT = ["PLC_STACKTOP = PLC_STACKTOP or (%(inparam1)s > %(inparam2)s)"]

# Compare two numbers for 1st is GT or EQ 2nd, and OR the result with the logic stack.
PLCCompOrGE = ["PLC_STACKTOP = PLC_STACKTOP or (%(inparam1)s >= %(inparam2)s)"]

# Compare two numbers for 1st is LT 2nd, and OR the result with the logic stack.
PLCCompOrLT = ["PLC_STACKTOP = PLC_STACKTOP or (%(inparam1)s < %(inparam2)s)"]

# Compare two numbers for 1st is LT or EQ 2nd, and OR the result with the logic stack.
PLCCompOrLE = ["PLC_STACKTOP = PLC_STACKTOP or (%(inparam1)s <= %(inparam2)s)"]


# Compare two numbers for equality and AND the result with the logic stack.
PLCCompAndEqu = ["PLC_STACKTOP = PLC_STACKTOP and (%(inparam1)s == %(inparam2)s)"]

# Compare two numbers for not equality and AND the result with the logic stack.
PLCCompAndNeq = ["PLC_STACKTOP = PLC_STACKTOP and (%(inparam1)s != %(inparam2)s)"]

# Compare two numbers for 1st is GT or EQ 2nd, and AND the result with the logic stack.
PLCCompAndGE = ["PLC_STACKTOP = PLC_STACKTOP and (%(inparam1)s >= %(inparam2)s)"]

# Compare two numbers for 1st is GT 2nd, and AND the result with the logic stack.
PLCCompAndGT = ["PLC_STACKTOP = PLC_STACKTOP and (%(inparam1)s > %(inparam2)s)"]

# Compare two numbers for 1st is LT or EQ 2nd, and AND the result with the logic stack.
PLCCompAndLE = ["PLC_STACKTOP = PLC_STACKTOP and (%(inparam1)s <= %(inparam2)s)"]

# Compare two numbers for 1st is LT 2nd, and AND the result with the logic stack.
PLCCompAndLT = ["PLC_STACKTOP = PLC_STACKTOP and (%(inparam1)s < %(inparam2)s)"]

########################################################################

