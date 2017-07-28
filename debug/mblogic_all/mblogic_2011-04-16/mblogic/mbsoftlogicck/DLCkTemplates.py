##############################################################################
# Project: 	MBLogic
# Module: 	DLCkTemplates.py
# Purpose: 	Instruction templates for a Click-like PLC.
# Language:	Python 2.5
# Date:		31-Aug-2009.
# Ver:		09-Aug-2010.
# Author:	M. Griffin.
# Copyright:	2010 - Michael Griffin   <m.os.griffin@gmail.com>
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
This module defines certain instruction templates for a DL Click-like PLC. 
The templates are used when auto-generating blocks of IL code.
This needs to be customised for each model of PLC being emulated.
"""

# Template for an empty subroutine.
PLCSubrTemplate = """SBR %s

NETWORK 1
RT
"""

# This is used to look up the instruction opcode by class to allow programs
# to assemble IL data. 
InstrTypeLookup = {'comment' : '//', 'sbr' : 'SBR'}


