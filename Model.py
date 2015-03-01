'''Model for steam game mover

The file system is the ultimate data source.'''

import configparser, os, os.path
from gi.repository import GObject


'''Config structure

[DEFAULT]
Window_position = x,y
Window_size = width,height
Maximized = true/false

[STEAM_FOLDER_LIST]
Path = /
Sort_by = games/size
Sort_type = ascending/descending

[OTHER_FOLDER_LIST]
Path = /
Sort_by = games/size
Sort_type = ascending/descending

'''

config_filename = 'settings.ini'
config = configparser.ConfigParser()
config.read(config_filename)

# Create sections
c = config['DEFAULT']

if 'STEAM_FOLDER_LIST' not in config:
	config['STEAM_FOLDER_LIST'] = {}
if 'OTHER_FOLDER_LIST' not in config:
	config['OTHER_FOLDER_LIST'] = {}
	
c_liststore_primary = config['STEAM_FOLDER_LIST']
c_liststore_secondary = config['OTHER_FOLDER_LIST']




def save_application_state():
	'''Saves application state - including window size and position
	
	Assumes the configparser was being updated for duration of program'''
	with open(config_filename, 'w') as configfile:
		config.write(configfile)





class Model(GObject.GObject):
	''' The data model'''
	
	# Create custom signals to support View changing after Model updates
	__gsignals__ = {
		'primary_list_updated': (GObject.SIGNAL_RUN_FIRST, None, (int,)),
		'secondary_list_updated': (GObject.SIGNAL_RUN_FIRST, None, (int,)),
		'game_moving_update': (GObject.SIGNAL_RUN_FIRST, None, (GObject.TYPE_PYOBJECT, int, int,))
	}
	
	def __init__(self, window):
		
		GObject.GObject.__init__(self)
		
		self.window = window
		
		# Load settings from settings file, or use defaults if no file is present
		# configparser handles if file doesn't exist, or if section doesn't exist
		self.primary_path = c_liststore_primary.get('path', os.path.expanduser("~") + '/.steam/steam/SteamApps/common')
		self.secondary_path = c_liststore_secondary.get('path', None)
		
		self.window_size = list(c.get('window_size', '845,612').split(','))
		self.window_size = [int(self.window_size[0]), int(self.window_size[1])]
		self.window_position = list(c.get('window_position', '-1,-1').split(','))
		self.window_position = [int(self.window_position[0]), int(self.window_position[1])]
		self.window_maximize = bool(c.get('window_maximize', False))
		
		# Get directory contents
		self.primary_path_dirs = os.listdir(self.primary_path)
		# listdir() uses the current path if the value passed to it is None
		if self.secondary_path is None:
			self.secondary_path_dirs = []
		else:
			self.secondary_path_dirs = os.listdir(self.secondary_path)
		
		
		
		
		'''This was the previous way I was doing signals - it had the same UI blocking problem as the __gsignals__ dictionary'''
		# Custom signals - what the view needs to know about
		#GObject.signal_new('primary_list_updated', self.window, GObject.SIGNAL_RUN_LAST, GObject.TYPE_PYOBJECT, (GObject.TYPE_PYOBJECT,)) 
		#GObject.signal_new('secondary_list_updated', self.window, GObject.SIGNAL_RUN_LAST, GObject.TYPE_PYOBJECT, (GObject.TYPE_PYOBJECT,)) 
		#GObject.signal_new('game_moving_update', self.window, GObject.SIGNAL_RUN_LAST, GObject.TYPE_PYOBJECT, (GObject.TYPE_PYOBJECT, GObject.TYPE_INT, GObject.TYPE_INT)) 



		
		# Liststore values
		# These doesn't /really/ belong here. I want to keep the liststore sort order in the settings file so it persists between sessions
		# Putting it here keeps all the settings file stuff in one place.
		self.liststore_primary_sort = {
			'by' : c_liststore_primary.get('sort_by', None),
			'type' : c_liststore_primary.get('sort_type', 'ascending')
		}
		self.liststore_secondary_sort = {
			'by' : c_liststore_secondary.get('sort_by', None),
			'type' : c_liststore_secondary.get('sort_type', 'ascending')
		}
		
	
	
	###
	# Accessor functions
	###
	
	
	def get_primary_path(self):
		'''Get the primary path'''
		return self.primary_path
		
	def set_primary_path(self, path):
		'''Set the primary path and call update for primary path games list'''
		self.primary_path = path
		self._update_primary_path_dirs()
		c_liststore_primary['path'] = path
	
	def _update_primary_path_dirs(self):
		'''Used by set_primary_path - updates the primary path games list'''
		if self.primary_path is None:
			self.primary_path_dirs = []
		else:
			self.primary_path_dirs = os.listdir(self.primary_path)
		self.emit('primary_list_updated', 1)
		
		
	def get_secondary_path(self):
		'''Get the secondary path'''
		return self.secondary_path
		
	def set_secondary_path(self, path):
		'''Set the secondary path and call update for secondary path games list'''
		self.secondary_path = path
		self._update_secondary_path_dirs()
		c_liststore_secondary['path'] = path
		
	def _update_secondary_path_dirs(self):
		'''Used by set_secondary_path - updates the secondary path games list'''	
		if self.secondary_path is None:
			self.secondary_path_dirs = []
		else:
			self.secondary_path_dirs = os.listdir(self.secondary_path)
		self.emit('secondary_list_updated', 1)
		
		
		
	def get_primary_games(self):
		return self._get_games('primary')
		
	def get_secondary_games(self):
		return self._get_games('secondary')
		
	def _get_games(self, path_type):
		'''Used by get_primary_games and get_secondary_games. 
		Type is primary or secondary'''
		
		if path_type == 'primary':
			p = self.primary_path
			p_dirs = self.primary_path_dirs
		elif path_type == 'secondary':
			p = self.secondary_path
			p_dirs = self.secondary_path_dirs
		
		result = []
		for directory in p_dirs:
			# Append: name_of_game , size_of_folder
			if directory is None:
				return []
			else:
				result.append( [directory, _get_directory_size(os.path.join(p,directory), nice_format=True), _get_directory_size(os.path.join(p,directory))] )
		
		return result



	# Primary sort by
	def get_liststore_primary_sort_by(self):
		return self.liststore_secondary_sort['by']
	def set_liststore_primary_sort_by(self, value):
		self.liststore_primary_sort['by'] = value
		c_liststore_primary['sort_by'] = value
	
	# Primary sort type
	def get_liststore_primary_sort_type(self):
		return self.liststore_secondary_sort['type']
	def set_liststore_primary_sort_type(self, value):
		self.liststore_primary_sort['type'] = value
		c_liststore_primary['sort_type'] = value
	
	# Secondary sort by
	def get_liststore_secondary_sort_by(self):
		return self.liststore_secondary_sort['by']
	def set_liststore_secondary_sort_by(self, value):
		self.liststore_secondary_sort['by'] = value
		c_liststore_secondary['sort_by'] = value
	
	# Secondary sort type	
	def get_liststore_secondary_sort_type(self):
		return self.liststore_secondary_sort['type']
	def set_liststore_secondary_sort_type(self, value):
		self.liststore_secondary_sort['type'] = value
		c_liststore_secondary['sort_type'] = value
	
	
	
	# Window resizing / moving
	def get_window_position(self):
		return self.window_position
	def set_window_position(self, x, y):
		self.window_position = [x,y]
		c['window_position'] = str(x) + ',' + str(y)
		
	def get_window_size(self):
		return self.window_size
	def set_window_size(self, width, height):
		self.window_size = [width,height]
		c['window_size'] = str(width) + ',' + str(height)
		
	def get_window_maximized(self):
		return self.window_maximize
	def set_window_maximized(self, maximize):
		self.window_maximize = maximize
		c['maximize'] = str(maximize)


	def move_games_to_secondary(self, games, move_dialog):
		'''Moves games to primary list.
		
		games is a list of games (the directories, not including the path)
		move_dialog is the dialog which provides feedback to the user on progress of the move'
		
		move_dialog is kind of an ID to recognise which move is taking place (in case 
		I allow multiple move dialogs in the future). Rather than passing an ID though,
		I'm just passing the dialog object instead'''
		print('moving games to secondary')
		current_file_number = 1
		total_file_number = 20
		self.emit('game_moving_update', move_dialog, current_file_number, total_file_number)
		
		import time
		time.sleep(0.5)
		self.emit('game_moving_update', move_dialog, 5, 20)
		time.sleep(0.5)
		self.emit('game_moving_update', move_dialog, 10, 20)
		time.sleep(0.5)
		self.emit('game_moving_update', move_dialog, 15, 20)
		
		self.emit('game_moving_update', move_dialog, 19, 20)

# If directory contents has changed, post a signal


# Move game dir to other disk drive
# Post a signal
# Also post many signals showing the progress


'''

update primary list			on dir change or game move
update secondary list		on dir change or game move


'''



def _get_directory_size(path, nice_format=False):
	''' Returns the size of a directory in gigabytes 
	
	Copied from: http://stackoverflow.com/questions/1392413/calculating-a-directory-size-using-python
	Uses "du -s" as it it significantly faster than pure Python directory recursion
	'''
	import subprocess
	size = int(subprocess.check_output(['du','-s', path]).split()[0].decode('utf-8'))
	
	if nice_format:
		size = float(size) / 1024 / 1024
		size = round(size, 1)
		size = str(size).split('.0')[0] # Remove .0 if it ends in that
	
	return size


def _get_file_count(path):
	'''Returns the number of files in a directory (path)
	
	Counting is recursive (will count files in subdirectories) and will not count directories themselves as files.'''
	return sum([len(files) for r, d, files in os.walk(path)])








