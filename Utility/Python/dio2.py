import sys
import re
import glob
import os
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from scipy.interpolate import interp1d

patternBench = '.+(ON|OFF).+=(\d*).+=(\d*).+'
patternSyscall = '\s`(\S+)`\s+->\s+(\d+.\d+e[+-]\d+)\s+(\d+.\d+e[+-]\d+)'

if len(sys.argv) < 2:
    print('Error: need directory.')
    exit()

syscalls = []

minorTicks = [1.7e-7, 3e-7, 5.3e-7, 1.7e-6, 3e-6, 5.3e-6, 1.7e-5, 3e-5, 5.3e-5, 1.7e-4, 3e-4, 5.3e-4, 1.7e-3, 3e-3, 5.3e-3, 1.7e-2, 3e-2, 5.3e-2, 1.7e-1, 3e-1, 5.3e-1, 1.7e+0, 3e+0, 5.3e+0, 1.7e+1, 3e+1, 5.3e+1, 1.7e+2, 3e+2, 5.3e+2, 1.7e+3, 3e+3, 5.3e+3, 1.7e+4, 3e+4, 5.3e+4, 1.7e+5, 3e+5, 5.3e+5]

def readFile(fileName):
    try:
        lines = open(fileName, 'r').readlines()
        if len(lines) == 0:
            raise IOError()
    except IOError:
        print('Error: no such file ' + fileName + ' or empty')
        exit()
    on_tot = []
    off_tot = []
    on_mean = []
    off_mean = []
    ncycle = None
    nproc = None
    state = None
    for line in lines:
        matchBench = re.match(patternBench, line, flags=0)
        # Ha matchato l'inizio del benchmark
        if matchBench:
            ncycle = int(matchBench.group(2))
            nproc = int(matchBench.group(3))
            state = matchBench.group(1)
        else:
            matchSyscall = re.match(patternSyscall, line, flags=0)
            # Ha matchato una syscall
            if matchSyscall:
                name = matchSyscall.group(1)
                (syscalls.append(name) if name not in syscalls else None)
                on_tot.append(float(matchSyscall.group(2))) if state == 'ON' else off_tot.append(float(matchSyscall.group(2)))
                on_mean.append(float(matchSyscall.group(3))) if state == 'ON' else off_mean.append(float(matchSyscall.group(3)))
    return (on_tot, on_mean, off_tot, off_mean, ncycle, nproc)


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
    ax.set_ylabel('Tempo (secondi)')
    ax.set_xlabel('System calls')
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()

def prepareLin(valueon, valueoff, title, labelx):
    '''
    fig, ax = plt.subplots()
    ax.set_xscale('log')
    ax.plot(labelx, valueon, 'ro');
    ax.plot(labelx, valueoff, 'bo ')
    ax.set_ylim(bottom=0)
    ax.set_title(title)
    ax.set_ylabel('Tempo d\'esecuzione (secondi)')
    ax.set_xlabel('ncycle')
    ax.legend(legend)
    fig.tight_layout()'''
    f, (ax1, ax2) = plt.subplots(2, 1)
    ax1.plot(labelx, valueon, 'ro')
    ax1.tick_params(axis='x',which='minor',bottom=False)
    ax2.plot(labelx, valueoff, 'bo')
    ax1.set_title(title + ' LKRG attivo')
    ax2.set_title(title + ' LKRG disattivo')
    ax1.set_xscale('log')
    ax2.set_xscale('log')
    ax1.set_xlabel('ncycle');
    ax2.set_xlabel('ncycle');
    ax1.set_ylabel('Tempo (secondi)');
    ax2.set_ylabel('Tempo (secondi)');
    ax1.get_yaxis().set_major_formatter(matplotlib.ticker.StrMethodFormatter("{x:1.2e}"))
    ax2.get_yaxis().set_major_formatter(matplotlib.ticker.StrMethodFormatter("{x:1.2e}"))
    ax2.tick_params(axis='x',which='minor',bottom=False)
    f.tight_layout()

def multipage(filename, figs=None, dpi=200):
    pp = PdfPages(filename)
    if figs is None:
        figs = [plt.figure(n) for n in plt.get_fignums()]
    for fig in figs:
        fig.savefig(pp, format='pdf')
    pp.close()

a_on_tot, a_on_mean, a_off_tot, a_off_mean, a_ncycle, a_nproc = readFile(sys.argv[1] + "result1.txt")
b_on_tot, b_on_mean, b_off_tot, b_off_mean, b_ncycle, b_nproc = readFile(sys.argv[1] + "result10.txt")
c_on_tot, c_on_mean, c_off_tot, c_off_mean, c_ncycle, c_nproc = readFile(sys.argv[1] + "result100.txt")
d_on_tot, d_on_mean, d_off_tot, d_off_mean, d_ncycle, d_nproc = readFile(sys.argv[1] + "result1000.txt")
e_on_tot, e_on_mean, e_off_tot, e_off_mean, e_ncycle, e_nproc = readFile(sys.argv[1] + "result10000.txt")

prepareLog(np.c_[a_off_tot, a_on_tot], ['LKRG disattivo', 'LKRG attivo'], 'SysBench (ncycle=' + str(a_ncycle) + ', nproc=' + str(a_nproc) + ')', [x for x in minorTicks if x <= max(a_on_tot) and x >= min(a_off_tot)], syscalls)
prepareLog(np.c_[b_off_tot, b_on_tot], ['LKRG disattivo', 'LKRG attivo'], 'SysBench (ncycle=' + str(b_ncycle) + ', nproc=' + str(b_nproc) + ')', [x for x in minorTicks if x <= max(b_on_tot) and x >= min(b_off_tot)], syscalls)
prepareLog(np.c_[c_off_tot, c_on_tot], ['LKRG disattivo', 'LKRG attivo'], 'SysBench (ncycle=' + str(c_ncycle) + ', nproc=' + str(c_nproc) + ')', [x for x in minorTicks if x <= max(c_on_tot) and x >= min(c_off_tot)], syscalls)
prepareLog(np.c_[d_off_tot, d_on_tot], ['LKRG disattivo', 'LKRG attivo'], 'SysBench (ncycle=' + str(d_ncycle) + ', nproc=' + str(d_nproc) + ')', [x for x in minorTicks if x <= max(d_on_tot) and x >= min(d_off_tot)], syscalls)
prepareLog(np.c_[e_off_tot, e_on_tot], ['LKRG disattivo', 'LKRG attivo'], 'SysBench (ncycle=' + str(e_ncycle) + ', nproc=' + str(e_nproc) + ')', [x for x in minorTicks if x <= max(e_on_tot) and x >= min(e_off_tot)], syscalls)

multipage('totale.pdf')
plt.close('all')
'''
for a, b, c, d, e, sysc in zip(a_off_mean, b_off_mean, c_off_mean, d_off_mean, e_off_mean, syscalls):
    prepareLin([a, b, c, d, e], 'Media singola `' + sysc + '`LKRG disattivo', [a_ncycle, b_ncycle, c_ncycle, d_ncycle, e_ncycle])

multipage('mediaoff.pdf')
plt.close('all')

for a, b, c, d, e, sysc in zip(a_on_mean, b_on_mean, c_on_mean, d_on_mean, e_on_mean, syscalls):
    prepareLin([a, b, c, d, e], 'Media singola `' + sysc + '`LKRG attivo', [a_ncycle, b_ncycle, c_ncycle, d_ncycle, e_ncycle])

multipage('mediaon.pdf')
'''

output = open("data.txt", "w")

for a, a1, b, b1, c, c1, d, d1, e, e1, sysc in zip(a_on_mean, a_off_mean, b_on_mean, b_off_mean, c_on_mean, c_off_mean, d_on_mean, d_off_mean, e_on_mean, e_off_mean, syscalls):
    prepareLin([a, b, c, d, e], [a1, b1, c1, d1, e1], 'Media `' + sysc + '`', [a_ncycle, b_ncycle, c_ncycle, d_ncycle, e_ncycle])
    mediaon = np.mean([a, b, c, d, e])
    stdon = np.std([a, b, c, d, e])
    mediaoff = np.mean([a1, b1, c1, d1, e1])
    stdoff = np.std([a1, b1, c1, d1, e1])
    output.write('\\hline\n{} & {:.3e} & {:.3e} & {:.3e} & {:.3e} \\\\\n'.format(sysc, mediaon, mediaoff, stdon, stdoff))

multipage('media.pdf')
output.write('\\hline\n')
output.close()
