import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.console
import numpy as np

from pyqtgraph.dockarea import *

from gnuradio import gr, analog, bench, streamops
import pmtf

from gnuradio.pyqtgraph.numpy import *

app = pg.mkQApp('DockArea Example')
pg.setConfigOptions(antialias=True)
win = QtGui.QMainWindow()
area = DockArea()
win.setCentralWidget(area)
win.resize(3000,2000)
win.setWindowTitle('pyqtgraph example: dockarea')

samp_rate = 32000
interval = 0.1

fg = gr.flowgraph()
src = analog.sig_source_f(samp_rate, analog.waveform_t.cos, 12, 1.0)
src2 = analog.sig_source_f(samp_rate, analog.waveform_t.cos, 15, 1.0)
throttle = streamops.throttle(samp_rate)
inj = bench.time_tag_injector(gr.sizeof_float, interval, samp_rate)
# snk = pg_plot_widget_f(100000, 'hello world')
snk = pg_time_sink_f('hello world', 100000, nports=2)

src3 = analog.sig_source_c(samp_rate, analog.waveform_t.triangle, 12, 1.0)
throttle2 = streamops.throttle(samp_rate)
snk2 = pg_time_sink_c('hello world 2', 100000)
fg.connect((src,throttle, inj, snk))
fg.connect(src2,0, snk,1)
fg.connect((src3,throttle2, snk2))

d1 = Dock('a')
d2 = Dock('b')
# d3 = Dock('c')
area.addDock(d1,'top')
area.addDock(d2,'top',d1)
# area.addDock(d3,'top')
d1.addWidget(snk.widget())
d2.addWidget(snk2.widget())
# d2.addWidget(snk2.widget())




## first dock gets save/restore buttons
# w1 = pg.LayoutWidget()
# label = QtGui.QLabel(""" -- DockArea Example -- 
# This window has 6 Dock widgets in it. Each dock can be dragged
# by its title bar to occupy a different space within the window 
# but note that one dock has its title bar hidden). Additionally,
# the borders between docks may be dragged to resize. Docks that are dragged on top
# of one another are stacked in a tabbed layout. Double-click a dock title
# bar to place it in its own window.
# """)
# saveBtn = QtGui.QPushButton('Save dock state')
# restoreBtn = QtGui.QPushButton('Restore dock state')
# restoreBtn.setEnabled(False)
# w1.addWidget(label, row=0, col=0)
# w1.addWidget(saveBtn, row=1, col=0)
# w1.addWidget(restoreBtn, row=2, col=0)
# d2.addWidget(w1)
# state = None
# def save():
#     global state
#     state = area.saveState()
#     restoreBtn.setEnabled(True)
# def load():
#     global state
#     area.restoreState(state)
# saveBtn.clicked.connect(save)
# restoreBtn.clicked.connect(load)

fg.start()

win.show()

# fg.wait()

if __name__ == '__main__':
    pg.exec()