#! /usr/bin/python3

import sys
from PyQt4.QtGui import *
from PyQt4 import QtGui
from PyQt4 import QtCore


def on_click(self):
    folder1 = QFileDialog.getExistingDirectory(QWidget(), 'Open Folder', '/')
    textbox1.setText(folder1)


# create our window
app = QApplication(sys.argv)
w = QWidget()
w.setWindowTitle('Choose destination for selected key')
w.resize(850, 500)

num=5

statbox = []
for s in range(num):
    statbox.append(QLineEdit(w))
    statbox[s].setReadOnly(True)
    statbox[s].move(30,20+(80*s))
    statbox[s].resize(180,40)


textbox = []
for t in range(num):
    textbox.append(QLineEdit(w))
    textbox[t].move(170,20+(80*t))
    textbox[t].resize(280,40)


button = []
for b in range(num):
    button.append(QPushButton('Browse'))
    button[b].move(500,25+(80*b))
    button[b].resize(80,40)


for bc in button:
    bc.clicked.connect(on_click)


buttonWidget = QWidget()

layout = QVBoxLayout()
AbsButton = QRadioButton("Absolute Path")
RelButton = QRadioButton("Relative Path")
RadioGroup= QButtonGroup(buttonWidget)
RadioGroup.addButton(AbsButton)
RadioGroup.addButton(RelButton)
RadioGroup.setExclusive(True)
buttonWidget.move(30,20)
buttonWidget.resize(180,80)
layout.addWidget(AbsButton)
layout.addWidget(RelButton)



buttons = QtGui.QDialogButtonBox(
    QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
    QtCore.Qt.Horizontal)


# Show the window and run the app
w.show()
app.exec_()
