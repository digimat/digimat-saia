/*
	Error texts for MB-HMI demo.
	10-Mar-2009.
*/

// Communications errors.
MBT_ErrorText = {"tagnotfound" : "The address tag is not recognised by the server.",
"badtype" : "The data value is of an incompatible type.",
"outofrange" : "The data value is out of range.",
"writeprotected" : "An attempt was made to write to an address which is write protected or otherwise not writable.",
"addresserror" : "An error occurred in attempting to map the tag to the internal server address representation.",
"servererror" : "An unspecified error has occurred in the server which prevents the request from being completed.",
"tagnotfound" : "The tag name requested by the client is not valid.",
"accessdenied" : "The client does not have authorisation to access this tag. "
};

// Protocol status.
MBT_StatusText = {
"ok" : "No errors.",
"protocolerror" : "An error was encountered in the protocol and the entire message was discarded by the server.",
"commanderror" : "A request command field provided incorrect or invalid data.",
"servererror" : "An unspecified error has occurred in the server which prevents the request from being completed.",
"unauthorised" : "The client is not authorised to communicate with this server.",
"noclistempty" : "The client attempted to read using NOC without an NOC list being present in the server.",
"comstimeout" : "A communications time out occurred when attempting to read from the server."
};

// Alarm state descriptions.
MBT_AlarmStatesText = {
"alarm" : "Fault is active",
"ackalarm" : "Alarm acknowledged",
"ok" : "Fault cleared",
"ackok" : "Fault cleared and acknowledged",
"inactive" : "Alarm inactive"
};

