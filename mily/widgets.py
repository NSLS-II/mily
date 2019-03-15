from qtpy import QtWidgets
from ophyd import Device
import datetime
from pyqtgraph.parametertree import parameterTypes as pTypes


def label_layout(name, required, widget, label_pos='h'):
    hlayout = QtWidgets.QHBoxLayout()
    if label_pos == 'h':
        llayout = QtWidgets.QHBoxLayout()
    elif label_pos == 'v':
        llayout = QtWidgets.QVBoxLayout()
    else:
        raise ValueError(f'label_pos: {label_pos} is invalid.  ' +
                         'must be one of {"h", "v"}')
    label = QtWidgets.QLabel(name)
    cb = QtWidgets.QCheckBox()
    hlayout.addWidget(cb)
    llayout.addWidget(label)
    llayout.addWidget(widget)
    hlayout.addLayout(llayout)
    hlayout.addStretch()

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


class OphydKinds(QtWidgets.QTreeWidget):
    def __init__(self, *args, obj, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_object(obj)

    def set_object(self, obj):
        self._obj = obj

        def fill_item(item, value):
            item.setExpanded(True)
            child = QtWidgets.QTreeWidgetItem([value.name,
                                               str(value.kind)])
            item.addChild(child)
            if isinstance(value, Device):
                for k in value.component_names:
                    fill_item(child, getattr(value, k))

        self.clear()
        fill_item(self.invisibleRootItem(), obj)


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
