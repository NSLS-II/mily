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


def reload_widget_stylesheet(widget, cascade=False):
    """
    Reload the stylesheet of a QWidget

    When a ``pyqtProperty`` is updated, a widget does not automatically reapply
    its stylesheet. This is an issue if a stylesheet is conditionally applied
    based on the ``pyqtProperty`` value. This method handles reapplying the
    existing stylesheet to guarantee that interface is up-to-date with any
    changes to the contained properties

    Parameters
    ----------
    widget: QWidget

    cascade: bool, optional
        Any child of the provided widget will also re-update its stylesheet
    """
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()
    if cascade:
        for child in widget.children():
            if isinstance(child, QWidget):
                reload_widget_stylesheet(child, cascade=True)


def raise_to_operator(exc, execute=True):
    """
    Utility function to show a Python Exception in QMessageBox

    The type and representation of the Exception are shown in a pop-up
    QMessageBox. The entire traceback is available via a drop-down detailed
    text box in the QMessageBox

    Parameters
    ----------
    exc: Exception

    execute: bool, optional
        Whether to execute the QMessageBox
    """
    # Assemble QMessageBox with Exception details
    err_msg = QMessageBox()
    err_msg.setText(f'{exc.__class__.__name__}: {exc}')
    err_msg.setWindowTitle(type(exc).__name__)
    err_msg.setIcon(QMessageBox.Critical)
    # Format traceback as detailed text
    with io.StringIO() as handle:
        traceback.print_tb(exc.__traceback__, file=handle)
        handle.seek(0)
        err_msg.setDetailedText(handle.read())
    if execute:
        # Execute
        err_msg.exec_()
    return err_msg
