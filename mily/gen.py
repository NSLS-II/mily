from qtpy import QtWidgets
from mily.widgets import MText, MISpin, MFSpin
import numpy as np
import inspect


class FunctionUI(QtWidgets.QWidget):

    @staticmethod
    def process_signature(sig):
        out = {}
        for k, v in sig.parameters.items():
            npdt = np.dtype(v.annotation).kind
            if npdt == 'i':
                w = MISpin(name=k)
            elif npdt == 'f':
                w = MFSpin(name=k)
                w.setDecimals(3)
            elif npdt == 'U':
                w = MText(name=k)
            else:
                w = QtWidgets.QLabel(npdt)
            try:
                w.setKeyboardTracking(False)
            except AttributeError:
                pass

            out[k] = w
        return out

    def __init__(self, func):
        super().__init__()
        self._func = func
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self._params = {}

        for k, w in self.process_signature(
                inspect.signature(func)).items():
            hlayout = QtWidgets.QHBoxLayout()
            layout.addLayout(hlayout)

            label = QtWidgets.QLabel(k)
            hlayout.addWidget(label)

            hlayout.addStretch()

            self._params[k] = w
            hlayout.addWidget(w)

    def get_parameters(self):
        return {k: v
                for w in self._params.values()
                for k, v in w.get_parameters().items()}

    def run_me(self):
        return self._func(**self.get_parameters())
