from regex import P
from gnuradio import pyqtgraph as grpg
from gnuradio import gr
import numpy as np
import pyqtgraph as pg
from pyqtgraph.graphicsItems.GradientEditorItem import Gradients
from pyqtgraph.graphicsItems.NonUniformImage import NonUniformImage

from gnuradio import gr

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
from pyqtgraph.dockarea import *
from gnuradio.pyqtgraph.numpy import *

class pg_waterfall_sink_base:
    def __init__(self, **kwargs):
        title = kwargs['title']
        self.nplot = kwargs['size']
        self.nfft = kwargs['nfft']

        self.nports = kwargs.get('nports', 1)
        self.iscomplex = kwargs['iscomplex']
        self._widget = pg.GraphicsLayoutWidget()
        # self._plot = self._widget.addPlot(title=title, row=0, col=0)
        if title:
            self._widget.addLabel(title)
            self._widget.nextRow()
        self._vb = self._widget.addViewBox()
        self._lut = pg.HistogramLUTItem(orientation="horizontal") #, levelMode='rgba')
        self._waterfall_img = pg.ImageItem(self.stft(np.zeros((self.nplot,),dtype=np.complex64), self.nfft))
        self._vb.addItem(self._waterfall_img)
        self._x = [0.0, 1.0]
        self._widget.nextRow()
        self._widget.addItem(self._lut)        
        
        self._lut.gradient.loadPreset('flame')
        self._lut.setImageItem(self._waterfall_img)

        self.cnt = 0
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000) 

    def stft(self, a, n_fft, window=np.hanning):  
        n = n_fft
        rpad = n - a.shape[-1] % n
        wins = np.pad(a, (0, rpad)).reshape(-1, n) * window(n)
        fftc = np.fft.fftshift(np.fft.fft(wins, n=n), axes=1) #[..., n // 2 : n]
        fftr = np.real(fftc * np.conj(fftc))
        return fftr

    def update(self):   
        self.cnt += 1   

        self._buffer = np.random.normal(loc=0.5, scale=0.010, size=(self.nplot,))

        # print(self._buffer)
        spec = self.stft(self._buffer, self.nfft)
        
        # print(spec)
        # self._waterfall_img.setLookupTable(self._lut, autolevel=True)
        # self._waterfall_img.scale((self._x[-1] - self._x[0]) / len(self._x), 1)
        self._waterfall_img.setImage(spec.transpose(),
                                   autoLevels=False, autoRange=False)    
        h = self._waterfall_img.getHistogram()
        self._lut.plot.setData(*h)
        self._vb.autoRange()

    def widget(self):
        return self._widget


class pg_waterfall_sink_c(pg_waterfall_sink_base):
    def __init__(self, **kwargs):
        self.iscomplex = True
        addl_kwargs = {'iscomplex': self.iscomplex}
        addl_kwargs.update(kwargs)
        pg_waterfall_sink_base.__init__(self, **addl_kwargs)
        
        self._buffer = 0.5*np.ones((self.nplot,),dtype=np.complex64)


class untitled(gr.flowgraph):
    def __init__(self):
        gr.flowgraph.__init__(self, "Not titled yet")
        self.win = QtGui.QMainWindow()
        self.area = DockArea()
        self.win.setCentralWidget(self.area)
        self.win.resize(1000,500)
        self.win.setWindowTitle("Not titled yet")
        self.docks = []

        self.pyqtgraph_pg_waterfall_sink_0 = self.pyqtgraph_pg_waterfall_sink_0 = pg_waterfall_sink_c(title=None, size=1000000, nfft=8192, nports=1)
        self.docks.append(Dock('pyqtgraph_pg_waterfall_sink_0'))
        self.area.addDock(self.docks[-1],'top')
        self._pyqtgraph_pg_waterfall_sink_0_widget = self.pyqtgraph_pg_waterfall_sink_0.widget()
        self.docks[-1].addWidget(self._pyqtgraph_pg_waterfall_sink_0_widget)


def main(flowgraph_cls=untitled, options=None):
    app = pg.mkQApp('DockArea Example')
    pg.setConfigOptions(antialias=True)
    fg = flowgraph_cls()
    fg.win.show()
    app.exec()

if __name__ == '__main__':
    main()
