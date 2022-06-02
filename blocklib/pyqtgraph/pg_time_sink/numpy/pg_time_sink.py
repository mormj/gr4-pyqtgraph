from gnuradio import pyqtgraph as grpg
from gnuradio import gr
import numpy as np
import pyqtgraph as pg

class pg_time_sink_f(grpg.pg_time_sink_f):
    def __init__(self, *args, **kwargs):
        grpg.pg_time_sink_f.__init__(self, *args, **kwargs, impl = grpg.pg_time_sink_f.available_impl.pyshell)
        self.set_pyblock_detail(gr.pyblock_detail(self))
    
        title = args[0]
        nplot = args[1]
        nports = args['nports'] if 'nports' in kwargs else 1

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

        inbuf = gr.get_input_array(self, inputs, 0)
        if (len(self._buffer) > nin):
            self._buffer = np.hstack((self._buffer[nin:], inbuf))
        else:
            n = nin - len(self._buffer)
            self._buffer = inbuf[n:nin]

        inputs[0].consume(nin)
        
        return gr.work_return_t.WORK_OK