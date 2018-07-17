import sys
import matplotlib.pyplot as plt
plt.ion()
from matplotlib.backends.qt_compat import QtWidgets, QtCore, QtGui


schema = {'title':
             {'widget_name': 'titleEdit',
              'input': 'QLineEdit',
              'label': 'QLabel',
              'type': str,
              'track': 'textChanged',
              'get': 'text',
              'set': 'setText'},
          'author':
             {'widget_name': 'authorEdit',
              'input': 'QLineEdit',
              'label': 'QLabel',
              'type': str,
              'track': 'textChanged',
              'get': 'text',
              'set': 'setText'},
          'review':
             {'widget_name': 'reviewEdit',
              'input': 'QTextEdit',
              'label': 'QLabel',
              'type': str,
              'track': '',
              'get': 'toPlainText',
              'set': 'setText'}}


class GUI(QtWidgets.QWidget):
    def __init__(self, schema):
        super().__init__()
        self._schema = schema
        self.initUI()

    def initUI(self):
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(10)

        for i, (k, v) in enumerate(self._schema.items()):
            setattr(self, k, getattr(QtWidgets, v['label'])(k.capitalize()))
            setattr(self, v['widget_name'], getattr(QtWidgets, v['input'])())
            grid.addWidget(getattr(self, k), i+1, 0)
            grid.addWidget(getattr(self, v['widget_name']), i+1, 1)

        self.setLayout(grid)

        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('Review')
        self.show()


# Working implementation:
class_dict = {k: property(lambda self, v=v: getattr(getattr(gui, v['widget_name']), v['get'])(),
                          lambda self, val, v=v: getattr(getattr(gui, v['widget_name']), v['set'])(val))
              for k, v in schema.items()}

# Non-working implementation:
"""
class_dict = {}
for k, v in schema.items():
    def _get(self):
        return getattr(getattr(gui, v['widget_name']), v['get'])()
    def _set(self, val):
        getattr(getattr(gui, v['widget_name']), v['set'])(val)
    class_dict[k] = property(_get, _set)
"""
Controller = type('Controller', (), class_dict)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    gui = GUI(schema=schema)
    controller = Controller()

