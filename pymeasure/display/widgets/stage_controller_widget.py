# -*- coding: utf-8 -*-
"""
Created on Wed Jun 22 19:34:07 2022

@author: mazzotti
"""

from ..Qt import QtGui
from .tab_widget import TabWidget
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QGroupBox, QDialog, QVBoxLayout, QGridLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
import numpy as np
from tkinter import Tk, filedialog
from pymeasure.experiment import Procedure
from pymeasure.experiment import IntegerParameter, FloatParameter
from pymeasure.experiment import Results
from pymeasure.experiment import Worker
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QRunnable, QThreadPool

import logging

from ..log import LogHandler
from ..Qt import QtGui
from .tab_widget import TabWidget

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())




import traceback, sys

class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    
    
    def __init__(self, axis, position):
        super().__init__()
        self.axis = axis
        self.axis.define_position(position)

    

    def run(self):
        self.progress.emit(self.axis.position)
        self.finished.emit()

        
#This Widget Class is used to move the stage to the exact position
  
class StageControllerWidget(TabWidget, QtGui.QWidget):
    """ Widget to display measurement information in Gui

    It is recommended to include this widget in all subclasses of
    :class:`ManagedWindowBase<pymeasure.display.windows.ManagedWindowBase>`
    """
    def __init__(self, name, procedure, parent=None):
        super().__init__(name, parent)
        self.layout = QVBoxLayout(self)
        
        self.procedure = procedure
        self.controller = self.procedure.controller
        self.start = procedure.start
        self.end = procedure.end

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tabs.resize(300,200)
        
        # Add tabs
        self.tabs.addTab(self.tab1,"Axis 1")
        self.tabs.addTab(self.tab2,"Axis 2")
        self.tabs.addTab(self.tab3,"Axis 3")
    
        # Create first tab
        self.tab1.layout = QVBoxLayout(self)
        self.currPosition1 = QLineEdit(self)
        self.currPosition2 = QLineEdit(self)
        self.currPosition3 = QLineEdit(self)
        
        
        self.position1 = QDoubleSpinBox(self)
        self.position1.setRange(0, 40)
        
        self.tab1.layout.addWidget(QLabel("Set Position of Stage "))
        self.tab1.layout.addWidget(self.position1)

        self.move1 = QPushButton("Move")
        self.move1.setStyleSheet("background-color : grey")
        self.move1.clicked.connect(lambda: self.move(1,float(self.position1.value())))
        self.tab1.layout.addWidget(self.move1)
        hbox1 = QHBoxLayout(self)
        hbox1.setSpacing(10)
        hbox1.addWidget(QLabel("Current Position of Stage"))
        self.enabled1 = QPushButton("Enable motor", self)
        self.enabled1.clicked.connect(lambda:(self.enableMotor(self.controller.x, self.enabled1, self.currPosition2)))
        if (self.controller.x.enabled):
            self.enabled1.setText("Disable motor")
            self.currPosition1.setText(str(self.controller.x.position))
        else:
            self.enabled1.setText("Enable motor")
            self.currPosition1.setText("NO STAGE")

        hbox1.addWidget(self.currPosition1)
        hbox1.addWidget(self.enabled1)
        
        hboxWidget = QWidget()
        hboxWidget.setLayout(hbox1)
        self.tab1.layout.addWidget(hboxWidget)
        self.tab1.layout.setSpacing(0)
        self.tab1.setLayout(self.tab1.layout)
        
        # Create second tab
        self.tab2.layout = QVBoxLayout(self)
        self.position2 = QDoubleSpinBox(self)
        self.position2.setRange(0, 40)
        
        self.tab2.layout.addWidget(QLabel("Set Position of Stage"))
        self.tab2.layout.addWidget(self.position2)
        self.move2 = QPushButton("Move")
        # changing color of button
        self.move2.setStyleSheet("background-color : grey")
        self.move2.clicked.connect(lambda: self.move(2,float(self.position2.value())))
        self.tab2.layout.addWidget(self.move2)
        
        hbox2 = QHBoxLayout(self)
        hbox2.setSpacing(10)
        hbox2.addWidget(QLabel("Current Position of Stage"))
        hbox2.addWidget(self.currPosition2)
        self.enabled2 = QPushButton("Enable motor", self)
        self.enabled2.clicked.connect(lambda: self.enableMotor(self.controller.y, self.enabled2, self.currPosition2))
        hbox2.addWidget(self.enabled2)

        if(self.controller.y.enabled):
            self.enabled2.setText("Disable motor")
            self.currPosition2.setText(str(self.controller.y.position))
        else:
            self.enabled2.setText("Enable motor")
            self.currPosition2.setText("NO STAGE")


        hboxWidget2 = QWidget()
        hboxWidget2.setLayout(hbox2)
        self.tab2.layout.addWidget(hboxWidget2)
        self.tab2.layout.setSpacing(0)
        self.tab2.setLayout(self.tab2.layout)
        
        
        
        # Create first tab
        self.tab3.layout = QVBoxLayout(self)
        self.position3 = QDoubleSpinBox(self)
        self.position3.setRange(0, 40)
        self.tab3.layout.setSpacing(0)
        self.tab3.layout.addWidget(QLabel("Set Position of Stage"))
        self.tab3.layout.addWidget(self.position3)
        self.move3 = QPushButton("Move")
        self.move3.setStyleSheet("background-color : grey")
        self.move3.clicked.connect(lambda: self.move(3,float(self.position3.value())))
        self.tab3.layout.addWidget(self.move3)
        
        hbox3 = QHBoxLayout(self)
        hbox3.setSpacing(10)
        hbox3.addWidget(QLabel("Current Position of Stage"))
        hbox3.addWidget(self.currPosition3)

        self.enabled3 = QPushButton(self)
        hbox3.addWidget(self.enabled3)
        self.enabled3.clicked.connect(lambda: self.enableMotor(self.controller.phi, self.enabled3, self.currPosition3))
        if (self.controller.phi.enabled):
            self.enabled3.setText("Disable motor")
            self.currPosition3.setText(str(self.controller.phi.position))
        else:
            self.enabled3.setText("Enable motor")
            #self.enabled3.setEnabled(False)
            self.currPosition3.setText("NO STAGE")

        hboxWidget3 = QWidget()
        hboxWidget3.setLayout(hbox3)
        self.tab3.layout.addWidget(hboxWidget3)
        self.tab3.layout.setSpacing(0)
        self.tab3.setLayout(self.tab3.layout)
        

        
        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def enableMotor(self, axis, button, position):
        self.axis = axis
        self.enabled = button
        self.position = position
        if axis != None:
            if (self.enabled.text() == "Enable motor"):
                self.controller.y.enable()
                self.position.setText(str(axis.position))
                self.enabled.setText("Disable motor")
            else:
                self.axis.disable()
                self.enabled.setText("Enable motor")
                self.position.setText("Motor disabled")
        else:
            return

    def reportProgress(self, s):
        log.info("%d%% done" % s)
        self.currPosition2.setText(str(self.controller.y.position))
        
        """Long-running task."""
        msg = QMessageBox(1, "Information", "Stage has been moved to position " + str(self.controller.y.position), QMessageBox.Ok)
        msg.exec()

    def move(self, axis, position):
        self.thread = QThread()
        if(axis == 1):
            self.worker = Worker(self.controller.x,self.position1.value())
            # Final resets
            self.move1.setEnabled(False)
            self.thread.finished.connect(
                lambda: self.move1.setEnabled(True)
            )
        if(axis == 2):
            self.worker = Worker(self.controller.y,self.position2.value())
            self.move2.setEnabled(False)
            self.thread.finished.connect(
                lambda: self.move2.setEnabled(True)
            )
        if(axis == 3):
            self.worker = Worker(self.controller.phi,self.position3.value())
            self.move3.setEnabled(False)
            self.thread.finished.connect(
                lambda: self.move3.setEnabled(True)
            )
        
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.progress.connect(self.reportProgress)
        self.thread.start()
            
            

    def _setup_ui(self):
        self.view = QtGui.QPlainTextEdit()
        self.view.setReadOnly(True)
        
    
        





    
            
    
    