# -*- coding:utf-8 -*-
# Author: zhang yongquan
# Email: zhyongquan@gmail.com
# GitHub: https://github.com/zhyongquan

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import re
from datetime import datetime

class function:
    name = ""
    description = ""
    line_start = 0
    line_end = 0

    def __init__(self, name):
        self.name = name

    def tojason(self):
        return ""

    def show(self):
        return

    def __str__(self):
        str = "name={0}, description={1}".format(self.name, self.description) \
              + "\nline_start={0}, line_end={1}".format(self.line_start, self.line_end)
        return str


class calobject(function):
    type = ""
    unit = ""
    value = []

    def __init__(self, name):
        super().__init__(name)
        self.value = []  # clear value for new instance

    def getlabel(self, axis, name, unit):
        if len(name) > 0 and len(unit) > 0:
            return "{0}({1})".format(name, unit)
        elif len(name) > 0:
            return name
        elif len(unit) > 0:
            return "{0}({1})".format(axis, unit)
        else:
            return axis

    def __str__(self):
        str = super().__str__() \
              + "\ntype={0}, unit={1}".format(self.type, self.unit) \
              + "\nvalue=\n" + self.value.__str__()
        return str


class axis(calobject):

    def show(self):
        x = range(0, len(self.value) - 1, 1)
        plt.plot(x, self.value, marker='o')
        plt.title(name)
        plt.xlabel(self.getlabel("x", "", ""))
        plt.ylabel(self.getlabel("y", self.name, self.unit))
        # for i in range(0, len(self.value) - 1):
        #     plt.text(i, self.value[i], "{0},{1}".format(i, self.value[i]))
        plt.show()


class calibration(calobject):
    x = axis("")
    y = axis("")

    def __init__(self, name):
        super().__init__(name)
        self.x = axis("")
        self.y = axis("")
        self.keyword = ""
        self.distirb = []

    def show(self):
        if self.type == "CURVE" or self.type == "MAP" or self.type == "VAL_BLK":
            if self.type == "CURVE":
                plt.plot(self.x.value, self.value, marker='o')
                plt.title(self.name)
                plt.xlabel(self.getlabel("x", self.x.name, self.x.unit))
                plt.ylabel(self.getlabel("y", self.name, self.unit))
                # for i in range(0, len(self.value)):
                #     plt.text(self.x.value[i], self.value[i], "{0},{1}".format(self.x.value[i], self.value[i]))
                plt.show()
            elif self.type == "MAP":
                X, Y = np.meshgrid(self.y.value, self.x.value)  # exchange for plot
                nx = len(self.x.value)
                ny = len(self.y.value)
                Z = np.zeros((nx, ny))
                for i in range(0, nx):
                    for j in range(0, ny):
                        Z[i, j] = self.value[j][i]
                fig = plt.figure()
                ax = Axes3D(fig)
                p = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap='rainbow')
                fig.colorbar(p)
                ax.set_title(self.name)
                ax.set_ylabel(self.getlabel("x", self.x.name, self.x.unit))  # exchange for plot
                ax.set_xlabel(self.getlabel("y", self.y.name, self.y.unit))  # exchange for plot
                ax.set_zlabel(self.getlabel("z", self.name, self.unit))
                plt.show()
            elif self.type == "VAL_BLK":
                if not isDigit(self.value[0]):
                    return
                x = range(0, len(self.value) - 1, 1)
                plt.title(self.name)
                plt.plot(x, self.value, marker='o')
                plt.xlabel(self.getlabel("x", "", ""))
                plt.ylabel(self.getlabel("y", self.name, self.unit))
                # for i in range(0, len(self.value)):
                #     plt.text(i, self.value[i], "{0},{1}".format(i, self.value[i]))
                plt.show()

    def __str__(self):
        str = super().__str__()
        if len(self.x.value) > 0:
            str = str + "\naxis x\n" + self.x.__str__()
        if len(self.y.value) > 0:
            str = str + "\naxis y\n" + self.y.__str__()
        return str


class dcminfo:
    file_content = "KONSERVIERUNG_FORMAT 2.0"
    comment_indicator = '*'
    string_delimiter = '"'
    functions = {}
    calibrations = {}
    axises = {}
    calobjects = {"functions": functions, "calibrations": calibrations, "axises": axises}
    line_count = 0
    regex = r"(\"[^\"\\\\]*(?:\\\\.[^\"\\\\]*)*\")|(?:[^\\ \t]+)"
    keywords = {"FESTWERT"  : "VALUE", 
                "KENNLINIE" : "CURVE", 
                "KENNFELD"  : "MAP",
                "GRUPPENKENNFELD"   : "MAP",
                "GRUPPENKENNLINIE"  : "CURVE",
                "STUETZSTELLENVERTEILUNG" : "VAL_BLK",
                "TEXTSTRING" : "TEXT",
                }

    def __init__(self,dcmfile=None):
        self.functions = {}
        self.calibrations = {}
        self.axises = {}
        self.calobjects = {"function": self.functions, "calibration": self.calibrations, "axis": self.axises}
        if dcmfile is not None:
            self.read(dcmfile)
        return

    def addfunction(self, fun):
        # if not fun.name in self.functions.keys():
        self.functions[fun.name] = fun

    def addcalibration(self, calname):
        # if not cal.name in self.calibrations.keys():
        if calname not in self.calibrations.keys():
            self.calibrations[calname] = calibration(calname)
            return self.calibrations[calname]
        else:
            return None

    def addaxis(self, ax):
        # if not ax.name in self.axises.keys():
        self.axises[ax.name] = ax
        # for cal in self.calibrations:
        #     if cal.x.name == ax.name:
        #         cal.x = ax
        #     if cal.y.name == ax.name:
        #         cal.y = ax

    def getcalobject(self, name):
        type = 'calibration'
        if type in self.calobjects.keys() and name in self.calobjects[type].keys():
            return self.calobjects[type][name]
        else:
            return None

    def split(self, line):
        matches = re.finditer(self.regex, line, re.MULTILINE)
        txt = {}
        for matchNum, match in enumerate(matches, start=1):
            txt[matchNum] = match.group().strip('"')
        return txt

    def read(self, dcmfile):
        self.functions.clear()
        self.calibrations.clear()
        self.axises.clear()
        line_count = 0
        with open(dcmfile, 'r') as file:
            # first line: Description Header
            line = file.readline()
            line_count = 1
            cal = calibration("")
            y_value = []
            while True:
                line = file.readline()
                line_count = line_count + 1
                if not line:
                    break
                line = line.strip()
                if len(line) == 0 or (line.startswith(self.comment_indicator) and not line.startswith("*SST")):
                    continue
                else:
                    txt = self.split(line)
                    if txt[1] == "FKT":
                        # function
                        fun = function(txt[2])
                        fun.description = txt[4]
                        fun.line_start = line_count
                        fun.line_end = line_count
                        self.addfunction(fun)
                    elif txt[1] in self.keywords.keys():
                        # calibration block
                        cal = calibration(txt[2])
                        cal.keyword = txt[1]
                        cal.type = self.keywords[txt[1]]
                        cal.line_start = line_count
                    elif txt[1].startswith("*SST"):
                        cal.ditrib.append(line)
                    elif txt[1] == "LANGNAME":
                        cal.description = txt[2]
                    elif txt[1] == "FUNKTION":
                        cal.fun = txt[2]
                    elif txt[1] == "EINHEIT_X":
                        cal.x.unit = txt[2]
                    elif txt[1] == "EINHEIT_Y":
                        cal.y.unit = txt[2]
                    elif txt[1] == "EINHEIT_W":
                        cal.unit = txt[2]
                    elif txt[1] == "ST/X":
                        for i in range(2, len(txt) + 1):
                            cal.x.value.append(float(txt[i]))
                    elif txt[1] == "ST/Y":
                        cal.y.value.append(float(txt[2]))
                        if len(y_value) > 0:
                            cal.value.append(y_value)
                            y_value = []
                    elif txt[1] == "TEXT" and cal.type == "STRING":
                        cali.value.append(txt[2])
                    elif txt[1] == "WERT":
                        if cal.type == "VALUE":
                            cal.value.append(float(txt[2]))
                        elif cal.type == "CURVE":
                            for i in range(2, len(txt) + 1):
                                cal.value.append(float(txt[i]))
                        elif cal.type == "MAP":
                            for i in range(2, len(txt) + 1):
                                y_value.append(float(txt[i]))
                    elif txt[1] == "END":
                        if len(y_value) > 0:
                            cal.value.append(y_value)
                            y_value = []
                        cal.line_end = line_count
                        self.calibrations[cal.name] = cal

            print("find functions:{0}, calibrations:{1}, axises:{2}".format(len(self.functions), len(self.calibrations),
                                                                            len(self.axises)))
            self.line_count = line_count

    def getDCMDefStr(self, calobj):
        valuelines = []
        splitlength = 6
        if calobj.type == "VALUE":
            assert(len(calobj.value) == 1)
            valuelines.append(f'   WERT {calobj.value[0]}')
        elif calobj.type == "CURVE":
            if calobj.x.value:
                valuelines += splitGroup('   ST/X', calobj.x.value, splitlength)
            if calobj.y.value:
                valuelines += splitGroup('   ST/Y', calobj.y.value, splitlength)
            if calobj.value:
                valuelines += splitGroup('   WERT', calobj.value, splitlength)
        elif calobj.type == "MAP":
            assert(len(calobj.value) == len(calobj.y.value))
            assert(len(calobj.value[0]) == len(calobj.x.value))
            valuelines += splitGroup('   ST/X', calobj.x.value, splitlength)
            for y_val, val in zip(calobj.y.value, calobj.value):
                valuelines.append(f'   ST/Y {y_val}')
                valuelines += splitGroup('   WERT', val, splitlength)
        else:
             raise ValueError(f"Type atttibute: {calobj.type} for {calobj.name}")

        deflines = []
        deflines.append(f'{calobj.keyword} {calobj.name} {str(len(calobj.x.value)) if len(calobj.x.value)>0 else ""} {str(len(calobj.y.value)) if len(calobj.y.value)>0 else ""}')
        if calobj.type == "CURVE" and calobj.distirb:
            deflines += calobj.distirb
        deflines.append(f'   LANGNAME "{calobj.description}"')
        if calobj.x.value:
            deflines.append(f'   EINHEIT_X "{calobj.x.unit}"')
        if calobj.y.value:
            deflines.append(f'   EINHEIT_Y "{calobj.y.unit}"')
        if calobj.value:
            deflines.append(f'   EINHEIT_W "{calobj.unit}"')
        if calobj.type == "MAP" and calobj.distirb:
            deflines += calobj.distirb
        deflines += valuelines
        deflines.append('END')

        definestr = '\n'.join(deflines)
        return definestr

    def genDcmFile(self, tgtDCMPath, deflist):
        with open(tgtDCMPath, 'w', encoding='utf-8') as f:
            f.write('* encoding="UTF-8"\n')
            f.write('* DAMOS format')
            f.write(f' generated by pydcm at time {datetime.now()}\n\n')
            f.write('KONSERVIERUNG_FORMAT 2.0\n\n')
            defstr = '\n\n'.join(deflist)
            f.write(defstr)
            f.close()
        print(f'DCM generated: {tgtDCMPath}')


def splitGroup(prefix, list, length):
    lines = []
    for i in range(0, len(list), length):
        group = list[i:i+length]
        line = prefix + ' ' + ' '.join(map(str, group))
        lines.append(line)
    return lines

def isDigit(x):
    try:
        float(x)
        return True
    except ValueError:
        return False
