/*
	Message texts. These are application message texts which are displayed
	to the operator. These differ from applicatoin configuration data
	in that they are language (locale) specific. These should include:
	1) Alarm message texts.
	2) Event message texts.
	3) Any other messages required.

	You need to replace the examples here with the actual alarm and event 
	(and other) tags and messages from your application. 
*/

/* Alarm message texts. This translates the alarm tags to the message texts
	which are displayed to the operator. Replace the tags and messages
	with your own actual data. You can add or remove records as necessary.
*/
MBT_AlarmText = {
"PB1Alarm" : "PB1 was pressed.",
"PB2Alarm" : "PB2 was pressed.",
"PB3Alarm" : "PB3 was pressed.",
"PB4Alarm" : "PB4 was pressed."
};

/* Event message texts. This translates the event tags to the message texts
	which are displayed to the operator. Replace the tags and messages
	with your own actual data. You can add or remove records as necessary.
*/
MBT_EventText = {
"PumpRunning" : "Tank pump is running.",
"PumpStopped" : "Tank pump is stopped.",
"Tank1Empty" : "Tank 1 is empty.",
"Tank1Full" : "Tank 1 is full.",
"Tank2Empty" : "Tank 2 is empty.",
"Tank2Full" : "Tank 2 is full."
};



