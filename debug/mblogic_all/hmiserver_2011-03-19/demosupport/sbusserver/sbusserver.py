#!/usr/bin/python
##############################################################################
# Project:  SBusServer
# Module:   sbusserver.py
# Purpose:  EtherSBus UDP Server (slave).
# Language: Python 2.6
# Date:     19-Nov-2009.
# Ver:      08-May-2010.
# Author:   M. Griffin.
# Copyright:    2009 - 2010 - Michael Griffin       <m.os.griffin@gmail.com>
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
# Important:    WHEN EDITING THIS FILE, USE TABS TO INDENT - NOT SPACES!
##############################################################################

SoftwareVersion = '08-May-2010'

_HelpStr = """
===========================================================
SBusServer

This program provides a simple asynchronous EtherSBus UDP server (slave).
It supports SBus commands 2, 3, 5, 6, 11, 13, and 16. This is strictly
a passive server and offers no client (master) functionality.

2 - Read Flags
3 - Read Inputs
5 - Read Outputs
6 - Read Registers
11 - Write flags
13 - Write outputs
14 - Write Registers

The server contains an SBus memory map which is defined as follows:
Flags, Inputs, Outputs, and Registers are defined for their full
address range (0 to 65535). Inputs are mapped to be the same as flags. That
is, writing to a flag will change the corresponding input.

The server listens on port 5050 by default. This may be changed to any other
port number through the use of the "-p" command line parameter.
E.g.    "./sbusserver.py -p 5555"  (For Linux)
    "c:\python26\python sbusserver.py -p 5555"  (For MS Windows)

Options:
-p - port. E.g. -p 1234

Author: Michael Griffin
Copyright 2009 - 2010 Michael Griffin. This is free software. You may
redistribute copies of it under the terms of the GNU General Public License
<http://www.gnu.org/licenses/gpl.html>. There is NO WARRANTY, to the
extent permitted by law.
"""

############################################################

import SocketServer
import getopt, sys
import signal
import time

from mbprotocols import SBusMsg
from mbprotocols import ModbusDataStrLib

import traceback

############################################################
class GetOptions:
    """Get the command line options. The only option is
    the port number. The default port is 5050.
    """

    ########################################################
    def __init__(self):
        self._port = 5050

        # Read the command line options.
        try:
            opts, args = getopt.getopt(sys.argv[1:], 'p:',
                ['port'])
        except:
            print(_HelpStr)
            sys.exit()

        # Parse out the options.
        for o, a in opts:
            # Port number.
            if o == '-p':
                try:
                    self._port = int(a)
                except:
                    print('Invalid port number.')
                    sys.exit()

            else:
                print('Unrecognised option %s %s' % (o, a))
                sys.exit()

    ########################################################
    def GetPort(self):
        """Return the port setting.
        """
        return self._port

############################################################


##############################################################################

class SBusMemTable:
    """Data table for the server.
    """

    ########################################################
    def __init__(self):
        """Create the data tables. These include registers, flags,
        inputs, and outputs.
        """

        self._MaxMem = 65535            # Maximum address.

        # Initialise the data table lists.
        self._Flags = [False] * (self._MaxMem + 1)
        self._Inputs = self._Flags  # Inputs are the same as flags.
        self._Outputs = [False] * (self._MaxMem + 1)
        self._Registers = [0] * (self._MaxMem + 1)


    ########################################################
    def GetFlags(self, addr, qty):
        """Return qty coil values as a list of booleans.
        addr (integer) - Flag address.
        qty (integer) - Number of flags desired.
        Returns a list of booleans.
        """
        return self._Flags[addr : addr + qty]

    def SetFlags(self, addr, qty, data):
        """Store the data from a list of booleans to the flags.
        addr (integer) - Flag address.
        qty (integer) - Number of flags to set.
        data (list of booleans) - Data.
        """
        self._Flags[addr : addr + qty] = data[:qty]


    ########################################################
    def GetInputs(self, addr, qty):
        """Same as GetFlags, but works on inputs.
        """
        return self._Inputs[addr : addr + qty]

    def SetInputs(self, addr, qty, data):
        """Same as SetFlags, but works on inputs.
        """
        self._Inputs[addr : addr + qty] = data[:qty]


    ########################################################
    def GetOutputs(self, addr, qty):
        """Same as GetFlags, but works on outputs.
        """
        return self._Outputs[addr : addr + qty]

    def SetOutputs(self, addr, qty, data):
        """Same as SetFlags, but works on outputs.
        """
        self._Outputs[addr : addr + qty] = data[:qty]



    ########################################################
    def GetRegisters(self, addr, qty):
        """Return qty register values as a list of signed integers.
        addr (integer) - Register address.
        qty (integer) - Number of registers desired.
        Returns a list of integers.
        """
        return self._Registers[addr : addr + qty]

    def SetRegisters(self, addr, qty, data):
        """Store the data in a list of signed integers to the registers.
        addr (integer) - Register address.
        qty (integer) - Number of registers to set.
        data (list of integers) - Data.
        """
        self._Registers[addr : addr + qty] = data[:qty]


############################################################

# This handles all the messages.
class MsgHandler(SocketServer.DatagramRequestHandler):
    """This handles all the received messages.
    """
    def handle(self):
        ReceivedData = self.rfile.read()

        if ReceivedData:

            print "RXDATA"

            # Decode message.
            try:
                (TelegramAttr, MsgSequence, StnAddr, CmdCode, DataAddr,
                    DataCount, MsgData, MsgResult) = SBServerMsg.SBRequest(ReceivedData)
            # We can't decode this message at all, so just drop the request and stop here.
            # Can't decode the message, because the length is invalid.
            except SBusMsg.MessageLengthError:
                print('Server %d - Invalid message length. %s' % (CmdOpts.GetPort(), time.ctime()))
                MsgResult = False
                MsgSequence = 0
            # Message had a CRC error.
            except SBusMsg.CRCError:
                print('Server %d - Bad CRC. %s' % (CmdOpts.GetPort(), time.ctime()))
                MsgResult = False
                MsgSequence = 0
            # All other errors.
            except:
                traceback.print_exc()
                print('Server %d - Request could not be decoded. %s' % (CmdOpts.GetPort(), time.ctime()))
                MsgResult = False
                MsgSequence = 0

            ReplyData = ''

            # Handle the command, but only if know the parameters are valid.
            if (MsgResult):
                # Decode messages. If we get an error in reading/writing memory or
                # in constructing messages, we will consider this to be an SBus error.
                try:
                    # Read Flags.
                    if CmdCode == 2:
                        MemData = MemMap.GetFlags(DataAddr, DataCount)
                        MsgData = ModbusDataStrLib.boollist2bin(MemData)
                        ReplyData = SBServerMsg.SBResponse(MsgSequence, CmdCode, 0, MsgData)

                    # Read Inputs
                    elif CmdCode == 3:
                        MemData = MemMap.GetInputs(DataAddr, DataCount)
                        MsgData = ModbusDataStrLib.boollist2bin(MemData)
                        ReplyData = SBServerMsg.SBResponse(MsgSequence, CmdCode, 0, MsgData)

                    # Read Outputs
                    elif CmdCode == 5:
                        MemData = MemMap.GetOutputs(DataAddr, DataCount)
                        MsgData = ModbusDataStrLib.boollist2bin(MemData)
                        ReplyData = SBServerMsg.SBResponse(MsgSequence, CmdCode, 0, MsgData)

                    # Read Registers
                    elif CmdCode == 6:
                        MemData = MemMap.GetRegisters(DataAddr, DataCount)
                        MsgData = SBusMsg.signedint32list2bin(MemData)
                        ReplyData = SBServerMsg.SBResponse(MsgSequence, CmdCode, 0, MsgData)

                    # Write flags
                    elif CmdCode == 11:
                        MemData = ModbusDataStrLib.bin2boollist(MsgData)
                        MemMap.SetFlags(DataAddr, DataCount, MemData)
                        ReplyData = SBServerMsg.SBResponse(MsgSequence, CmdCode, 0, '')

                    # Write outputs
                    elif CmdCode == 13:
                        MemData = ModbusDataStrLib.bin2boollist(MsgData)
                        MemMap.SetOutputs(DataAddr, DataCount, MemData)
                        ReplyData = SBServerMsg.SBResponse(MsgSequence, CmdCode, 0, '')

                    # Write Registers
                    elif CmdCode == 14:
                        MemData = SBusMsg.signedbin2int32list(MsgData)
                        MemMap.SetRegisters(DataAddr, DataCount, MemData)
                        ReplyData = SBServerMsg.SBResponse(MsgSequence, CmdCode, 0, '')

                    # We don't understand this command code.
                    else:
                        print('Server %d - Unsupported command code %d' % (CmdOpts.GetPort(), CmdCode))
                        ReplyData = SBServerMsg.SBErrorResponse(MsgSequence)

                # We don't understand this message.
                except:
                    ReplyData = SBServerMsg.SBErrorResponse(MsgSequence)

            # The message was bad, so we return a NAK response.
            else:
                ReplyData = SBServerMsg.SBErrorResponse(MsgSequence)


            # Send the reply.
            try:
                self.wfile.write(ReplyData)
            except:
                # If we have an error here, there's not much we can do about it.
                print('Server %d - Could not reply to request. %s' % (CmdOpts.GetPort(), time.ctime()))



############################################################

# Signal handler.
def SigHandler(signum, frame):
    print('Operator terminated server at %s' % time.ctime())
    sys.exit()


# Initialise the signal handler.
signal.signal(signal.SIGINT, SigHandler)


# Get the command line parameter options.
CmdOpts = GetOptions()

# Initialise the data table.
MemMap = SBusMemTable()

# Initialise the server protcol library. We will use a large data
# table for all addresses.
SBServerMsg = SBusMsg.SBusServerMessages(65535, 65535, 65535, 65535)

############################################################

# Print the start up greetings.
print('\n\nSBusServer version %s' % SoftwareVersion)
print('Starting server on port %d. %s' % (CmdOpts.GetPort(), time.ctime()))


# # Initialise the main server using the selected port and start it up. This runs forever.
SocketServer.UDPServer(('',CmdOpts.GetPort()), MsgHandler).serve_forever()


############################################################


