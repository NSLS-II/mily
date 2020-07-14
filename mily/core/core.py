import os
import re
from qtpy.QtWidgets import QApplication
from qtpy.QtCore import Qt
from qtpy import PYQT5, PYSIDE2

import logging
logger = logging.getLogger(__name__)


# Adapted from matplotlib.backends.backend_qt5.py::_create_qApp
def create_qApp(*args):
    """
    Creates QApplication object.

    Parameters
    ----------
    *args:
        The list of arguments that are passed to QApplication constructor.
        Typically this would be a list of command-line parameters `sys.argv`.

    Returns
    -------
    Reference to QApplication object.
    """

    qApp = QApplication.instance()
    if qApp is None:
        # check for DISPLAY env variable on X11 build of Qt
        try:
            if PYQT5:
                from PyQt5 import QtX11Extras  # noqa: F401
            elif PYSIDE2:
                from PySide2 import QtX11Extras  # noqa: F401
            else:
                logger.warning("Function 'create_qApp': is called with Qt package that is "
                               "not supported. The program may not work as expected.")
                raise ImportError
            del QtX11Extras
            is_x11_build = True
        except ImportError:
            is_x11_build = False
        if is_x11_build:
            display = os.environ.get('DISPLAY')
            if display is None or not re.search(r':\d', display):
                raise RuntimeError('Invalid DISPLAY variable')

        qApp = QApplication(*args)
        qApp.lastWindowClosed.connect(qApp.quit)

    try:
        qApp.setAttribute(Qt.AA_UseHighDpiPixmaps)
        qApp.setAttribute(Qt.AA_EnableHighDpiScaling)
    except AttributeError:
        pass

    return qApp
