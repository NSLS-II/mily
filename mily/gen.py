from qtpy import QtWidgets
from mily.widgets import MText, MISpin, MFSpin, label_layout
import numpy as np
import inspect


class FunctionUI(QtWidgets.QWidget):

    @staticmethod
    def process_parameter(param):
        k = param.name
        npdt = np.dtype(param.annotation).kind
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
        return w

    def __init__(self, func):
        super().__init__()
        self._func = func
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self._params = {}

        for k, p in inspect.signature(func).parameters.items():
            w = self.process_parameter(p)
            self._params[k] = w
            layout.addLayout(label_layout(k, w))

    def get_parameters(self):
        return {k: v
                for w in self._params.values()
                for k, v in w.get_parameters().items()}

    def run_me(self):
        return self._func(**self.get_parameters())


class RunnableFunctionUI(FunctionUI):
    def __init__(self, func):
        super().__init__(func)

        self.go_button = QtWidgets.QPushButton('RUN')
        self.layout().addWidget(self.go_button)
        self.go_button.clicked.connect(self.run_me)
