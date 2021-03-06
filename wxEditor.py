#!/usr/bin/python


# Application name : wxEditor
# Description : A simple text editor written purely in python. 
#               The program is intended as a standalone text editor, 
#		but also as a starting point for other python
#               projects that need text editing capabilities.
#
# Copyright (C) 2013  Martin Engqvist
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# LICENSE:
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Application is a heavily modified version of the wxKonTEXT editor written by Matteo "kaworu" Paroni <m.paroni@inwind.it>
#
#
#

from string import *
from os import access,listdir
import sys, os
import wx
#from wxPython.wx import *
#from wxPython.stc import *
from wxPython.lib.buttons import *
from wxPython.lib.colourselect import *

import wx.richtext as rt



wx.InitAllImageHandlers()    #I insert the handlers to support all types of image in our case gif
files={}   #list with all configuration files

files['default_dir'] = os.path.abspath(os.path.dirname(sys.argv[0]))+"/"
files['default_dir']=replace(files['default_dir'], "\\", "/")
files['default_dir']=replace(files['default_dir'], "library.zip", "")
variables=files['default_dir']+"variables"   ##path to the file of the global variables

execfile(variables) #gets all the pre-assigned variables
 



############# function to handle fatal errors ##################
def error(number, lol):
	file=open(files['default_dir']+"/errors", "r")
	stringa=file.readlines()
	file.close()
	dlg= wx.MessageDialog(lol,stringa[number], "Error", wx.OK)
	if dlg.ShowModal() == wx.ID_OK:
		dlg.Destroy()
		lol.Destroy()
	dlg.Destroy()
	lol.Destroy()

############# function to handle non-fatal errors ###################
def error_window(number, lol):
	file=open(files['default_dir']+"/errors", "r")
	stringa=file.readlines()
	file.close()
	dlg= wx.MessageDialog(lol,stringa[number], "Error", wx.OK)
	if dlg.ShowModal() == wx.ID_OK:
		dlg.Destroy()
	dlg.Destroy()



########### class for text ######################
class RichTextFrame(rt.RichTextCtrl):
	dir_to_file=0			#variable related to the path of the file is 0 if the file is 'new
	syntaxo=None			#number of the menu item to highlight
	modify=1				#to check if the file 'was changed after the rescue
	dire=""
	def __init__(self, parent, ID):
		rt.RichTextCtrl.__init__(self, parent, ID, style = wx.NO_FULL_REPAINT_ON_RESIZE | wx.NO_BORDER)
		#self.rtc = rt.RichTextCtrl(self, style=wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER);
		#wx.CallAfter(self.rtc.SetFocus)
		
		
##		self.CmdKeyAssign(ord('+'), wx.STC_SCMOD_CTRL, wx.STC_CMD_ZOOMIN)
##		self.CmdKeyAssign(ord('-'), wx.STC_SCMOD_CTRL, wx.STC_CMD_ZOOMOUT)
##		self.EmptyUndoBuffer()
		
	
		
################## method defenitions #####################3

	def syntax(self):
		'''Defines the text font, color and other properties'''
##		self.StyleClearAll()
#		self.StyleSetSpec(0, "fore:#000000, back:#00FF00, face:%(font)s,size:%(size)d" % faces) #sets text color
#		self.StyleSetSpec(wx.STC_STYLE_LINENUMBER, "back:#FFFFFF,face:%(font)s,size:%(size)d" % faces) #sets color of left margin and text that goes there
		
##		self.StyleSetBackground(0, '#00FF00') #for the wx.STC_CHARSET_ANSI style (the 0)
##		self.StyleSetBackground(wx.STC_STYLE_DEFAULT, wx.Colour(255,255,255, wx.ALPHA_TRANSPARENT)) #set background color of everything that is not text
		
#		self.SetSelBackground(True, '#FF00FF') #selection background color
#		self.SetSelForeground(True, '#00FF00') #selection foreground color

		
	def open_document(self, dir_to_file, dire, syntax=None):
   		'''Makes sure that file opening is ok, otherwise gives error'''
		try:
			self.SetValue(open(dir_to_file).read())
			self.dir_to_file=dir_to_file
			self.syntax=syntax #do no add brackets to syntax
			self.modify=0
			self.dire=dire
		except:
			error_window(0, self)
			

########### Drop file onto editor ###############################

class MyFileDropTarget(wx.FileDropTarget):
	def __init__(self, window):
		wx.FileDropTarget.__init__(self)
		self.window = window

	def OnDropFiles(self, x, y, filenames):
		for file in filenames:
			variable=split(file, dir_separator)
			name=variable[len(variable)-1]
			self.window.page_area(name, file, "")

############# start frame #############################
class MyFrame(wx.Frame):
	frame_1_toolbar=0 #variable that will contain 'the toolbar
	menubar=0  #
	default_syntax=0  #variable that contains the index for the syntax of text documents
	tab_list=[] #list of tabs 
	current_tab=0 #contains the current tab
	panel=[] #list of panels for the textbox
	search_word="" #contains the word with which to conduct the search
	position=0 #
	row=0 #rownumber
	line=0 #linenumber
	dir_to_open="./"
	def __init__(self, parent, id, title):
		wx.Frame.__init__(self, parent, id, title)
		ID=wx.NewId()
		self.notebook_1 = wx.Notebook(self, ID, style=0) ######create blank notebook
		wx.EVT_NOTEBOOK_PAGE_CHANGED(self, ID, self.page_change)
		wx.EVT_CLOSE(self, self.OnCloseWindow)

		#create Menu Bar
		self.create_menu()

		#create statusbar
		self.frame_1_statusbar = self.CreateStatusBar(3)

		#Create Tool Bar
		self.__generate_toolbar()
		self.__set_properties()
		self.__do_layout()

		#get info for windosize
		sizefile=open(files['size'], "r")   ##open the file to set the window size
		sizelist=sizefile.readlines()
		x=replace(sizelist[0], "\\n", "")
		y=replace(sizelist[1], "\\n", "")
		sizefile.close()
		self.SetSize((int(x),int(y)))
		self.new_document("")


######### definition of utility methods ###############
	def new_document(self, evt): #new tab
 		'''Function for generating new document'''
 		self.generate_tab("")
 		self.tab_list[len(self.tab_list)-1].syntax() #load font and text options for the new tab
	 		
	def generate_tab(self, ev): #the actual function for making new tab
		'''Function for generating a tab'''
		number=len(self.tab_list)
		
		self.panel.append(wx.Panel(self.notebook_1, -1))
		ID=wx.NewId()
		
		self.tab_list.append(RichTextFrame(self.panel[number], ID)) #add tab to the tab list
		self.tab_list[number].modify=0
		rt.EVT_RICHTEXT_CHARACTER(self, ID, self.update_text)
		
		#rt.EVT_UPDATEUI(self.tab_list[number], ID, self.OnUpdateUI) #update new tab
		#############
		dt = MyFileDropTarget(self)
		self.tab_list[number].SetDropTarget(dt)
		############
		self.tab_list[number].syntaxo=self.default_syntax
		sizer=wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(self.tab_list[number], 1, wx.EXPAND, 0)
		self.notebook_1.AddPage(self.panel[number], "New_document_"+str(number))
		self.panel[number].SetSizer(sizer)
		
		
		if(number==0): #re-enable tools if they were inactivated before
   			self.frame_1_toolbar.EnableTool(502, 1)
    			self.frame_1_toolbar.EnableTool(503, 1)
    			self.frame_1_toolbar.EnableTool(504, 1)
    			self.frame_1_toolbar.EnableTool(505, 1)
    			self.frame_1_toolbar.EnableTool(506, 1)
			self.frame_1_toolbar.EnableTool(507, 1)
			self.frame_1_toolbar.EnableTool(509, 1)
			self.frame_1_toolbar.EnableTool(510, 1)
			self.frame_1_toolbar.EnableTool(511, 1)
		if wx.Platform == '__WXMSW__':
			foo=self.notebook_1.GetSize()     #piece of code so that it works on Win
			self.notebook_1.SetSize((foo[0], foo [1]-1))        
			self.notebook_1.SetSize(foo)             
##		if(wordwraping==0):
##			self.tab_list[number].SetWrapMode(wx.STC_WRAP_NONE)
##			
##		else:
##			self.tab_list[number].SetWrapMode(wx.STC_WRAP_WORD)
		self.notebook_1.SetSelection(number) #switch to the new tab


	def page_change(self, ev):
		'''When changing between tabs'''
		self.Refresh()
		self.current_tab=self.notebook_1.GetSelection()
		self.OnUpdateUI(1) #update statusbar
		if self.tab_list[self.current_tab].CanUndo(): #if undo is available
			self.menubar.Enable(9, 1)
			self.frame_1_toolbar.EnableTool(513, 1) #undo
		else:
			self.menubar.Enable(9, 0)
			self.frame_1_toolbar.EnableTool(513, 0) #undo
			
		if self.tab_list[self.current_tab].CanRedo(): #if redo is available
			self.menubar.Enable(10, 1)
			self.frame_1_toolbar.EnableTool(514, 1) #redo
		else:
			self.menubar.Enable(10, 0)
			self.frame_1_toolbar.EnableTool(514, 0) #redo
		self.tab_list[self.current_tab].SetFocus()   #to restore the pointer
		

	def update_text(self, ev):
		self.tab_list[self.current_tab].modify=1
		self.current_tab=self.notebook_1.GetSelection()
		if self.tab_list[self.current_tab].CanUndo(): #if undo is available
			self.menubar.Enable(9, 1)
			self.frame_1_toolbar.EnableTool(513, 1) #undo
		else:
			self.menubar.Enable(9, 0)
			self.frame_1_toolbar.EnableTool(513, 0) #undo
			
		if self.tab_list[self.current_tab].CanRedo(): #if redo is available
			self.menubar.Enable(10, 1)
			self.frame_1_toolbar.EnableTool(514, 1) #redo
		else:
			self.menubar.Enable(10, 0)
			self.frame_1_toolbar.EnableTool(514, 0) #redo
		self.OnUpdateUI("")

	def OnUpdateUI(self, evt):
		'''Updates statusbar'''
		#this stuff is for the statusbar
		if len(self.tab_list) == 0:
			string = ''
		elif self.tab_list[self.current_tab].modify==0:
			string = ''
		elif self.tab_list[self.current_tab].modify==1:
			string = 'File not yet saved'
		frame_1_statusbar_fields = [string]
		for i in range(len(frame_1_statusbar_fields)):
			self.frame_1_statusbar.SetStatusText(frame_1_statusbar_fields[i], 1)
		

	def info(self, event):
		dialog = wx.MessageDialog(self, '''
Application name : wxEditor
Description : A simple text editor written purely in python. 
The program is intended as a standalone text editor, but also 
as a starting point for other python projects that need text 
editing capabilities. Enjoy!

Copyright (C) 2013  Martin Engqvist

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
LICENSE:
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.
 
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Library General Public License for more details.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get source code at: https://github.com/0b0bby0/wxEditor

''', 'About wxEditor', wx.OK)
		dialog.ShowModal()
		dialog.Destroy()
######################################################    		
	def close_tab(self, number):
    		"""Function for closing a given single tab"""
    		if(self.tab_list[self.current_tab].modify==0): #if file was not modified, close it
    			self.notebook_1.DeletePage(number)
    			del self.tab_list[number]
    			del self.panel[number]
    		else: #make sure it gets saved
    			file=open(files['default_dir']+"/errors", "r")
    			string=file.readlines()
    			file.close()
    			dlg= wx.MessageDialog(self,self.notebook_1.GetPageText(number)+" "+string[9],  string[8], wx.YES_NO)
    			if dlg.ShowModal() == wx.ID_YES:
    				self.save_as_file("")
    			dlg.Destroy()
    			self.notebook_1.DeletePage(number)
    			del self.tab_list[number]
    			del self.panel[number]
		self.OnUpdateUI(1) #update statusbar
		
	def close_single(self, evt):
		'''Function for closing last tab'''
		control=self.current_tab
		if(len(self.tab_list)==1): #serves to close the last tab
			control=0
		self.close_tab(control)
		if(control!=0):
			self.current_tab=control-1
		else:
			self.current_tab=control
		if(len(self.tab_list)==0): #if no tabs, grey out icons to make them inactive
			self.frame_1_toolbar.EnableTool(502, 0)
			self.frame_1_toolbar.EnableTool(503, 0)
			self.frame_1_toolbar.EnableTool(504, 0)
			self.frame_1_toolbar.EnableTool(505, 0)
			self.frame_1_toolbar.EnableTool(506, 0)
			self.frame_1_toolbar.EnableTool(507, 0)
			self.frame_1_toolbar.EnableTool(509, 0)
			self.frame_1_toolbar.EnableTool(510, 0)
			self.frame_1_toolbar.EnableTool(511, 0) 
#			self.frame_1_toolbar.EnableTool(512, 0) #highlight
			self.frame_1_toolbar.EnableTool(513, 0) #undo
			self.frame_1_toolbar.EnableTool(514, 0) #redo
			self.menubar.Enable(9, 0)
			self.menubar.Enable(10, 0)

	def close_all(self, evt):
		'''Function for closing all tabs'''
    		cycle=range(len(self.tab_list))
    		for i in cycle:
    			self.close_single("")
    			
	def save_all(self, evt):
		'''Function for saving all open documents'''
    		variable=self.current_tab
    		cycle=range(len(self.tab_list))
    		for i in cycle:
    			self.notebook_1.SetSelection(i)
    			self.save_file("")
    		self.notebook_1.SetSelection(variable)

    			
	def change_highlight(self, ev):
		"""Function to kill all settings for a tab and then display again with new options"""
		variable=self.tab_list[self.current_tab].modify #has something to do whether the document was modified or not
		bar=self.tab_list[self.current_tab].GetText() #get text in tab
		size=self.tab_list[self.current_tab].GetSize() #get size of tab
		ID=wx.NewId()
		self.tab_list[self.current_tab].Destroy() #seems to kill the display of current tab 

		self.tab_list[self.current_tab]=RichTextFrame(self.panel[self.current_tab], ID) #make new tab with new ID
		sizer=wx.BoxSizer(wx.HORIZONTAL) #block of code to make sure the panel has the right size
		sizer.Add(self.tab_list[self.current_tab], ID, wx.EXPAND, 0)
		self.panel[self.current_tab].SetSizer(sizer)
		self.panel[self.current_tab].SetAutoLayout(1)
		self.tab_list[self.current_tab].SetSize(size)
#		wx.EVT_STC_CHARADDED(self.style_text[self.current_tab], ID, self.update_text)
		
		self.tab_list[self.current_tab].syntax() #call syntax function to update text look
		self.tab_list[self.current_tab].SetText(bar) #brings text from the old tab that was destroyed
		self.tab_list[self.current_tab].modify=variable
		if(wordwraping==0): #check for wordwrap to make sure that the new text is displayed correctly
			self.tab_list[self.current_tab].SetWrapMode(wx.STC_WRAP_NONE)
		else:
			self.tab_list[self.current_tab].SetWrapMode(wx.STC_WRAP_WORD)
    
	def open_file(self, event ):
		'''Function for opening file'''
		dlg = wx.FileDialog( self, style=wx.OPEN|wx.FILE_MUST_EXIST,   defaultDir =self.dir_to_open ,wildcard='TXT files (*)|*|Any file (*)|*')
		dlg.ShowModal()
		fileName = dlg.GetFilename()
		all_path=dlg.GetPath()
		dire=dlg.GetDirectory()
		dlg.Destroy()
		if( fileName == None or fileName == "" ):
			return
		else: 
			self.page_area(fileName, all_path, dire)
			self.dir_to_open=dire
	
	def page_area(self, fileName, all_path, dire):
		'''This function actually opens the file'''
		try:
			if(len(self.tab_list)!=1 or self.notebook_1.GetPageText(0)!="New_document_0" or self.tab_list[0].modify!=0 or len(self.tab_list[0].GetValue())!=0):
					self.generate_tab("")
			ext=extensions.keys()
			self.tab_list[len(self.tab_list)-1].LoadFile(all_path, type=rt.RICHTEXT_TYPE_ANY) #I'll need to change the type
			#variable=split(fileName, ".")

			self.notebook_1.SetPageText(len(self.tab_list)-1, fileName)
			self.tab_list[self.current_tab].dir_to_file=all_path
			self.tab_list[len(self.tab_list)-1].modify=0

		except:
			error_window(11, self)

	def save_file(self, evt):
		'''Function for saving file'''
		try:
			text = self.tab_list[self.current_tab].GetValue()
			file=open(self.tab_list[self.current_tab].dir_to_file, "w")
			file.write(text)
			file.close()
			variable=split(self.tab_list[self.current_tab].dir_to_file, ".")
			ext=extensions.keys()
			self.tab_list[self.current_tab].modify=0
			self.OnUpdateUI(1) #update statusbar
		except:
			self.save_as_file("")
		

	def save_as_file(self, evt):
		'''Function for saving file as'''
		dlg = wx.FileDialog( self, style=wx.SAVE | wx.OVERWRITE_PROMPT,defaultDir=self.tab_list[self.current_tab].dire ,wildcard='TXT files (*)|*|Any file (*)|*')
		dlg.ShowModal()
		all_path=dlg.GetPath()
		fileName=dlg.GetFilename()
		dire=dlg.GetDirectory()
		dlg.Destroy()
		if(fileName == None or fileName == ""):
			return
		else:
			try:
				self.tab_list[self.current_tab].dire=dire
				self.tab_list[self.current_tab].dir_to_file=all_path
				self.notebook_1.SetPageText(self.current_tab, fileName)
				###################
				if wx.Platform == '__WXMSW__':
					foo=self.GetSize()       #piece of code to make it work on win
					if (self.IsMaximized()):
						foo=self.notebook_1.GetSize()       #piece of code to make it work on win
						self.notebook_1.SetSize((foo[0], foo [1]-1))
						self.notebook_1.SetSize(foo)
				###################
				self.save_file("")
			except:
				error_window(7, self)

	def quit(self, evt):
		'''Function for quiting program'''
    		self.close_all("")
    		self.Destroy()

	def wordwrap(self, evt):
		'''Function changes the global variable wordwraping from 0 to 1 or from 1 to 0'''
		global wordwraping
		if(wordwraping==0):
			for i in range(len(self.tab_list)):
				self.tab_list[i].SetWrapMode(wx.STC_WRAP_WORD)
			self.edit_files(3,"wordwraping=", 1)
			wordwraping=1
		else:
			for i in range(len(self.tab_list)):
				self.tab_list[i].SetWrapMode(wx.STC_WRAP_NONE)
			self.edit_files(3,"wordwraping=", 0)
			wordwraping=0
    		
	def edit_files(self, line, variabile, string):
		'''Function used to change the global variables stored in an external text file'''
    		variable=open(files['default_dir']+"/"+files['global'], "r")
    		text=variable.readlines()
    		variable.close()
    		text[line]=variabile+str(string)+"\n"
    		variable=open(files['default_dir']+"/"+files['global'], "w")
    		cycle=range(len(text))
    		for i in cycle:
    			variable.write(text[i])
    		variable.close()
    		
	def font_config(self, evt):
		'''Changes font'''
		data= wx.FontData()
		dlg= wx.FontDialog(self, data)
		if dlg.ShowModal()==wx.ID_OK:
			data=dlg.GetFontData()
			data= data.GetChosenFont()
			font=data.GetFaceName()
			size=data.GetPointSize()
			global faces
			faces={'font' : font, 'size' : size}
			corrente=self.current_tab
			variable=range(len(self.tab_list))
			for i in variable:
				self.notebook_1.SetSelection(i)
				self.change_highlight("")
			self.notebook_1.SetSelection(corrente)
			file=open(files['default_dir']+"/"+files['font'], "w")
			file.write("faces={'font' : '"+font+"', 'size' : "+str(size)+"}")
			file.close()
    		
			
######################## Classical methods for editors ##################################################

	def print_setup(self, evt):
		'''Print'''
		foo=cgi.escape(self.tab_list[self.current_tab].GetText())
		testo=replace(foo, "\n", "<br>")
		testo=replace(testo, "\r\n", "<br>")
		testo=replace(testo, " ", " &nbsp;")
		testo=replace(testo, "\t", " &nbsp;&nbsp;&nbsp;&nbsp;")

		self.printData = wx.PrintData()
		self.printData.SetPaperId(wx.PAPER_A4)
		pdd = wx.PrintDialogData()
		pdd.SetPrintData(self.printData)

		pdd.EnablePrintToFile(0)
		pdd.SetMinPage(1)
		pdd.SetMaxPage(5)
		pdd.SetAllPages(True)
		dlg = wx.PrintDialog(self, pdd)
		if dlg.ShowModal() == wx.ID_OK:
			pdd = dlg.GetPrintDialogData()
		else:
			dlg.Destroy()
			return
		dlg.Destroy()
		printer = wx.Printer(pdd)
		printout = wx.HtmlPrintout(title=str(self.tab_list[self.current_tab].dir_to_file))
		printout.SetMargins(top=15, bottom=15, left=13, right=13)
		printout.SetHtmlText(testo)
		printer.Print(self, printout, prompt=FALSE)
		printout.Destroy()

	def preview(self, evt):
		variable=""

	def uppercase(self, evt):
		'''Change selection to uppercase'''
		selection=self.tab_list[self.current_tab].GetSelection()
		string=upper(self.tab_list[self.current_tab].GetStringSelection())
		self.tab_list[self.current_tab].Replace(selection[0], selection[1],string)
		self.tab_list[self.current_tab].SetSelection(selection[0], selection[1])
		return 1
	    
	def lowercase(self, evt):
		'''Change selection to lowercase'''
		selection=self.tab_list[self.current_tab].GetSelection()
		string=lower(self.tab_list[self.current_tab].GetStringSelection())
		self.tab_list[self.current_tab].Replace(selection[0], selection[1],string)
		self.tab_list[self.current_tab].SetSelection(selection[0], selection[1])
		return 1

	def copy(self, evt):
		'''Copy text'''
		self.tab_list[self.current_tab].Copy()

	def paste(self, evt):
		'''Paste text'''
		self.tab_list[self.current_tab].Paste()
		
	def cut(self, evt):
		'''Cut text'''
		self.tab_list[self.current_tab].Cut()

	def select_all(self, evt):
		'''Select all text'''
		self.tab_list[self.current_tab].SelectAll()
	
	def undo(self, evt):
		'''Undo action'''
		self.tab_list[self.current_tab].Undo()
		try:
			self.update_text("")
		except:
			return 0
	
	def redo(self, evt):
		'''Redo action'''
		self.tab_list[self.current_tab].Redo()
		try:
			self.update_text("")
		except:
			return 0

	def search_up(self, evt):
		'''Search upwards'''
		self.search(2)
	
	def search_down(self, evt):
		'''Search downwards'''
		self.search(1)
	
	def search(self, searchtype):
		'''This is the function for the actual search'''
		if(searchtype==2):
			end=0
			start=self.tab_list[self.current_tab].GetSelection()[1]-1 #selection?
			if start == -3:
				start=self.tab_list[self.current_tab].GetInsertionPoint()-1 #or single char position?
			text = self.tab_list[self.current_tab].GetValue() #get document text
			searchword = self.search_word.GetValue() #get searchword
			for i in range(len(text)):
				if searchword == text[start-i-len(searchword):start-i]: #go through text until searchword is found
					self.tab_list[self.current_tab].SetSelection(start-i-len(searchword),start-i)
					break
				
		else:
			start=self.tab_list[self.current_tab].GetSelection()[0]+1
			if start == -3:
				start=self.tab_list[self.current_tab].GetInsertionPoint()+1
			text = self.tab_list[self.current_tab].GetValue()
			searchword = self.search_word.GetValue()
			for i in range(len(text)):
				if searchword == text[start+i:start+i+len(searchword)]:
					self.tab_list[self.current_tab].SetSelection(start+i, start+i+len(searchword))
					break
		#if (to==-1):
		#	error_window(12, self)
		#else:
		#	self.tab_list[self.current_tab].SetSelection(to,to+len(self.search_word.GetValue()))

	
	def choose_highlight_color(self):
		'''Used to specify which color to use for highlights'''
		self.tab_list[self.current_tab].current_highlight_color = '#FF00FF'
	
	def color_highlight(self, evt):
		'''For changing background color of text ranges'''
		selection=self.tab_list[self.current_tab].GetSelection() #get range
		self.choose_highlight_color() #get color
		color = self.tab_list[self.current_tab].current_highlight_color
		self.attr = rt.RichTextAttr()
		self.attr.SetFlags(wx.TEXT_ATTR_BACKGROUND_COLOUR) #do I need the flag?
		self.attr.SetBackgroundColour(color)
		self.tab_list[self.current_tab].SetStyleEx(rt.RichTextRange(selection[0], selection[1]), self.attr)
		self.update_text("")
		#How do I refer back to this to delete selections?
	
###################### Defines graphical methods ########################################    
       
	def search_tool(self):
		'''Generates the search textbox'''
		self.search_word=wx.TextCtrl(self.frame_1_toolbar, -1, "")
		self.frame_1_toolbar.AddControl(self.search_word)

	def __generate_toolbar(self):
		'''Generates toolbar with icons'''
	
		self.frame_1_toolbar = wx.ToolBar(self, -1, style=wx.TB_HORIZONTAL|wx.TB_FLAT|wx.TB_DOCKABLE)
		self.SetToolBar(self.frame_1_toolbar)      ###instantiate the toolbar

   		#syntax for toolbar
   		#AddLabelTool(self, id, label, bitmap, bmpDisabled, kind, shortHelp, longHelp, clientData) 
   		
   		#New Document
   		self.frame_1_toolbar.AddLabelTool(500, "New Document", wx.Bitmap(files['default_dir']+"/icon/new.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, 'New File', "New File") #last one is the one displayed in status bar
   		wx.EVT_TOOL(self, 500, self.new_document)
		#Open File
   		self.frame_1_toolbar.AddLabelTool(501, "Open File", wx.Bitmap(files['default_dir']+"/icon/open.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, 'Load File', 'Load File')
   		wx.EVT_TOOL(self, 501, self.open_file)
		#Save current file
   		self.frame_1_toolbar.AddLabelTool(502, "Save current file", wx.Bitmap(files['default_dir']+"/icon/save.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, 'Save File', 'Save File')
   		wx.EVT_TOOL(self, 502, self.save_file)
		#Save as
   		self.frame_1_toolbar.AddLabelTool(503, "Save as", wx.Bitmap(files['default_dir']+"/icon/saveas.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, 'Save File As', 'Save File As')
   		wx.EVT_TOOL(self, 503, self.save_as_file)
		#Close current document
   		self.frame_1_toolbar.AddLabelTool(511, "Close current document", wx.Bitmap(files['default_dir']+"/icon/close.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, 'Close Current File', 'Close Current File')
   		wx.EVT_TOOL(self, 511, self.close_single)
		#Cut
   		self.frame_1_toolbar.AddLabelTool(504, "Cut", wx.Bitmap(files['default_dir']+"/icon/cut.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, 'Cut', 'Cut')
   		wx.EVT_TOOL(self, 504, self.cut)
		#Copy
   		self.frame_1_toolbar.AddLabelTool(505, "Copy", wx.Bitmap(files['default_dir']+"/icon/copy.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, 'Copy', 'Copy')
   		wx.EVT_TOOL(self, 505, self.copy)
		#Paste
   		self.frame_1_toolbar.AddLabelTool(506, "Paste", wx.Bitmap(files['default_dir']+"/icon/paste.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, 'Paste', 'Paste')
   		wx.EVT_TOOL(self, 506, self.paste)
   		#Undo
   		self.frame_1_toolbar.AddLabelTool(513, "Undo", wx.Bitmap(files['default_dir']+"/icon/undo.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, 'Undo', 'Undo')
   		wx.EVT_TOOL(self, 513, self.undo)   
   		#Redo
   		self.frame_1_toolbar.AddLabelTool(514, "Redo", wx.Bitmap(files['default_dir']+"/icon/redo.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, 'Redo', 'Redo')
   		wx.EVT_TOOL(self, 514, self.redo) 
		#Search Upward
   		self.frame_1_toolbar.AddLabelTool(507, "Search Upward", wx.Bitmap(files['default_dir']+"/icon/up.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, 'Search Upward', 'Search Upward')
   		wx.EVT_TOOL(self, 507, self.search_up)
		#Search window
		self.search_tool()
		#Search Downward
   		self.frame_1_toolbar.AddLabelTool(509, "Search Downward", wx.Bitmap(files['default_dir']+"/icon/down.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, 'Search Downward', 'Search Downward')
   		wx.EVT_TOOL(self, 509, self.search_down)
		#Print current window
   		self.frame_1_toolbar.AddLabelTool(510, "Print current window", wx.Bitmap(files['default_dir']+"/icon/print.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, 'Print Current Window', 'Print Current Window')
   		wx.EVT_TOOL(self, 510, self.print_setup)
		#Highlight text
#   		self.frame_1_toolbar.AddLabelTool(512, "Highlight Text", wx.Bitmap(files['default_dir']+"/icon/highlight.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, 'Highlight Text', 'Highlight Text')
#   		wx.EVT_TOOL(self, 512, self.color_highlight)   		
   		
   		self.frame_1_toolbar.EnableTool(513, 0) #undo
		self.frame_1_toolbar.EnableTool(514, 0) #redo
   			

	def __set_properties(self):
		'''General layout of the window'''
		self.SetTitle("wxEditor") #title at top of program
		icon=wx.Icon(files['default_dir']+files['icon']+"/"+"icon.ico", wx.BITMAP_TYPE_ICO)
		self.SetIcon(icon)
		#statusbar settings
		self.frame_1_statusbar.SetStatusWidths([-1, -1, -1])
		frame_1_statusbar_fields = ["Ready..", "", ""]
		for i in range(len(frame_1_statusbar_fields)):
			self.frame_1_statusbar.SetStatusText(frame_1_statusbar_fields[i], i)
		#toolbar settings
		self.frame_1_toolbar.SetMargins((2, 2))
		self.frame_1_toolbar.SetToolPacking(4)
		self.frame_1_toolbar.SetToolSeparation(5)
		self.frame_1_toolbar.SetToolBitmapSize((32, 32))
		self.frame_1_toolbar.Realize()


	def __do_layout(self):
		sizer_1 = wx.BoxSizer(wx.VERTICAL)
		sizer_1.Add(self.notebook_1, 1, wx.EXPAND, 0)
		self.SetAutoLayout(1)
		self.SetSizer(sizer_1)
		sizer_1.Fit(self)
		sizer_1.SetSizeHints(self)
		self.Layout()
		self.Centre()

	def OnCloseWindow(self, e):
		self.close_all("")
		foo=self.GetSize()  ###except for the window size of file 
		if(self.IsMaximized()==0):
			file=open(files['size'], "w")
			file.write(str(foo[0])+"\n"+str(foo[1]))
			file.close()
		self.Destroy()

################################################### Sets up the menu ##################################################
	def create_menu(self):     #method for creating menu
		self.menubar = wx.MenuBar()
		self.SetMenuBar(self.menubar)
		self.menu = wx.Menu()
			
		#new document
		item=wx.MenuItem(self.menu, 1, "New\tCtrl+Q", "New Document")
		self.menu.AppendItem(item)
		wx.EVT_MENU(self, 1, self.new_document)

		#open document
		item=wx.MenuItem(self.menu, 2, "Open\tCtrl+O", "Open Document")
		self.menu.AppendItem(item)
		wx.EVT_MENU(self, 2, self.open_file)
		self.menu.AppendSeparator()

		#save document
		item=wx.MenuItem(self.menu, 3, "Save\tCtrl+S", "Save current document")
		self.menu.AppendItem(item)
		wx.EVT_MENU(self, 3, self.save_file)

		#save document as
		item=wx.MenuItem(self.menu, 4, "Save as", "Save a copy of current document")
		self.menu.AppendItem(item)
		wx.EVT_MENU(self, 4, self.save_as_file)

		#save all
		item=wx.MenuItem(self.menu, 5, "Save all", "Save all open tabs")
		self.menu.AppendItem(item)
		wx.EVT_MENU(self, 5, self.save_all)
		self.menu.AppendSeparator()

		#close single
		item=wx.MenuItem(self.menu, 5, "Close", "Close current document")
		self.menu.AppendItem(item)
		wx.EVT_MENU(self, 5, self.close_single)

		#close all
		item=wx.MenuItem(self.menu, 6, "Close all", "Close all tabs")
		self.menu.AppendItem(item)
		wx.EVT_MENU(self, 6, self.close_all)
		self.menu.AppendSeparator()

		#quit
		item=wx.MenuItem(self.menu, 7, "Exit", "Exit program")
		self.menu.AppendItem(item)
		wx.EVT_MENU(self, 7, self.quit)

		self.menubar.Append(self.menu, "File")

		######################### For 'Edit' menu item #############################################
		self.menu = wx.Menu()
		#undo
		item=wx.MenuItem(self.menu, 9, "Undo\tCtrl+Z", "Undo")
		self.menu.AppendItem(item)
		wx.EVT_MENU(self, 9, self.undo)

		#redo
		item=wx.MenuItem(self.menu, 10, "Redo\tCtrl+Y", "Redo")
		self.menu.AppendItem(item)
		wx.EVT_MENU(self, 10, self.redo)
		self.menu.AppendSeparator() #________________________devider

		#cut
		item=wx.MenuItem(self.menu, 11, "Cut\tCtrl+X", "Cut selected text")
		self.menu.AppendItem(item)
		wx.EVT_MENU(self,11, self.cut)

		#copy
		item=wx.MenuItem(self.menu, 12, "Copy\tCtrl+C", "Copy selected text")
		self.menu.AppendItem(item)
		wx.EVT_MENU(self, 12, self.copy)

		#paste
		item=wx.MenuItem(self.menu, 13, "Paste\tCtrl+V", "Paste selected text")
		self.menu.AppendItem(item)
		wx.EVT_MENU(self, 13, self.paste)
		self.menu.AppendSeparator() #________________________devider

		#select all
		item=wx.MenuItem(self.menu, 14, "Select all", "Select all text")
		self.menu.AppendItem(item)
		wx.EVT_MENU(self, 14, self.select_all)
		self.menu.AppendSeparator() #________________________devider

		#uppercase
		item=wx.MenuItem(self.menu, 34, "Uppercase\tCtrl+W", "Convert selected text to uppercase")
		self.menu.AppendItem(item)
		wx.EVT_MENU(self, 34, self.uppercase)

		#lowercase
		item=wx.MenuItem(self.menu, 35, "Lowercase\tCtrl+E", "Convert selected text to lowercase")
		self.menu.AppendItem(item)
		wx.EVT_MENU(self, 35, self.lowercase)
		self.menu.AppendSeparator() #________________________devider

		#select font
		item=wx.MenuItem(self.menu, 15, "Select font\tCtrl+F", "Select font and textsize")
		self.menu.AppendItem(item)
		wx.EVT_MENU(self, 15, self.font_config)

		#wordwrap
		item = wx.MenuItem(self.menu, 20, "Word wrap", "Automatic word wrap", wx.ITEM_CHECK)
		self.menu.AppendItem(item)
		wx.EVT_MENU(self,20, self.wordwrap)

		self.menubar.Append(self.menu, "Edit")

		########## For 'Help' menu item #############
		self.menu = wx.Menu()
		#about program
		item = wx.MenuItem(self.menu, 21, "About", "About this program")
		self.menu.AppendItem(item)
		wx.EVT_MENU(self, 21, self.info)

		self.menubar.Append(self.menu, "Help")

		self.menubar.Enable(9, 0) #undo
		self.menubar.Enable(10, 0) #redo
		self.menubar.Check(20, wordwraping) #word wrap
		

class MySplashScreen(wx.SplashScreen):
	'''Class for defining the startup splash screen'''
	def __init__(self):
		self.args=sys.argv[1:]
		bmp = wx.Image(files['default_dir']+files['icon']+"/"+"splash.png").ConvertToBitmap()
		wx.SplashScreen.__init__(self, bmp, wx.SPLASH_CENTRE_ON_SCREEN|wx.SPLASH_TIMEOUT, 100, None, -1, style = wx.SIMPLE_BORDER|wx.FRAME_NO_TASKBAR|wx.STAY_ON_TOP)
		wx.EVT_CLOSE(self, self.OnClose)

	def OnClose(self, evt):
		app.frame.Show(1)
		self.Destroy()

class MySplashApp(wx.App): #for splash screen
	def OnInit(self):
		frame=MySplashScreen()
		frame.Show(1)
		frame.Centre()
		return True
		
	def open_fin(self):
		self.MainLoop()
	def OnClose(self, evt):
		self.Exit()
	
class MyApp(wx.App):
	def OnInit(self):
		args=sys.argv[1:]
		#print(args)
		self.frame=MyFrame(None, -1, "wxEditor")
		self.frame.Centre()
		return True

splashapp = MySplashApp()

#Main loop ------------------------------ Run application
app=MyApp()
#app.frame.Show(1)
app.MainLoop()
