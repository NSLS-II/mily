from qtpy import QtWidgets
from ophyd import Device
import datetime
from pyqtgraph.parametertree import parameterTypes as pTypes


def vstacked_label(name, widget):
    "Add a label above a widget"
    vlayout = QtWidgets.QVBoxLayout()
    label = QtWidgets.QLabel(name)
    vlayout.addWidget(label)
    vlayout.addWidget(widget)
    return vlayout


def hstacked_label(name, widget):
    "Add a label to the left of widget"
    layout = QtWidgets.QHBoxLayout()
    label = QtWidgets.QLabel(name)
    layout.addWidget(label)
    layout.addWidget(widget)
    return layout


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


class MComboBox(QtWidgets.QComboBox):
    '''A ``PyQt5.QtWidgets.QComboBox`` that matches the ``mily`` syntax.

    This adds ``get_parameters(self)`` and ``set_default(self,v)`` methods that
    are common for all ``mily`` widgets to make the consumer code easier. It
    also adds a ``name`` attribute and ``__init__`` argument.

    Parameters
    ----------
    args: various
        args passed to ``PyQt5.QtWidgets.QComboBox.__init__(...)``.
    items : dict, optional
        optional dict mapping a 'display name' to items to include in the
        dropdown list.
    kwargs: various
        kwargs passed to ``pyQt5.QtWidgets.QComboBox.__init__(...)``.
    '''

    def __init__(self, name, items={}, **kwargs):
        super().__init__(**kwargs)
        self._name = name
        for i, (key, val) in enumerate(items.items()):
            self.addItem(key)
            self.setItemData(i, val)

    def get_parameters(self):
        '''returns a ``{name: currentData}`` dictionary. '''
        return {self._name: self.currentData()}

    def set_default(self, currentData):
        '''set ``self.currentData`` to ``currentData``.'''
        if currentData is not None:
            index = self.findData(currentData)
            self.setCurrentIndex(index)


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


# Modified from pyqtgraph examples
class MetaDataEntry(pTypes.GroupParameter):
    def __init__(self, **opts):
        opts['type'] = 'group'
        opts['addText'] = "Add"
        opts['addList'] = ['str', 'float', 'int']
        pTypes.GroupParameter.__init__(self, **opts)

    def addNew(self, typ):
        val = {
            'str': '',
            'float': 0.0,
            'int': 0
        }[typ]
        self.addChild(dict(name=f"MD ({len(self.childs)+1})",
                           type=typ, value=val,
                           removable=True,
                           renamable=True))

    def get_metadata(self):
        return {k: v
                for k, (v, _) in self.getValues().items()}
