from gi.repository import Gtk

class Dialog(Gtk.Dialog):
	'''The dialog to show files being moved. 

	It doesn't use a glade file because I want to make a custom dialog 
	that looks like the nautilus file operations dialog, and it would
	need it's own glade file and builder etc - which makes the code
	more complicated.

	This dialog has 2 rows
	1. The progress bar and cancel button
	2. xGB of yGB

	The dialog is modal because I /think/ I need threads to do multiple game moves at once'''

	def __init__(self, parent):
		Gtk.Dialog.__init__(self, "Moving games", parent, flags=Gtk.DialogFlags.MODAL)

		self.set_default_size(400, 50)

		#label = Gtk.Label("This is a dialog to display additional information")
		
		#
		#box.add(label)
		
		
		# Create the progress bar row first
		self.box_progress_bar = Gtk.Box(Gtk.Orientation.HORIZONTAL, spacing=7)
		
		self.progressbar = Gtk.ProgressBar()
		self.progressbar.set_valign(Gtk.Align.CENTER)
		self.box_progress_bar.pack_start(self.progressbar, True, True, 3)
		
		self.button_cancel = Gtk.Button(image=Gtk.Image(stock=Gtk.STOCK_CANCEL))
		self.box_progress_bar.pack_start(self.button_cancel, False, False, 3)
		

		# Create file size row
		self.box_file_size = Gtk.Box(Gtk.Orientation.HORIZONTAL, spacing=7)
		self.label_x = Gtk.Label()
		self.label_y = Gtk.Label()
		self.label_of = Gtk.Label(' of ')
		
		self.label_x.set_halign(Gtk.Align.START)
		self.label_y.set_halign(Gtk.Align.START)
		self.label_of.set_halign(Gtk.Align.START)
		
		self.box_file_size.pack_start(self.label_x, True, True, 0)
		self.box_file_size.pack_start(self.label_of, True, True, 0)
		self.box_file_size.pack_start(self.label_y, True, True, 0)
		
		
		# Add rows to dialog for display
		box = self.get_content_area()
		box.add(self.box_progress_bar)
		box.add(self.box_file_size)
		
		
		# Signals
		self.button_cancel.connect("clicked", self.on_button_cancel_clicked)
		
		self.show_all()
	
		
	def on_button_cancel_clicked(self, widget):
		self.destroy()
		# TODO: Undo file move (or emit signal that results in that)
			
	def update(self, current_number, total_number):
		'''Updates the dialog box - "X of Y" values and progress bar.'''
		
		# Close dialog if work is complete
		if current_number == total_number:
			self.destroy()
		else:
			self.label_x.set_text(str(current_number) + ' GiB')
			self.label_y.set_text(str(total_number) + ' GiB')
			self.progressbar.set_fraction(current_number / total_number)
