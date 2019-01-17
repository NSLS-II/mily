from qtpy import QtWidgets
from mily.widgets import (MText, MISpin, MFSpin, MDateTime,
                          label_layout, merge_parameters, DetectorSelector,
                          MoverRanger)
import numpy as np
import inspect
import datetime
from bluesky.plans import scan


class FunctionUI(QtWidgets.QWidget):

    @staticmethod
    def process_parameter(param):
        k = param.name
        npdt = np.dtype(param.annotation).kind
        np_map = {'i': MISpin,
                  'f': MFSpin,
                  'U': MText}

        type_map = {datetime.datetime: MDateTime}
        try:
            w = np_map[npdt](name=k)
        except KeyError:
            try:
                w = type_map[param.annotation](name=k)
            except KeyError:
                w = QtWidgets.QLabel(str(param.annotation))

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
            layout.addLayout(label_layout(
                k,
                (p.default is p.empty),
                w))
            if p.default is not p.empty:
                try:
                    w.set_default(p.default)
                except AttributeError:
                    pass

    def get_parameters(self):
        return merge_parameters(self._params.values())

    def run_me(self):
        return self._func(**self.get_parameters())


class RunnableFunctionUI(FunctionUI):
    def __init__(self, func):
        super().__init__(func)

        self.go_button = QtWidgets.QPushButton('RUN')
        self.layout().addWidget(self.go_button)
        self.go_button.clicked.connect(self.run_me)


class REQueue(QtWidgets.QWidget):

    def __init__(self, RE, queue, motors, detectors):
        super().__init__()
        # random state it holds
        self.RE = RE
        self.queue = queue
        self.motors = {m.name: m for m in motors}

        # layout :(

        main_layout = QtWidgets.QHBoxLayout()
        self.setLayout(main_layout)
        left_pannel = QtWidgets.QVBoxLayout()
        right_pannel = QtWidgets.QVBoxLayout()
        main_layout.addLayout(left_pannel)
        main_layout.addLayout(right_pannel)

        self.detectors_widget = DetectorSelector(detectors=detectors)
        right_pannel.addWidget(self.detectors_widget)
        self.mr = MoverRanger('a', mover=None)
        cb = QtWidgets.QComboBox()
        cb.addItems(list(self.motors))

        cb.activated[str].connect(lambda k: self.mr.set_mover(self.motors[k]))

        right_pannel.addWidget(cb)
        right_pannel.addWidget(self.mr)
        self.go_button = QtWidgets.QPushButton('SCAN!')
        right_pannel.addWidget(self.go_button)

        def runner():
            self.queue.put(scan(self.detectors_widget.active_detectors,
                                *self.mr.get_args()))

        self.go_button.clicked.connect(runner)

    def add_to_queue(self, func, *args, **kwargs):
        self.queue.put(func(self.checked_detectors, *args, **kwargs))
