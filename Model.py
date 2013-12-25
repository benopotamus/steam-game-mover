import os, sys, shutil, ast
from wx.lib.pubsub import Publisher as pub		

config_file = sys.path[0] + os.sep + '.config'




# Improve shutil.copy2
# Makes a copy of 'copy2', then makes a new copy2 with broadcasting and includes the original copy2 in the flow, then assigns the new copy2 to the shutil namespace so it is used instead of the original
shutil.builtin_copy2 = shutil.copy2

def copy2(src,dst):
	'''Wraps shutil.copy2 so it broadcasts whenever a file has been copied
	
	Used for progress dialog
	'''
	# Call original copy2
	shutil.builtin_copy2(src,dst)
	# Broadcast file copied
	pub.sendMessage("FILE MOVED", None)
	
shutil.copy2 = copy2
	
	
	
	

def _update_settings_file(attribute, value):
	'''Writes the new settings to the settings file
	
	File format
	
	primary=[path]
	secondary=[path]
	'''
	
	
	# Ensure value is string (for lazy saving)
	value = str(value)
		
	with open(config_file, 'r+') as FILE:
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
		FILE.truncate() # Discard remaining file contents (after this position)


def get_directory_size(path, unit='B'):
	''' Returns the size of a directory - in bytes by default. 
	
	Also supports KB
	
	Copied from: http://stackoverflow.com/questions/1392413/calculating-a-directory-size-using-python
	Apparently this has the same result as "du -sb"
	'''
	
	total_size = 0
	seen = set()

	for dirpath, dirnames, filenames in os.walk(path):
		for f in filenames:
			fp = os.path.join(dirpath, f)

			try:
				stat = os.stat(fp)
			except OSError:
				continue

			if stat.st_ino in seen:
				continue

			seen.add(stat.st_ino)

			total_size += stat.st_size
	
	if unit == 'KB':
		total_size = int(total_size / 1024)
	
	return total_size  # default size in bytes


def get_file_count(path):
	'''Returns the number of files in a directory (path)
	
	Counting is recursive (will count files in subdirectories) and will not count directories themselves as files.'''
	return sum([len(files) for r, d, files in os.walk(path)])
	
		

class Model:
	def __init__(self):
		self.window_coords = None
		self.window_size = None
		
		self.primary_path = None
		self.primary_path_folders = None
		self.secondary_path = None
		self.secondary_path_folders = None
		
		
		# If config file exists, initialize values from there
		if os.path.isfile(config_file):	
			with open(config_file, 'r+') as FILE:
				size_set = False
				
				# Get the primary and secondary paths from the settings file (if present)
				for line in FILE:
					
					if line.startswith('primary'):
						value = line[line.find('=')+1:].rstrip()
						self.change_primary_path(value)
						
					elif line.startswith('secondary'):
						value = line[line.find('=')+1:].rstrip()
						self.change_secondary_path(value)
							
					elif line.startswith('window_coords'):
						value = line[line.find('=')+1:].rstrip()
						self.change_window_coords(ast.literal_eval(value))
						
					elif line.startswith('window_size'):
						value = line[line.find('=')+1:].rstrip()
						self.change_window_size(ast.literal_eval(value))

		
		
		else:
			with open(config_file, 'w') as FILE:
				primary_path = os.path.expanduser("~") + '/.steam/steam/SteamApps/common'
				self.change_primary_path(primary_path)
				FILE.write('primary=' + primary_path + os.linesep)
				FILE.write('secondary=')
				pub.sendMessage("NO SIZE FOUND", True)	
		

	def change_primary_path(self, path):
		if os.path.exists(path):
			self.primary_path = path
			self._update_list('primary')
			_update_settings_file('primary', path)
			pub.sendMessage("PRIMARY PATH CHANGED", 
				{ 'path': self.primary_path,
				  'path_folders' : self.primary_path_folders
				})		
			
	def change_secondary_path(self, path):
		if os.path.exists(path):
			self.secondary_path = path
			self._update_list('secondary')
			_update_settings_file('secondary', path)
			pub.sendMessage("SECONDARY PATH CHANGED", 
				{ 'path': self.secondary_path,
				  'path_folders' : self.secondary_path_folders
				})


	def change_window_size(self, size):
		self.window_size = size
		_update_settings_file('window_size', size)
		pub.sendMessage("WINDOW SIZE CHANGED", self.window_size)

	def change_window_coords(self, coords):
		self.window_coords = coords
		_update_settings_file('window_coords', coords)
		pub.sendMessage("WINDOW COORDS CHANGED", self.window_coords)
	
	def move_games_to_secondary(self, game_names):
		'''Moves a folder to the secondary storage'''
		self._move_games_common(game_names, 'secondary')
	
	def move_games_to_primary(self, game_names):
		'''Moves a folder to the primary storage'''
		self._move_games_common(game_names, 'primary')


		
	def _move_games_common(self, game_names, listtype):	
		if listtype == 'secondary':
			message_type = 'SECONDARY'
			# If moving games to secondary, broadcast that files are being moved _from_ primary (used to show the progress dialog)
			pub.sendMessage("MOVING GAMES", { 
				'initial_path' : self.primary_path,
				'final_path' : self.secondary_path,
				'game_names' : game_names})
		elif listtype == 'primary':
			message_type = 'PRIMARY'
			# If moving games to primary, broadcast that files are being moved _from_ secondary (used to show the progress dialog)
			pub.sendMessage("MOVING GAMES", { 
				'initial_path' : self.secondary_path,
				'final_path' : self.primary_path,
				'game_names' : game_names})
		
		
		# Move games
		for game in game_names:
			p = self.primary_path + os.sep + game
			s = self.secondary_path + os.sep + game
			
			if listtype == 'secondary':
				# Move game folder to secondary
				shutil.move(p,s) # Includes "FILE MOVED" broadcast
				# Create symlink back to primary folder
				os.symlink(s,p)
				
			elif listtype == 'primary':
				# Remove symlink on primary
				os.remove(p)
				# Move game folder back to primary
				shutil.move(s,p) # Includes "FILE MOVED" broadcast
			
		
		self._update_list('primary')
		self._update_list('secondary')
		
		pub.sendMessage("GAMES MOVED TO " + message_type, 
			{ 'primary_path_folders' : self.primary_path_folders,
			  'secondary_path_folders' : self.secondary_path_folders,
			})
	
	def _update_list(self, listtype):
		if listtype == 'primary':
			self.primary_path_folders = os.listdir(self.primary_path)
			path = self.primary_path
			folders = self.primary_path_folders
		elif listtype == 'secondary':
			self.secondary_path_folders = os.listdir(self.secondary_path)
			path = self.secondary_path
			folders = self.secondary_path_folders
			
		for folder in folders[:]:
			if os.path.islink(path + os.sep + folder):
				folders.remove(folder)
