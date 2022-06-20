from regex import P
from gnuradio import pyqtgraph as grpg
from gnuradio import gr
import numpy as np
import pyqtgraph as pg

class pg_table(grpg.pg_table):
    def __init__(self, *args, **kwargs):
        grpg.pg_table.__init__(self, *args, **kwargs, impl = grpg.pg_table.available_impl.pyshell)
        self.set_pyblock_detail(gr.pyblock_detail(self))       
           
        self._widget = pg.TableWidget()
        data = np.array([
            (1,   1.6,   'x'),
            (3,   5.4,   'y'),
            (8,   12.5,  'z'),
            (443, 1e-12, 'w'),
            ], dtype=[('Column 1', int), ('Column 2', float), ('Column 3', object)])
            
        self._widget.setData(data)

        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50) 

    def update(self):       
        pass
            
    def widget(self):
        return self._widget

    def handle_msg_in(self):
        pass