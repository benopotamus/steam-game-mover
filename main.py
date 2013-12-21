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

import os, shutil, ast, wx
import layout


def update_settings_file(attribute, value):
	'''Writes the new settings to the settings file
	
	File format
	
	primary=[path]
	secondary=[path]
	'''
		
	with open('.config', 'r+') as FILE:
		new_contents = []
		attribute_found = False
		
		# Loop over the lines in the file to find the line with the matching attribute name
		for line in FILE:
			# when the line is found, replace it with the value passed in
			if line.startswith(attribute):
				new_contents.append(attribute + '=' + value)
				attribute_found = True
			# otherwise just use the existing line
			else:
				new_contents.append(line.rstrip())
		
		# If the attribute was not found in the file, then add it
		if attribute_found is not True:
			new_contents.append(attribute + '=' + value)
		
		FILE.seek(0)
		FILE.write(os.linesep.join(new_contents))


	
	
	
def setup_frame():
	'''Performs startup setup.
	
	Specifically sets the dirpickers.
	Also creates config file if it doesn't already exist'''
	# TODO: resolve GTK bug which preent this from working
	
	primary_path = None
	secondary_path = ''
	
	# If file does not exist, create it and add the default primary path
	if not os.path.isfile('.config'):	
		with open('.config', 'w') as FILE:
			primary_path = os.path.expanduser("~") + '/.steam/steam/SteamApps/common/'
			app.frame.left_dirpicker.SetPath(primary_path)
			app.frame.left_listbox.SetItems( os.listdir(primary_path) )
			FILE.write('primary=' + primary_path + os.linesep)
			FILE.write('secondary=' + os.linesep)
			
	else:
		with open('.config', 'r+') as FILE:
			
			size_set = False
			
			# Get the primary and secondary paths from the settings file (if present)
			for line in FILE:
				
				if line.startswith('primary'):
					value = line[line.find('=')+1:].rstrip()
					app.frame.left_dirpicker.SetPath(value)
					app.frame.left_listbox.SetItems( os.listdir(value) )
					
				elif line.startswith('secondary'):
					value = line[line.find('=')+1:].rstrip()
					if value != '':
						app.frame.right_dirpicker.SetPath(value)
						app.frame.right_listbox.SetItems( os.listdir(value) )
						
				elif line.startswith('window_coords'):
					value = line[line.find('=')+1:].rstrip()
					app.frame.SetPosition(ast.literal_eval(value))
					
				elif line.startswith('window_size'):
					size_set = True
					value = line[line.find('=')+1:].rstrip()
					app.frame.SetSize(ast.literal_eval(value))
			
			# If the size was not set using config values then use wxPython's autosizing
			if size_set is not True:
				app.frame.Fit()


	

class Frame(layout.MainFrame):
	'''Used wxFormBuilder to create the UI so create an instance of that and overwrite necessary methods and attributes)'''
	
	def move_folder_to_secondary( self, event ):
		'''Moves a folder to the secondary storage'''
		primary_path = app.frame.left_dirpicker.GetPath().rstrip(os.sep)
		secondary_path = app.frame.right_dirpicker.GetPath().rstrip(os.sep)
		games = app.frame.left_listbox.GetSelectionsStrings()
		
		for game in games:
			p = primary_path + os.sep + game
			s = secondary_path + os.sep + game
			# Move game folder to secondary drive
			shutil.move(p, s)
			# Create symlink back to primary folder
			os.symlink(s, p)
		
		event.Skip()
	
	def move_folder_to_primary( self, event ):
		'''Moves a folder to the primary storage'''
		event.Skip()
		
	def on_change_dir_choice( self, event ):
		'''Save path of dirpicker to file and update corresponding listbox items'''
		obj = event.GetEventObject()
		path = obj.GetPath()
		name = obj.GetName()
		
		game_folders = os.listdir(path)
		
		if name == 'primary_dirpicker':
			self.left_listbox.SetItems(game_folders)
			update_settings_file('primary',path)
			
		elif name == 'secondary_dirpicker':
			self.right_listbox.SetItems(game_folders)
			update_settings_file('secondary',path)
		
		event.Skip()
	
	def on_frame_close( self, event ):
		''' Save window position and size on close'''
		update_settings_file('window_coords', str(self.GetPosition()) )
		update_settings_file('window_size', str(self.GetSize()) )
		event.Skip()

	
class App(wx.App):
	
	def OnInit(self):
		self.frame = Frame(parent=None)
		self.frame.Show()
		self.SetTopWindow(self.frame)
		return True
		
if __name__ == '__main__':
	app = App()
	setup_frame()
	app.MainLoop()
