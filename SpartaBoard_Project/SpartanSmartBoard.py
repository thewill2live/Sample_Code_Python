# Spartan Smart Board System
# Main project file - Spartan Smart Board Software
# Last updated: 8/2/15 22:00


# ========== Library Setup ==========
# General Use Libraries
import time # used for time delay on cam test
import os # used for os._exit command

# PiCamera Specific Libraries
import picamera # used for PiNoIR Cam
from picamera.array import PiRGBArray # used for storing video frame data

# Graphic User Interface Libraries
from pymouse import PyMouse # used for mouse manipulation
import pymouse # used for mouse manipulation
import wx # used for GUI development
from wx.lib.pubsub import pub # used for GUI development
import sys # used for command line inputs

# Open Computer Vision Libraries
import cv2 # the openCV library
import numpy as np # the python number library

# ------------------- BEGIN ssbGUI CLASS --------------------
# Class for Control Panel GUI
class ssbGUI(wx.Frame):
	# Constructor Function
	def __init__(self, parent, title):
		super(ssbGUI, self).__init__(parent, title='Spartan Smart Board',size=(260, 200))
		self.InitUI() # Call the class' InitUI function
		self.camObj = ssbCAM(None) # instantiate a camera object
		self.Centre() # center the window on screen
		self.Show() # show the window
		
	# Customized Initialization function
	def InitUI(self):
		panel = wx.Panel(self) # top level panel
		vbox = wx.BoxSizer(wx.VERTICAL) # top level vertical sizer
		fgs = wx.FlexGridSizer(2, 2) # 2x2 grid sizer
		title = wx.StaticText(panel, label="Spartan Smart Board\nPlease Select a service:") # informational text
		self.nfo = wx.StaticText(panel, label="Please Select a Service") # action prompt text
		
		button_1 = wx.Button(panel, label="Calibrate") # button to run calibration
		button_2 = wx.Button(panel, label="Interface\nMode") # button to run trackig with clicks
		button_3 = wx.Button(panel, label="Presenter\nMode") # button to run tracking without clicks
		button_4 = wx.Button(panel, label="Quit") # quit button

		self.Bind(wx.EVT_BUTTON, self.buttonCallback) # bind the buttons to the callback function

		fgs.AddMany([(button_1, 1, wx.EXPAND), (button_2, 1, wx.EXPAND),\
					 (button_3, 1, wx.EXPAND), (button_4, 1, wx.EXPAND)]) # add button widgets to the grid sizer

		vbox.Add(title, proportion=1, flag=wx.ALIGN_CENTER ) # add title to the vertical box
		vbox.Add(fgs, proportion=2, flag=wx.ALIGN_CENTER ) # add grid to the vertical box
		vbox.Add(self.nfo,proportion=1,flag=wx.ALIGN_CENTER) # add info message
		panel.SetSizer(vbox) # set panel sizer

	# Callback function for the buttons
	def buttonCallback(self,evt):
		button_pressed = evt.GetEventObject().GetLabel() # get the label of the button pressed

		if button_pressed == "Calibrate": # if calibrate button pressed
			print "Starting Calibration...." #DEBUG INFO PRINTOUT
			cal = False # initialize the calibration return variable to false
			app = wx.App() # start the app for GUI
			start = wx.MessageBox("Would you like to sart the SSb interface?",\
									"Start Interface?", wx.YES_NO) # prompt user
			if os.path.isfile('config.ssb'): # if config file found				
				ans = wx.MessageBox("An existing configuration file was found. Do you want to overwrite it?",\
									"Overwrite Config?", wx.YES_NO) # prompt user
				if ans:
					cal = self.camObj.getCorners(15) # get 4 corners
			else: # if no config found, default to running the calibrate process
				cal = self.camObj.getCorners(15) # get 4 corners
			print "Calibration completed...." #DEBUG INFO PRINTOUT
			if start:
				self.camObj.showVideo(True) # start interface mode by default
				print "Starting Interface Mode...." #DEBUG INFO PRINTOUT

		elif button_pressed == "Interface\nMode": # if interface mode button pressed
			self.camObj.showVideo(True)
			print "Starting Interface Mode...." #DEBUG INFO PRINTOUT

		elif button_pressed == "Presenter\nMode": # if presenter mode button pressed
			self.camObj.showVideo(False)
			print "Starting Presenter Mode...." #DEBUG INFO PRINTOUT

		elif button_pressed == "Quit": # if quit button pressed
			print "all proc's are dead!"#DEBUG INFO PRINTOUT
			os._exit(8) # exit on a success
# ------------------- END ssbGUI CLASS --------------------

# ------------------- BEGIN splashFrame CLASS --------------------
# Class for Start-up Splash Screen
class splashScreen(wx.SplashScreen):
	# Constructor Function
	def __init__(self, parent=None):
		image = wx.Image('/home/pi/SSBrepo/spartansmartboard/SSB.png').ConvertToBitmap() # map image to screen
		wx.SplashScreen.__init__(self, image, wx.SPLASH_CENTRE_ON_SCREEN|wx.SPLASH_TIMEOUT,2000,parent) # call splash screen widget
		wx.Yield() # exit the splash screen
# ------------------- END splashFrame CLASS --------------------

# ------------------- BEGIN calibFrame CLASS --------------------
# Class for calibration square frames
class calibFrame(wx.Frame):
	# Constructor Function
    def __init__(self, parent, pos, colr):
        wx.Frame.__init__(self, parent, size=(25,25), style=wx.NO_BORDER) # make new frame
        self.Maximize() # maximize the size of the frame
        self.SetPosition(pos) # move frame to start location
        self.SetOwnBackgroundColour(colr) # set frame color
        self.Show(True) # show the frame
# ------------------- END calibFrame CLASS --------------------

# ------------------- BEGIN ssbCAM CLASS --------------------
# Class for Camera operations
class ssbCAM:
	# Constructor Function
	def __init__(self,parent):
		self.parent = parent # save parent information for later reference
		self.cam_handle = picamera.PiCamera() # create the camera object
		self.top_left_corner = (0,0) # make top left variable
		self.top_right_corner = (0,0) # make top right variable
		self.bottom_left_corner = (0,0) # make bottom left variable
		self.bottom_right_corner = (0,0) # make bottom right variable
		self.adj_top_left_corner = (0,0) # make adjusted top left variable
		self.adj_top_right_corner = (0,0) # make adjusted top right variable
		self.adj_bot_left_corner = (0,0) # make adjusted bottom left variable
		self.adj_bot_right_corner = (0,0) # make adjusted bottom right variable
		self.horiz_intersect = (0,0) # init the horizontal intersection point
		self.vert_intersect = (0,0) # init the vertical intersection point
		self.horiz_opposing = (0,0,0) # init ABC of equation for horizontal opposing line
		self.vert_opposing = (0,0,0) # inti ABC of equation for vertical opposing line
		self.cam_res = (640,480) # store camera res (resolution that the camera input images are saved to)
		self.screen_res = (0,0) # store the screen res (resolution of the actual screen seen)
		self.output_res = (0,0) # init the output res (resolution of the monitor connected)
		self.scaleX = 0 # init the scale factor for X direction
		self.scaleY = 0 # init the scale factor for Y direction
		self.initialize() # call defined initialize function

	# Function to initialize variable values	
	def initialize(self):
		self.cam_handle.hflip = False # Don't flip the camera view horizontally
		self.cam_handle.resolution = self.cam_res # set resolution to 640x480
		app = wx.App() # start the app to get the screen resolution
		self.output_res = wx.DisplaySize() # store the display size

		# Check for config file and load last known values
		if os.path.isfile('config.ssb'):
			askLoad = wx.MessageBox("Existing configuration file was found, do you want to load it?",\
									"Load Config?", wx.YES_NO)# prompt the user to decide on loading a previous config
			if askLoad:
				# set all the saved values from the system's config file
				ifile = open('config.ssb','r') # open config file to read
				self.top_left_corner = eval(ifile.readline().rstrip())
				self.top_right_corner = eval(ifile.readline().rstrip())		
				self.bottom_left_corner = eval(ifile.readline().rstrip())	
				self.bottom_right_corner = eval(ifile.readline().rstrip())	
				self.adj_top_left_corner = eval(ifile.readline().rstrip())	
				self.adj_top_right_corner = eval(ifile.readline().rstrip())	
				self.adj_bot_left_corner = eval(ifile.readline().rstrip())	
				self.adj_bot_right_corner = eval(ifile.readline().rstrip())	
				self.horiz_intersect = eval(ifile.readline().rstrip())		
				self.vert_intersect = eval(ifile.readline().rstrip())
				self.horiz_opposing = eval(ifile.readline().rstrip())
				self.vert_opposing = eval(ifile.readline().rstrip())
				self.cam_res = eval(ifile.readline().rstrip())
				self.screen_res = eval(ifile.readline().rstrip())
				self.output_res = eval(ifile.readline().rstrip())
				self.scaleX = eval(ifile.readline().rstrip())
				self.scaleY = eval(ifile.readline().rstrip())
				ifile.close() # close file

	# Camera Preview Function
	def showCam(self,tsec_arg):
		self.cam_handle.start_preview() # Show camera preview
		time.sleep(tsec_arg) # wait <tsec_arg> seconds
		self.cam_handle.stop_preview() # Close camera preview

	# Get Camera Sample Function
	def getSample(self, tsec_arg, capture_arg=0, filename_arg=None):
		if filename_arg is None or capture_arg == 0: # if no values entered for picture count and filename
			self.cam_handle.start_preview() # Show camera preview
			time.sleep(tsec_arg) # wait <tsec_arg> seconds
		else: # if a value was entered for how many pictures to take
			time_div = int(tsec_arg) / capture_arg # get time division between image captures
			time_diff = tsec_arg - (time_div * capture_arg) # get remainder time after images taken
			self.cam_handle.start_preview() # Show camera preview
			for i in range(0, capture_arg):
				time.sleep(time_div) # wait 1 time division seconds
				self.cam_handle.capture(filename_arg + '_' + str(i) + '.jpg') # take a sample picture
			if time_diff:
				time.sleep(time_diff) # delay for the remainer of the time
		self.cam_handle.stop_preview() # Close camera preview

	# Function to continually print out the X,Y coordinates of the mouse pointer
	def showMouseLoc(self):
		try:
			m = PyMouse() # make mouse object
			while(1):
				print m.position() # print the position
		except KeyboardInterrupt:
			pass

	# Function for camera to video option
	def showVideo(self,click_allow_arg):
		lower_IR = np.array([0,0,50]) # lower bound of CV filter
		upper_IR = np.array([255,255,255]) # upper bound of CV filter
		rawCapture = PiRGBArray(self.cam_handle, size=self.cam_res) # capture to array
		m = PyMouse() # make mouse object
		prev_maxLoc = (0,0) # init previous maxLoc
		try:
			for frame in self.cam_handle.capture_continuous(rawCapture, format = 'bgr', use_video_port=True):
				image = frame.array # get the array values for that frame
				mask = cv2.inRange(image, lower_IR, upper_IR) # mask according to lower/upper filter values
				(minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(mask) # find min/max values of image
				true_pnt = self.get_true_point(maxLoc)
				print true_pnt #DEBUG INFO PRINTOUT
				adjusted_maxx = int(((true_pnt[0]) * self.output_res[0])/(self.screen_res[0])) # take the distance from the edge and perform dimensional analysis
				adjusted_maxy = int(((true_pnt[1]) * self.output_res[1])/(self.screen_res[1])) # take the distance from the edge and perform dimensional analysis
				if click_allow_arg: # if user wants to have clicks when IR found
					if maxLoc != (0,0): # if not on the default location			
						m.press(adjusted_maxx,adjusted_maxy, 1) # press the "mouse" button at location found
					elif prev_maxLoc != (0,0) and maxLoc == (0,0): # if the current value is the default and the last value wasn't the default, release
						m.release(prev_maxLoc[0],prev_maxLoc[1], 1) # release the "mouse" button
				else: # only move the mouse, no clicking
					if maxLoc != (0,0): # if not on the default location
						m.move(adjusted_maxx,adjusted_maxy) # move the mouse
				prev_maxLoc = (adjusted_maxx,adjusted_maxy) # set previous to be current max loc
				cv2.circle(image, maxLoc, 21, (255,0,0), 2) # place circle on brightest spot
				cv2.imshow("TestWindow", cv2.resize(image,(160,120))) # show the image in a tiny window
				cv2.waitKey(1) & 0xFF # needed for preview
				rawCapture.seek(0) # return to the 0th byte
				rawCapture.truncate() # clear array for next frame
				print "Mouse at: ", m.position() #DEBUG INFO PRINTOUT
		except KeyboardInterrupt: # used to quit the function
			rawCapture.seek(0) # return to the 0th byte
			rawCapture.truncate() # clear array for next frame

	# Function to obtain X/Y coordinates for the corners
	def getCorners(self,tol_arg):
		lower_IR = np.array([0,0,50]) # lower bound of CV filter
		upper_IR = np.array([180,100,255]) # upper bound of CV filter
		rawCapture = PiRGBArray(self.cam_handle, size=self.cam_res) # capture to array
		try:
			# init test point arrays (last one on each array is for the avg)
			top_left = [(0,0),(0,0),(0,0),(0,0),(0,0)]
			top_right = [(0,0),(0,0),(0,0),(0,0),(0,0)]
			bottom_left = [(0,0),(0,0),(0,0),(0,0),(0,0)]
			bottom_right = [(0,0),(0,0),(0,0),(0,0),(0,0)]
			app = wx.App() # start the app to get the screen resolution
			screenSize = wx.DisplaySize() # get the screen size
			names = [('Top Left',(0,0)),('Top Right',(screenSize[0]-25,0)),('Bottom Left',(0,screenSize[1]-25)),('Bottom Right',(screenSize[0]-25,screenSize[1]-25))] # list of names of the corners
			i = 0 # iterator to step through corner names
			wx.MessageBox('Please click and hold the pen button'
						'\nat each of the 4 red boxes until they disappear.'
						'\n(Top Left, Top Right, Bottom Left, Bottom Right)','Calibrate')
			for curr_corner in [top_left,top_right,bottom_left,bottom_right]:
				aCalibFrame = calibFrame(None,names[i][1],'Red') # make the starting frame
				print "Go to ", names[i][0], ':' # prompt user to move 
				time.sleep(2) # wait 2 seconds to avoid picking up on the next point too early
				failcount = 0 # init the failcount
				for frame in self.cam_handle.capture_continuous(rawCapture, format = 'bgr', use_video_port=True):
					maxLoc = (0,0) # init maxLoc
					image = frame.array # get the array values for that frame
					mask = cv2.inRange(image, lower_IR, upper_IR) # mask according to lower/upper filter values
					maxLoc = cv2.minMaxLoc(mask)[3] # find max location of image
					cv2.waitKey(1) & 0xFF # needed for preview
										
					if maxLoc != (0,0): # if not a default value
						print "Found: ", maxLoc #DEBUG INFO PRINTOUT
						if curr_corner[0] == (0,0): # if this corner's array has yet to be initialized
							curr_corner[0] = maxLoc # store the max location
						else: # if the first array value is already set
							match = True # set match flag to be true
							next = 0 # init the next index to be filled
							for x in range(0,4):
								if curr_corner[x] != (0,0): # if dealing with an initialized coordinate
									if (maxLoc[0] not in range(curr_corner[x][0] - tol_arg, curr_corner[x][0] + tol_arg)) \
											or (maxLoc[1] not in range(curr_corner[x][1] - tol_arg, curr_corner[x][1] + tol_arg)):
										match = False # set flag to false if a point outside of the tolerance is found
										failcount += 1 # increment the fail count
								else:
									next = x # store the index of the next open slot
									break # move to the next item in the list
							if next == 0: # if we're at the end of the list
								aCalibFrame.Destroy() # remove existing frame
								# get average of the points
								avg_x = 0 # init the average x
								avg_y = 0 # init the average y
								for y in range(0,4):
									avg_x += curr_corner[y][0]# sum the x values
									avg_y += curr_corner[y][1]# sum the y values
								curr_corner[4] = ((avg_x/4),(avg_y/4)) # int divide by 4 to get average
								if i == 0:
									self.top_left_corner = ((avg_x/4),(avg_y/4)) # store the top left corner values
								elif i == 1:
									self.top_right_corner = ((avg_x/4),(avg_y/4)) # store the top right corner values
								elif i == 2:
									self.bottom_left_corner = ((avg_x/4),(avg_y/4)) # store the bottom left corner values
								elif i == 3:
									self.bottom_right_corner = ((avg_x/4),(avg_y/4)) # store the bottom right corner values
								i += 1 # increment the iterator
								rawCapture.seek(0) # return to the 0th byte
								rawCapture.truncate() # clear array for next frame
								break
							elif failcount >=20: # if at least 20 failed attempts
								wx.MessageBox('The calibration process was unsuccsessful.\nAn accurate reading could not be determined.'
												'\nPlease try again.','Calibration FAILED', wx.ICON_ERROR)
								rawCapture.seek(0) # return to the 0th byte
								rawCapture.truncate() # clear array for next frame
								return(False) # return with fail case
							else:
								if match: # if a value was read in within the tolerance allowed
									curr_corner[next] = maxLoc # set the max location as the next entry to be averaged
					rawCapture.seek(0) # return to the 0th byte
					rawCapture.truncate() # clear array for next frame
			print "Corners:\nTop Left = ", self.top_left_corner, "\nTop Right = ",self.top_right_corner \
				, "\nBottom Left = ",self.bottom_left_corner, "\nBottom Right = ",self.bottom_right_corner # DEBUG INFO PRINTOUT
			self.calibrate() # calibrate the screen to account for skew
		except KeyboardInterrupt: # used to quit the function
			pass
		return(True) # return with success case

	# Function to calculate the 4 coordinates of the acutal rectangle view
	def calibrate(self):
		#points([topleft],	[topright],	[bottomleft],	[bottomright]) --> points([x1,y1], 		[x2,y2], 		[x3,y3],			[x4,y4])
		(top_l, top_r, bot_l, bot_r) = [self.top_left_corner,self.top_right_corner,self.bottom_left_corner,self.bottom_right_corner]

		top_line = self.line_eq(top_l, top_r) # get ABC of equation for top horiz line
		bottom_line = self.line_eq(bot_l, bot_r) # get ABC of equation for bot horiz line
		right_line =  self.line_eq(top_r, bot_r) # get ABC of equation for right vert line
		left_line = self.line_eq(top_l, bot_l) # get ABC of equation for left vert line
		
		self.horiz_intersect = self.intersection(top_line, bottom_line) # get point for horizontal intersection
		self.vert_intersect = self.intersection(right_line, left_line) # get point for verical intersection
		
		#calculate distance from points to lines to determine opposing line
		if abs(self.horiz_intersect[0]-top_l[0]) < abs(self.horiz_intersect[0]-top_r[0]): # if intersection point is closer to the left line
			self.vert_opposing = right_line # the right line is the opposing line
		else:
			self.vert_opposing = left_line # the left line is the opposing line
		if abs(self.vert_intersect[1]-top_r[1]) < abs(self.vert_intersect[1]-bot_r[1]): # if intersection point is closer to the top line
			self.horiz_opposing = bottom_line # the bottom line is the opposing line
		else:
			self.horiz_opposing = top_line # the top line is the opposing line

		#get adjusted values for 4 true corners
		self.adj_top_left_corner = (self.intersection(self.line_eq(top_l, self.vert_intersect), self.horiz_opposing)[0],self.intersection(self.line_eq(top_l, self.horiz_intersect), self.vert_opposing)[1])
		self.adj_top_right_corner = (self.intersection(self.line_eq(top_r, self.vert_intersect), self.horiz_opposing)[0],self.intersection(self.line_eq(top_r, self.horiz_intersect), self.vert_opposing)[1])
		self.adj_bot_left_corner = (self.intersection(self.line_eq(bot_l, self.vert_intersect), self.horiz_opposing)[0],self.intersection(self.line_eq(bot_l, self.horiz_intersect), self.vert_opposing)[1])
		self.adj_bot_right_corner = (self.intersection(self.line_eq(bot_r, self.vert_intersect), self.horiz_opposing)[0],self.intersection(self.line_eq(bot_r, self.horiz_intersect), self.vert_opposing)[1])

		self.screen_res = (abs(self.adj_top_left_corner[0] - self.adj_top_right_corner[0]),
						   abs(self.adj_top_left_corner[1] - self.adj_bot_left_corner[1])) # store the screen res
		
		#scale amounts
		self.scaleX = self.output_res[0]/self.screen_res[0]
		self.scaleY = self.output_res[1]/self.screen_res[1]
		print "Output resolution is: ", self.output_res #DEBUG INFO PRINTOUT
		print "Input resolution is: ", self.screen_res #DEBUG INFO PRINTOUT
		print "Scale factor is: ", self.scaleX,',',self.scaleY #DEBUG INFO PRINTOUT

		# write the configuration to a file
		ofile = open('config.ssb', 'w') # open file for writing configuration values

		ofile.write(str(self.top_left_corner) + '\n') # write top left variable
		ofile.write(str(self.top_right_corner) + '\n') # write top right variable
		ofile.write(str(self.bottom_left_corner) + '\n') # write bottom left variable
		ofile.write(str(self.bottom_right_corner) + '\n') # write bottom right variable
		ofile.write(str(self.adj_top_left_corner) + '\n') # write adjusted top left variable
		ofile.write(str(self.adj_top_right_corner) + '\n') # write adjusted top right variable
		ofile.write(str(self.adj_bot_left_corner) + '\n') # write adjusted bottom left variable
		ofile.write(str(self.adj_bot_right_corner) + '\n') # write adjusted bottom right variable
		ofile.write(str(self.horiz_intersect) + '\n') # write horizontal intersection point
		ofile.write(str(self.vert_intersect) + '\n') # write vertical intersection point
		ofile.write(str(self.horiz_opposing) + '\n') # write ABC of equation for horizontal opposing line
		ofile.write(str(self.vert_opposing) + '\n') # write ABC of equation for vertical opposing line
		ofile.write(str(self.cam_res) + '\n') # write camera res
		ofile.write(str(self.screen_res) + '\n') # write screen res
		ofile.write(str(self.output_res) + '\n') # write output res
		ofile.write(str(self.scaleX) + '\n') # write scale factor for X direction
		ofile.write(str(self.scaleY) + '\n') # write scale factor for Y direction
		ofile.close() # close the config file
		wx.MessageBox('The calibration process was\ncompleated succsessfully!','Calibration SUCCESS', wx.ICON_INFORMATION) # signal successful calibration

	# Function for converting two points into an equation of a line in the form of Ax + By = C
	def line_eq(self, p1, p2):	
		A = (p1[1]  - p2[1]) #Y1 - Y2
		B = (p2[0] - p1[0]) #X2 - X1
		C = (p1[0] * p2[1] - p2[0] * p1[1]) #X1*Y2 - X2*Y1
		return A, B, -C

	# Function for determining intersection of two lines from the A,B,C values of their line equations
	def intersection(self, line1, line2):
		# D = X1
		D = line1[0] * line2[1] - line1[1] * line2[0]
		Dx = line1[2] * line2[1] - line1[1] * line2[2]
		Dy = line1[0] * line2[2] - line1[2] * line2[0]
		if D != 0:
			x = Dx/D
			y = Dy/D
			return x, y
		else:
			return -1,-1 # fail case is -1,-1

	# Function for adjusting points on the skewed plane to their respective values in the rectangular plane
	def get_true_point(self, old_point):
		vert_point = self.intersection(self.line_eq(old_point, self.horiz_intersect), self.vert_opposing) # get vertical intersection
		horiz_point = self.intersection(self.line_eq(old_point, self.vert_intersect), self.horiz_opposing)	# get horizontal intersection
		if (vert_point[0] > 0) and (vert_point[1] > 0) and (horiz_point[0] > 0) and (horiz_point[1] > 0): # Check for illegal values from intersection 
			true_point = (horiz_point[0] - self.adj_top_left_corner[0], vert_point[1] - self.adj_top_left_corner[1])
		else: # fail case
			true_point = (0,0) # default to null value
		return true_point
	
	# ---------- TEST SUITE FUNCTIONS ---------- 
	# Unit Test for the showCam function
	def ut_showCam(self):
		self.showCam(10) # call the showcam function for 10 seconds
		# NOTE: visual confirmation required for test
		
	# Unit Test for the getSample function
	def ut_getSample(self):
		self.getSample(15, 3,'Utest') # call the get sample function to take 3 images in 15 seconds called Utest
		# check to see if images were made
		files = os.listdir() # get the current contents of the directory
		totalfiles = 0 # init the file count variable
		for item in files:
			if item[0:5] == 'Utest': # if a test output file found
				totalfiles += 1 # increment the file count variable
		if totalfiles == 3: # if there were 3 test output files found
			print "Get Sample Test: SUCCESS!"
		else:
			print "Get Sample Test: FAILED!"
		
	# Unit Test for the showMouseLoc function
	def ut_showMouseLoc(self):
		points = [(120,120), (600,480), (500,1000), (800,200)]
		m = PyMouse() # make mouse object
		for point in points:
			print "Moving to: ", point
			m.move(point[0],point[1])
			print "The Mouse is at:", m.position()
		print "Test complete!"	
		
	# Unit Test for the showVideo function
	def ut_showVideo(self):
		self.showVideo(False) # call the show video function without allowing clicks
		# NOTE: visual confirmation required for test
			
	# Unit Test for the getCorners function
	def ut_getCorners(self):
		if self.getCorners(10): # call the get corners function with a +/- of 10 pixels
			print "Get Corners Test: SUCCESS!"
		else:
			print "Get Corners Test: FAILED!"
# ------------------- END ssbCAM CLASS --------------------

# Main Function
def main():
	if len(sys.argv) > 1: # if an argument was passed, go to command line debug mode (1st argument is always the .py file itself)
		initCam = ssbCAM(None) # make the PiCamera object
		print "Commands:\n'show' = Show the camera for 30 seconds\n'sample' = Take 5 images over 10 seconds"
		print "'video' = Start video tracking, click on points found\n'video nc' = Start video tracking, no clicking"
		print "'calibrate' = Calibrate the screen\n'mouse' = Show X,Y location of mouse"
		print "'quit' = Terminate the program"
		while 1: # run infinitely until "quit" command breaks the loop
			nput = raw_input('Please enter a command:') # get user input
			if nput == 'show':
				initCam.showCam(30) # show cam for 30 seconds
			elif nput == 'sample':
				initCam.getSample(10, 5, 'testfile') # take 5 images over 10 seconds named testfile_x.jpg
			if nput == 'video':
				initCam.showVideo(True) # send the camera video to openCV
			elif nput == 'video nc':
				initCam.showVideo(False) # send the camera video to openCV (no clicking allowed)
			elif nput == 'calibrate':
				if os.path.isfile('config.ssb'): # if config file found
					ans = raw_input("An existing configuration file was found. Do you want to overwrite it (Y/N)?")
					if ans.lower() == 'y':
						initCam.getCorners(5) # get 4 corners
				else: # if no config found, default to running the calibrate process
					initCam.getCorners(5) # get 4 corners
					#initCam.calibrate() # calibrate the screen to account for skew
			elif nput == 'mouse':
				initCam.showMouseLoc() # show the mouse X,Y
			elif nput == 'quit':
				break # exit loop
	else: # normal operation with GUI
		app = wx.App()
		splash = splashScreen()
		splash.Show()
		ssbGUI(None, title='Spartan Smart Board') # start the GUI
		app.MainLoop()

	print "Spartan Smart Board System Shut Down COMPLETE. GOOD BYE!" # print notifier

# ========== Program Main ==========
if __name__ == '__main__':
	main() # call the main function
	print "Program Executed Successfully" # print success confirmation
	os._exit(8) # exit with condition code = success
else:
	os._exit(4) # exit with condition code = fail
