from qtpy.QtWidgets import QWidget


def test_one_plus_one_is_two():
    "Check that one and one are indeed two."
    assert 1 + 1 == 2


def test_gui(qtbot):
    """Trivial PyQt test"""
    wd =QWidget()
    qtbot.addWidget(wd)
    wd.show()
