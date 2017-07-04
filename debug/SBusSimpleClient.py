##############################################################################
# Project:  SBusSimpleClient
# Module:   SBusSimpleClient.py
# Purpose:  Simple EtherSBus client (master).
# Language: Python 2.6
# Ver:      06-May-2010.
# Author:   M. Griffin.
# Copyright:    2009 - 2010 - Michael Griffin       <m.os.griffin@gmail.com>
#
# SBusSimpleClient is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# SBusSimpleClient is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with SBusSimpleClient. If not, see <http://www.gnu.org/licenses/>.
#
# Important:    WHEN EDITING THIS FILE, USE TABS TO INDENT - NOT SPACES!
##############################################################################

import socket
import SBusMsg

##############################################################################


# Simple EtherSBus TCP Client.
class SBusSimpleClient(SBusMsg.SBusClientMessages):
    """Simple SAIA EtherSBus TCP Client.
    """

    #############################################################
    def __init__(self, host, port, timeout):
        """Initialise the parameters with the host, port, and timeout.
            and open the network socket.
        host (string) = IP address of server.
        port (integer) = Port number of server.
        timeout (float) = Time out in seconds.
        """
        self._Host = host
        self._Port = port
        self._TimeOut = timeout
        # Initialise the messages.
        SBusMsg.SBusClientMessages.__init__(self)

        # Initialise the Ethernet port.
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.settimeout(timeout)

    #############################################################
    # Close the Ethernet connection.
    def __del__(self):
        self._socket.close()

    #############################################################
    def SendRequest(self, msgsequence, stnaddr, cmdcode, datacount, dataaddr, msgdata=None):
        """Encode and send an SBus Ethernet client request message.
        Parameters:
            msgsequence (integer) = A sequentialy incrementing integer (0 - 65535).
            stnaddr (integer) = Serial station address (0 - 255).
            cmdcode (integer) = The SBus command (2, 3, 5, 6, 11, 13, or 14).
            datacount (integer) = Number of addresses to read or write (0 - 255).
            dataaddr (integer) = Data table address to read or write (0 - 65535).
            msgdata (binary string) = The data to write (optional). This must be
                a packed binary string.
        Invalid parameters (including unsupported command codes) will cause a
            ParamError exception. Invalid data will also cause an
            exception to be raised.
        """
        # Construct the EtherSBus message.
        message = self.SBRequest(msgsequence, stnaddr, cmdcode, datacount, dataaddr, msgdata)
        # Send the message via UDP.
        self._socket.sendto(message, (self._Host, self._Port))

    #############################################################
    def ReceiveResponse(self):
        """Extract the data from a server response message.
        Parameters: Message = This is a string containing the raw binary message as received.
        Returns:
            telegramattr (integer) = The telegram attribute.
                    0 = Request, 1 = response, 2 = ack/nak. This should be 1 for a
                    response to a read, and 2 for a response to a write.
            msgsequence (integer) = This should be an echo of the sequence in the request.
            msgdata (string) = A packed binary string with the message data. If the
                telegramattr was ack/nak, then this will contain the ack/nak code.
                0 = ack. Non-zero = nak (error).
        An invalid message length will cause a MessageLengthError exception.
        A bad CRC will raise a CRCError exception.
        """
        recvmsg = self._socket.recv(1024)
        return self.SBResponse(recvmsg)

    #############################################################
    def MakeRawRequest(self, msgsequence, stnaddr, cmdcode, datacount, dataaddr, msgdata=None):
        """
        Construct an EtherSBus client request but do not send it.
        Parameters are the same as for SendRequest.
        Returns a string.
        """
        return self.SBRequest(msgsequence, stnaddr, cmdcode, datacount, dataaddr, msgdata)

    #############################################################
    def SendRawRequest(self, Request):
        """Send a previously constructed EtherSBus request to the server.
        Parameters: message (string).
        """
        self._socket.sendto(Request, (self._Host, self._Port))

    #############################################################
    def GetRawResponse(self):
        """Get the raw message response string from the server, but
        do not decode it into parameters.
        Returns a string.
        """
        return self._socket.recv(1024)


if __name__ == "__main__":
    pass
