from qtpy.QtWidgets import QWidget, QLineEdit


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
    with qtbot.waitExposed(line_edit):
        line_edit.show()

    line_edit.setFocus()

    qtbot.waitUntil(lambda: line_edit.hasFocus())

    assert line_edit.hasFocus()
