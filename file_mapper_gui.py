#! /usr/bin/python3



import sys
import os
import json
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *

def are_parent_and_child(parent, child):
    while child.isValid():
        if child == parent:
            return True
        child = child.parent()
    return False


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


    def checkState(self, index):
        while index.isValid():
            if index in self.checks:
                return self.checks[index]
            index = index.parent()
        return QtCore.Qt.Unchecked


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


    def get_savepath(self):
        """Allow user to set name and directory of JSON to be created."""
        savepath = str(QFileDialog.getSaveFileName(anchor_win, 'Save As'))
        if not savepath.endswith('.json'):  # Add file extension if user didn't
            savepath += '.json'
        return savepath


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

if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    anchor_win = QMainWindow()

    # Allow user to choose directory to populate checkable directory model
    example_path = str(QFileDialog.getExistingDirectory(anchor_win, 'Select Example Directory'))

    # Create and display custom SelectionWindow so user can select files to delete
    win = SelectionWindow()
    win.show()

    sys.exit(app.exec_())
