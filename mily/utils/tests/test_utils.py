from qtpy.QtWidgets import QMessageBox

from mily.utils import raise_to_operator


def test_raise_to_operator_msg(monkeypatch, qtbot):

    monkeypatch.setattr(QMessageBox, 'exec_', lambda x: 1)
    exc_dialog = None
    try:
        1/0
    except ZeroDivisionError as exc:
        exc_dialog = raise_to_operator(exc)

    qtbot.addWidget(exc_dialog)
    assert exc_dialog is not None
    assert 'ZeroDivisionError' in exc_dialog.text()
