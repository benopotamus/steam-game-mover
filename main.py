#!/usr/bin/env python
from gi.repository import Gtk
import Model, Dialog_move

class Handler:
	def on_window_delete_event(self, *args):
		Model.save_application_state()
		Gtk.main_quit(*args)
		
	
	def on_window_configure_event(self, window, event):
		'''Get data to rememeber window position and size between sessions
		
		This could have been done on quit but the plan was to save this data to file as it changed. 
		For the moment I have opted to save on quit instead as resizing and moving generate many events for the duration of those actions.
		The downside is if the program crashes the settings will be lost - not a big deal for a program like this one.
		'''
		model.set_window_position(event.x, event.y)
		model.set_window_size(event.width, event.height)
		model.set_window_maximized(window.is_maximized())
		

	def on_button_move_to_secondary_clicked(self, button):
		(liststore_data, pathlist) = treeview_primary_selection.get_selected_rows()
		
		games_list = []
		for path in pathlist:
			tree_iter = liststore_data.get_iter(path)
			value = liststore_data.get_value(tree_iter,0)
			games_list.append(value)
		
		if len(games_list) > 0:
			# Display dialog
			dialog = Dialog_move.Dialog(window)
			# Tell model to move games
			model.move_games_to_secondary(games_list, dialog)
		
		
		
		#if treeiter != None:
		#	print( "You selected", data[treeiter][0])
			
		#model.move_games_to_secondary()
		#window.emit('primary_list_updated', 'test string')
		
		
		#response = dialog.run()
		#dialog.run()

		'''if response == Gtk.ResponseType.OK:
			print("The OK button was clicked")
		elif response == Gtk.ResponseType.CANCEL:
			print("The Cancel button was clicked")'''

		#dialog.destroy()
		
		

	def on_button_move_to_primary_clicked(self, button):
		print("on_button_move_to_primary_clicked")

	def on_filechooserbutton_primary_selection_changed(self, button):
		model.set_primary_path(button.get_filename())
		
	def on_filechooserbutton_secondary_selection_changed(self, button):
		model.set_secondary_path(button.get_filename())
		
	def on_button_cancel_move_clicked(self, button):
		pass
	
	def on_dialog_move_delete_event(self, dialog, event):
		dialog.hide()


# Custom handlers for signals emitted by model
# `window` is a parameter only because all signals are defined on it
def primary_list_updated(window, msg):
	liststore_primary.clear()
	for row in model.get_primary_games():
		liststore_primary.append(row)

def secondary_list_updated(window, msg):
	liststore_secondary.clear()
	for row in model.get_secondary_games():
		liststore_secondary.append(row)

def game_moving_update(window, dialog, current_file_number, total_file_number):
	'''Updates the view (move dialog box) "X of Y" numbers and progress bar'''
	print('runnning game_moving_update')
	dialog.update(current_file_number, total_file_number)




# Builder loads widgets from glade file
# .get_object() is used to get a reference to the widget
builder = Gtk.Builder()
builder.add_from_file("main.glade")
builder.connect_signals(Handler())

builder.get_object('treemodelsort_primary').set_sort_column_id(0, Gtk.SortType.ASCENDING)
builder.get_object('treemodelsort_secondary').set_sort_column_id(0, Gtk.SortType.ASCENDING)

liststore_primary = builder.get_object('liststore_primary')
liststore_secondary = builder.get_object('liststore_secondary')

treeview_primary = builder.get_object('treeview_primary')
treeview_secondary = builder.get_object('treeview_secondary')

treeview_primary_selection = treeview_primary.get_selection()
treeview_secondary_selection = treeview_secondary.get_selection()

window = builder.get_object("window")
model = Model.Model(window)


# Bind callbacks (defined above) for model signals
model.connect('primary_list_updated', primary_list_updated)
model.connect('secondary_list_updated', secondary_list_updated)

model.connect('game_moving_update', game_moving_update)



### 
# Populate View with initial data
###

### Window parameters

# Window size
s = model.get_window_size()
window.resize(s[0], s[1])

# Window position
s = model.get_window_position()
# If the settings file did not exist at startup, the model position is -1,-1
if s[0] == -1:
	window.set_position(Gtk.WindowPosition.CENTER)
else:
	window.move(s[0], s[1])
	
# Window maximisation
if model.get_window_maximized():
	window.maximize()

# File chooser buttons - simulates the "selection-changed" action and signal
filechooserbutton_primary = builder.get_object("filechooserbutton_primary")
filechooserbutton_secondary = builder.get_object("filechooserbutton_secondary")

if filechooserbutton_primary.set_current_folder(model.get_primary_path()): # This line simulates the UI action
	# set_current_folder returns true if successful, emit the appropriate signal
	filechooserbutton_primary.emit('selection-changed') # This line simulates the signal emiting
	
if model.get_secondary_path() is not None and filechooserbutton_secondary.set_current_folder(model.get_secondary_path()):
	# set_current_folder returns true if successful, emit the appropriate signal
	filechooserbutton_secondary.emit('selection-changed')


window.show_all()
Gtk.main()
