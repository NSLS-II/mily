from .table_interface import MTableInterfaceWidgetWithExport
from .widgets import MText, MComboBox, MISpin, MFSpin
from bluesky.plans import scan
from bluesky.simulators import summarize_plan
from ophyd.sim import hw

hw = hw()


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


class SimpleFunctionWidget(MTableInterfaceWidgetWithExport):
    '''A ``MTableInterfaceWidgetWithExport`` for use with simple_function.

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


# simplest possible tableinterface RunEngine GUI example
def simple_REfunction(label='label', det=hw.det, motor=hw.motor, start=0,
                      stop=3, num_steps=3):
    '''A simple function that can performs summarize_plan on a scan plan.'''

    plan = scan([det], motor, start, stop, num_steps, md={'plan_label': label})
    summarize_plan(plan)


class SimpleREfunctionWidget(MTableInterfaceWidgetWithExport):
    '''A ``MTableInterfaceWidgetWithExport`` for use with simple_REfunction.

    Adds custom ``detectors``, ``motors``, ``editor_map`` and ``default_rows``
    attributes which contain some function specfic information and/or user
    configurable information.

   To run this example as a standalone window use the following:

    ..code-block:: python

        from bluesky_ui.table_interface_examples import SimpleREfunctionWidget
        from PyQt5.QtWidgets import QApplication
        app = QApplication([])
        window = SimpleREfunctionWidget('simple_REfunction')
        window.show()
        app.exec_()

    '''

    # NOTE I have made these 'class' variables as I am considering
    # that we may want to make them traitlets for user config reasons.
    detectors = [hw.det, hw.det1, hw.det2]
    motors = [hw.motor, hw.motor1, hw.motor2]
    default_rows = [
        {'label': 'plan_1', 'det': hw.det, 'motor': hw.motor, 'start': 0,
         'stop': 2, 'num_steps': 3},
        {'label': 'plan_2', 'det': hw.det1, 'motor': hw.motor1, 'start': -3,
         'stop': 3, 'num_steps': 7},
        {'label': 'plan_3', 'det': hw.det2, 'motor': hw.motor2, 'start': -4,
         'stop': 4, 'num_steps': 9}]

    def __init__(self, name, *args, **kwargs):
        _det_dict = {det.name: det for det in self.detectors}
        _motor_dict = {motor.name: motor for motor in self.motors}
        self.editor_map = {'label': MText,
                           'det': partialclass(MComboBox,
                                               {'items': _det_dict}),
                           'motor': partialclass(MComboBox,
                                                 {'items': _motor_dict}),
                           'start': MFSpin,
                           'stop': MFSpin,
                           'num_steps': MISpin}
        super().__init__(simple_REfunction, name, *args, **kwargs)
