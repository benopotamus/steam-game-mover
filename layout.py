# -*- coding: utf-8 -*- 

import wx
import wx.xrc


class ListBox(wx.ListBox):
	'''A new ListBox class where the only difference is the addition of a GetSelectionsStrings method'''
	def GetSelectionsStrings(self):
		'''Retrieves a list of strings of the selected items in a listbox'''
		result = []
		
		for selection in self.GetSelections():
			result.append(self.GetString(selection))
		
		return result


class MainFrame ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 811,237 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL, name = u"Steam mover" )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		main_boxsizer = wx.BoxSizer( wx.HORIZONTAL )
		
		left_boxsizer = wx.BoxSizer( wx.VERTICAL )
		
		self.left_header = wx.StaticText( self, wx.ID_ANY, u"SteamApps folder", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.left_header.Wrap( -1 )
		self.left_header.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )
		
		left_boxsizer.Add( self.left_header, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )
		
		self.left_dirpicker = wx.DirPickerCtrl( self,  message="Select a folder", name='primary_dirpicker' )
		left_boxsizer.Add( self.left_dirpicker, 0, wx.ALL|wx.EXPAND, 5 )
		
		left_listboxChoices = []
		self.left_listbox = ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, left_listboxChoices, wx.LB_EXTENDED|wx.LB_NEEDED_SB|wx.LB_SORT )
		left_boxsizer.Add( self.left_listbox, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		main_boxsizer.Add( left_boxsizer, 1, wx.EXPAND, 5 )
		
		buttons_boxsizer = wx.BoxSizer( wx.VERTICAL )
		
		
		buttons_boxsizer.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.move_right_button = wx.Button( self, wx.ID_ANY, u">", wx.Point( 20,40 ), wx.DefaultSize, 0 )
		buttons_boxsizer.Add( self.move_right_button, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.move_left_button = wx.Button( self, wx.ID_ANY, u"<", wx.DefaultPosition, wx.DefaultSize, 0 )
		buttons_boxsizer.Add( self.move_left_button, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		
		buttons_boxsizer.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		
		main_boxsizer.Add( buttons_boxsizer, 0, wx.EXPAND|wx.FIXED_MINSIZE|wx.LEFT|wx.RIGHT, 15 )
		
		right_boxsizer = wx.BoxSizer( wx.VERTICAL )
		
		self.right_header = wx.StaticText( self, wx.ID_ANY, u"Other folder", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.right_header.Wrap( -1 )
		self.right_header.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )
		
		right_boxsizer.Add( self.right_header, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )
		
		self.right_dirpicker = wx.DirPickerCtrl( self,  message="Select a folder", name='secondary_dirpicker' )
		right_boxsizer.Add( self.right_dirpicker, 0, wx.ALL|wx.EXPAND, 5 )
		
		right_listboxChoices = []
		self.right_listbox = ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, right_listboxChoices, wx.LB_EXTENDED|wx.LB_NEEDED_SB|wx.LB_SORT )
		right_boxsizer.Add( self.right_listbox, 1, wx.ALL|wx.EXPAND, 5 )		
		
		main_boxsizer.Add( right_boxsizer, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( main_boxsizer )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.on_frame_close )
		self.left_dirpicker.Bind( wx.EVT_DIRPICKER_CHANGED, self.on_change_dir_choice )
		self.move_right_button.Bind( wx.EVT_BUTTON, self.move_folder_to_secondary )
		self.move_left_button.Bind( wx.EVT_BUTTON, self.move_folder_to_primary )
		self.right_dirpicker.Bind( wx.EVT_DIRPICKER_CHANGED, self.on_change_dir_choice )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def on_change_dir_choice( self, event ):
		print 'dir changed'
		event.Skip()
	
	def move_folder_to_secondary( self, event ):
		event.Skip()
	
	def move_folder_to_primary( self, event ):
		event.Skip()
		
	def on_frame_close( self, event ):
		event.Skip()
	

