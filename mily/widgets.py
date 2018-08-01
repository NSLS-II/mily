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
        self.setRange(-2**32, 2**32)

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
        self.setRange(-2**32, 2**32)

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
    def __init__(self, mover, steps=10, **kwargs):
        super().__init__(**kwargs)
        self.name = mover.name
        hlayout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel(self.name)
        lower = self.lower = MFSpin('start')
        upper = self.upper = MFSpin('stop')
        stps = self.steps = MISpin('steps')
        stps.setValue(steps)

        hlayout.addWidget(label)
        hlayout.addStretch()
        hlayout.addWidget(lower)
        hlayout.addWidget(upper)
        hlayout.addWidget(stps)
        self.setLayout(hlayout)
