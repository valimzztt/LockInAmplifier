# -*- coding: utf-8 -*-
"""
Created on Tue Jun 14 15:23:19 2022

@author: mazzotti
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Jun 14 15:04:14 2022

@author: mazzotti
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 22:32:49 2022

@author: mazzotti
"""



import logging
from ..log import LogHandler
from ..Qt import QtGui
from .tab_widget import TabWidget
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QGroupBox, QDialog, QVBoxLayout, QGridLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
import re

import pymeasure
from pymeasure.instruments.srs import SR830
import pymeasure.display.inputs

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ParametersWidget(TabWidget, QtGui.QWidget):
    """ Widget to display logging information in GUI

    It is recommended to include this widget in all subclasses of
    :class:`ManagedWindowBase<pymeasure.display.windows.ManagedWindowBase>`
    """

    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self._setup_ui()
        self._layout()
        #initializes the lockin amplifier to control
        self.lockin = SR830("GPIB::8")
        
        


    def _setup_ui(self):
        self.view = QtGui.QPlainTextEdit()
        self.view.setReadOnly(True)
        

    def _layout(self):
        up = QVBoxLayout()
        up.addWidget(self.TimeConstant2())
        up.addWidget(self.Sensitivity())
        up.addWidget(self.FilterSlopes())



        
        down = QHBoxLayout()
        down.addWidget(self.Input())
        down.addWidget(self.InputConfig())
        down.addWidget(self.inputNotchConfig())

        
        w1 = QWidget()
        w1.setLayout(up)
        w2 = QWidget()
        w2.setLayout(down)
        
        
        self.layout =  QVBoxLayout()
        self.layout.addWidget(w1)
        self.layout.addWidget(w2)
        
        widget = QWidget()
        widget.setLayout(self.layout)
        self.setLayout(self.layout)
    def Input(self):
        layout = QVBoxLayout()
        header = QVBoxLayout()
        header.addStretch(0)
        grounding = QVBoxLayout()
        grounding.setSpacing(10)
        grounding.addStretch(0)
        
        b1 = QRadioButton ("Float")
        b1.setChecked(True)
        b2 = QRadioButton ("Grounds")
        grounding.addWidget(QLabel("Input Groundings"))
        grounding.addWidget(b1)
        grounding.addWidget(b2)
        b1.clicked.connect(lambda: self.setInputGroundings(0))
        b2.clicked.connect(lambda: self.setInputGroundings(1))
        
        coupling = QVBoxLayout()
        coupling.setSpacing(10)
        coupling.addStretch(0)
        
        b3 = QRadioButton ("AC")
        b3.setChecked(True)
        b4 = QRadioButton ("DC")
        coupling.addWidget(QLabel("Input Couplings"))
        coupling.addWidget(b3)
        coupling.addWidget(b4)
        b3.clicked.connect(lambda: self.setInputCouplings(0))
        b4.clicked.connect(lambda: self.setInputCouplings(1))
        
        w1 = QWidget()
        w1.setLayout(grounding)
        w2 = QWidget()
        w2.setLayout(coupling)
        layout.addWidget(w1)
        layout.addWidget(w2)

        w_final = QWidget()
        w_final.setLayout(layout)
        return w_final
        
    def InputConfig(self):
        layout = QVBoxLayout()
        header = QVBoxLayout()
        header.addStretch(0)
        controlsGroup = QVBoxLayout()
        controlsGroup.setSpacing(10)
        controlsGroup.addStretch(0)
        
        b1 = QRadioButton ("A")
        b2 = QRadioButton ("A - B")
        b3 = QRadioButton ("I (1 MOhm)")
        b4 = QRadioButton ("I (100 MOhm)")
        controlsGroup.addWidget(b1)
        controlsGroup.addWidget(b2)
        controlsGroup.addWidget(b3)
        controlsGroup.addWidget(b4)
        
        b1.clicked.connect(lambda: self.setInputConfig(0))
        b2.clicked.connect(lambda: self.setInputConfig(1))
        b3.clicked.connect(lambda: self.setInputConfig(2))
        b4.clicked.connect(lambda: self.setInputConfig(3))
        
        w = QWidget()
        w.setLayout(controlsGroup)
        header.addWidget(QLabel("Input Configuration"))
        header.addWidget(w)
        
        w_final = QWidget()
        w_final.setLayout(header)
        layout.addWidget(w_final)
      
        #Final Widget brining all together
        widget = QWidget()
        widget.setLayout(layout)
        return widget

   # INPUT_CONFIGS = ['A', 'A - B', 'I (1 MOhm)', 'I (100 MOhm)']
    def setInputConfig(self, option):
        self.lockin.input_config = self.lockin.INPUT_CONFIGS[option]
    def setInputGroundings(self, option):
        self.lockin.input_grounding = self.lockin.INPUT_GROUNDINGS[option]
    def setInputCouplings(self, option):
        self.lockin.input_coupling = self.lockin.INPUT_COUPLINGS[option]

    def FilterSlopes(self):
        layout = QVBoxLayout()
        final_layout = QVBoxLayout()
        header = QVBoxLayout()
        header.addStretch(0)
        
        b1 = QRadioButton ("6 dB")
        b2 = QRadioButton ("12 dB")
        b3 = QRadioButton ("18 dB")
        b4 = QRadioButton ("24 dB")
        
        b1.clicked.connect(lambda: self.setFilterSlope(0))
        b2.clicked.connect(lambda: self.setFilterSlope(1))
        b3.clicked.connect(lambda: self.setFilterSlope(2))
        b4.clicked.connect(lambda: self.setFilterSlope(3))
        
        
        layout.addWidget(b1)
        layout.addWidget(b2)
        layout.addWidget(b3)
        layout.addWidget(b4)
        
        w = QWidget()
        w.setLayout(layout)
        header.addWidget(QLabel("Filter Slopes"))
        header.addWidget(w)
        
        w_final = QWidget()
        w_final.setLayout(header)
        return w_final
    
    def setFilterSlope(self, option):
        self.lockin.filter_slope = self.lockin.FILTER_SLOPES[option]

        
        

    
    def Sensitivity(self):
        layout = QHBoxLayout()
        self.cb = QComboBox()
        
        SENSITIVITIES = [
        2e-9, 5e-9, 10e-9, 20e-9, 50e-9, 100e-9, 200e-9,
        500e-9, 1e-6, 2e-6, 5e-6, 10e-6, 20e-6, 50e-6, 100e-6,
        200e-6, 500e-6, 1e-3, 2e-3, 5e-3, 10e-3, 20e-3,
        50e-3, 100e-3, 200e-3, 500e-3, 1
        ]
        sens = [str(i) for i in SENSITIVITIES]
        self.cb.addItems(sens)
        self.cb.currentIndexChanged.connect(self.setSensitivity)

        self.sensitivity = QLabel("Sensitivity")
        #self.sensitivity.setStyleSheet("border: 2px solid black;")
        layout.addWidget(self.sensitivity)
        layout.addWidget(self.cb)
         
        widget  = QWidget()
        widget.setLayout(layout)
        return widget
    
    def setSensitivity(self):
        print(self.cb.currentText())
        #set the sensitivty of the lockin amplifier to the given value
        self.lockin.sensitivity = float(self.cb.currentText())
        

    def inputNotchConfig(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.addStretch(0)
        
        b1 = QRadioButton ("None")
        b2 = QRadioButton ("Line")
        b3 = QRadioButton ("2 x Line")
        b4 = QRadioButton ("Both")
        
        layout.addWidget(QLabel("Input Notch Configurations"))
        layout.addWidget(b1)
        layout.addWidget(b2)
        layout.addWidget(b3)
        layout.addWidget(b4)
        b1.clicked.connect(lambda: self.setInputNotchConfig(1))
        b2.clicked.connect(lambda: self.setInputNotchConfig(2))
        b3.clicked.connect(lambda: self.setInputNotchConfig(3))
        b4.clicked.connect(lambda: self.setInputNotchConfig(4))
        
        #Final Widget brining all together
        widget = QWidget()
        widget.setLayout(layout)
        return widget
    
    def setInputNotchConfig(self, option):
        if(option == 1):
            self.lockin.input_notch_config = self.lockin.INPUT_NOTCH_CONFIGS[0]
        if(option == 2):
            self.lockin.input_notch_config = self.lockin.INPUT_NOTCH_CONFIGS[1]
        if(option == 3):
            self.lockin.input_notch_config = self.lockin.INPUT_NOTCH_CONFIGS[2]
        if(option == 4):
            self.lockin.input_notch_config = self.lockin.INPUT_NOTCH_CONFIGS[3]

    def TimeConstant2(self):
        layout = QHBoxLayout()
        self.cb = QComboBox()

        SENSITIVITIES = [
            2e-9, 5e-9, 10e-9, 20e-9, 50e-9, 100e-9, 200e-9,
            500e-9, 1e-6, 2e-6, 5e-6, 10e-6, 20e-6, 50e-6, 100e-6,
            200e-6, 500e-6, 1e-3, 2e-3, 5e-3, 10e-3, 20e-3,
            50e-3, 100e-3, 200e-3, 500e-3, 1
        ]
        time_constants= ["10 µs", "30 µs", "100 µs", "300 µs", "1 ms", "3 ms", "10 ms", "30 ms", "100 ms", "300 ms",
                          "1 s", "3 s", "10 s", "30 s"]
        self.cb.addItems(time_constants)
        self.cb.currentIndexChanged.connect(self.setTime)

        layout.addWidget(QLabel("Time Constant"))
        layout.addWidget(self.cb)

        widget = QWidget()
        widget.setLayout(layout)
        return widget
    def setTime(self):
        print("Hello")

    def TimeConstants1(self):
        layout = QVBoxLayout()
        self.cb = QComboBox()
        TIME_CONSTANTS1 = [
            10e-6, 30e-6, 100e-6, 300e-6, 1e-3, 3e-3, 10e-3,
            30e-3, 100e-3, 300e-3, 1, 3, 10, 30, 100, 300, 1e3,
            3e3, 10e3, 30e3
        ]
        TIME_CONSTANTS = ["10 µs", "30 µs", "100 µs", "300 µs", "1 ms", "3 ms", "10 ms", "30 ms", "100 ms", "300 ms", "1 s", "3 s", "10 s", "30 s"]
        sens = [re.findall('[0-9]+', str(i)) for i in TIME_CONSTANTS]
        print(sens)
        #sens = [str(i) for i in SENSITIVITIES]
        self.cb.addItems(sens)
        self.cb.currentIndexChanged.connect(self.setSensitivity)
		
        layout.addWidget(QLabel("Sensitivity"))
        layout.setSpacing(0)
        layout.addWidget(self.cb)
         
        widget  = QWidget()
        widget.setLayout(layout)
        return widget
    
    def TimeConstants(self):
        layout = QHBoxLayout()
        
        TIME_CONSTANTS = [
        2e-9, 5e-9, 10e-9, 20e-9, 50e-9, 100e-9, 200e-9,
        500e-9, 1e-6, 2e-6, 5e-6, 10e-6, 20e-6, 50e-6, 100e-6,
        200e-6, 500e-6, 1e-3, 2e-3, 5e-3, 10e-3, 20e-3,
        50e-3, 100e-3, 200e-3, 500e-3, 1
        ]
        
        
        b1 = QRadioButton ("3")
        b2 = QRadioButton ("1")
        b3 = QRadioButton ("x100")
        b4 = QRadioButton ("x10")
        b5 = QRadioButton ("x1")
        b6 = QRadioButton ("ks")
        b7 = QRadioButton ("s")
        b8 = QRadioButton ("m")
        b9 = QRadioButton ("µm")
        
        controlsGroup = QVBoxLayout()
        controlsGroup.setSpacing(10)
        controlsGroup.addStretch(0)
        controlsGroup.addWidget(b1)
        controlsGroup.addWidget(b2)
        
        
        controlsGroup2 = QVBoxLayout()
        controlsGroup2.setSpacing(10)
        controlsGroup2.addStretch(0)
        
        controlsGroup2.addWidget(b3)
        controlsGroup2.addWidget(b4)
        controlsGroup2.addWidget(b5)
        
        controlsGroup3 = QVBoxLayout()
        controlsGroup3.setSpacing(10)
        controlsGroup3.addStretch(0)
        
        controlsGroup3.addWidget(b6)
        controlsGroup3.addWidget(b7)
        controlsGroup3.addWidget(b8)
        controlsGroup3.addWidget(b9)
        
        
        b1.clicked.connect(lambda: self.setTimeConstantMag(1))
        b2.clicked.connect(lambda: self.setTimeConstantMag(2))
        b3.clicked.connect(lambda: self.setTimeConstantMag2(1))
        b4.clicked.connect(lambda: self.setTimeConstantMag2(2))
        b5.clicked.connect(lambda: self.setTimeConstantMag2(3))
        b6.clicked.connect(lambda: self.setTimeConstantUnit(1))
        b7.clicked.connect(lambda: self.setTimeConstantUnit(2))
        b8.clicked.connect(lambda: self.setTimeConstantUnit(3))
        b9.clicked.connect(lambda: self.setTimeConstantUnit(4))

        w = QWidget()
        w2 = QWidget()
        w3 = QWidget()
    
        w.setLayout(controlsGroup)
        w2.setLayout(controlsGroup2)
        w3.setLayout(controlsGroup3)
        layout.addWidget(w)
        layout.addWidget(w2)
        layout.addWidget(w3)
    
    
        #Final Widget brining all together
        widget = QWidget()
        widget.setLayout(layout)
        return widget
    
    def setTimeConstantMag(self, option):
        if(option == 1):
            self.mag = 1
        if(option == 2):
            self.mag = 2
    def setTimeConstantMag2(self, option):
        if(option == 1):
            self.mag2 = 1
        if(option == 2):
            self.mag2 = 2
    def setTimeConstantUnit(self, option):
        if(option == 1):
            self.unit = 1
        if(option == 2):
            self.unit = 2
        if(option == 3):
            self.unit = 3
        if(option == 4):
            self.unit = 4



            
    

    

