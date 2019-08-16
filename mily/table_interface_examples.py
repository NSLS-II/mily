from .table_interface import MFunctionTableInterfaceWidget
from .widgets import MText, MComboBox, MISpin, MFSpin


def partialclass(cls, partial_kwargs):
    '''Returns a partial class with 'partial_kwargs' values set


    This function returns a class whereby any args/kwargs in the dictionary
    ``partial_kwargs`` are set.

    Parameters
    ----------
    partial_kwargs : dict
        a dict mapping arg/kwarg parameters to values.
    '''

    class PartialClass(cls):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **partial_kwargs, **kwargs)
    return PartialClass


# simplest possible tableInterface GUI example
def simple_function(str_var='label', selector_var='yes', float_var=1.0,
                    int_var=2):
    '''A simple function that prints its arguments as a tuple.'''

    print((str_var, selector_var, float_var, int_var))


class SimpleFunctionWidget(MFunctionTableInterfaceWidget):
    '''A ``MFunctionTableInterfaceWidget`` for use with simple_function.

    Adds custom ``selector_values``, ``editor_map`` and ``default_rows``
    attributes which contain some function specfic information and/or user
    configurable information.

    To run this example as a standalone window use the following:

    ..code-block:: python

        from mily.table_interface_examples import SimplefunctionWidget
        from PyQt5.QtWidgets import QApplication
        app = QApplication([])
        window = SimplefunctionWidget('simple_function')
        window.show()
        app.exec_()

    '''

    # NOTE I have made these 'class' variables as I am considering
    # that we may want to make them traitlets for user config reasons.
    selector_values = ['yes', 'no', 'maybe']
    default_rows = [{'str_var': 'plan_1', 'selector_var': True,
                     'float_var': 1.1, 'int_var': 1},
                    {'str_var': 'plan_2', 'selector_var': False,
                     'float_var': 2.2, 'int_var': 2},
                    {'str_var': 'plan_3', 'selector_var': None,
                     'float_var': 3.3, 'int_var': 3}]

    def __init__(self, name, *args, **kwargs):
        _sel_dict = {'yes': True, 'no': False, 'maybe': None}
        self.editor_map = {'str_var': MText,
                           'selector_var': partialclass(MComboBox,
                                                        {'items': _sel_dict}),
                           'float_var': MFSpin,
                           'int_var': MISpin}
        super().__init__(simple_function, name, *args, **kwargs)
