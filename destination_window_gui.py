#! /usr/bin/python3

import sys
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import *
from PyQt4 import QtGui

# create our window
app = QApplication(sys.argv)
w = QWidget()
w.setWindowTitle('Choose destination for selected key')

# Create textbox
textbox = QLineEdit(w)
textbox.move(170, 20)
textbox.resize(280,40)

textbox2 = QLineEdit(w)
textbox2.move(170, 100)
textbox2.resize(280,40)

# Set window size.
w.resize(650, 500)

# Create a button in the window
button = QPushButton('Browse', w)
button.move(500,25)

button2 = QPushButton('Browse', w)
button2.move(500,105)


# Create the actions
@pyqtSlot()
def on_click(self):
    # QtGui.QMainWindow.on_click(self)
    #
    # layout = QtGui.QVBoxLayout(self)

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

# connect the signals to the slots
button.clicked.connect(on_click)

# Show the window and run the app
w.show()
app.exec_()
