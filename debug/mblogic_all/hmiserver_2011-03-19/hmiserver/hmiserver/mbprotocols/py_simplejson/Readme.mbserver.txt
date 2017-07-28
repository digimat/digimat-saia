Read Me for MBServer / MBLogic installation of simplejson.
Date: 09-01-2008

This is the third party "simplejson" package which provides JSON 
encoding and decoding for MBServer / MBLogic. The full package should
be found in this directory as a compressed "gz" file. The files unpacked
here are the ones actually required for this application.

The version provided here is intended as a fall-back in the event
that simplejson is not installed in the normal Python site package 
location.

If you are using MBServer / MBLogic from Linux, you should install the
"simplejson" package normally using your package manager. This will normally
give you an optimised 'C' version instead of the pure Python version. This 
in turn will give you a (small) increase in performance and a (small) 
decrease in CPU load.

If you are using MBServer / MBLogic from MS-Windows, you can try installing
"simplejson" into the normal "site-packages". You can also try compiling the
'C' source code from the full package in the archive file to get an optimised 
version.

If you do not install "simplejson" directly into the normal Python site package
location, MBServer / MBLogic will use the version located here. This version
has been renamed "py_simplejson" to avoid conflicts with any version of
"simplejson" which is already installed in the standard location. Also, the 
"decoder.py" file has been modified to permit the package to be renamed. The 
modification is shown below:

Original:
	from simplejson.scanner import make_scanner

Changed to:
	from scanner import make_scanner


This package is present as a transitional solution to allow MBServer / MBLogic 
to be used on Python version 2.5. When MBServer / MBLogic has been tested on and
moved to versions 2.6 / 3.0, this package will no longer be included, as a 
JSON library is part of the standard libraries in those versions.


