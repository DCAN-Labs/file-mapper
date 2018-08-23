#! /usr/bin/python3

import sys
import os
import json
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class SelectionWindow(QtGui.QDialog):
    """GUI window where user selects items to be deleted in the chosen directory."""

    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        layout = QtGui.QVBoxLayout(self)

        # Add checkable directory tree defined in CheckableDirModel
        model = CheckableDirModel()
        self.view = QtGui.QTreeView()
        self.view.setModel(model)

        # Make window resize to contents
	self.view.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.view.header().setStretchLastSection(False)

        # Set root directory to example path chosen earlier by user
        self.view.setRootIndex(model.index(example_path))
	#/mnt/max/shared/code/internal/utilities/custom_clean
	# Set appearance of SelectionWindow object
        self.resize(1000, 500)
        self.setWindowTitle("Choose Items to Copy/Move/Symlink")
        layout.addWidget(self.view)

        # Add OK and Cancel buttons
        buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(model.makeJSON)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    anchor_win = QMainWindow()

    # Allow user to choose directory to populate checkable directory model
    example_path = str(QFileDialog.getExistingDirectory(anchor_win, 'Select Example Directory'))

    # Create and display custom SelectionWindow so user can select files to delete
    win = SelectionWindow()
    win.show()

    sys.exit(app.exec_())
