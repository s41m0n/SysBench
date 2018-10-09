import sys
import re
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

patternBench = '.+(ON|OFF).+=(\d*).+=(\d*).+'
patternSyscall = '\s`(\S+)`\s+->\s+(\d+.\d+|\/)'

ncycle = None
nproc = None
state = None
missTest = None
syscalls = []
benchOn = []
benchOff = []

if len(sys.argv) == 1 or '.txt' not in sys.argv[1]:
    print('Error: need a filename (.txt)')
    exit()

def readFile(filename):
	try:
    	lines = open(sys.argv[1], 'r').readlines()
    	if len(lines) == 0:
        	raise IOError()
	except IOError:
    	print('Error: no such file' + sys.argv[1] + 'or empty')
    	exit()

	for line in lines:
    	matchBench = re.match(patternBench, line, flags=0)
    	# Ha matchato l'inizio del benchmark
    	if matchBench:
        	if state is not None and state == matchBench.group(1):
            	print('Error: cannot test, module state is not changed')
            	exit()
        	if ncycle is not None and ncycle != matchBench.group(2):
            	print('Error: cannot compair benchmarks with different ncycle')
            	exit()
        	if nproc is not None and nproc != matchBench.group(3):
	            print('Error: cannot compair benchmarks with different nproc')
    	        exit()
        	ncycle = matchBench.group(2)
	        state = matchBench.group(1)
    	    nproc = matchBench.group(3)
    	else:
	        matchSyscall = re.match(patternSyscall, line, flags=0)
    	    # Ha matchato una syscall
        	if matchSyscall:
            	if matchSyscall.group(2) != '/':
                	benchOn.append(float(matchSyscall.group(2))) if state == 'ON' else benchOff.append(float(matchSyscall.group(2)))
                	(syscalls.append(matchSyscall.group(1)) if matchSyscall.group(1) not in syscalls else None)

if len(benchOff) == 0 or len(benchOn) == 0:
    print('Error: not enough benchmarks to compare')
    exit()
if len(benchOn) != len(benchOff):
    print('Error: cannot compare due to missing tests')
    exit()

minorTicks = [1.7e-6, 3e-6, 5.3e-6, 1.7e-5, 3e-5, 5.3e-5, 1.7e-4, 3e-4, 5.3e-4, 1.7e-3, 3e-3, 5.3e-3, 1.7e-2, 3e-2, 5.3e-2, 1.7e-1, 3e-1, 5.3e-1, 1.7e+0, 3e+0, 5.3e+0, 1.7e+1, 3e+1, 5.3e+1, 1.7e+2, 3e+2, 5.3e+2]

def prepareLog(values, cols, title, ticks, syscalls):
    fig, ax = plt.subplots()
    df = pd.DataFrame(values, columns=cols)
    df.plot.bar(ax=ax)
    ax.set_yscale('log', basey=10)
    ax.set_xticklabels(syscalls, rotation=45)
    ax.set_yticks(ticks, minor = True)
    ax.tick_params(axis = 'y', which = 'minor', labelsize = 6)
    ax.get_yaxis().set_major_formatter(matplotlib.ticker.StrMethodFormatter("{x:1.0e}"))
    ax.get_yaxis().set_minor_formatter(matplotlib.ticker.StrMethodFormatter("{x:1.1e}"))
    ax.set_ylabel('Tempo d\'esecuzione (secondi)')
    ax.set_xlabel('System calls')
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()

def prepareLin(values, cols, title, ticks, syscalls):
    fig, ax = plt.subplots()
    df = pd.DataFrame(values, columns=cols)
    df.plot.bar(ax=ax)
    ax.set_xticklabels(syscalls, rotation=45)
    ax.tick_params(axis = 'y', which = 'minor', labelsize = 6)
    ax.set_ylabel('Tempo d\'esecuzione (secondi)')
    ax.set_xlabel('System calls')
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()

#both
prepareLog(np.c_[benchOn, benchOff], ['LKRG attivo', 'LKRG disattivo'], 'SysBench (ncycle=' + ncycle + ', nproc=' + nproc + ')', [x for x in minorTicks if x <= max(benchOn)], syscalls)
'''
#diff
diff = [a - b for a,b in zip(benchOn, benchOff)]
prepareLog(np.c_[diff], ['LKRG attivo - LKRG disattivo'], 'Attivo - Disattivo (ncycle=' + ncycle + ', nproc=' + nproc + ')', [x for x in minorTicks if x <= max(diff) and x >= min(diff)], syscalls)
#setX + open ACTIVE
setX = benchOn[:-4]
prepareLin(np.c_[setX], ['LKRG attivo'], 'SetX and open', [x for x in setX if x <= max(setX) and x >= min(setX)], syscalls[:-4])
#others ACTIVE
others = benchOn[-4:]
prepareLin(np.c_[others], ['LKRG attivo'], 'Fork execve and modules', [x for x in others if x <= max(others) and x >= min(others)], syscalls[-4:])
#setX + open DISACTIVE
setXoff = benchOff[:-4]
prepareLin(np.c_[setXoff], ['LKRG disattivo'], 'SetX and open', [x for x in setXoff if x <= max(setXoff) and x >= min(setXoff)], syscalls[:-4])
#others DISACTIVE
othersoff = benchOff[-4:]
prepareLin(np.c_[othersoff], ['LKRG disattivo'], 'Fork execve and modules', [x for x in othersoff if x <= max(othersoff) and x >= min(othersoff)], syscalls[-4:])
'''

plt.show()