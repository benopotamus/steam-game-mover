steam-game-mover
===========

Intended for SSD Steam users - moves selected game folders to another directory (presumably on a different HDD) and creates a symlink back so Steam doesn't know the difference :-D

This is an excuse for me to play around with wxPython - feel free to submit code improvements or complete TODO items below :-D


# Compatibility

Definitely works on Linux. It may work with MacOSX and unlikely to work with Windows due to the use of symlinking - unless Python is smart enough to work that out for me.

There is another application which does this same function for Windows called Steam Mover - http://www.traynier.com/software/steammover


# TODO

* Add a progress indicator when moving files (at present the application appears to hang but it is actually waiting for the move to happen in the background)
* Maybe add directory sizes to games list
* Add application icon
* Make compatible with MacOSX and Windows
* Investigate / resolve potential GTK wxPython wxDirPicker bug. It _seems_ to not fire directory selection events using the GTK initial drop-down list. It does fire them if the user invokes the DirPicker dialog by choosing "Other" from the list. At the moment this is simulated by the big button above the game lists.


