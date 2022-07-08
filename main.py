# This is a sample Python script.

"""
Created on Tue Jun  7 14:13:05 2022

@author: mazzotti
"""

# Simple Procedure
import pymeasure
from pymeasure.instruments.srs import SR830
import pymeasure.display.inputs
import numpy as np
import pandas as pd
from time import sleep
from pymeasure.experiment import Procedure
from pymeasure.experiment import IntegerParameter, FloatParameter, Parameter
from pymeasure.experiment import Results
from pymeasure.experiment import Worker
from pymeasure.log import console_log

from pymeasure.display.Qt import QtGui
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import IntegerParameter, FloatParameter, Parameter, ListParameter, BooleanParameter
import sys
from time import sleep
import tempfile
import logging
from PyQt5.QtWidgets import QMessageBox
import PyQt5.QtWidgets
from PyQt5 import QtWidgets
from pymeasure.experiment.results import CSVFormatter
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QRunnable, QThreadPool
from PyQt5.QtCore import pyqtSlot
from pymeasure.instruments.newport.esp300 import ESP300
import sys
from csv import DictWriter
import os.path
from pathlib import Path

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class RandomProcedure(Procedure):
    # initialize all the class attributes
    controller = ESP300("GPIB::1")

    # parameters of the procedure
    iterations = IntegerParameter('Loop Iterations', default=5)
    delay = FloatParameter('Delay Time', units='s', default=0.2)
    start = IntegerParameter("start", units="m", default=0)
    steps = IntegerParameter("steps", default=5)
    increment = FloatParameter("increment", default=1)

    filename = Parameter("filename", default="default")
    saving = BooleanParameter("saving", default=True)
    path = Parameter("path", default=r"C:\Users\mazzotti\Desktop\MPI Stuttgart Internship Doc\Python\LabView")
    axis = ListParameter("axis", [1, 2, 3])

    end = start.value + increment.value * steps.value

    DATA_COLUMNS = ["Voltage", "Stage_Position", "Range", "Average"]

    def execute(self):
        # we need to monitor that the position of tha stage matches exactly the range we have set and we do it without any worker so on the MainThread
        # default will be stage 1
        # first set the correct stage/axis
        # start a separate thread here
        # create a QThread which is a handler and start the worker hat is handled by it
        self.data_filename = self.path + "\\" + self.filename + ".csv"
        if (self.axis == 1):
            self.stage = self.controller.x
        elif (self.axis == 2):
            self.stage = self.controller.y
        elif (self.axis == 3):
            self.stage = self.controller.phi

        self.end = self.start + self.increment * self.steps
        self.range_x = np.linspace(self.start, self.end, self.steps + 1)

        self.data_points = self.steps + 1
        self.averages = 50
        self.max_current = self.end
        self.min_current = self.start

        if (self.current_iter == 0):
            # we move the stage on the same thread as the lockin amplifier (trial)
            with open(self.data_filename, 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                dictwriter_object = DictWriter(csvfile, fieldnames=self.DATA_COLUMNS)
                dictwriter_object.writeheader()
                for point in self.range_x:
                    self.stage.define_position(point)
                    self.lockin.reset_buffer()
                    sleep(0.1)
                    self.lockin.start_buffer()
                    data_measurement = {
                        'Voltage': self.lockin.x, "Stage_Position": self.stage.position, "Range": point, "Average": 0
                    }
                    self.emit('results', data_measurement)

                    sleep(0.01)

                    # Pass the dictionary as an argument to the Writerow()
                    dictwriter_object.writerow(data_measurement)

                    if self.should_stop():
                        log.info("User aborted the procedure")
                        # TODO: REMEMBER TO SAVE THE DATA TO FILE
                        break
        else:
            df = pd.read_csv(self.data_filename)
            row = 0
            for point in self.range_x:
                self.stage.define_position(point)
                self.lockin.reset_buffer()
                sleep(0.1)
                self.lockin.start_buffer()
                print(df.at[row, "Voltage"])
                data_measurement = {
                    'Voltage': self.lockin.x, "Stage_Position": self.stage.position, "Range": point,
                    "Average": df.at[row, "Voltage"]
                }
                self.emit('results', data_measurement)

                sleep(0.01)

                # Pass the dictionary as an argument to the Writerow()
                sum_voltage = (self.current_iter * df.at[row, "Average"] + data_measurement.get("Voltage")) / (
                            self.current_iter + 1)

                df.at[row, "Average"] = sum_voltage
                df.to_csv(self.data_filename, index=False)
                row = row + 1

                if self.should_stop():
                    log.info("User aborted the procedure")
                    # TODO: REMEMBER TO SAVE THE DATA TO FILE
                    break

    def shutdown(self):
        log.info("Finished measuring Random Procedure")

    def get_start(self):
        return self.start

    def get_end(self):
        return self.end


import csv
import pandas as pd


class MainWindow(ManagedWindow):

    def __init__(self):
        # Connect and configure the instrument
        log.info("Connecting and configuring the instrument")

        super().__init__(
            procedure_class=RandomProcedure,
            inputs=['iterations', 'delay', "start", "steps", "increment", "filename", "path", "axis"],
            inputComand=["start", "steps", "increment", "filename", "path"],
            inputStages=["1", "2"],
            displays=['iterations', 'delay', "start", "steps", "increment", "filename", "path", "axis"],
            x_axis="Range",
            y_axis='Voltage'
        )

        self.setWindowTitle('Lock-in Amplifier')

    def queue(self):
        # filename = tempfile.mkdtemp()
        # this is the deprecated version (not secure) and should actually be replaced with the one above

        procedure1 = self.make_procedure()
        iterations = procedure1.get_parameter("iterations")

        range_x = np.arange(procedure1.get_parameter("start"), procedure1.get_parameter("end"),
                            procedure1.get_parameter("steps")).tolist()

        avg_voltage = np.zeros(len(range_x))

        average = dict(zip(range_x, avg_voltage))
        previous_experiment = None
        for curr in range(iterations):
            filename = tempfile.mktemp()
            procedure = self.make_procedure()
            procedure.set_current_iteration(curr)

            if (procedure.saving):
                path = procedure.get_parameter("path")
                filename_loc = procedure.get_parameter("filename")
                self.data_filename = path + "/" + filename_loc + ".csv"
                results = Results(procedure, (filename))
            # results = Results(procedure,(filename, self.data_filename))

            else:
                results = Results(procedure, filename)

            experiment = self.new_experiment(results, curr)

            self.manager.queue(experiment)

    def get_start(self):
        return self.start


if __name__ == "__main__":
    app = PyQt5.QtWidgets.QApplication(sys.argv)
    app.setStyleSheet("QLabel{font-size: 11pt;}")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


