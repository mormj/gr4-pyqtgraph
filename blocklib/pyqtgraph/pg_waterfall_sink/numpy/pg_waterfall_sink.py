from gnuradio import gr
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore

class pg_waterfall_sink_base:
    def __init__(self, blk, **kwargs):
        print(kwargs)
        self._blk = blk
        title = kwargs['title']
        self.nplot = kwargs['size']
        self.nfft = kwargs['nfft']
        self.samp_rate = kwargs['samp_rate']
        self.fc = kwargs['fc']
        colormap = kwargs['colormap']

        self.nports = kwargs.get('nports', 1)
        self.iscomplex = kwargs['iscomplex']
        self._widget = pg.GraphicsLayoutWidget()
        self._plot = self._widget.addPlot(title=title, row=0, col=0)
        # if title:
        #     self._widget.addLabel(title)
        #     self._widget.nextRow()
        # self._vb = self._widget.addViewBox()
        self._lut = pg.HistogramLUTItem(orientation="horizontal") #, levelMode='rgba')
        self._waterfall_img = pg.ImageItem(self.stft(np.zeros((self.nplot,),dtype=np.complex64), self.nfft))
        self._plot.setLabel(axis='bottom', text='Frequency (Hz)')
        self._plot.setLabel(axis='left', text='Time (s)')
        self._plot.invertY()
        self._plot.addItem(self._waterfall_img)
        self._x = [0.0, 1.0]
        self._widget.nextRow()
        self._widget.addItem(self._lut)        
        
        self._lut.gradient.loadPreset(colormap)
        self._lut.setImageItem(self._waterfall_img)


        self.cnt = 0
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50) 

    def stft(self, a, n_fft, window=np.hanning):  
        n = n_fft
        rpad = n - a.shape[-1] % n
        wins = np.pad(a, (0, rpad)).reshape(-1, n) * window(n)
        fftc = np.fft.fftshift(np.fft.fft(wins, n=n), axes=1) #[..., n // 2 : n]
        fftr = np.real(fftc * np.conj(fftc))
        return fftr

    def update(self):   
        self.cnt += 1   
        # print(self._buffer)
        spec = np.flipud(self.stft(self._buffer, self.nfft))
        
        # print(spec)
        # self._waterfall_img.setLookupTable(self._lut, autolevel=True)
        # self._waterfall_img.scale((self._x[-1] - self._x[0]) / len(self._x), 1)
        self._waterfall_img.setImage(spec.transpose(),
                                   autoLevels=False, autoRange=False) 

        num_ffts = int( ((self.nplot + self.nfft - 1) // self.nfft))   
        self._waterfall_img.setRect(QtCore.QRectF(self.fc - self.samp_rate / 2.0, 0, self.samp_rate, num_ffts / self.samp_rate))

        h = self._waterfall_img.getHistogram()
        self._lut.plot.setData(*h)
        # self._lut.autoHistogramRange()

    def widget(self):
        return self._widget


class pg_waterfall_sink_c(pg_waterfall_sink_base):
    def __init__(self, blk, **kwargs):
        self.iscomplex = True
        addl_kwargs = {'iscomplex': self.iscomplex}
        addl_kwargs.update(kwargs)
        pg_waterfall_sink_base.__init__(self, blk, **addl_kwargs)
        
        self._buffer = np.zeros((self.nplot,),dtype=np.complex64)

    def work(self, wio):
        p = 0
        input = wio.inputs()[0]
        # because this is a sync block, each input should have the same n_items
        nin = input.n_items
        inbuf = gr.get_input_array(self._blk, wio, p)
        if (len(self._buffer) > nin):
            self._buffer = np.hstack((self._buffer[nin:], inbuf))
        else:
            n = nin - len(self._buffer)
            self._buffer = inbuf[n:nin]

        input.consume(nin)
        return gr.work_return_t.OK