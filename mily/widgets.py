from qtpy import QtWidgets
import datetime


def label_layout(name, required, widget):
    hlayout = QtWidgets.QHBoxLayout()
    label = QtWidgets.QLabel(name)
    cb = QtWidgets.QCheckBox()
    hlayout.addWidget(cb)
    hlayout.addWidget(label)
    hlayout.addStretch()
    hlayout.addWidget(widget)

    if required:
        cb.setChecked(True)
        cb.setEnabled(False)
    else:
        cb.setCheckable(True)
        cb.stateChanged.connect(widget.setEnabled)
        cb.setChecked(False)
        widget.setEnabled(False)

    return hlayout


def vstacked_label(name, widget):
    vlayout = QtWidgets.QVBoxLayout()
    label = QtWidgets.QLabel(name)
    vlayout.addWidget(label)
    vlayout.addWidget(widget)
    return vlayout


def merge_parameters(widget_iter):
    return {k: v
            for w in widget_iter
            for k, v in w.get_parameters().items()
            if w.isEnabled()}


class MText(QtWidgets.QLineEdit):
    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self._name = name

    def get_parameters(self):
        return {self._name: self.text()}

    def set_default(self, v):
        if v is not None:
            self.setText(v)


class MISpin(QtWidgets.QSpinBox):
    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self._name = name
        self.setKeyboardTracking(False)
        self.setRange(-2**16, 2**16)

    def get_parameters(self):
        return {self._name: self.value()}

    def set_default(self, v):
        if v is not None:
            self.setValue(v)


class MFSpin(QtWidgets.QDoubleSpinBox):
    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self._name = name
        self.setDecimals(3)
        self.setKeyboardTracking(False)
        self.setRange(-2**16, 2**16)

    def get_parameters(self):
        return {self._name: self.value()}

    def set_default(self, v):
        if v is not None:
            self.setValue(v)


class MDateTime(QtWidgets.QDateTimeEdit):
    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self._name = name
        self.setDateTime(datetime.datetime.now())
        self.setCalendarPopup(True)

    def get_parameters(self):
        return {self._name: self.dateTime().toPyDateTime()}

    def set_default(self, v):
        if v is not None:
            self.setDateTime(v)


class MoverRanger(QtWidgets.QWidget):
    def __init__(self, name, mover=None, *,
                 start_name='start',
                 stop_name='stop',
                 steps_name='steps',
                 steps=10, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.mover = None
        hlayout = QtWidgets.QHBoxLayout()
        label = self.label = QtWidgets.QLabel('')
        lower = self.lower = MFSpin(start_name)
        upper = self.upper = MFSpin(stop_name)
        stps = self.steps = MISpin(steps_name)
        stps.setValue(steps)
        stps.setMinimum(1)

        hlayout.addWidget(label)
        hlayout.addStretch()
        hlayout.addLayout(vstacked_label(start_name, lower))
        hlayout.addLayout(vstacked_label(stop_name, upper))
        hlayout.addLayout(vstacked_label(steps_name, stps))
        self.setLayout(hlayout)

        if mover is not None:
            self.set_mover(mover)

    def set_mover(self, mover):
        self.mover = mover
        self.label.setText(mover.name)
        limits = getattr(mover, 'limits', (0, 0))
        upper = self.upper
        lower = self.lower
        # (0, 0) is the epics way of saying 'no limits'
        if limits != (0, 0):
            lower.setRange(*limits)
            upper.setRange(*limits)

        egu = getattr(mover, 'egu', None)
        if egu is not None:
            lower.setSuffix(f' {egu}')
            upper.setSuffix(f' {egu}')

    def get_parameters(self):
        return merge_parameters([self.lower, self.upper, self.steps])


class BoundingBox(QtWidgets.QWidget):
    def __init__(self, name, **kwargs):
        pass
