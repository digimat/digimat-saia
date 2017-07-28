##############################################################################
# Project: 	MBLogic
# Module: 	DLCkInstructions.py
# Purpose: 	Define instructions for a DL Click-like PLC.
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

import DLCkAddrValidate as AddrVal
import DLCkInstrLib
import DLCkLibs

import PLCInstStdLib

##############################################################################


# List to hold instruction definitions.
InstrDefList = [
# The following code is automatically generated.
# Comment line
{'opcode' : '//', 'description' : 'Comment line', 
	'instruction' : PLCInstStdLib.PLCComment, 'type' : 'instr', 'class' : 'comment', 
	'instrdefault' : None, 'params' : -1, 'validator' : AddrVal.CommentStr, 
	'ladsymb' : 'none', 'monitor' : 'none'},
# Network
{'opcode' : 'NETWORK', 'description' : 'Network', 
	'instruction' : PLCInstStdLib.PLCNetwork, 'type' : 'instr', 'class' : 'rung', 
	'instrdefault' : None, 'params' : 1, 'validator' : AddrVal.IntConstant, 
	'ladsymb' : 'none', 'monitor' : 'none'},
# AND bit with top of logic stack
{'opcode' : 'AND', 'description' : 'AND bit with top of logic stack', 
	'instruction' : PLCInstStdLib.PLCAnd, 'type' : 'instr', 'class' : 'and', 
	'instrdefault' : None, 'params' : 1, 'validator' : AddrVal.BoolXYCTCTSC, 
	'ladsymb' : 'noc', 'monitor' : 'bool'},
# AND NOT bit with top of logic stack
{'opcode' : 'ANDN', 'description' : 'AND NOT bit with top of logic stack', 
	'instruction' : PLCInstStdLib.PLCAndNot, 'type' : 'instr', 'class' : 'and', 
	'instrdefault' : None, 'params' : 1, 'validator' : AddrVal.BoolXYCTCTSC, 
	'ladsymb' : 'ncc', 'monitor' : 'booln'},
# AND top two values on logic stack
{'opcode' : 'ANDSTR', 'description' : 'AND top two values on logic stack', 
	'instruction' : PLCInstStdLib.PLCAndStr, 'type' : 'instr', 'class' : 'andstr', 
	'instrdefault' : None, 'params' : 0, 'validator' : AddrVal.NoParams, 
	'ladsymb' : 'andstr', 'monitor' : 'bool'},
# OR bit with top of logic stack
{'opcode' : 'OR', 'description' : 'OR bit with top of logic stack', 
	'instruction' : PLCInstStdLib.PLCOr, 'type' : 'instr', 'class' : 'or', 
	'instrdefault' : None, 'params' : 1, 'validator' : AddrVal.BoolXYCTCTSC, 
	'ladsymb' : 'noc', 'monitor' : 'bool'},
# OR NOT bit with top of logic stack
{'opcode' : 'ORN', 'description' : 'OR NOT bit with top of logic stack', 
	'instruction' : PLCInstStdLib.PLCOrNot, 'type' : 'instr', 'class' : 'or', 
	'instrdefault' : None, 'params' : 1, 'validator' : AddrVal.BoolXYCTCTSC, 
	'ladsymb' : 'ncc', 'monitor' : 'booln'},
# OR top two values on logic stack
{'opcode' : 'ORSTR', 'description' : 'OR top two values on logic stack', 
	'instruction' : PLCInstStdLib.PLCOrStr, 'type' : 'instr', 'class' : 'orstr', 
	'instrdefault' : None, 'params' : 0, 'validator' : AddrVal.NoParams, 
	'ladsymb' : 'orstr', 'monitor' : 'bool'},
# Output logic stack to bit
{'opcode' : 'OUT', 'description' : 'Output logic stack to bit', 
	'instruction' : PLCInstStdLib.PLCOut, 'type' : 'instr', 'class' : 'output1', 
	'instrdefault' : None, 'params' : 1, 'validator' : AddrVal.BoolYC, 
	'ladsymb' : 'out', 'monitor' : 'bool'},
# Output logic stack to multiple bits
{'opcode' : 'OUT', 'description' : 'Output logic stack to multiple bits', 
	'instruction' : DLCkInstrLib.DLCkOutRange, 'type' : 'instr', 'class' : 'output1', 
	'instrdefault' : None, 'params' : 2, 'validator' : AddrVal.BoolYC_YC, 
	'ladsymb' : 'out2', 'monitor' : 'bool'},
# Output logic stack one shot to multiple bits
{'opcode' : 'PD', 'description' : 'Output logic stack one shot to multiple bits', 
	'instruction' : DLCkInstrLib.DLCkDiffPDRange, 'type' : 'instr', 'class' : 'output1', 
	'instrdefault' : False, 'params' : 2, 'validator' : AddrVal.BoolYC_YC, 
	'ladsymb' : 'pd2', 'monitor' : 'bool'},
# Output logic stack one shot
{'opcode' : 'PD', 'description' : 'Output logic stack one shot', 
	'instruction' : PLCInstStdLib.PLCDiffPD, 'type' : 'instr', 'class' : 'output1', 
	'instrdefault' : False, 'params' : 1, 'validator' : AddrVal.BoolYC, 
	'ladsymb' : 'pd', 'monitor' : 'bool'},
# Reset bit if logic stack true
{'opcode' : 'RST', 'description' : 'Reset bit if logic stack true', 
	'instruction' : PLCInstStdLib.PLCOutReset, 'type' : 'instr', 'class' : 'output1', 
	'instrdefault' : None, 'params' : 1, 'validator' : AddrVal.BoolYC, 
	'ladsymb' : 'rst', 'monitor' : 'bool'},
# Reset multiple bits if logic stack true
{'opcode' : 'RST', 'description' : 'Reset multiple bits if logic stack true', 
	'instruction' : DLCkInstrLib.DLCkResetRange, 'type' : 'instr', 'class' : 'output1', 
	'instrdefault' : None, 'params' : 2, 'validator' : AddrVal.BoolYC_YC, 
	'ladsymb' : 'rst2', 'monitor' : 'bool'},
# Set bit if logic stack true
{'opcode' : 'SET', 'description' : 'Set bit if logic stack true', 
	'instruction' : PLCInstStdLib.PLCOutSet, 'type' : 'instr', 'class' : 'output1', 
	'instrdefault' : None, 'params' : 1, 'validator' : AddrVal.BoolYC, 
	'ladsymb' : 'set', 'monitor' : 'bool'},
# Set multiple bits if logic stack true
{'opcode' : 'SET', 'description' : 'Set multiple bits if logic stack true', 
	'instruction' : DLCkInstrLib.DLCkSetRange, 'type' : 'instr', 'class' : 'output1', 
	'instrdefault' : None, 'params' : 2, 'validator' : AddrVal.BoolYC_YC, 
	'ladsymb' : 'set2', 'monitor' : 'bool'},
# Store bit onto logic stack
{'opcode' : 'STR', 'description' : 'Store bit onto logic stack', 
	'instruction' : PLCInstStdLib.PLCStr, 'type' : 'instr', 'class' : 'store', 
	'instrdefault' : None, 'params' : 1, 'validator' : AddrVal.BoolXYCTCTSC, 
	'ladsymb' : 'noc', 'monitor' : 'bool'},
# Store NOT bit onto logic stack
{'opcode' : 'STRN', 'description' : 'Store NOT bit onto logic stack', 
	'instruction' : PLCInstStdLib.PLCStrNot, 'type' : 'instr', 'class' : 'store', 
	'instrdefault' : None, 'params' : 1, 'validator' : AddrVal.BoolXYCTCTSC, 
	'ladsymb' : 'ncc', 'monitor' : 'booln'},
# AND if parm1 equals param2
{'opcode' : 'ANDE', 'description' : 'AND if parm1 equals param2', 
	'instruction' : PLCInstStdLib.PLCCompAndEqu, 'type' : 'instr', 'class' : 'and', 
	'instrdefault' : None, 'params' : 2, 'validator' : AddrVal.CompareWordWord, 
	'ladsymb' : 'compeq', 'monitor' : '='},
# AND if parm1 >= parm2
{'opcode' : 'ANDGE', 'description' : 'AND if parm1 >= parm2', 
	'instruction' : PLCInstStdLib.PLCCompAndGE, 'type' : 'instr', 'class' : 'and', 
	'instrdefault' : None, 'params' : 2, 'validator' : AddrVal.CompareWordWord, 
	'ladsymb' : 'compge', 'monitor' : '>='},
# AND if parm1 > parm2
{'opcode' : 'ANDGT', 'description' : 'AND if parm1 > parm2', 
	'instruction' : PLCInstStdLib.PLCCompAndGT, 'type' : 'instr', 'class' : 'and', 
	'instrdefault' : None, 'params' : 2, 'validator' : AddrVal.CompareWordWord, 
	'ladsymb' : 'compgt', 'monitor' : '>'},
# AND if parm1 <= parm2
{'opcode' : 'ANDLE', 'description' : 'AND if parm1 <= parm2', 
	'instruction' : PLCInstStdLib.PLCCompAndLE, 'type' : 'instr', 'class' : 'and', 
	'instrdefault' : None, 'params' : 2, 'validator' : AddrVal.CompareWordWord, 
	'ladsymb' : 'comple', 'monitor' : '<='},
# AND if parm1 < parm2
{'opcode' : 'ANDLT', 'description' : 'AND if parm1 < parm2', 
	'instruction' : PLCInstStdLib.PLCCompAndLT, 'type' : 'instr', 'class' : 'and', 
	'instrdefault' : None, 'params' : 2, 'validator' : AddrVal.CompareWordWord, 
	'ladsymb' : 'complt', 'monitor' : '<'},
# AND if parm1 is not equal to parm2
{'opcode' : 'ANDNE', 'description' : 'AND if parm1 is not equal to parm2', 
	'instruction' : PLCInstStdLib.PLCCompAndNeq, 'type' : 'instr', 'class' : 'and', 
	'instrdefault' : None, 'params' : 2, 'validator' : AddrVal.CompareWordWord, 
	'ladsymb' : 'compneq', 'monitor' : '!='},
# OR if parm1 equals parm2
{'opcode' : 'ORE', 'description' : 'OR if parm1 equals parm2', 
	'instruction' : PLCInstStdLib.PLCCompOrEqu, 'type' : 'instr', 'class' : 'or', 
	'instrdefault' : None, 'params' : 2, 'validator' : AddrVal.CompareWordWord, 
	'ladsymb' : 'compeq', 'monitor' : '='},
# OR if parm1 >= parm2
{'opcode' : 'ORGE', 'description' : 'OR if parm1 >= parm2', 
	'instruction' : PLCInstStdLib.PLCCompOrGE, 'type' : 'instr', 'class' : 'or', 
	'instrdefault' : None, 'params' : 2, 'validator' : AddrVal.CompareWordWord, 
	'ladsymb' : 'compge', 'monitor' : '>='},
# OR if parm1 > parm2
{'opcode' : 'ORGT', 'description' : 'OR if parm1 > parm2', 
	'instruction' : PLCInstStdLib.PLCCompOrGT, 'type' : 'instr', 'class' : 'or', 
	'instrdefault' : None, 'params' : 2, 'validator' : AddrVal.CompareWordWord, 
	'ladsymb' : 'compgt', 'monitor' : '>'},
# OR if parm1 <= parm2
{'opcode' : 'ORLE', 'description' : 'OR if parm1 <= parm2', 
	'instruction' : PLCInstStdLib.PLCCompOrLE, 'type' : 'instr', 'class' : 'or', 
	'instrdefault' : None, 'params' : 2, 'validator' : AddrVal.CompareWordWord, 
	'ladsymb' : 'comple', 'monitor' : '<='},
# OR if parm1 < parm2
{'opcode' : 'ORLT', 'description' : 'OR if parm1 < parm2', 
	'instruction' : PLCInstStdLib.PLCCompOrLT, 'type' : 'instr', 'class' : 'or', 
	'instrdefault' : None, 'params' : 2, 'validator' : AddrVal.CompareWordWord, 
	'ladsymb' : 'complt', 'monitor' : '<'},
# OR if parm1 is not equal to parm2
{'opcode' : 'ORNE', 'description' : 'OR if parm1 is not equal to parm2', 
	'instruction' : PLCInstStdLib.PLCCompOrNeq, 'type' : 'instr', 'class' : 'or', 
	'instrdefault' : None, 'params' : 2, 'validator' : AddrVal.CompareWordWord, 
	'ladsymb' : 'compneq', 'monitor' : '!='},
# STR if parm1 equals parm2
{'opcode' : 'STRE', 'description' : 'STR if parm1 equals parm2', 
	'instruction' : PLCInstStdLib.PLCCompStrEqu, 'type' : 'instr', 'class' : 'store', 
	'instrdefault' : None, 'params' : 2, 'validator' : AddrVal.CompareWordWord, 
	'ladsymb' : 'compeq', 'monitor' : '='},
# STR if parm1 >= parm2
{'opcode' : 'STRGE', 'description' : 'STR if parm1 >= parm2', 
	'instruction' : PLCInstStdLib.PLCCompStrGE, 'type' : 'instr', 'class' : 'store', 
	'instrdefault' : None, 'params' : 2, 'validator' : AddrVal.CompareWordWord, 
	'ladsymb' : 'compge', 'monitor' : '>='},
# STR if parm1 > parm2
{'opcode' : 'STRGT', 'description' : 'STR if parm1 > parm2', 
	'instruction' : PLCInstStdLib.PLCCompStrGT, 'type' : 'instr', 'class' : 'store', 
	'instrdefault' : None, 'params' : 2, 'validator' : AddrVal.CompareWordWord, 
	'ladsymb' : 'compgt', 'monitor' : '>'},
# STR if parm1 <= parm2
{'opcode' : 'STRLE', 'description' : 'STR if parm1 <= parm2', 
	'instruction' : PLCInstStdLib.PLCCompStrLE, 'type' : 'instr', 'class' : 'store', 
	'instrdefault' : None, 'params' : 2, 'validator' : AddrVal.CompareWordWord, 
	'ladsymb' : 'comple', 'monitor' : '<='},
# STR if parm1 < parm2
{'opcode' : 'STRLT', 'description' : 'STR if parm1 < parm2', 
	'instruction' : PLCInstStdLib.PLCCompStrLT, 'type' : 'instr', 'class' : 'store', 
	'instrdefault' : None, 'params' : 2, 'validator' : AddrVal.CompareWordWord, 
	'ladsymb' : 'complt', 'monitor' : '<'},
# STR if parm1 is not equal to parm2
{'opcode' : 'STRNE', 'description' : 'STR if parm1 is not equal to parm2', 
	'instruction' : PLCInstStdLib.PLCCompStrNeq, 'type' : 'instr', 'class' : 'store', 
	'instrdefault' : None, 'params' : 2, 'validator' : AddrVal.CompareWordWord, 
	'ladsymb' : 'compneq', 'monitor' : '!='},
# Copy a value to a register no-oneshot
{'opcode' : 'COPY', 'description' : 'Copy a value to a register no-oneshot', 
	'instruction' : DLCkInstrLib.DLCkCopySingleNoOns, 'type' : 'instr', 'class' : 'output1', 
	'instrdefault' : False, 'params' : 3, 'validator' : AddrVal.CopySingleNoOns, 
	'ladsymb' : 'copy', 'monitor' : 'none'},
# Copy a value to a register without checks
{'opcode' : 'COPY', 'description' : 'Copy a value to a register without checks', 
	'instruction' : DLCkInstrLib.DLCkCopySingleReg, 'type' : 'instr', 'class' : 'output1', 
	'instrdefault' : False, 'params' : 3, 'validator' : AddrVal.CopySingleReg, 
	'ladsymb' : 'copy', 'monitor' : 'none'},
# Copy a single value to a register
{'opcode' : 'COPY', 'description' : 'Copy a single value to a register', 
	'instruction' : DLCkInstrLib.DLCkCopySingle, 'type' : 'instr', 'class' : 'output1', 
	'instrdefault' : False, 'params' : 3, 'validator' : AddrVal.CopySingle, 
	'ladsymb' : 'copy', 'monitor' : 'none'},
# Copy a block of data
{'opcode' : 'CPYBLK', 'description' : 'Copy a block of data', 
	'instruction' : DLCkInstrLib.DLCkCopyBlock, 'type' : 'instr', 'class' : 'output1', 
	'instrdefault' : False, 'params' : 4, 'validator' : AddrVal.CopyBlock, 
	'ladsymb' : 'cpyblk', 'monitor' : 'none'},
# Fill a block of data
{'opcode' : 'FILL', 'description' : 'Fill a block of data', 
	'instruction' : DLCkInstrLib.DLCkCopyFill, 'type' : 'instr', 'class' : 'output1', 
	'instrdefault' : False, 'params' : 4, 'validator' : AddrVal.CopyFill, 
	'ladsymb' : 'fill', 'monitor' : 'none'},
# Pack bits into a register
{'opcode' : 'PACK', 'description' : 'Pack bits into a register', 
	'instruction' : DLCkInstrLib.DLCkCopyPack, 'type' : 'instr', 'class' : 'output1', 
	'instrdefault' : False, 'params' : 4, 'validator' : AddrVal.CopyPack, 
	'ladsymb' : 'pack', 'monitor' : 'none'},
# Unpack bits from a register
{'opcode' : 'UNPACK', 'description' : 'Unpack bits from a register', 
	'instruction' : DLCkInstrLib.DLCkCopyUnpack, 'type' : 'instr', 'class' : 'output1', 
	'instrdefault' : False, 'params' : 4, 'validator' : AddrVal.CopyUnpack, 
	'ladsymb' : 'unpack', 'monitor' : 'none'},
# Count down
{'opcode' : 'CNTD', 'description' : 'Count down', 
	'instruction' : DLCkInstrLib.DLCkCounterCNTD, 'type' : 'instr', 'class' : 'output2', 
	'instrdefault' : None, 'params' : 2, 'validator' : AddrVal.CounterWord, 
	'ladsymb' : 'cntd', 'monitor' : 'none'},
# Count up
{'opcode' : 'CNTU', 'description' : 'Count up', 
	'instruction' : DLCkInstrLib.DLCkCounterCNTU, 'type' : 'instr', 'class' : 'output2', 
	'instrdefault' : None, 'params' : 2, 'validator' : AddrVal.CounterWord, 
	'ladsymb' : 'cntu', 'monitor' : 'none'},
# Up/down counter
{'opcode' : 'UDC', 'description' : 'Up/down counter', 
	'instruction' : DLCkInstrLib.DLCkCounterUDC, 'type' : 'instr', 'class' : 'output3', 
	'instrdefault' : None, 'params' : 2, 'validator' : AddrVal.CounterWord, 
	'ladsymb' : 'udc', 'monitor' : 'none'},
# AND negative differential
{'opcode' : 'ANDND', 'description' : 'AND negative differential', 
	'instruction' : PLCInstStdLib.PLCDiffAndND, 'type' : 'instr', 'class' : 'and', 
	'instrdefault' : False, 'params' : 1, 'validator' : AddrVal.BoolXYCTCTSC, 
	'ladsymb' : 'nocnd', 'monitor' : 'bool'},
# AND positive differential
{'opcode' : 'ANDPD', 'description' : 'AND positive differential', 
	'instruction' : PLCInstStdLib.PLCDiffAndPD, 'type' : 'instr', 'class' : 'and', 
	'instrdefault' : False, 'params' : 1, 'validator' : AddrVal.BoolXYCTCTSC, 
	'ladsymb' : 'nocpd', 'monitor' : 'bool'},
# OR negative differential
{'opcode' : 'ORND', 'description' : 'OR negative differential', 
	'instruction' : PLCInstStdLib.PLCDiffOrND, 'type' : 'instr', 'class' : 'or', 
	'instrdefault' : False, 'params' : 1, 'validator' : AddrVal.BoolXYCTCTSC, 
	'ladsymb' : 'nocnd', 'monitor' : 'bool'},
# OR positive differential
{'opcode' : 'ORPD', 'description' : 'OR positive differential', 
	'instruction' : PLCInstStdLib.PLCDiffOrPD, 'type' : 'instr', 'class' : 'or', 
	'instrdefault' : False, 'params' : 1, 'validator' : AddrVal.BoolXYCTCTSC, 
	'ladsymb' : 'nocpd', 'monitor' : 'bool'},
# STORE negative differential
{'opcode' : 'STRND', 'description' : 'STORE negative differential', 
	'instruction' : PLCInstStdLib.PLCDiffStorND, 'type' : 'instr', 'class' : 'store', 
	'instrdefault' : False, 'params' : 1, 'validator' : AddrVal.BoolXYCTCTSC, 
	'ladsymb' : 'nocnd', 'monitor' : 'bool'},
# STORE positive differential
{'opcode' : 'STRPD', 'description' : 'STORE positive differential', 
	'instruction' : PLCInstStdLib.PLCDiffStorPD, 'type' : 'instr', 'class' : 'store', 
	'instrdefault' : False, 'params' : 1, 'validator' : AddrVal.BoolXYCTCTSC, 
	'ladsymb' : 'nocpd', 'monitor' : 'bool'},
# Program end
{'opcode' : 'END', 'description' : 'Program end', 
	'instruction' : PLCInstStdLib.PLCEnd, 'type' : 'instr', 'class' : 'output0', 
	'instrdefault' : None, 'params' : 0, 'validator' : AddrVal.NoParams, 
	'ladsymb' : 'end', 'monitor' : 'none'},
# Program end conditional
{'opcode' : 'ENDC', 'description' : 'Program end conditional', 
	'instruction' : PLCInstStdLib.PLCEndCond, 'type' : 'instr', 'class' : 'output1', 
	'instrdefault' : None, 'params' : 0, 'validator' : AddrVal.NoParams, 
	'ladsymb' : 'endc', 'monitor' : 'none'},
# For/next loop
{'opcode' : 'FOR', 'description' : 'For/next loop', 
	'instruction' : DLCkInstrLib.DLCkFor, 'type' : 'for', 'class' : 'for', 
	'instrdefault' : False, 'params' : 2, 'validator' : AddrVal.ForParams, 
	'ladsymb' : 'for', 'monitor' : 'none'},
# Next in For/next loop
{'opcode' : 'NEXT', 'description' : 'Next in For/next loop', 
	'instruction' : DLCkInstrLib.DLCkNext, 'type' : 'next', 'class' : 'next', 
	'instrdefault' : None, 'params' : 0, 'validator' : AddrVal.NoParams, 
	'ladsymb' : 'next', 'monitor' : 'none'},
# Call subroutine
{'opcode' : 'CALL', 'description' : 'Call subroutine', 
	'instruction' : PLCInstStdLib.PLCSubrCall, 'type' : 'call', 'class' : 'output1', 
	'instrdefault' : None, 'params' : 1, 'validator' : AddrVal.SubrParam, 
	'ladsymb' : 'call', 'monitor' : 'none'},
# Return from subroutine
{'opcode' : 'RT', 'description' : 'Return from subroutine', 
	'instruction' : PLCInstStdLib.PLCSubrRet, 'type' : 'instr', 'class' : 'output0', 
	'instrdefault' : None, 'params' : 0, 'validator' : AddrVal.NoParams, 
	'ladsymb' : 'rt', 'monitor' : 'none'},
# Return from subroutine conditional
{'opcode' : 'RTC', 'description' : 'Return from subroutine conditional', 
	'instruction' : PLCInstStdLib.PLCSubrRetCond, 'type' : 'instr', 'class' : 'output1', 
	'instrdefault' : None, 'params' : 0, 'validator' : AddrVal.NoParams, 
	'ladsymb' : 'rtc', 'monitor' : 'none'},
# Define a subroutine
{'opcode' : 'SBR', 'description' : 'Define a subroutine', 
	'instruction' : PLCInstStdLib.PLCSubrDef, 'type' : 'sbr', 'class' : 'sbr', 
	'instrdefault' : None, 'params' : 1, 'validator' : AddrVal.SubrParam, 
	'ladsymb' : 'none', 'monitor' : 'none'},
# Search table for equal to
{'opcode' : 'FINDEQ', 'description' : 'Search table for equal to', 
	'instruction' : DLCkInstrLib.DLCkFindEQ, 'type' : 'instr', 'class' : 'output1', 
	'instrdefault' : False, 'params' : 6, 'validator' : AddrVal.Search, 
	'ladsymb' : 'findeq', 'monitor' : 'none'},
# Search table for >=
{'opcode' : 'FINDGE', 'description' : 'Search table for >=', 
	'instruction' : DLCkInstrLib.DLCkFindGE, 'type' : 'instr', 'class' : 'output1', 
	'instrdefault' : False, 'params' : 6, 'validator' : AddrVal.Search, 
	'ladsymb' : 'findge', 'monitor' : 'none'},
# Search table for >
{'opcode' : 'FINDGT', 'description' : 'Search table for >', 
	'instruction' : DLCkInstrLib.DLCkFindGT, 'type' : 'instr', 'class' : 'output1', 
	'instrdefault' : False, 'params' : 6, 'validator' : AddrVal.Search, 
	'ladsymb' : 'findgt', 'monitor' : 'none'},
# Incremental search table for equal to
{'opcode' : 'FINDIEQ', 'description' : 'Incremental search table for equal to', 
	'instruction' : DLCkInstrLib.DLCkFindIEQ, 'type' : 'instr', 'class' : 'output1', 
	'instrdefault' : False, 'params' : 6, 'validator' : AddrVal.Search, 
	'ladsymb' : 'findieq', 'monitor' : 'none'},
# Incremental search table for >=
{'opcode' : 'FINDIGE', 'description' : 'Incremental search table for >=', 
	'instruction' : DLCkInstrLib.DLCkFindIGE, 'type' : 'instr', 'class' : 'output1', 
	'instrdefault' : False, 'params' : 6, 'validator' : AddrVal.Search, 
	'ladsymb' : 'findige', 'monitor' : 'none'},
# Incremental search table for >
{'opcode' : 'FINDIGT', 'description' : 'Incremental search table for >', 
	'instruction' : DLCkInstrLib.DLCkFindIGT, 'type' : 'instr', 'class' : 'output1', 
	'instrdefault' : False, 'params' : 6, 'validator' : AddrVal.Search, 
	'ladsymb' : 'findigt', 'monitor' : 'none'},
# Incremental search table for <=
{'opcode' : 'FINDILE', 'description' : 'Incremental search table for <=', 
	'instruction' : DLCkInstrLib.DLCkFindILE, 'type' : 'instr', 'class' : 'output1', 
	'instrdefault' : False, 'params' : 6, 'validator' : AddrVal.Search, 
	'ladsymb' : 'findile', 'monitor' : 'none'},
# Incremental search table for <
{'opcode' : 'FINDILT', 'description' : 'Incremental search table for <', 
	'instruction' : DLCkInstrLib.DLCkFindILT, 'type' : 'instr', 'class' : 'output1', 
	'instrdefault' : False, 'params' : 6, 'validator' : AddrVal.Search, 
	'ladsymb' : 'findilt', 'monitor' : 'none'},
# Incremental search table for not equal
{'opcode' : 'FINDINE', 'description' : 'Incremental search table for not equal', 
	'instruction' : DLCkInstrLib.DLCkFindINE, 'type' : 'instr', 'class' : 'output1', 
	'instrdefault' : False, 'params' : 6, 'validator' : AddrVal.Search, 
	'ladsymb' : 'findine', 'monitor' : 'none'},
# Search table for <=
{'opcode' : 'FINDLE', 'description' : 'Search table for <=', 
	'instruction' : DLCkInstrLib.DLCkFindLE, 'type' : 'instr', 'class' : 'output1', 
	'instrdefault' : False, 'params' : 6, 'validator' : AddrVal.Search, 
	'ladsymb' : 'findle', 'monitor' : 'none'},
# Search table for <
{'opcode' : 'FINDLT', 'description' : 'Search table for <', 
	'instruction' : DLCkInstrLib.DLCkFindLT, 'type' : 'instr', 'class' : 'output1', 
	'instrdefault' : False, 'params' : 6, 'validator' : AddrVal.Search, 
	'ladsymb' : 'findlt', 'monitor' : 'none'},
# Search table for not equal
{'opcode' : 'FINDNE', 'description' : 'Search table for not equal', 
	'instruction' : DLCkInstrLib.DLCkFindNE, 'type' : 'instr', 'class' : 'output1', 
	'instrdefault' : False, 'params' : 6, 'validator' : AddrVal.Search, 
	'ladsymb' : 'findne', 'monitor' : 'none'},
# Shift register move bits to right
{'opcode' : 'SHFRG', 'description' : 'Shift register move bits to right', 
	'instruction' : DLCkInstrLib.DLCkShiftRegister, 'type' : 'instr', 'class' : 'output3', 
	'instrdefault' : False, 'params' : 2, 'validator' : AddrVal.BoolC_C, 
	'ladsymb' : 'shfrg', 'monitor' : 'none'},
# On delay timer
{'opcode' : 'TMR', 'description' : 'On delay timer', 
	'instruction' : DLCkInstrLib.DLCkTimerTMR, 'type' : 'instr', 'class' : 'output1', 
	'instrdefault' : None, 'params' : 3, 'validator' : AddrVal.TimerWord, 
	'ladsymb' : 'tmr', 'monitor' : 'none'},
# On delay accumulating timer
{'opcode' : 'TMRA', 'description' : 'On delay accumulating timer', 
	'instruction' : DLCkInstrLib.DLCkTimerTMRA, 'type' : 'instr', 'class' : 'output2', 
	'instrdefault' : None, 'params' : 3, 'validator' : AddrVal.TimerWord, 
	'ladsymb' : 'tmra', 'monitor' : 'none'},
# Off delay timer
{'opcode' : 'TMROFF', 'description' : 'Off delay timer', 
	'instruction' : DLCkInstrLib.DLCkTimerTMROFF, 'type' : 'instr', 'class' : 'output1', 
	'instrdefault' : None, 'params' : 3, 'validator' : AddrVal.TimerWord, 
	'ladsymb' : 'tmroff', 'monitor' : 'none'},
# Decimal math
{'opcode' : 'MATHDEC', 'description' : 'Decimal math', 
	'instruction' : DLCkInstrLib.DLCkMath, 'type' : 'instr', 'class' : 'output1', 
	'instrdefault' : False, 'params' : -1, 'validator' : DLCkLibs.DecMathComp.MathDecVal, 
	'ladsymb' : 'mathdec', 'monitor' : 'none'},
# Hexadecimal math
{'opcode' : 'MATHHEX', 'description' : 'Hexadecimal math', 
	'instruction' : DLCkInstrLib.DLCkMath, 'type' : 'instr', 'class' : 'output1', 
	'instrdefault' : False, 'params' : -1, 'validator' : DLCkLibs.HexMathComp.MathHexVal, 
	'ladsymb' : 'mathhex', 'monitor' : 'none'},
# Sum a range of registers
{'opcode' : 'SUM', 'description' : 'Sum a range of registers', 
	'instruction' : DLCkInstrLib.DLCkSum, 'type' : 'instr', 'class' : 'output1', 
	'instrdefault' : False, 'params' : 4, 'validator' : AddrVal.SumRegisters, 
	'ladsymb' : 'sum', 'monitor' : 'none'}

]


