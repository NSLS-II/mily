"""
Various Qt Utilities
"""
import io
import traceback

from qtpy.QtWidgets import QWidget, QMessageBox


def clear_layout(layout):
    """
    Clear a QLayout

    This method acts recursively, clearing any child layouts that may be
    contained within the layout itself. All discovered widgets are marked for
    deletion.

    Parameters
    ----------
    layout : QLayout
    """
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()
        elif child.layout():
            clear_layout(child.layout())


def raise_to_operator(exc):
    """
    Utility function to show a Python Exception in QMessageBox

    The type and representation of the Exception are shown in a pop-up
    QMessageBox. The entire traceback is available via a drop-down detailed
    text box in the QMessageBox

    Parameters
    ----------
    exc: Exception
    """
    # Assemble QMessageBox with Exception details
    err_msg = QMessageBox()
    err_msg.setText(f'{exc.__class__.__name__}: {exc}')
    err_msg.setWindowTitle(type(exc).__name__)
    err_msg.setIcon(QMessageBox.Critical)
    # Format traceback as detailed text
    handle = io.StringIO()
    traceback.print_tb(exc.__traceback__, file=handle)
    handle.seek(0)
    err_msg.setDetailedText(handle.read())
    # Execute
    err_msg.exec_()
    return err_msg
