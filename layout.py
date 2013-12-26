# -*- coding: utf-8 -*- 

import os, sys, wx
from wx.lib.pubsub import Publisher as pub
import Model


class ListBox(wx.ListBox):
	'''A new ListBox class where the only difference is the addition of a GetSelectionsStrings method'''
	def GetSelectionsStrings(self):
		'''Retrieves a list of strings of the selected items in a listbox'''
		result = []
		
		for selection in self.GetSelections():
			result.append(self.GetString(selection))
		
		return result



class Moving_progress_dialog(object):
	'''Wraps (and creates) the ProgressDialog to show progress when files are moved. 
	
	Dialog is updated in response to direct method calls which are in response to file moving broadcasts from the model
	
	Both paths are needed. The initial path to get the total file size being moved and the final path (the path games are being moved to) to update current total transferred'''
	def __init__(self, frame, initial_path, final_path, game_names):
		self.frame = frame
		self.initial_path = initial_path
		self.final_path = final_path
		self.game_names = game_names
		
		# Subscribe to file copy broadcasts from shutil.copy2 (one broadcast per file)
		pub.subscribe(self.update_dialog, "FILE MOVED")
		# Subscribe to finished moving broadcast
		pub.subscribe(self.destroy_dialog, "GAMES MOVED TO SECONDARY")
		pub.subscribe(self.destroy_dialog, "GAMES MOVED TO PRIMARY")
		
		
		self.initial_dirs = []
		self.final_dirs = []
		# Create full game paths for both initial and secondary
		for game in self.game_names:
			self.initial_dirs.append(self.initial_path + os.sep + game)
			self.final_dirs.append(self.final_path + os.sep + game)
		
		
		# Get total file count of initial directories (the ones being moved)
		self.total = 0
		for d in self.initial_dirs:
			self.total = self.total + Model.get_file_count(d)
		
		
		# Create and display dialog
		self.dlg = wx.ProgressDialog(
			"Moving files",
			"                                                 ", # The width of the dialog is initial defined by the width of this string
			maximum=self.total,
			parent=self.frame)
		
		
		# This counter is used to limit the number of times the directory size is checked
		# I'm not sure if this needed, but it seems wasteful to recount the all directory files after every file transfer. 
		# Counting them every 5 file transfers seems fine :-)
		self.counter_for_next_update = 5
		
		
		
	def update_dialog(self, message):
	
		# Every 5 files moved, update dialog
		if self.counter_for_next_update == 5:
			transferred_total = 0
			
			# Loop through the final directory paths and total up the size of the ones that have been moved
			# shutil does a move by copying and then deleting, so size must be counted on the copied to end.
			for d in self.final_dirs:
				if os.path.exists(d):
					transferred_total = transferred_total + Model.get_file_count(d)
			
			
			# Update dialog with new count value
			(keepGoing, skip) = self.dlg.Update(transferred_total)
			
			# Reset counter
			self.counter_for_next_update = 0
		

		self.counter_for_next_update = self.counter_for_next_update + 1
	
	
	
	def destroy_dialog(self, message):
		'''Closes the dialog'''
		self.dlg.Destroy()



class MainFrame ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = "Steam mover", pos = wx.DefaultPosition, size = wx.Size( 811,237 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL, name = "Steam mover" )
		
		icon = wx.Icon(sys.path[0] + os.sep + 'icon.png', wx.BITMAP_TYPE_PNG)
		self.SetIcon(icon)
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		main_boxsizer = wx.BoxSizer( wx.HORIZONTAL )
		
		left_boxsizer = wx.BoxSizer( wx.VERTICAL )
		
		self.left_header = wx.StaticText( self, wx.ID_ANY, u"SteamApps folder", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.left_header.Wrap( -1 )
		self.left_header.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )
		
		left_boxsizer.Add( self.left_header, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )
		
		#self.left_dirpicker = wx.DirPickerCtrl( self,  message="Select a folder", name='primary_dirpicker' )
		#left_boxsizer.Add( self.left_dirpicker, 0, wx.ALL|wx.EXPAND, 5 )
		self.primary_dir_choice_button = wx.Button(self, -1, "Select a folder")
		left_boxsizer.Add( self.primary_dir_choice_button, 0, wx.ALL|wx.EXPAND, 5 )
		
		left_listboxChoices = []
		self.left_listbox = ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, left_listboxChoices, wx.LB_EXTENDED|wx.LB_NEEDED_SB|wx.LB_SORT )
		left_boxsizer.Add( self.left_listbox, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		main_boxsizer.Add( left_boxsizer, 1, wx.EXPAND, 5 )
		
		buttons_boxsizer = wx.BoxSizer( wx.VERTICAL )
		
		
		buttons_boxsizer.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.move_right_button = wx.Button( self, label=">", pos=wx.Point( 20,40 ), name='move_to_secondary_button' )
		buttons_boxsizer.Add( self.move_right_button, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.move_left_button = wx.Button( self, label="<", name='move_to_primary_button')
		buttons_boxsizer.Add( self.move_left_button, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		
		buttons_boxsizer.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		
		main_boxsizer.Add( buttons_boxsizer, 0, wx.EXPAND|wx.FIXED_MINSIZE|wx.LEFT|wx.RIGHT, 15 )
		
		right_boxsizer = wx.BoxSizer( wx.VERTICAL )
		
		self.right_header = wx.StaticText( self, wx.ID_ANY, u"Other folder", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.right_header.Wrap( -1 )
		self.right_header.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )
		
		right_boxsizer.Add( self.right_header, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )
		
		#self.right_dirpicker = wx.DirPickerCtrl( self,  message="Select a folder", name='secondary_dirpicker' )
		#right_boxsizer.Add( self.right_dirpicker, 0, wx.ALL|wx.EXPAND, 5 )
		self.secondary_dir_choice_button = wx.Button(self, -1, "Select a folder")
		right_boxsizer.Add( self.secondary_dir_choice_button, 0, wx.ALL|wx.EXPAND, 5 )
		
		right_listboxChoices = []
		self.right_listbox = ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, right_listboxChoices, wx.LB_EXTENDED|wx.LB_NEEDED_SB|wx.LB_SORT )
		right_boxsizer.Add( self.right_listbox, 1, wx.ALL|wx.EXPAND, 5 )		
		
		main_boxsizer.Add( right_boxsizer, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( main_boxsizer )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.on_frame_close )
		#self.left_dirpicker.Bind( wx.EVT_DIRPICKER_CHANGED, self.on_change_dir_choice )
		self.primary_dir_choice_button.Bind( wx.EVT_BUTTON, self.on_change_primary_dir_choice )
		self.move_right_button.Bind( wx.EVT_BUTTON, self.on_games_move )
		self.move_left_button.Bind( wx.EVT_BUTTON, self.on_games_move )
		#self.right_dirpicker.Bind( wx.EVT_DIRPICKER_CHANGED, self.on_change_dir_choice )
		self.secondary_dir_choice_button.Bind( wx.EVT_BUTTON, self.on_change_secondary_dir_choice )
	
	def __del__( self ):
		pass
	

