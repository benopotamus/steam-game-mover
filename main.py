#!/usr/bin/env python

'''Allows easy moving (with symlinking) of folders to and from the SteamApps folder.

Intended for users with an SSD that cannot hold all their Steam games. Allows them to easily move games not currently being played to a slower drive easily. And then move them back at a later date. The symlinking means the games can still be played regardless of which drive they are on.



	 This program is free software: you can redistribute it and/or modify
	 it under the terms of the GNU General Public License as published by
	 the Free Software Foundation, either version 3 of the License, or
	 (at your option) any later version.

	 This program is distributed in the hope that it will be useful,
	 but WITHOUT ANY WARRANTY; without even the implied warranty of
	 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	 GNU General Public License for more details.

	 You should have received a copy of the GNU General Public License
	 along with this program.  If not, see <http://www.gnu.org/licenses/>.
	 
'''

import os, wx
import layout, Model
from wx.lib.pubsub import Publisher as pub
	


class Frame(layout.MainFrame):
	'''Used wxFormBuilder to create the UI so create an instance of that and overwrite necessary methods and attributes)'''
	
	def __init__(self, parent):
		super( Frame, self ).__init__(parent)
		
		#### The following binds/subscribes controller functions to model broadcasts ####
		# These will all just take the broadcast and update the view/widgets from layout.py
		pub.subscribe(self.primary_path_changed, "PRIMARY PATH CHANGED")
		pub.subscribe(self.secondary_path_changed, "SECONDARY PATH CHANGED")
		pub.subscribe(self.games_move_to_secondary, "GAMES MOVED TO SECONDARY")
		pub.subscribe(self.games_move_to_primary, "GAMES MOVED TO PRIMARY")
		pub.subscribe(self.display_move_dialog, "MOVING GAMES")
		pub.subscribe(self.window_size_changed, "WINDOW SIZE CHANGED")
		pub.subscribe(self.window_coords_changed, "WINDOW COORDS CHANGED")
		pub.subscribe(self.use_default_window_size, "NO SIZE FOUND")
		
		# Model is created after subscriptions because it broadcasts on instantiation (when it gets settings from config file)
		self.model = Model.Model()
		
	
	#### The following 'on' methods are bound to the widgets in layout.py	####
	
	def on_games_move( self, event ):
		if event.GetEventObject().GetName() == 'move_to_secondary_button':
			games = self.left_listbox.GetSelectionsStrings()
			self.model.move_games_to_secondary(games)
		elif event.GetEventObject().GetName() == 'move_to_primary_button':
			games = self.right_listbox.GetSelectionsStrings()
			self.model.move_games_to_primary(games)
		event.Skip()
	
	def on_change_primary_dir_choice(self, event):
		# In this case we include a "New directory" button. 
		dlg = wx.DirDialog(self, "Choose a directory:", style=wx.DD_DEFAULT_STYLE)
		if dlg.ShowModal() == wx.ID_OK:
			self.model.change_primary_path(dlg.GetPath())
		# Only destroy a dialog after we're done with it
		dlg.Destroy()
		
	def on_change_secondary_dir_choice(self, event):
		# In this case we include a "New directory" button. 
		dlg = wx.DirDialog(self, "Choose a directory:", style=wx.DD_DEFAULT_STYLE)
		if dlg.ShowModal() == wx.ID_OK:
			self.model.change_secondary_path(dlg.GetPath())
		# Only destroy a dialog after we're done with it
		dlg.Destroy()
	
	def on_frame_close( self, event ):
		''' Save window position and size on close'''
		self.model.change_window_size(self.GetSize())
		self.model.change_window_coords(self.GetPosition())
		event.Skip()
		
		
		
	
	#### Broadcast response methods ####
	
	def primary_path_changed(self,message):
		self.primary_dir_choice_button.SetLabel(message.data['path'])
		self.left_listbox.SetItems(message.data['path_folders'])
		
	def secondary_path_changed(self,message):
		self.secondary_dir_choice_button.SetLabel(message.data['path'])
		self.right_listbox.SetItems(message.data['path_folders'])
		
	def games_move_to_secondary(self,message):
		self.left_listbox.SetItems(message.data['primary_path_folders'])
		self.right_listbox.SetItems(message.data['secondary_path_folders'])
	# Same method for games_move_to_primary
	games_move_to_primary = games_move_to_secondary
		
	def window_size_changed(self,message):
		self.SetSize(message.data)
		
	def window_coords_changed(self,message):
		self.SetPosition(message.data)
	
	def use_default_window_size(self,message):
		self.Fit()
		
	def display_move_dialog(self, message):
		'''When model broadcasts games are being moved, creates a file moving (progress) dialog'''
		self.progress_dialog = layout.Moving_progress_dialog(self, message.data['initial_path'], message.data['final_path'], message.data['game_names'])
	
	
	
class App(wx.App):
	
	def OnInit(self):
		self.frame = Frame(parent=None)
		self.frame.Show()
		self.SetTopWindow(self.frame)		
		return True
		
if __name__ == '__main__':
	app = App()
	app.MainLoop()
