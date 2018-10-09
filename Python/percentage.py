import glob
import sys
import os
import re
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

patternSyscall = '(\S+) & (\d+\.\d+e[+-]\d+) & (\d+\.\d+e[+-]\d+).+'

syscalls = []


def readFile(fileName):
    try:
        lines = open(fileName, 'r').readlines()
        if len(lines) == 0:
            raise IOError()
    except IOError:
        print('Error: no such file ' + fileName + ' or empty')
        exit()
    inc = []
    for line in lines:
        matchSyscall = re.match(patternSyscall, line, flags=0)
        # Ha matchato una syscall
        if matchSyscall:
            (syscalls.append(matchSyscall.group(1)) if matchSyscall.group(1) not in syscalls else None)
            inc.append(float(matchSyscall.group(2)) * 100 / float(matchSyscall.group(3)))
    return inc

def prepareData(data1, data2, data3, filename):
    output = open(filename, "w")
    for val1, val2, val3, sysc in zip(data1, data2, data3, syscalls):
        output.write('\\hline\n{} & {:.0f} & {:.0f} & {:.0f} \\\\\n'.format(sysc, val1, val2, val3))
    output.write('\\hline\n')
    output.write('\\hline\nMedia & {:.0f} & {:.0f} & {:.0f}\\\\\n'.format(med1, med2, med3))
    output.close()

ub = readFile('dataUb.txt')
deb = readFile('dataDeb.txt')
mint = readFile('dataMint.txt')
med1, med2, med3 = np.mean(ub), np.mean(deb), np.mean(mint)

prepareData(ub, deb, mint, 'compare.txt')