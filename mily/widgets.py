from qtpy import QtWidgets


def label_layout(name, widget):
    hlayout = QtWidgets.QHBoxLayout()
    label = QtWidgets.QLabel(name)
    hlayout.addWidget(label)
    hlayout.addStretch()
    hlayout.addWidget(widget)
    return hlayout


class MText(QtWidgets.QLineEdit):
    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self._name = name

    def get_parameters(self):
        return {self._name: self.text()}


class MISpin(QtWidgets.QSpinBox):
    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self._name = name

    def get_parameters(self):
        return {self._name: self.value()}


class MFSpin(QtWidgets.QDoubleSpinBox):
    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self._name = name
        self.setDecimals(3)

    def get_parameters(self):
        return {self._name: self.value()}
