from .table_interface import MFunctionTableInterfaceWidget
from functools import partial
from .widgets import MText, MComboBox, MISpin, MFSpin


def mcombobox_factory(name, items, parent, **kwargs):
    """Allows functools.partial to be employed to define 'items'."""
    return MComboBox(name, parent=parent, items=items, **kwargs)


# simplest possible tableInterface GUI example
def simple_function(str_var='label', selector_var='yes', float_var=1.0,
                    int_var=2):
    """A simple function that prints its arguments as a tuple."""

    print((str_var, selector_var, float_var, int_var))


class SimpleFunctionWidget(MFunctionTableInterfaceWidget):
    """A ``MFunctionTableInterfaceWidget`` for use with simple_function.

    Adds custom ``selector_values``, ``editor_map`` and ``default_rows``
    attributes which contain some function specfic information and/or user
    configurable information.

    To run this example as a standalone window use the following:

    ..code-block:: python

        from mily.table_interface_examples import SimpleFunctionWidget
        from PyQt5.QtWidgets import QApplication
        app = QApplication([])
        window = SimpleFunctionWidget('simple_function')
        window.show()
        app.exec_()

    """

    def __init__(self, name, *args, **kwargs):
        _sel_dict = {'yes': True, 'no': False, 'maybe': None}
        self.selector_values = list(_sel_dict.keys())
        default_parameters = [{'str_var': 'plan_1', 'selector_var': True,
                               'float_var': 1.1, 'int_var': 1},
                              {'str_var': 'plan_2', 'selector_var': False,
                               'float_var': 2.2, 'int_var': 2},
                              {'str_var': 'plan_3', 'selector_var': None,
                               'float_var': 3.3, 'int_var': 3}]

        table_editor_map = {'str_var': MText,
                            'selector_var': partial(mcombobox_factory,
                                                    items=_sel_dict),
                            'float_var': MFSpin,
                            'int_var': MISpin}
        super().__init__(simple_function, name, *args,
                         table_editor_map=table_editor_map,
                         default_parameters=[{}, *default_parameters, {}],
                         **kwargs)
