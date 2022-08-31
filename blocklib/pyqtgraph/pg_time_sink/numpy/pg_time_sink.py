from regex import P
from gnuradio import pyqtgraph as grpg
from gnuradio import gr
import numpy as np
import pyqtgraph as pg

class pg_time_sink_base:
    def __init__(self, blk, **kwargs):

        self._blk = blk
        self.colors = ['blue','red','green','magenta','cyan','yellow','white','gray','darkCyan','darkMagenta','darkYellow','darkGray']
        
        title = kwargs['title']
        nplot = kwargs['size']

        self.nports = kwargs.get('nports', 1)
        self.iscomplex = kwargs['iscomplex']
        self._widget = pg.PlotWidget(title=title, background='w')

        self._nplot = nplot 
        self._nbuffers = 2*self.nports if self.iscomplex else self.nports
        self._buffers = []
        self._curves = []

        idx = 0
        self._tags = []
        for p in range(self.nports):
            ncurves = 2 if self.iscomplex else 1
            for i in range(ncurves):
                self._buffers.append(np.zeros((nplot,)))
                c = self._widget.plot(self._buffers[p])
                c.setPen(self.colors[idx], antialias=True)
                self._curves.append(c)
                idx += 1

            self._tags.append(
                {"buffer": [],
                "points": [],
                "text": [],
                "arrows": []}
            )
                
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50) 

    def update(self):       
        n = 2 if self.iscomplex else 1
        for p in range(self.nports):
            idx = 0
            to_remove = []
            self._curves[n*p].setData(y=self._buffers[n*p])
            if self.iscomplex:
                self._curves[n*p+1].setData(y=self._buffers[n*p+1])
            for tag in self._tags[p]["buffer"]:
                if tag.offset() >= self._n_buf_start and tag.offset() < self._n_buf_end:
                    if (idx >= len(self._tags[p]["points"])):
                        self._tags[p]["points"].append(pg.CurvePoint(self._curves[p]))
                        self._widget.addItem(self._tags[p]["points"][idx])
                        self._tags[p]["text"].append(pg.TextItem("test", anchor=(0.5, -0.2)))
                        self._tags[p]["text"][idx].setParentItem(self._tags[p]["points"][idx])
                        self._tags[p]["arrows"].append(pg.ArrowItem(headLen=10, headWidth=5, angle=90))
                        self._tags[p]["arrows"][idx].setParentItem(self._tags[p]["points"][idx])

                    self._tags[p]["points"][idx].setPos(float(tag.offset()-self._n_buf_start)/(len(self._buffers[n*p])-1))
                    # self._tag_text[idx].setText(f'{self._buffer[tag.offset()-self._n_buf_start]:0.1f}')
                    self._tags[p]["text"][idx].setText(str(tag))

                    idx+=1
                else:
                    to_remove.append(tag)

                for ii in range(idx,len(self._tags[p]["points"])):
                    self._widget.removeItem(self._tags[p]["points"][ii])

                self._tags[p]["points"] = self._tags[p]["points"][:idx]
                self._tags[p]["text"] = self._tags[p]["text"][:idx]
                self._tags[p]["arrows"] = self._tags[p]["arrows"][:idx]

            for remove_tag in to_remove:
                self._tags[p]["buffer"].remove(remove_tag)

            

    def widget(self):
        return self._widget

class pg_time_sink_f(pg_time_sink_base):
    def __init__(self, blk, **kwargs):

        self.iscomplex = False
        addl_kwargs = {'iscomplex': self.iscomplex}
        addl_kwargs.update(kwargs)

        pg_time_sink_base.__init__(self, blk, **addl_kwargs)  
        

    def work(self, wio):
        for p, input in enumerate(wio.inputs()):

            # because this is a sync block, each input should have the same n_items
            nin = input.n_items
            nr = input.nitems_read()
            tags = input.tags_in_window(0,nin)
            # each tag should be associated with an index in the buffer
            self._tags[p]["buffer"] += tags

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


class pg_time_sink_c( pg_time_sink_base):
    def __init__(self, blk, **kwargs):
        self.iscomplex = True
        addl_kwargs = {'iscomplex': self.iscomplex}
        addl_kwargs.update(kwargs)
        pg_time_sink_base.__init__(self, blk, **addl_kwargs)
        

    def work(self, wio):
        for p, input in enumerate(wio.inputs()):
            # because this is a sync block, each input should have the same n_items
            nin = input.n_items

            nr = input.nitems_read()
            tags = input.tags_in_window(0,nin)
            # each tag should be associated with an index in the buffer
            self._tags[p]["buffer"] += tags

            # The absolute offsets at the beginning and end of the buffer
            #  Pruning can be done in the update function
            self._n_buf_end = nr+nin
            self._n_buf_start = nr-(len(self._buffers[2*p])-nin)

            inbuf = gr.get_input_array(self._blk, wio, p)
            if (len(self._buffers[p]) > nin):
                self._buffers[2*p] = np.hstack((self._buffers[p][nin:], np.real(inbuf)))
                self._buffers[2*p+1] = np.hstack((self._buffers[p][nin:], np.imag(inbuf)))
            else:
                n = nin - len(self._buffers[p])
                self._buffers[2*p] = np.real(inbuf[n:nin])
                self._buffers[2*p+1] = np.imag(inbuf[n:nin])

            input.consume(nin)
        
        return gr.work_return_t.OK