from qtpy import QtWidgets
from mily.widgets import MText, MISpin, MFSpin
import numpy as np


class FunctionUI(QtWidgets.QWidget):
    def __init__(self, func):
        super().__init__()
        self._func = func
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self._params = {}

        for k, v in func.__annotations__.items():
            hlayout = QtWidgets.QHBoxLayout()
            layout.addLayout(hlayout)

            label = QtWidgets.QLabel(k)
            hlayout.addWidget(label)

            hlayout.addStretch()
            npdt = np.dtype(v).kind
            if npdt == 'i':
                w = MISpin(name=k, parent=self)
            elif npdt == 'f':
                w = MFSpin(name=k, parent=self)
                w.setDecimals(3)
            elif npdt == 'U':
                w = MText(name=k, parent=self)
            else:
                w = QtWidgets.QLabel(npdt)
            try:
                w.setKeyboardTracking(False)
            except AttributeError:
                pass

            self._params[k] = w
            hlayout.addWidget(w)

    def get_parameters(self):
        return {k: v
                for w in self._params.values()
                for k, v in w.get_parameters().items()}

    def run_me(self):
        return self._func(**self.get_parameters())
