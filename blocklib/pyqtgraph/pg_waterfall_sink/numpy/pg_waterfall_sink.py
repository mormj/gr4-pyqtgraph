from regex import P
from gnuradio import pyqtgraph as grpg
from gnuradio import gr
import numpy as np
import pyqtgraph as pg
from pyqtgraph.graphicsItems.GradientEditorItem import Gradients

class pg_waterfall_sink_base:
    def __init__(self, *args, **kwargs):
        self.colors = ['blue','red','green','magenta','cyan','yellow','white','gray','darkCyan','darkMagenta','darkYellow','darkGray']
        
        title = args[0]
        self.nplot = args[1]

        self.nports = kwargs.get('nports', 1)
        self.iscomplex = kwargs['iscomplex']
        self._widget = pg.GraphicsLayoutWidget()
        self._plot = self._widget.addPlot(title="Waterfall", row=0, col=0)
        # self._lut = pg.HistogramLUTItem(orientation="horizontal") #, levelMode='rgba')
        self._waterfall_img = None
        self._x = [0.0, 1.0]
        # self._widget.nextRow()
        # self._widget.addItem(self._lut)        
        cmap = pg.colormap.get("viridis")
        self._lut = cmap.getLookupTable(0, 1, 1024)
        
        # Gradients['gor'] = {'ticks': [(0.0, (74, 158, 71)), (0.5, (255, 230, 0)), (1, (191, 79, 76))], 'mode': 'rgb'}
        # self._lut.gradient.loadPreset('flame')
        self._plot.setMouseEnabled(x=False, y=False)


        self.cnt = 0
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50) 

    def update(self):   
        self.cnt += 1   
        if not self._waterfall_img:
            self._waterfall_img = pg.ImageItem()
            # self._waterfall_img.scale((self._x[-1] - self._x[0]) / len(self._x), 1)
            self._waterfall_img.setLookupTable(self._lut)
            self._waterfall_img.setZValue(-1)
            self._plot.addItem(self._waterfall_img)


        def stft(a, n_fft=128, window=np.hanning):  
            n = n_fft
            rpad = n - a.shape[-1] % n
            wins = np.pad(a, (0, rpad)).reshape(-1, n) * window(n)
            fftc = np.fft.fftshift(np.fft.fft(wins, n=n), axes=1) #[..., n // 2 : n]
            fftr = np.real(fftc * np.conj(fftc))
            return fftr

        # print(self._buffer)
        spec = stft(self._buffer)
        # print(spec)
        self._waterfall_img.setLookupTable(self._lut)
        # self._waterfall_img.scale((self._x[-1] - self._x[0]) / len(self._x), 1)
        self._waterfall_img.setImage(spec,
                                   autoLevels=False, autoRange=False, levels=(0.0, 1024.0))    
        # h = self._waterfall_img.getHistogram()
        # self._lut.plot.setData(*h)

    def widget(self):
        return self._widget


class pg_waterfall_sink_c(grpg.pg_waterfall_sink_c, pg_waterfall_sink_base):
    def __init__(self, *args, **kwargs):
        self.iscomplex = True
        addl_kwargs = {'iscomplex': self.iscomplex}
        addl_kwargs.update(kwargs)
        pg_waterfall_sink_base.__init__(self, *args, **addl_kwargs)
        grpg.pg_waterfall_sink_c.__init__(self, *args, **kwargs, impl = grpg.pg_waterfall_sink_c.available_impl.pyshell)
        self.set_pyblock_detail(gr.pyblock_detail(self))       
        
        self._buffer = np.zeros((self.nplot,),dtype=np.complex64)

    def work(self, wio):
        p = 0
        input = wio.inputs()[0]
        # because this is a sync block, each input should have the same n_items
        nin = input.n_items
        inbuf = gr.get_input_array(self, wio, p)
        if (len(self._buffer) > nin):
            self._buffer = np.hstack((self._buffer[nin:], inbuf))
        else:
            n = nin - len(self._buffer)
            self._buffer = inbuf[n:nin]

        input.consume(nin)
        return gr.work_return_t.WORK_OK