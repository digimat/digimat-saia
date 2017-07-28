/* Connection status definitions. These are applied to the client
connection status. The keys must match the keys used by the server.
The values are in the format ["Display text", "css style"]. The
display text can be changed to whatever is desired. The CSS style
must match a defined CSS style. 
*/

// Communications client connection status.
TextDefsConnections = {"starting" : ["Starting", "statusalert"],
			"running" : ["Running", "statusok"],
			"stopped" : ["Stopped", "statusalert"],
			"faulted" : ["Faulted", "statusfault"],
			"notstarted" : ["Not Started", "statusalert"]
			};

// Communications client command status.
TextDefsComCmds = {"ok" : ["No errors", "statusok"],
		"badfunc" : ["Unsupported function", "statusfault"],
		"badaddr" : ["Invalid address", "statusfault"],
		"badqty" : ["Invalid quantity", "statusfault"],
		"deviceerr" : ["Device error", "statusfault"],
		"frameerr" : ["Frame error", "frameerr"],				
		"connection" : ["Client connection lost", "statusfault"],
		"timeout" : ["Message time out", "statusfault"],
		"servererr" : ["Undefined server error", "statusfault"],
		"badtid" : ["TID Error", "statusalert"],
		"noresult" : ["No results", "statusalert"]
		};

// General ok/alert/error status.
TextDefsGeneralStat =  {"ok" : ["Ok", "statusok"],
			"alert" : ["Alert", "statusalert"],
			"error" : ["Error", "statusfault"],
			"nodata" : ["No data", "statusalert"]
			};

// Soft logic system ok/alert/error status.
TextDefsPLCStat =  {"running" : ["Running", "statusok"],
			"alert" : ["Error", "statusalert"],
			"stopped" : ["Stopped", "statusfault"]
			};

// General condition messages.
TextDefsGeneralMsgs =  {"incremental" : "Incremental",
			"disabled" : "Disabled"
			};


