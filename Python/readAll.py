import glob
import sys
import os
import re
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

patternBench = '.+(ON|OFF).+'
patternSyscall = '.+`(\S+)`.+(\d+\.\d+e[+-]\d+)'

syscalls = []
on = {}
off = {}

def readFile(fileName):
    try:
        lines = open(fileName, 'r').readlines()
        if len(lines) == 0:
            raise IOError()
    except IOError:
        print('Error: no such file ' + fileName + ' or empty')
        exit()
    state = None
    for line in lines:
        matchBench = re.match(patternBench, line, flags=0)
        # Ha matchato l'inizio del benchmark
        if matchBench:
            state = matchBench.group(1)
        else:
            matchSyscall = re.match(patternSyscall, line, flags=0)
            # Ha matchato una syscall
            if matchSyscall:
            	name = matchSyscall.group(1)
            	(syscalls.append(name) if name not in syscalls else None)
            	name = name[:-2]
            	if name not in on and name not in off:
            		on[name] = [];
            		off[name] = [];
                on[name].append(float(matchSyscall.group(2))) if state == 'ON' else off[name].append(float(matchSyscall.group(2)))

'''          
def prepareLin(valon, valoff, cols, title, labelx):
	fig, ax = plt.subplots()
	ax.plot(labelx, valon, 'ro');
	ax.plot(labelx, valoff, 'bo');
	ax.set_title(title)
	ax.legend(cols)
	fig.tight_layout()
'''

def multipage(filename, figs=None, dpi=200):
    pp = PdfPages(filename)
    print(plt.get_fignums())
    if figs is None:
        figs = [plt.figure(n) for n in plt.get_fignums()]
    for fig in figs:
        fig.savefig(pp, format='pdf')
    pp.close()

def prepareAll():
    length = [y for y in range(1, 1+len(on['setuid']))]
    for sysc, key in zip(syscalls, on):
    	xticks = np.linspace(0, len(length), 11)
    	fig, ax = plt.subplots()
    	ax.plot(length, on[key], 'ro')
    	ax.plot(length, off[key], 'bo')
    	ax.set_xticks(xticks)
    	ax.get_yaxis().set_major_formatter(matplotlib.ticker.StrMethodFormatter("{x:1.2e}"))
    	ax.set_ylim(bottom=0)
        ax.set_xlim(left=0)
    	ax.set_ylabel('Tempo (secondi)')
    	ax.set_xlabel('N. del test')
    	ax.set_title(sysc)
    	ax.legend(['LKRG attivo', 'LKRG disattivo'])
    	fig.tight_layout();

def prepareData():
    output = open("data.txt", "w")
    for key, sysc in zip(on, syscalls):
        mediaon = np.mean(on[key])
        stdon = np.std(on[key])
        mediaoff = np.mean(off[key])
        stdoff = np.std(off[key])
        output.write('\\hline\n{} & {:.3e} & {:.3e} & {:.3e} & {:.3e} \\\\\n'.format(sysc, mediaon, mediaoff, stdon, stdoff))
    output.write('\\hline\n')
    output.close()



for filename in glob.glob(os.path.join(sys.argv[1], '*.txt')):
	readFile(filename);
'''
for keyon, keyoff in zip(on, off):
	prepareLin(on[keyon], off[keyoff], ['LKRG attivo', 'LKRG disattivo'], str(keyon), [x for x in range(1, 1+ len(on[keyon]))])
'''
prepareAll()
prepareData()
multipage('output.pdf')