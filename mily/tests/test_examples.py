from qtpy.QtWidgets import QWidget, QLineEdit
from qtpy import PYQT5


def test_one_plus_one_is_two():
    "Check that one and one are indeed two."
    assert 1 + 1 == 2


def test_gui(qtbot):
    """Trivial PyQt test"""
    wd = QWidget()
    qtbot.addWidget(wd)
    wd.show()


def test_focus(qtbot):
    """Check that window manager is working"""
    line_edit = QLineEdit()
    qtbot.addWidget(line_edit)
    if PYQT5:
        with qtbot.waitExposed(line_edit):  # Supported only by PyQt5
            line_edit.show()
    else:
        qtbot.waitForWindowShown(line_edit)  # Works with Pyside2
        line_edit.show()

    line_edit.setFocus()

    qtbot.waitUntil(lambda: line_edit.hasFocus())

    assert line_edit.hasFocus()
