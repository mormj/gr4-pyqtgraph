import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.console
import numpy as np

from pyqtgraph.dockarea import *

from gnuradio import gr, analog, bench, streamops
import pmtf

from gnuradio.pyqtgraph.numpy import *

class pg_plot_widget_f(gr.sync_block):
    def __init__(self, nplot, title=''):
        gr.sync_block.__init__(
            self,
            name='pg_plot_widget')

        self.add_port(gr.port_f('in', gr.INPUT))
        self._widget = pg.PlotWidget(title=title)

        self._nplot = nplot
        self._buffer = np.zeros((nplot,))
        self._curve = self._widget.plot(self._buffer)
        self._curve.setPen('gray')

        self._tag_buffer = []
        self._tag_points = []
        self._tag_text = []
        self._tag_arrows = []

        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)

    def update(self):
        # self._widget.plot(self._buffer, clear=True)
        self._curve.setData(y=self._buffer)

        # Plot in the appropriate tags for the current plot window
        idx = 0
        to_remove = []
        for tag in self._tag_buffer:
            if tag.offset() >= self._n_buf_start and tag.offset() < self._n_buf_end:
                if (idx >= len(self._tag_points)):
                    self._tag_points.append(pg.CurvePoint(self._curve))
                    self._widget.addItem(self._tag_points[idx])
                    self._tag_text.append(pg.TextItem("test", anchor=(0.5, -0.2)))
                    self._tag_text[idx].setParentItem(self._tag_points[idx])
                    self._tag_arrows.append(pg.ArrowItem(angle=90))
                    self._tag_arrows[idx].setParentItem(self._tag_points[idx])

                self._tag_points[idx].setPos(float(tag.offset()-self._n_buf_start)/(len(self._buffer)-1))
                # self._tag_text[idx].setText(f'{self._buffer[tag.offset()-self._n_buf_start]:0.1f}')
                self._tag_text[idx].setText(str(tag))

                idx+=1
            else:
                to_remove.append(tag)

            for ii in range(idx,len(self._tag_points)):
                self._widget.removeItem(self._tag_points[ii])

            self._tag_points = self._tag_points[:idx]
            self._tag_text = self._tag_text[:idx]
            self._tag_arrows = self._tag_arrows[:idx]

        for remove_tag in to_remove:
            self._tag_buffer.remove(remove_tag)

    def widget(self):
        return self._widget

    def work(self, inputs, outputs):
        # print('work')
        nin = inputs[0].n_items

        nr = inputs[0].nitems_read()
        tags = inputs[0].tags_in_window(0,nin)
        # each tag should be associated with an index in the buffer
        self._tag_buffer += tags

        # The absolute offsets at the beginning and end of the buffer
        #  Pruning can be done in the update function
        self._n_buf_end = nr+nin
        self._n_buf_start = nr-(len(self._buffer)-nin)

        inbuf = self.get_input_array(inputs, 0)
        if (len(self._buffer) > nin):
            self._buffer = np.hstack((self._buffer[nin:], inbuf))
        else:
            n = nin - len(self._buffer)
            self._buffer = inbuf[n:nin]

        inputs[0].consume(nin)
        
        return gr.work_return_t.WORK_OK


app = pg.mkQApp('DockArea Example')
win = QtGui.QMainWindow()
area = DockArea()
win.setCentralWidget(area)
win.resize(1000,500)
win.setWindowTitle('pyqtgraph example: dockarea')

samp_rate = 32000
interval = 0.1

fg = gr.flowgraph()
src = analog.sig_source_f(samp_rate, analog.waveform_type.cos, 12, 1.0)
src2 = analog.sig_source_f(samp_rate, analog.waveform_type.cos, 15, 1.0)
throttle = streamops.throttle(samp_rate)
inj = bench.time_tag_injector(gr.sizeof_float, interval, samp_rate)
# snk = pg_plot_widget_f(100000, 'hello world')
snk = pg_time_sink_f('hello world', 100000, 2)
# snk2 = pg_time_sink_f('hello world 2', 100000)
fg.connect((src,throttle, inj, snk))
fg.connect(src2,0, snk,1)

d1 = Dock('a')
d2 = Dock('b')
d3 = Dock('c')
area.addDock(d1,'top')
# area.addDock(d2,'top',d1)
# area.addDock(d3,'top')
d1.addWidget(snk.widget())
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