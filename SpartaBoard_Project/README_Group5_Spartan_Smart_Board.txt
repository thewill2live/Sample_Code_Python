Spartan Smart Board System
README File 1 of 1
Project Advisor: Professor Donald Hung
Group Members:
    Wilson Luc
    Erick Lui
    Wilson Nguyen
    Miguel Patino
Last updated: 8/4/15 00:45

=============================================================
========== Installation and Execution Instructions ==========
=============================================================

To run the Python files for the software you will need to 
have a Raspberry Pi (preferably a Pi 2 Model B) and a 
Raspberry Pi NoIR camera. The camera should be attached to 
the Raspberry Pi using the CSI bus connection that exists on
the microprocessor board.

The Raspberry Pi should be running the Rasbian OS which has
Python 2.7 inatalled by default. Follow the software steps
below to get the running environment set up.

Library Setup:
1 - Open a 'Terminal' command line prompt.
2 - Using the 'sudo apt-get install' command, install the 
    Picamera, PyMouse, wxPython, and openCV libraries.
	Your commands should look like the following:
        $ sudo apt-get install python-picamera
        $ sudo apt-get install pymouse
        $ sudo apt-get install python-wxgtk2.8
        $ sudo apt-get install libopencv-dev python-opencv
3 - Create the following folder structure and place a copy
	of the 'SpartanSmartBoard.py' and 'SpartaPaint.py' 
    source code files into the directory on the Raspberry 
	Pi unit. Also include the 'SSB.png' image as it is used 
	as part of the splash screen method and the system will
	not run properly without it.
	
	Directory: /home/pi/SSBrepo/spartansmartboard/
    
Program Execution:
There are two methods of execution for the software, a manual
execution through a command line interface, or a shortcut 
button/icon interface. Both are outlined below.

Option 1 - Command Line Execution
1 - Open a 'Terminal' cammand line prompt.
2 - Navigate to the directory in which you are holding
    the python files by using the 'cd' linux command 
	for changing directories.
3 - Run the following command in the Terminal to start the
    program execution for each piece of software:
        $ python SpartanSmartBoard.py
        $ python SpartaPaint.py
4 - Follow through the on-screen actions of the program.

Option 2 - Shortcut Button/Icon Execution
1 - Create a new file on the desktop of the Raspberry Pi
    by right clicking and selecting 'New File'.
2 - Name the files 'SSB.desktop' and 'SpartaPaint.desktop'
3 - Open the files in an editor and paste the following
	code into each one:
	
	For SpartaPaint.desktop:
		[Desktop Entry]
		Name=SpartaPaint
		Comment=Start a new instance of the Spartan Paint software
		Icon=/home/pi/SSBrepo/spartansmartboard/SJSU.jpg
		Exec=python /home/pi/SSBrepo/spartansmartboard/SpartaPaint.py
		Type=Application
		Encoding=UTF-8
		Terminal=false
		Categories=None;
	
	For SSB.desktop:
		[Desktop Entry]
		Name=Spartan Smart Board
		Comment=Start a new instance of the Spartan Smart Board system
		Icon=/home/pi/SSBrepo/spartansmartboard/SSB.png
		Exec=python /home/pi/SSBrepo/spartansmartboard/SpartanSmartBoard.py
		Type=Application
		Encoding=UTF-8
		Terminal=false
		Categories=None;
		
	Samples of these two .desktop files have been included
	in the code submission zipfile
		
	NOTE: In order for the icon settings to work correctly
	a copy of the SJSU.jpg file should also be included in
	the working directory.
4 - Click on each desktop icon to exexcute the respective
	progam.

======================================================
========== Glossary of Class Definitions ==========
======================================================
All defined classes are described in the entries below.
The classes are listed alphabetically by class name.


Class Name: calibFrame
Summary: Class for calibration frames used during the
		 Spartan Smart Board screen calibration process.
Member Functions: 1
Member Variables: 0
Description: Class defining the square target blocks
			 to be used by the end user as a targeting
			 point while running the calibration
			 function of the ssbCAM class. This class
			 has its objects declared by the ssbCAM
			 class.
			 
			 
Class Name: splashScreen
Summary: Class for Splash Screen visible during the
		 Spartan Smart Board software start-up.
Member Functions: 1
Member Variables: 0
Description: Class defining the splash screen to be
			 seen by the end user upon starting up
			 the Spartan Smart Board control panel.
			 This class has its objects declared by
			 the ssbGUI class.
			 
			 
Class Name: ssbCAM
Summary: Class for Main Camera Functionalities of the 
		 Spartan Smart Board system software. 
Member Functions: 16
Member Variables: 19
Description: Class defining all major functionalities
			 of the Spartan Smart Board tracking system.
			 Contains the functions for image capture,
			 image processing, calibration, OS manipulation,
			 data skew/scale adjustments, and all test 
			 functions for the Spartan Smart Board control
			 panel functionalities. This class has its 
			 objects declared by the ssbGUI class.
             
			 
Class Name: ssbGUI
Summary: Class for Graphic User Interface of the 
		 Spartan Smart Board control panel.
Member Functions: 3
Member Variables: 0
Description: Class defining the GUI for the SSB
			 control panel. Provides the end user
             with access to the calibration, interface
             mode, presentation mode, and quit 
			 functionalities of the system. This class
			 has its objects declared by the program's
			 main function.