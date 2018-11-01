#! /usr/bin/env python3
# 
# GUI Which helps the user to select files to be mapped and creates a JSON file
# 
# Original Author: Vasu Raguram
# 

#Import the necesarry libraries for the GUI to run.
import sys
import os
import json
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *

#Define the parent and child relationship that connects all of the aspects of the GUI
def are_parent_and_child(parent, child):
    while child.isValid():
        if child == parent:
            return True
        child = child.parent()
    return False

#First window to open that allows the user to choose the files/directories to be mapped
class SelectionWindow(QtGui.QDialog):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        layout = QtGui.QVBoxLayout(self)

        # Add checkable directory tree defined in CheckableDirModel
        self.model = CheckableDirModel()
        # model = DestinationWindow()
        self.view = QtGui.QTreeView()
        self.view.setModel(self.model)

        # Make window resize to contents
        self.view.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.view.header().setStretchLastSection(False)

        # Set root directory to example path chosen earlier by user
        self.view.setRootIndex(self.model.index(example_path))
        #/mnt/max/shared/code/internal/utilities/file_mapper
        # Set appearance of SelectionWindow object
        self.resize(1000, 500)
        self.setWindowTitle("Choose Items to Copy/Move/Symlink")
        layout.addWidget(self.view)

        # Add OK and Cancel buttons
        buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.open_dest)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def open_dest(self):
        destwindow = DestinationWindow()
        destwindow.show()


class CheckableDirModel(QtGui.QDirModel):
    """Model that populates SelectionWindow with a checkable directory tree."""
    def __init__(self, parent=None):
        QtGui.QDirModel.__init__(self, None)
        self.checks = {}

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.CheckStateRole and index.column() == 0:
            return self.checkState(index)
        return QtGui.QDirModel.data(self, index, role)


    def flags(self, index):
        return QtGui.QDirModel.flags(self, index) | QtCore.Qt.ItemIsUserCheckable

    #Code which verifies if the boxex are checked or not
    def checkState(self, index):
        while index.isValid():
            if index in self.checks:
                return self.checks[index]
            index = index.parent()
        return QtCore.Qt.Unchecked

    #Sets the value of the checkboxes for interpretation
    def setData(self, index, value, role):
        if role == QtCore.Qt.CheckStateRole and index.column() == 0:
            self.layoutAboutToBeChanged.emit()
            for i, v in self.checks.items():
                if are_parent_and_child(index, i):
                    self.checks.pop(i)
            self.checks[index] = value
            self.layoutChanged.emit()
            return True

        return QtGui.QDirModel.setData(self, index, value, role)

    #Gets the path from the checked files
    def get_savepath(self):
        """Allow user to set name and directory of JSON to be created."""
        savepath = str(QFileDialog.getSaveFileName(anchor_win, 'Save As'))
        if not savepath.endswith('.json'):  # Add file extension if user didn't
            savepath += '.json'
        return savepath

    #Pops a message up after the JSON creation process is complete
    def end_message(self, text):
        """Provide user-friendly information about whether JSON creation was successful."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
	msg.setText(text)
	msg.setWindowTitle('JSON creation process finished')

	msg.setStandardButtons(QMessageBox.Ok)
	msg.exec_()


    def get_directory_structure(self):
        """
        Based on user's selections, record relative paths and deletion state of all files in chosen
        directory in a nested dictionary.
        """
        dir_dict = {}
        rootdir = example_path.rstrip(os.sep)
        dir_dict['SOURCE'] = rootdir
        start = rootdir.rfind(os.sep) + 1

        for dirpath, dirnames, filenames in os.walk(rootdir):
            for filename in filenames:
                abs_path = os.path.join(dirpath, filename)
                # Record whether each file was marked as 'keep' or 'delete' based on checked status
                if self.checkState(self.index(abs_path)) == QtCore.Qt.Checked:
                    rel_path = os.path.relpath(abs_path, rootdir).lstrip(os.sep)
                    dir_dict[rel_path] = ''

        return dir_dict

    #Make the JSON file from the directory structure and the savepath retrieved from the previous function
    def makeJSON(self):
        """Add information from get_directory_structure to a JSON."""
	d = self.get_directory_structure()
	savepath = self.get_savepath()
	try:
	    with open(savepath, 'w') as json_file:
                json.dump(d, json_file, sort_keys=True, indent=4, separators=(',', ': '))
                msg_text = 'JSON created successfully.'
        except:
	    msg_text = 'JSON creation process was not successful. Please try again.'
	self.end_message(msg_text)

        # Make all windows disappear after end message window is closed
        QtCore.QCoreApplication.instance().quit()

#Window creation for mapping a destination for the  files
class DestinationWindow(QWidget):
    # create our window
    # app = QApplication(sys.argv)
    def __init__(self, parent=None):
        QWidget.__init__(self)

        self.setWindowTitle('Choose destination for selected key')

        # Create textbox
        textbox1 = QLineEdit(self)
        textbox1.move(170, 20)
        textbox1.resize(280,40)
        textbox1.setText("/")

        textbox2 = QLineEdit(self)
        textbox2.move(170, 100)
        textbox2.resize(280,40)

        # Set window size.
        self.resize(650, 500)

        # Create a button in the window
        button1 = QPushButton('Browse', self)
        button1.move(500,25)

        button2 = QPushButton('Browse', self)
        button2.move(500,105)

        #Connect the buttons when clicked to the on_click function
        button1.clicked.connect(self.on_click)
        button2.clicked.connect(self.on_click)


    #Function brings up the directory for destination in the editable text box
    def on_click(self):
        folder1 = QFileDialog.getExistingDirectory(QWidget(), 'Open Folder', '/')
        textbox1.setText(folder1)


#Opens all the windows in the GUI
if __name__ == '__main__':

    #Initializes the GUI window
    app = QtGui.QApplication(sys.argv)

    anchor_win = QMainWindow()

        # Allow user to choose directory to populate checkable directory model
    example_path = str(QFileDialog.getExistingDirectory(anchor_win, 'Select Example Directory'))

    # Create and display custom SelectionWindow so user can select files to delete
    win = SelectionWindow()
    win.show()

    sys.exit(app.exec_())
