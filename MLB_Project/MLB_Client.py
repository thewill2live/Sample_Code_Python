__author__ = 'Wilson Luc'

import pyodbc
import os
import Tkinter
from Tkinter import *
import tkFileDialog
import tkMessageBox
import tktable
import re
# --------------- GUI Definition ---------------
class ClientGUI(Tkinter.Tk):
    def __init__(self,parent): # define constructor function
        Tkinter.Tk.__init__(self,parent) # call inherited constructor function
        self.parent = parent # save parent information for later use
        self.title("Major League Baseball Database") # set title of program
        self.geometry('1000x600')
        self.iconbitmap(default='.\\MLB.ico') # set the icon image
        self.optionList_Table = ['-'] # table list
        self.optionList_Field = ['-'] # field (column) list
        self.optionList_Comp = ['=', '>=', '<=', '!=', '>', '<', 'Contains']
        self.tablesDict = {} # initialize the tables dictionary
        self.userNameVar = StringVar() # initialize the username return variable
        self.userPassVar = StringVar() # initialize the password return variable
        self.userNameVar.set('MLB_Fan1') #DEBUG
        self.userPassVar.set('spartanfan1') #DEBUG
        self.qryTableStr = StringVar() # initialize the query table string return variable
        self.qryTableStr.trace("w", self.TablesCallback) # set trace on table query variable
        self.qryFieldStr = StringVar() # initialize the query field string return variable
        self.qryFieldStr.trace("w", self.FieldCallback) # set tract on field query variable
        self.qryCompStr = StringVar() # intialize the query comparison string return variable
        self.qryValueStr = StringVar() # intialize the query value string return variable
        self.connectionVar = '' # initialize the access storage string
        self.tktableArray = tktable.ArrayVar() # initialize the results table variable
        self.results = [] # initialize the results return variable for query returns
        self.initialize() # call defined initialize function
        
        self.And1Var = IntVar() # initialize the and1 checkbox variable
        
        self.And2Var = IntVar() # initialize the and2 checkbox variable 
        self.And2Var.set(0) # set the box to unchecked by default
        
    def initialize(self): # define initialize function
        self.grid() # Create grid

        self.logo = Tkinter.PhotoImage(file='.\\newLogo.gif') # filepath for logo gif
        self.LogoLabel = Tkinter.Label(self,image=self.logo) # apply image to label
        self.LogoLabel.grid(column = 4, row = 1, columnspan = 3, rowspan = 3) # Add label to the grid

        # ---------------------- Server Login Section ----------------------
        self.LoginFrame = Tkinter.LabelFrame(self, text = "Server Login") # Create label frame
        self.LoginFrame.grid(column = 1, row = 1, ipadx = 2, padx = 10, sticky='W') # Add label frame to the grid

        self.UserNmLabel = Tkinter.Label(self.LoginFrame, text = "Username:") # Create username label
        self.UserNmLabel.grid(column = 2, row = 1) # Add label widget to the grid

        self.UserNmEntry = Tkinter.Entry(self.LoginFrame, textvariable = self.userNameVar) # Add entry box for username
        self.UserNmEntry.grid(column = 3, row = 1, columnspan = 3) # Add entry box to the grid

        self.PassLabel = Tkinter.Label(self.LoginFrame, text = "Password:") # Create password label
        self.PassLabel.grid(column = 2, row = 2) # Add label widget to the grid

        self.PassEntry = Tkinter.Entry(self.LoginFrame, textvariable = self.userPassVar, show = "*") # Add entry box for password
        self.PassEntry.grid(column = 3, row = 2, columnspan = 3, pady = 3) # Add entry box to the grid

        self.LoginButton = Tkinter.Button(self.LoginFrame, text = "Login", command = self.LoginButtonClick) # Create button widget. Tie button click to function LoginButtonClick defined below
        self.LoginButton.grid(column = 6, row = 1, columnspan = 6, rowspan = 2) # Add button widget to the grid

        # ---------------------- Query Parts Library Section ----------------------
        self.QueryFrame = Tkinter.LabelFrame(self, text = "Query Database") # Create label frame
        self.QueryFrame.grid(column = 1, row = 2, columnspan = 4, rowspan = 4, ipadx = 2, padx = 10, sticky='W') # Add label frame to the grid

        # -------------- FIRST QUERY
        self.TableLabel = Tkinter.Label(self.QueryFrame, text= "Category") # Create notification label
        self.TableLabel.grid(column = 2, row = 4) # Add label widget to the grid

        self.TableOptnMen = Tkinter.OptionMenu(self.QueryFrame, self.qryTableStr, *self.optionList_Field) # Create option menu for field
        self.TableOptnMen.configure(state= DISABLED) # Disable the option menu for table by default
        self.TableOptnMen.grid(column = 2, row = 5) # Add option widget to the grid

        self.FieldLabel = Tkinter.Label(self.QueryFrame, text= "Field") # Create notification label
        self.FieldLabel.grid(column = 3, row = 4) # Add label widget to the grid

        self.FieldOptnMen = Tkinter.OptionMenu(self.QueryFrame, self.qryFieldStr, *self.optionList_Field) # Create option menu for field
        self.FieldOptnMen.configure(state= DISABLED) # Disable the option menu for field by default
        self.FieldOptnMen.grid(column = 3, row = 5) # Add option widget to the grid

        self.CompLabel = Tkinter.Label(self.QueryFrame, text= "Comparison") # Create notification label
        self.CompLabel.grid(column = 4, row = 4) # Add label widget to the grid

        self.CompOptnMen = Tkinter.OptionMenu(self.QueryFrame, self.qryCompStr, *self.optionList_Comp) # Create option menu for comparator
        self.CompOptnMen.configure(state= DISABLED) # Disable the option menu for comparator by default
        self.CompOptnMen.grid(column = 4, row = 5) # Add option widget to the grid

        self.ValueLabel = Tkinter.Label(self.QueryFrame, text= "Value") # Create notification label
        self.ValueLabel.grid(column = 5, row = 4) # Add label widget to the grid

        self.QValueEntry = Tkinter.Entry(self.QueryFrame, textvariable = self.qryValueStr) # Add entry box for query value
        self.QValueEntry.grid(column = 5, row = 5, padx = 8) # Add entry box to the grid
        
        self.SearchButton = Tkinter.Button(self.QueryFrame, text="Search", command = self.SearchButtonClick, state = DISABLED) # Create button widget. Tie button click to function CancelButtonClick defined below
        self.SearchButton.grid(column = 6, row = 9, padx = 5) # Add button widget to the grid 

        # ---------------------- Library Results Section ----------------------
        self.ResultsFrame = Tkinter.LabelFrame(self, text = "Query Results") # Create label frame
        self.ResultsFrame.grid(column = 1, row = 6, columnspan = 4, ipadx = 2, padx = 10, sticky='EW') # Add label frame to the grid

        self.HScroll = Tkinter.Scrollbar(self.ResultsFrame, orient=HORIZONTAL) # create the horizontal scrollbar
        self.HScroll.grid(column = 2, row = 7, columnspan = 4, sticky= 'EW')

        self.VScroll = Tkinter.Scrollbar(self.ResultsFrame, orient=VERTICAL) # create the horizontal scrollbar
        self.VScroll.grid(column = 7, row = 6, rowspan = 2, sticky= 'NS')

        self.resultsTable = tktable.Table(self.ResultsFrame, rows = 30, cols = 30, state='disabled',titlerows=1, \
                                       selectmode='extended', variable=self.tktableArray, selecttype='row', colstretchmode='unset', \
                                       maxwidth=950, maxheight=190, xscrollcommand = self.HScroll.set, yscrollcommand = self.VScroll.set) # Create the results table
        self.resultsTable.grid(column= 2, row = 6, sticky='EW') # Add results table to the grid

        self.HScroll.config(command = self.resultsTable.xview) # set the horizontal scrolling function
        self.VScroll.config(command = self.resultsTable.yview) # set the vertical scrolling function
        
        self.ClearButton = Tkinter.Button(self, text="Clear Results", command = self.ClearResultsButtonClick, state = DISABLED) # Create button widget. Tie button click to function ClearResultsButtonClick defined below
        self.ClearButton.grid(column = 2, row = 8, columnspan = 2, pady = 10) # Add button widget to the grid

        self.CancelButton = Tkinter.Button(self, text="Cancel", command = self.CancelButtonClick) # Create button widget. Tie button click to function CancelButtonClick defined below
        self.CancelButton.grid(column = 4, row = 8, columnspan = 2, pady = 10) # Add button widget to the grid

    def TablesCallback(self, *args): # callback function for the Tables Option Menu
        keyVal = self.qryTableStr.get()
        if keyVal: # don't attempt to pull list of blank key
            self.FieldOptnMen.configure(state = DISABLED) # disable the field
            self.optionList_Field = self.tablesDict[keyVal] # get the dict list of fields
            # update the menu options
            self.qryFieldStr.set('') # blank the variable
            self.FieldOptnMen['menu'].delete(0, 'end') # remove all existing entries
            for item in self.optionList_Field: # add in the new entries to the menu
                self.FieldOptnMen['menu'].add_command(label=item, command = Tkinter._setit(self.qryFieldStr,item))
            self.FieldOptnMen.configure(state = 'normal') #re-enable the field

    def FieldCallback(self, *args): # callback function for the Field Option Menu
        keyVal = self.qryFieldStr.get()
        if keyVal: # don't attempt to enable the comp field of blank key
            self.CompOptnMen.configure(state = 'normal') # enable the field
        else:
            self.CompOptnMen.configure(state = DISABLED) # disable the field

    def LoginButtonClick(self): # define the LOGIN button click event action
        try: # TODO: Add config file for presetting all information for login/server
            cnxn = pyodbc.connect('DRIVER={ODBC Driver 11 for SQL SERVER};SERVER=WHEELSUNULTRA\SQLEXPRESS;uid='+ \
                                  self.userNameVar.get() +';pwd='+ self.userPassVar.get()) # Attempt to log in with credentials
        except Exception as excp:
            if excp[0] == '28000':
                print excp
                tkMessageBox.showerror("CONNECTION ERROR (PRPLC-59)", "Login credentials incorrect! Please check your username and password and try again.") # notify user
            elif excp[0] == '08001':
                print excp
                tkMessageBox.showerror("CONNECTION ERROR (PRPLC-62)", "Server could not be found! Please check your connection and try again.") # notify user
            else:
                print excp
                tkMessageBox.showerror("LOGIN ERROR (PRPLC-65)", "Unknown Error! Please contact the system administrator for assistance.") # notify user
        else:
            tkMessageBox.showinfo("LOGIN SUCCESS", "Your login credentials have been verified by the server.") # notify user of successful login
            # Setup the tables option menu
            Tables = cnxn.execute("SELECT * FROM information_schema.tables").fetchall() # get the list of tables
            TableList = [] # initialize an empty table list
            for table in Tables:
                TableList.append(table[2]) # append the table name to the list of tables
            self.optionList_Table = TableList # set the table list into the option variable
            # update the options on the option list
            self.qryTableStr.set('') # blank the variable
            self.TableOptnMen['menu'].delete(0, 'end') # remove all existing entries
            for item in self.optionList_Table:
                self.TableOptnMen['menu'].add_command(label=item, command = Tkinter._setit(self.qryTableStr,item))
                Columns = cnxn.execute("SELECT COLUMN_NAME FROM information_schema.columns WHERE TABLE_NAME = '" + item + "'").fetchall() # get list of columns
                # pull just the strings containing the column names
                cols = [] # initialize the columns list
                for entry in Columns:
                    cols.append(entry[0]) # take only the first item in each of the sublists (second item is always blank)
                self.tablesDict[item] = cols # create new dictionary entry
            self.TableOptnMen.configure(state= 'normal') # enable the option menu for comparator by default

            self.SearchButton['state'] = 'normal' # enable the search button
            self.ClearButton['state'] = 'normal' # enable the clear button
            self.connectionVar = cnxn # store connection handler

            
    def SearchButtonClick(self): # define the SEARCH button click event action
        # If you were able to get to here, you should have been able to log in and
        # establish a connection to the server, so no need to reestablish a connection here

        queryStr =  "SELECT * FROM " + self.qryTableStr.get() # setup base string
        if self.qryValueStr.get():
            if self.qryCompStr.get() == 'Contains': # if contains then use "Like"
                queryStr = queryStr + " WHERE " + self.qryFieldStr.get() + " LIKE '" + self.qryValueStr.get() + "';"
            else:
                queryStr = queryStr + " WHERE " + self.qryFieldStr.get() + " " + self.qryCompStr.get() + " '" + self.qryValueStr.get() + "';"
        else:
            queryStr = queryStr + ";"
        self.results = makeQuery(self.connectionVar, queryStr, 'USE MLB_World') # Call AUX function to make Query
        
        notifier_str = "Search Yielded %i record(s)!" % len(self.results) # compile results notification string
        tkMessageBox.showinfo("Results", notifier_str) # prompt user about records returned
        
        if self.results: # if a value was returned
            self.printResults() # call AUX fuction to update the results window

    def printResults(self):
        if self.results:  # if the results list is not empty
            print self.optionList_Field
            print "-----------------------------------------------------------"
            for item in self.results:
                print item
            rows_cnt = len(self.results) + 1 # get row count
            cols_cnt = len(self.optionList_Field) # get column count
            print "Row Count=", rows_cnt, " Col Count=", cols_cnt #DEBUG
            self.resultsTable.configure(rows = rows_cnt, cols = cols_cnt) # set the column count and row count
            for y in range(rows_cnt):
                for x in range(cols_cnt):
                    index = "%i,%i" % (y,x)
                    if y == 0:  # for first row, print column headings
                        self.tktableArray.set(index, self.optionList_Field[x]) # write column headings
                    else:
                        if not self.results[y-1][x] == None: # if value is non-null
                            if isinstance(self.results[y-1][x], float): 
                                self.tktableArray.set(index, "{0:.3f}".format(self.results[y-1][x])) # write results to the table as formatted float
                            else:
                                self.tktableArray.set(index, self.results[y-1][x]) # write results to the table
                        else:
                            self.tktableArray.set(index, "NULL") # write null value
            #self.setColWidth(rows_cnt, cols_cnt) # call AUX function to format column widths

    # def setColWidth(self, rows_arg, cols_arg):
        # for x in range(cols_arg):
            # longest_str = 0 # init the longest string length
            # for y in range(rows_arg):
                # index = "%i,%i" % (y,x)
                # if len(self.resultsTable.get(index)) > longest_str:
                    # longest_str = len(self.resultsTable.get(index))
            # self.resultsTable.width(x,longest_str + 3)
        # self.resultsTable.configure(colwidth = longest_str)

    def ClearResultsButtonClick(self): # define the CLEAR button click event action
        self.resultsTable.configure(rows = 30, cols = 30) # reset the table to a 30x30 grid
        for y in range(0,10):
            for x in range(0,10):
                index = "%i,%i" % (x,y)
                self.tktableArray.set(index, '') # blank contents of the cell


    def CancelButtonClick(self): # define the CANCEL button click event action
        self.quit()
# End class definition for MainGUI


def makeQuery(cnxn_arg, qry_arg, optn_arg='NONE'):
    print "Query:", qry_arg #DEBUG
    cursor = cnxn_arg.cursor()
    if not optn_arg == 'NONE':
        cursor.execute(optn_arg) # execute the line to set database to use
    cursor.execute(qry_arg) # execute the query line
    rows = cursor.fetchall()
    if len(rows) >= 1:
        return rows
    else:
        print "NONE FOUND"
        return []

# --------------------------------------------------
# ---------------- Main Function(s) ----------------
# --------------------------------------------------
def main():
    # ================= GUI SETUP SECTION =================
    app = ClientGUI(None) # make Client GUI window
    # ================= GUI SETUP SECTION END =================
    app.mainloop()

if __name__ == '__main__':
    main() # call main function
print "DONE"