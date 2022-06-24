from regex import P
from gnuradio import pyqtgraph as grpg
from gnuradio import gr
import numpy as np
import pyqtgraph as pg
import pmtf
from pyqtgraph.Qt import QtGui

class pg_table(grpg.pg_table):
    def __init__(self, *args, **kwargs):
        grpg.pg_table.__init__(self, *args, **kwargs, impl = grpg.pg_table.available_impl.pyshell)
        self.set_pyblock_detail(gr.pyblock_detail(self))       
           
        self._widget = pg.TableWidget()
        self.data = None
        self.data_changed = False
        # data = np.array([
        #     (1,   1.6,   'x'),
        #     (3,   5.4,   'y'),
        #     (8,   12.5,  'z'),
        #     (443, 1e-12, 'w'),
        #     ], dtype=[('Column 1', int), ('Column 2', float), ('Column 3', object)])
            
        # self._widget.setData(data)

        # self.timer = pg.QtCore.QTimer()
        # self.timer.timeout.connect(self.update)
        # self.timer.start(100) 

    # def update(self):    
    #     if self.data_changed:
    #         self._widget.setData(self.data)
    #         self.data_change = False

    def widget(self):
        return self._widget

    def handle_msg_in(self, msg):
        x = pmtf.map(msg)

        if not self.data:
            # self._widget.setHorizontalHeaderLabels(x.keys())
            # self._widget.setHorizontalHeaderItem(0, QtGui.QTableWidgetItem("asdf"))
            # self._widget.horizontalHeader().setVisible(True)
            # self.data = [x.keys(),]
            self.data = []

        # vals = []
        # for item in x.items():
        #      vals.append(item[1]())

        vals = {}
        for item in x.items():
             vals[item[0]] = item[1]()

        self.data.append(vals)
        self.data_changed = True
        self._widget.setData(self.data)


        