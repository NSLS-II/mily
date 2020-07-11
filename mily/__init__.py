from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


# make place holder
qApp = None


# Adapted from matplotlib.backends.backend_qt5.py::_create_qApp
def _create_qApp():
    """
    Only one qApp can exist at a time, so check before creating one.
    """
    from qtpy import QtWidgets, QtCore
    global qApp
    import os
    import re

    if qApp is None:
        app = QtWidgets.QApplication.instance()
        if app is None:
            # check for DISPLAY env variable on X11 build of Qt
            try:
                from PyQt5 import QtX11Extras  # noqa: F401
                del QtX11Extras
                is_x11_build = True
            except ImportError:
                is_x11_build = False
            if is_x11_build:
                display = os.environ.get('DISPLAY')
                if display is None or not re.search(r':\d', display):
                    raise RuntimeError('Invalid DISPLAY variable')

            qApp = QtWidgets.QApplication([b"mily"])
            qApp.lastWindowClosed.connect(qApp.quit)
        else:
            qApp = app

    try:
        qApp.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)
        qApp.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    except AttributeError:
        pass


_create_qApp()
