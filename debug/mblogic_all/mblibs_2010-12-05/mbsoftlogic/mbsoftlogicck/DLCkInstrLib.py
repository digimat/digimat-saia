##############################################################################
# Project: 	MBLogic
# Module: 	DLCkInstrLib.py
# Purpose: 	Define instructions strings for a DL Click-like PLC.
# Language:	Python 2.5
# Date:		03-Nov-2008.
# Ver:		25-Aug-2010.
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
This module implements instruction strings which are unique to the PLC model
the soft logic system is being patterned after.
"""

########################################################

# Up Counter CNTU.
DLCkCounterCNTU = ["try:", "\tPLC_TEMP1 = PLC_LOGICSTACK[-1]", "except:", "\tPLC_TEMP1 = False", 
	"PLC_CounterTimers.Counter(PLC_STACKTOP, False, PLC_TEMP1, '%(inparam1)s', %(inparam2)s, True)"]

# Down Counter CNTD.
DLCkCounterCNTD = ["try:", "\tPLC_TEMP1 = PLC_LOGICSTACK[-1]", "except:", "\tPLC_TEMP1 = False",
	"PLC_CounterTimers.Counter(False, PLC_STACKTOP, PLC_TEMP1, '%(inparam1)s', %(inparam2)s, False)"]

# Up-Down Counter UDC.
DLCkCounterUDC = ["try:", "\tPLC_TEMP1 = PLC_LOGICSTACK[-1]", "\tPLC_TEMP2 = PLC_LOGICSTACK[-2]",
	"except:", "\tPLC_TEMP1 = False", "\tPLC_TEMP2 = False",
	"PLC_CounterTimers.Counter(PLC_STACKTOP, PLC_TEMP1, PLC_TEMP2, '%(inparam1)s', %(inparam2)s, True)"]


# On delay timer TMR.
DLCkTimerTMR = ["PLC_CounterTimers.TimerTMR(PLC_STACKTOP, '%(inparam1)s', %(inparam2)s, '%(inparam3)s')"]

# Off delay timer TMROFF.
DLCkTimerTMROFF = ["PLC_CounterTimers.TimerTMROFF(PLC_STACKTOP, '%(inparam1)s', %(inparam2)s, '%(inparam3)s')"]

# On delay accumulating timer TMRA.
DLCkTimerTMRA = ["try:", "\tPLC_TEMP1 = PLC_LOGICSTACK[-1]", "except:", "\tPLC_TEMP1 = False",
	"PLC_CounterTimers.TimerTMRA(PLC_STACKTOP, PLC_TEMP1, '%(inparam1)s', %(inparam2)s, '%(inparam3)s')"]


########################################################

# For/Next loop. The one-shot code has to come first because a "FOR" instruction 
# gets additional indented code automatically appended to the end of it.
DLCkFor = ["PLC_TEMP1 = (not PLC_InstrDT['%(instrindex)s'] or not %(inparam2)s)",
	"PLC_InstrDT['%(instrindex)s'] = PLC_STACKTOP",
	"if (PLC_STACKTOP and PLC_TEMP1):", 
	"\tfor PLC_ForNext in range(%(inparam1)s):"]

# Next is defined as "pass" to allow an empty For loop.
DLCkNext = ["pass"]

########################################################


# Shift register.
DLCkShiftRegister = ["try:", "\tPLC_TEMP1 = PLC_LOGICSTACK[-1]",  "\tPLC_TEMP2 = PLC_LOGICSTACK[-2]", 
	"except:", "\tPLC_TEMP1 = False", "\tPLC_TEMP2 = False", 
"PLC_WordAccessors.ShiftRegister(PLC_STACKTOP, PLC_TEMP1, PLC_InstrDT['%(instrindex)s'], PLC_TEMP2, '%(inparam1)s', '%(inparam2)s')", 
	"PLC_InstrDT['%(instrindex)s'] = PLC_TEMP1"]

########################################################

# Copy Single instruction. This uses a subroutine.
DLCkCopySingle = ["if (PLC_STACKTOP and (not PLC_InstrDT['%(instrindex)s'] or not %(inparam3)s)):", 
	"\tPLC_WordAccessors.CopySingle(%(inparam1)s, '%(sourcetype)s', '%(inparam2)s', '%(desttype)s')",
	"PLC_InstrDT['%(instrindex)s'] = PLC_STACKTOP"]

# Copy Single instruction. This uses direct code instead of a subroutine. All size
# and type checking is done at compile time instead of run time. This is an optimised
# version of DLCkCopySingle for special cases.

# This version handles optimised copy *without* one shot.
DLCkCopySingleNoOns = ["if (PLC_STACKTOP):", 
	"\tPLC_DataWord['%(inparam2)s'] = %(inparam1)s",
	"\tPLC_DataBool['SC43'] = False",
	"\tPLC_DataBool['SC44'] = False"]

# This version handles optimised copy with one shot.
DLCkCopySingleReg = ["if (PLC_STACKTOP and (not PLC_InstrDT['%(instrindex)s'] or not %(inparam3)s)):", 
	"\tPLC_DataWord['%(inparam2)s'] = %(inparam1)s",
	"\tPLC_DataBool['SC43'] = False",
	"\tPLC_DataBool['SC44'] = False",
	"PLC_InstrDT['%(instrindex)s'] = PLC_STACKTOP"]


# Copy Fill instruction.
DLCkCopyFill = ["if (PLC_STACKTOP and (not PLC_InstrDT['%(instrindex)s'] or not %(inparam4)s)):", 
	"\tPLC_WordAccessors.CopyFill(%(inparam1)s, '%(inparam2)s', '%(inparam3)s', '%(desttype)s')",
	"PLC_InstrDT['%(instrindex)s'] = PLC_STACKTOP"]


# Copy Block instruction.
DLCkCopyBlock = ["if (PLC_STACKTOP and (not PLC_InstrDT['%(instrindex)s'] or not %(inparam4)s)):", 
	"\tPLC_WordAccessors.CopyBlock('%(inparam1)s', '%(inparam2)s', '%(inparam3)s', '%(desttype)s')",
	"PLC_InstrDT['%(instrindex)s'] = PLC_STACKTOP"]

# Copy Pack. Pack booleans into a register.
DLCkCopyPack = ["if (PLC_STACKTOP and (not PLC_InstrDT['%(instrindex)s'] or not %(inparam4)s)):", 
	"\tPLC_WordAccessors.CopyPack('%(inparam1)s', '%(inparam2)s', '%(inparam3)s')",
	"PLC_InstrDT['%(instrindex)s'] = PLC_STACKTOP"]

# Copy Unpack. Unpack booleans from a register.
DLCkCopyUnpack = ["if (PLC_STACKTOP and (not PLC_InstrDT['%(instrindex)s'] or not %(inparam4)s)):", 
	"\tPLC_WordAccessors.CopyUnpack('%(inparam1)s', '%(inparam2)s', '%(inparam3)s')",
	"PLC_InstrDT['%(instrindex)s'] = PLC_STACKTOP"]


########################################################

# Boolean table instructions.

# Out multiple bits.
DLCkOutRange = ["PLC_WordAccessors.Setbits(PLC_STACKTOP, '%(inparam1)s', '%(inparam2)s')"]

# Set multiple bits.
DLCkSetRange = ["if PLC_STACKTOP:", 
	"\tPLC_WordAccessors.Setbits(True, '%(inparam1)s', '%(inparam2)s')"]

# Reset multiple bits.
DLCkResetRange = ["if PLC_STACKTOP:", 
	"\tPLC_WordAccessors.Setbits(False, '%(inparam1)s', '%(inparam2)s')"]

# OUT Positive Differentiate for multiple bits. Turn on a range of bits for one scan.
DLCkDiffPDRange = \
["PLC_WordAccessors.Setbits((PLC_STACKTOP and not PLC_InstrDT['%(instrindex)s']), '%(inparam1)s', '%(inparam2)s')",
	"PLC_InstrDT['%(instrindex)s'] = PLC_STACKTOP"]

########################################################

# Search instructions.
# Search ==
DLCkFindEQ = ["if (PLC_STACKTOP and (not PLC_InstrDT['%(instrindex)s'] or not %(inparam6)s)):", 
"\tPLC_WordAccessors.Search(%(inparam1)s,'%(sourcetype)s','%(inparam2)s','%(inparam3)s','%(inparam4)s','%(inparam5)s','==', 0)",
"PLC_InstrDT['%(instrindex)s'] = PLC_STACKTOP"]

# Search == incremental.
DLCkFindIEQ = ["if (PLC_STACKTOP and (not PLC_InstrDT['%(instrindex)s'] or not %(inparam6)s)):", 
"\tPLC_WordAccessors.Search(%(inparam1)s,'%(sourcetype)s','%(inparam2)s','%(inparam3)s','%(inparam4)s','%(inparam5)s','==', 1)",
"PLC_InstrDT['%(instrindex)s'] = PLC_STACKTOP"]

# Search !=
DLCkFindNE = ["if (PLC_STACKTOP and (not PLC_InstrDT['%(instrindex)s'] or not %(inparam6)s)):", 
"\tPLC_WordAccessors.Search(%(inparam1)s,'%(sourcetype)s','%(inparam2)s','%(inparam3)s','%(inparam4)s','%(inparam5)s','!=', 0)",
"PLC_InstrDT['%(instrindex)s'] = PLC_STACKTOP"]

# Search != incremental.
DLCkFindINE = ["if (PLC_STACKTOP and (not PLC_InstrDT['%(instrindex)s'] or not %(inparam6)s)):", 
"\tPLC_WordAccessors.Search(%(inparam1)s,'%(sourcetype)s','%(inparam2)s','%(inparam3)s','%(inparam4)s','%(inparam5)s','!=', 1)",
"PLC_InstrDT['%(instrindex)s'] = PLC_STACKTOP"]

# Search >
DLCkFindGT = ["if (PLC_STACKTOP and (not PLC_InstrDT['%(instrindex)s'] or not %(inparam6)s)):", 
"\tPLC_WordAccessors.Search(%(inparam1)s,'%(sourcetype)s','%(inparam2)s','%(inparam3)s','%(inparam4)s','%(inparam5)s','>', 0)",
"PLC_InstrDT['%(instrindex)s'] = PLC_STACKTOP"]

# Search > incremental.
DLCkFindIGT = ["if (PLC_STACKTOP and (not PLC_InstrDT['%(instrindex)s'] or not %(inparam6)s)):", 
"\tPLC_WordAccessors.Search(%(inparam1)s,'%(sourcetype)s','%(inparam2)s','%(inparam3)s','%(inparam4)s','%(inparam5)s','>', 1)",
"PLC_InstrDT['%(instrindex)s'] = PLC_STACKTOP"]

# Search >=
DLCkFindGE = ["if (PLC_STACKTOP and (not PLC_InstrDT['%(instrindex)s'] or not %(inparam6)s)):", 
"\tPLC_WordAccessors.Search(%(inparam1)s,'%(sourcetype)s','%(inparam2)s','%(inparam3)s','%(inparam4)s','%(inparam5)s','>=', 0)",
"PLC_InstrDT['%(instrindex)s'] = PLC_STACKTOP"]

# Search >= incremental.
DLCkFindIGE = ["if (PLC_STACKTOP and (not PLC_InstrDT['%(instrindex)s'] or not %(inparam6)s)):", 
"\tPLC_WordAccessors.Search(%(inparam1)s,'%(sourcetype)s','%(inparam2)s','%(inparam3)s','%(inparam4)s','%(inparam5)s','>=', 1)",
"PLC_InstrDT['%(instrindex)s'] = PLC_STACKTOP"]

# Search <
DLCkFindLT = ["if (PLC_STACKTOP and (not PLC_InstrDT['%(instrindex)s'] or not %(inparam6)s)):", 
"\tPLC_WordAccessors.Search(%(inparam1)s,'%(sourcetype)s','%(inparam2)s','%(inparam3)s','%(inparam4)s','%(inparam5)s','<', 0)",
"PLC_InstrDT['%(instrindex)s'] = PLC_STACKTOP"]

# Search < incremental.
DLCkFindILT = ["if (PLC_STACKTOP and (not PLC_InstrDT['%(instrindex)s'] or not %(inparam6)s)):", 
"\tPLC_WordAccessors.Search(%(inparam1)s,'%(sourcetype)s','%(inparam2)s','%(inparam3)s','%(inparam4)s','%(inparam5)s','<', 1)",
"PLC_InstrDT['%(instrindex)s'] = PLC_STACKTOP"]

# Search <=
DLCkFindLE = ["if (PLC_STACKTOP and (not PLC_InstrDT['%(instrindex)s'] or not %(inparam6)s)):", 
"\tPLC_WordAccessors.Search(%(inparam1)s,'%(sourcetype)s','%(inparam2)s','%(inparam3)s','%(inparam4)s','%(inparam5)s','<=', 0)",
"PLC_InstrDT['%(instrindex)s'] = PLC_STACKTOP"]

# Search <= incremental.
DLCkFindILE = ["if (PLC_STACKTOP and (not PLC_InstrDT['%(instrindex)s'] or not %(inparam6)s)):", 
"\tPLC_WordAccessors.Search(%(inparam1)s,'%(sourcetype)s','%(inparam2)s','%(inparam3)s','%(inparam4)s','%(inparam5)s','<=', 1)",
"PLC_InstrDT['%(instrindex)s'] = PLC_STACKTOP"]


########################################################

# Math instructions.
DLCkMath = ["if (PLC_STACKTOP and (not PLC_InstrDT['%(instrindex)s'] or not %(inparam2)s)):", 
	"\tPLC_DataBool['SC40'] = False", "\tPLC_DataBool['SC43'] = False", "\tPLC_DataBool['SC46'] = False",
	"\ttry:",
	"\t\tPLC_Temp1 = %(inparam3)s",

	"\t\tif (PLC_BinMathLib.RangeError(PLC_Temp1, '%(desttype)s')):",
	"\t\t\tPLC_DataBool['SC43'] = True",
	"\t\telse:",
	"\t\t\tPLC_DataWord['%(inparam1)s'] = PLC_Temp1",

	"\texcept ZeroDivisionError:", 
	"\t\tPLC_DataBool['SC40'] = True",
	"\texcept:", "\t\tPLC_DataBool['SC46'] = True",
	"PLC_InstrDT['%(instrindex)s'] = PLC_STACKTOP"]


# Sum registers instruction. This is implemented as a separate instruction rather 
# than integrated into the math instruction because of the difficulty of handling it there.
DLCkSum = ["if (PLC_STACKTOP and (not PLC_InstrDT['%(instrindex)s'] or not %(inparam4)s)):", 
	"\tPLC_WordAccessors.SumRegisters('%(inparam1)s', '%(inparam2)s', '%(inparam3)s', '%(desttype)s')",
	"PLC_InstrDT['%(instrindex)s'] = PLC_STACKTOP"]

########################################################

