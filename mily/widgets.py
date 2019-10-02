from qtpy import QtWidgets
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
    def __init__(self, name, minimum=-2**16, maximum=2**16, **kwargs):
        super().__init__(minimum=minimum, maximum=maximum, **kwargs)
        self._name = name

    def get_parameters(self):
        return {self._name: self.value()}

    def set_default(self, v):
        if v is not None:
            self.setValue(v)


class MFSpin(QtWidgets.QDoubleSpinBox):
    def __init__(self, name, minimum=-2**16, maximum=2**16, **kwargs):
        super().__init__(minimum=minimum, maximum=maximum, **kwargs)
        self._name = name

    def get_parameters(self):
        return {self._name: self.value()}

    def set_default(self, v):
        if v is not None:
            self.setValue(v)


class MComboBox(QtWidgets.QComboBox):
    '''A ``PyQt5.QtWidgets.QComboBox`` that matches the ``mily`` syntax.

    This adds ``get_parameters(self)`` and ``set_default(self, v)`` methods
    that are common for all ``mily`` widgets to make the consumer code easier.
    It also adds a ``name`` attribute and ``__init__`` argument.

    Parameters
    ----------
    args : various
        args passed to ``PyQt5.QtWidgets.QComboBox.__init__(...)``.
    items : dict, optional
        optional dict mapping a 'display name' to items to include in the
        dropdown list.
    kwargs : various
        kwargs passed to ``pyQt5.QtWidgets.QComboBox.__init__(...)``.
    '''

    def __init__(self, name, items={}, **kwargs):
        super().__init__(**kwargs)
        self._name = name
        for i, (key, val) in enumerate(items.items()):
            self.addItem(key)
            self.setItemData(i, val)

    def get_parameters(self):
        '''Returns a ``{name: currentData}`` dictionary. '''
        return {self._name: self.currentData()}

    def set_default(self, currentData):
        '''Sets ``self.currentData`` to ``currentData``.'''
        if currentData is not None:
            index = self.findData(currentData)
            self.setCurrentIndex(index)


class MCheckBox(QtWidgets.QCheckBox):
    '''A ``PyQt5.QtWidgets.QCheckBox`` that matches the ``mily`` syntax.

    This adds ``get_parameters(self)`` and ``set_default(self, v)`` methods
    that are common for all ``mily`` widgets to make the consumer code easier.
    It also adds a ``name`` attribute and ``__init__`` argument.

    Parameters
    ----------
    args : various
        args passed to ``PyQt5.QtWidgets.QCheckBox.__init__(...)``.
    kwargs : various
        kwargs passed to ``PyQt5.QtWidgets.QCheckBox.__init__(...)``.
    '''

    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self._name = name

    def get_parameters(self):
        '''Returns a ``{name: isChecked}`` dictionary.'''
        return {self._name: self.isChecked()}

    def set_default(self, checkState):
        '''Sets ``self.isChecked`` to ``checkState``.'''
        if checkState is not None:
            self.setChecked(checkState)


class MSelector(QtWidgets.QGroupBox):
    '''A widget that displays a list of objects with 'checkboxes'.

    This adds ``get_parameters(self)`` and ``set_default(self, v)`` methods
    that are common for all ``mily`` widgets to make the consumer code easier.
    It also adds a ``name`` attribute and ``__init__`` argument. It results in
    a vertical list of objects (defined in the 'items' arg) with a
    corresponding checkbox for each item. It returns a list of checked items.

    Parameters
    ----------
    name : str
        name of the widget to be stored in ``self._name``
    option_list : list
        list of items to include checkboxes for.
    vertical : bool, optional
        optional boolean that indicates if the list should be displayed
        vertically (True) or horizontally (False). default is True.
    kwargs : various
        kwargs passed to ``PyQt5.QtWidgets.QGroupBox.__init__(...)``.
    '''

    def __init__(self, name, option_list, vertical=True, **kwargs):
        self._name = name
        super().__init__(title='', **kwargs)
        self.button_group = QtWidgets.QButtonGroup()
        self.button_group.setExclusive(False)
        if vertical:
            MainLayout = QtWidgets.QVBoxLayout()
        else:
            MainLayout = QtWidgets.QHBoxLayout()
        self.setLayout(MainLayout)
        for item in option_list:
            item_name = getattr(item, 'name', str(item))
            button = QtWidgets.QCheckBox(item_name, **kwargs)
            setattr(button, 'item', item)
            self.button_group.addButton(button)
            MainLayout.addWidget(button)

        # sets the layout width and height to fit inclosed widgets
        self.layout().setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        # ensure that the background is auto-filled
        self.setAutoFillBackground(True)

    def get_parameters(self):
        item_list = [b.item
                     for b in self.button_group.buttons()
                     if b.isChecked()]

        return {self._name: item_list}

    def set_default(self, value):
        # value is list of python values or objects.
        if value is not None:
            for button in self.button_group.buttons():
                button.setChecked(button.item in value)


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
