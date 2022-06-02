from regex import P
from gnuradio import pyqtgraph as grpg
from gnuradio import gr
import numpy as np
import pyqtgraph as pg

class pg_time_sink_f(grpg.pg_time_sink_f):
    def __init__(self, *args, **kwargs):
        grpg.pg_time_sink_f.__init__(self, *args, **kwargs, impl = grpg.pg_time_sink_f.available_impl.pyshell)
        self.set_pyblock_detail(gr.pyblock_detail(self))
    
        self.colors = ['blue','red','green','magenta','cyan','yellow','white','gray','darkCyan','darkMagenta','darkYellow','darkGray']

        title = args[0]
        nplot = args[1]
        self.nports = len(self.input_ports())

        self._widget = pg.PlotWidget(title=title)

        self._nplot = nplot
        self._buffers = []
        self._curves = []
        

        idx = 0
        self._tags = []
        for p in range(self.nports):
            self._buffers.append(np.zeros((nplot,)))
            c = self._widget.plot(self._buffers[p])
            c.setPen(self.colors[idx])
            self._curves.append(c)

            
            self._tags.append(
                {"buffer": [],
                "points": [],
                "text": [],
                "arrows": []}
            )
            idx += 1

        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)

    def update(self):       
        for p in range(self.nports):
            idx = 0
            to_remove = []
            self._curves[p].setData(y=self._buffers[p])
            for tag in self._tags[p]["buffer"]:
                if tag.offset() >= self._n_buf_start and tag.offset() < self._n_buf_end:
                    if (idx >= len(self._tags[p]["points"])):
                        self._tags[p]["points"].append(pg.CurvePoint(self._curves[p]))
                        self._widget.addItem(self._tags[p]["points"][idx])
                        self._tags[p]["text"].append(pg.TextItem("test", anchor=(0.5, -0.2)))
                        self._tags[p]["text"][idx].setParentItem(self._tags[p]["points"][idx])
                        self._tags[p]["arrows"].append(pg.ArrowItem(headLen=10, headWidth=5, angle=90))
                        self._tags[p]["arrows"][idx].setParentItem(self._tags[p]["points"][idx])

                    self._tags[p]["points"][idx].setPos(float(tag.offset()-self._n_buf_start)/(len(self._buffers[p])-1))
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

    def work(self, inputs, outputs):
        for p, input in enumerate(inputs):
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

            inbuf = gr.get_input_array(self, inputs, p)
            if (len(self._buffers[p]) > nin):
                self._buffers[p] = np.hstack((self._buffers[p][nin:], inbuf))
            else:
                n = nin - len(self._buffers[p])
                self._buffers[p] = inbuf[n:nin]

            input.consume(nin)
        
        return gr.work_return_t.WORK_OK