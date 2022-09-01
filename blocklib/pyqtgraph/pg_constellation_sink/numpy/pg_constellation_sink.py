from regex import P
from gnuradio import pyqtgraph as grpg
from gnuradio import gr
import numpy as np
import pyqtgraph as pg

class pg_constellation_sink:
    def __init__(self, blk, **kwargs):

        self._blk = blk
        self.colors = ['blue','red','green','magenta','cyan','yellow','white','gray','darkCyan','darkMagenta','darkYellow','darkGray']
        
        title = kwargs['title']
        nplot = kwargs['size']
        self.nports = kwargs.get('nports', 1)

        self._widget = pg.PlotWidget(title=title, background='w')
        self._plt = self._widget.getPlotItem()
        self._plt.setLabel(axis='bottom', text='In-Phase')
        self._plt.setLabel(axis='left', text='Quadrature')

        self._nplot = nplot 
        self._nbuffers =  self.nports
        self._buffers = []
        self._curves = []

        idx = 0
        
        for p in range(self.nports):

            self._buffers.append(np.zeros((nplot,)))
            c = self._widget.plot(np.real(self._buffers[p]), np.imag(self._buffers[p]), symbol='o', pen=None, symbolPen=None, symbolSize=10, symbolBrush=self.colors[p])
            self._curves.append(c)
            idx += 1
                
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50) 

    def update(self):       
        for p in range(self.nports):
            self._curves[p].setData(x=np.real(self._buffers[p]), y=np.imag(self._buffers[p]), )

    def widget(self):
        return self._widget

    def work(self, wio):
        for p, input in enumerate(wio.inputs()):

            # because this is a sync block, each input should have the same n_items
            nin = input.n_items
            nr = input.nitems_read()

            # The absolute offsets at the beginning and end of the buffer
            #  Pruning can be done in the update function
            self._n_buf_end = nr+nin
            self._n_buf_start = nr-(len(self._buffers[p])-nin)

            inbuf = gr.get_input_array(self._blk, wio, p)
            if (len(self._buffers[p]) > nin):
                self._buffers[p] = np.hstack((self._buffers[p][nin:], inbuf))
            else:
                n = nin - len(self._buffers[p])
                self._buffers[p] = inbuf[n:nin]

            input.consume(nin)
        
        return gr.work_return_t.OK
