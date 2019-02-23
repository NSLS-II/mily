"""
Various Qt Utilities
"""


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
