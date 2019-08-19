from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QTableView, QWidget, QLabel, QStyledItemDelegate,
                             QHBoxLayout, QVBoxLayout, QMessageBox,
                             QPushButton)
from .widgets import MText, vstacked_label


class MTableItemDelegate(QStyledItemDelegate):
    '''A ``QStyledItemDelegate`` for use with MTableInterfaceWidgets.

    This adds custom ``displayText``, ``setEditorData`` and ``setModelData``
    methods that work with the ``mily.widgets`` API. Namely, using the
    ``get_parameters`` and ``set_default`` methods for reading/writing
    to/from the editor widgets. It has a ``self.editor_map`` attribute that
    maps the column names to editor widgets. It also has a custom method for
    ``self.createEditor`` that uses ``self. editor_map`` and returns the
    correct editor on request. If editor_map is empty it uses an ``MText``
    widget for all columns. It also enforces the inclusion of a parent
    attribute (something that is optional in the ``QStyledItemDelegate``) and
    adds an ``_name`` attribute for consistency with the `mily.widgets`` API.
    '''

    def __init__(self, parent, name, *args, **kwargs):
        self._name = name
        super().__init__(*args, parent=parent, **kwargs)
        self.editor_map = getattr(self.parent(), 'editor_map', {})

    def displayText(self, value, locale):
        '''converts the value of the editor to a display string.

        This method is called whenever the associated model value is updated,
        and updates the associated TableView with the returned str_val for
        display. It is written such that it will ind the best str to asociate
        with the object, and will recursively change dict and list keys/items.
        '''

        def _get_display_str(value):
            '''recursively find a list of attr names for a DisplayText.

            This checks a number of attr names to see if any are present and
            can be used to give a displayText value. Otherwise it returns the
            str generated using ``str(value)``. It will recursively search
            ``dict`` and ``list`` values and return str(dict) or str(list)
            after setting displayText's for each key+value (for dicts) or item
            (for lists).
            '''
            if isinstance(value, list):  # recuresively treat lists
                list_val = []
                for item in value:
                    list_val.append(_get_display_str(item))
                str_val = str(list_val).replace('"', '').replace("'", "")
            elif isinstance(value, dict):  # recursively treat dicts
                dict_val = {}
                for key, val in value.items():
                    dict_val[_get_display_str(key)] = _get_display_str(val)
                str_val = str(dict_val).replace('"', '').replace("'", "")
            else:  # check individual values
                # Check a list of attrs that can return displayText values.
                for attr in ['name', '_name', '__name__']:
                    str_val = getattr(value, attr, None)
                    if str_val:
                        break
                # If none of the above worked
                if not str_val:
                    str_val = str(value)

            return str_val

        return _get_display_str(value)

    def setEditorData(self, editor, index):
        '''Sets the model data to the editor.

        This method is called whenever the editor is opened and sets the
        current value of the editor to that in the model. The change here is to
        use the ``mily.widget`` API ``editor.set_default(value)`` method. It
        also ensures that data associated with the "display" role in the model
        is used, which leads to a consistent approach with the
        ``self.setModelData(...)`` method.
        '''
        row = index.row()
        column = index.column()
        try:
            value = index.model().item(row, column).data(Qt.DisplayRole)
        except AttributeError:
            value = None
        editor.set_default(value)

    def setModelData(self, editor, model, index):
        '''Sets the editor data to the model.

        This method is called whenever the editor is closed _and_ a change has
        been made to the editor value. The change here is to ensure the use of
        the ``mily.widget`` API ``editor.get_parameter()`` method to extract
        the data from the editor. It then writes the data to the model,
        associating it with the "display" role for consistency with the
        ``self.setEditorData(...)`` method.
        '''
        model.setData(index, editor.get_parameters()[editor._name],
                      Qt.DisplayRole)

    def createEditor(self, parent, option, index):
        '''Creates the editor based on ``self.editor_map``.

        This method is whenever a user double clicks on a cell in order to edit
        its value. Based on the 'index' argument it works out which key in the
        ``self.editor_map`` dictionary relates to the cell to be edited, and
        creates the editor based on the type defined by the value for that key.
        '''
        column_name = list(self.editor_map.keys())[index.column()]

        editor = self.editor_map.get(column_name, MText)(column_name,
                                                         parent=parent)

        if editor:
            # ensure the editors background is opaque
            editor.setAutoFillBackground(True)
            # resize the table cell to fit the editor
            editor.setMinimumWidth(80)
            editor.parent().parent().setRowHeight(index.row(),
                                                  editor.height())
            editor.parent().parent().setColumnWidth(index.column(),
                                                    editor.width())

        return editor


class MTableInterfaceView(QTableView):
    '''Creates a table view and model for an ``MTableInterfaceWidget``.

    This creates a custom QTableView and sets some display options that are
    common to ``MTableInterfaceWidget`` tables. It also creates and sets the
    model and the delegate to be used in conjunction with this view.

    Parameters:
    *args/**kwargs : various
        args and kwargs to be passed to ``PyQt5.QtWidgets.QTableView``.
    delegate : QitemDelegate, optional
        The ``PyQt5.QItemDelegate`` to be associated with the class, default is
        the ``MTableItemDelegate``.
    model : QStandardItemModel, optional
        The ``PyQt5.QtGui.QStandardItemModel`` to be associated with the
        class, the default is ``PyQt5.QtGui.QStandardItemModel.
    '''

    def __init__(self, parent, name, *args, delegate=MTableItemDelegate,
                 model=QStandardItemModel, **kwargs):
        self._name = name
        super().__init__(*args, parent=parent, **kwargs)
        self.editor_map = getattr(self.parent(), 'editor_map', {})
        # Apply some style options
        self.horizontalHeader().setDefaultAlignment(Qt.AlignHCenter)
        self.setAlternatingRowColors(True)
        # set the table delegate
        self.setItemDelegate(delegate(self, self.parent()._name+'_model'))
        # set the model and set column headers from editor_map if possible
        self.setModel(model(self))
        if self.editor_map:
            column_names = list(self.editor_map.keys())
            self.model().setHorizontalHeaderLabels(column_names)
        # resize the table rows/columns to fit the displayText sizes
        self.resizeColumnsToContents()
        self.resizeRowsToContents()

        # resize the table to fit the contents on changes
        signals = [self.itemDelegate().closeEditor, self.model().rowsInserted,
                   self.model().dataChanged]
        for signal in signals:
            signal.connect(self.resizeColumnsToContents)
            signal.connect(self.resizeRowsToContents)

    def get_parameters(self):
        '''Return the entire data from the table.

        Returns the entire table data as a list of dicts, with each dict being
        a row that maps the column header to it's value. This follows the
        ``mily.widget`` API.
        '''
        column_names = list(self.editor_map.keys())
        model = self.model()
        parameters = []
        for row in range(0, model.rowCount()):
            row_params = {}
            for column in range(0, model.columnCount()):
                item = model.item(row, column)
                if item:
                    value = item.data(Qt.DisplayRole)
                else:
                    value=None
                row_params[column_names[column]] = value
            parameters.append(row_params)
        return {self._name: parameters}

    def set_default(self, parameters):
        '''Sets the default values from 'parameters' to the model

        Sets the data from 'parameters' to the model, overwriting any existing
        data in the model.This follows the ``mily.widget`` API.

        Parameters
        ----------
        parameters : [dicts]
            List of dicts  with each dict being a row that maps the column
            header to it's value.
        '''
        model = self.model()
        # Empty the model.
        model.removeRows(0, model.rowCount())
        # Add the new data to the model.
        for row_params in parameters:
            row_data = []
            # for each column in the model check if a default is given
            for column in range(0, model.columnCount()):
                header_item = model.horizontalHeaderItem(column)
                header = header_item.text()
                item = QStandardItem()
                value = row_params.get(header, None)
                item.setData(value, Qt.DisplayRole)
                row_data.append(item)
            model.appendRow(row_data)


class MTableInterfaceWidget(QWidget):
    '''Table like interface widget based on the ``mily`` API.

    This widget allows for 'sets' of the same parameters to be defined as rows
    in a table. The parameters are defined by the 'keys' in the dictionary
    self.editor_map, where the values of the dictionary are the widgets to be
    used to update the values for the given columns.In addition 2 other
    dictionaries ``self.prefix_editor_map`` and ``self.suffix_editor_map`` can
    be set in the same way to provide additional 'global' parameters to be
    returned by the method ``self.get_parameters()`` or inputted using the
    method ``self.set_defaults(...)`` before (prefix) or after (suffix) the
    ``self.tableView`` data. Prefix parameters appear above the table while
    suffix parameters appear below the table.

    In addition to the table prefix and suffix parameters there are a number of
    buttons on the widget for modifying the table. They are:
        +: adds a new row after the last selected row (or last row if none
            selected) ensuring that it contains a unique label.
        -: deletes the selected row(s).
        up: moves the selected row(s) up
        down: moves the selected row(s) down
        duplicate: duplicates the selected row(s)

    Finally a list of 'default values' to be loaded into the table on
    initialization is defined using ``self.default_rows``. This is passed to
    ``self.set_defaults(...)`` on initialization. The structure of the data to
    be passed into ``self.set_defaults(...)`` and the parameters value in the
    ``{self._name: parameters}`` dict returned by ``get_parameters()`` has the
    structure:

    ..code-block:: python

        [{prefix1_name: prefix1_value, ..., prefixN_name: prefixN_value},
         {col1_name: col1row1_value, ..., colN_name: colNrow1_value},
         ...,
         {col1_name: col1rowN_value, ..., colN_name: colNrowN_value},
         {suffix1_name: suffix1_value, ..., suffixN_name: suffixN_value}]

    Parameters
    ----------
    name : string
        The name of the widget, stored on self._name
    *args/**kwargs : various
        args and kwargs to be passed to ``PyQt5.QtWidgets.QWidget``.
    title : str
        The title to give the widget.
    label_header : str
        The header to use for the label column in the table.
    geometry : tuple
        The location and size of the widget given as a tuple with the values:
        ``(left, top, width, height)``.
    '''

    # A list of dicts mapping column names to default values, each dict is a
    # new row.
    default_rows = []

    def __init__(self, name, *args, delegate=MTableItemDelegate,
                 title='Default Title', label_header='label',
                 geometry=(100, 100, 800, 300), mainLayoutString=None,
                 **kwargs):
        super().__init__(*args, **kwargs)

        self._name = name
        self.title = title
        self.label_header = label_header
        self.geometry = geometry
        self.mainLayoutString = mainLayoutString
        self.setAutoFillBackground(True)
        # if a child class has not defined the editor maps define them.
        if not hasattr(self, 'editor_map'):
            self.editor_map = {}
        if not hasattr(self, 'suffix_editor_map'):
            self.suffix_editor_map = {}
        if not hasattr(self, 'prefix_editor_map'):
            self.prefix_editor_map = {}
        self._initUI(delegate)

    def _initUI(self, delegate):

        # set the title, location and size of the Widget
        self.setWindowTitle(self.title)
        self.setGeometry(*self.geometry)
        self.mainLayout = QVBoxLayout()

        # create a QLabel which describes the table
        if not self.mainLayoutString:
            self.mainLayoutString = (f'')

        self.mainLabel = QLabel(self.mainLayoutString)
        self.mainLayout.addWidget(self.mainLabel)

        # if any global parameters are specifed in prefix_editor_map add them
        if self.prefix_editor_map:
            self.prefixLayout = QHBoxLayout()
            for name, editor in self.prefix_editor_map.items():
                setattr(self, name, editor(name, parent=self.parent()))
                widget = getattr(self, name)
                self.prefixLayout.addLayout(vstacked_label(name, widget))
            self.mainLayout.addLayout(self.prefixLayout)

        # create the table view
        self.tableView = MTableInterfaceView(self, self._name+'_view',
                                             delegate=delegate)
        self.mainLayout.addWidget(self.tableView)

        # enable sorting of the table
        self.tableView.setSortingEnabled(True)

        # load the default_entries and resize the table columns
        self.set_default(self.default_rows)

        # if any global parameters are specifed in suffix_editor_map add them
        if self.suffix_editor_map:
            self.suffixLayout = QHBoxLayout()
            for name, editor in self.suffix_editor_map.items():
                setattr(self, name, editor(name, parent=self.parent()))
                widget = getattr(self, name)
                self.suffixLayout.addLayout(vstacked_label(name, widget))
            self.mainLayout.addLayout(self.suffixLayout)

        # create and add buttons
        self.btnLayout = QHBoxLayout()

        self.addRowBtn = QPushButton('+', self)
        self.addRowBtn.setToolTip('inserts a blank row(s) after the selected'
                                  'row(s)')
        self.addRowBtn.clicked.connect(self._addRow)
        self.btnLayout.addWidget(self.addRowBtn)

        self.delRowBtn = QPushButton('-', self)
        self.delRowBtn.setToolTip('deletes the selected row(s)')
        self.delRowBtn.clicked.connect(self._delRow)
        self.btnLayout.addWidget(self.delRowBtn)

        self.upRowBtn = QPushButton('up', self)
        self.upRowBtn.setToolTip('move currently selected row down')
        self.upRowBtn.clicked.connect(self._upRow)
        self.btnLayout.addWidget(self.upRowBtn)

        self.downRowBtn = QPushButton('down', self)
        self.downRowBtn.setToolTip('move currently selected row down')
        self.downRowBtn.clicked.connect(self._downRow)
        self.btnLayout.addWidget(self.downRowBtn)

        self.duplicateRowBtn = QPushButton('duplicate', self)
        self.duplicateRowBtn.setToolTip('inserts a duplicate of the selected '
                                        'row(s)')
        self.duplicateRowBtn.clicked.connect(self._duplicateRow)
        self.btnLayout.addWidget(self.duplicateRowBtn)

        # create the layout and add the widgets
        self.mainLayout.addLayout(self.btnLayout)
        self.setLayout(self.mainLayout)

    def get_parameters(self):
        '''Return the entire data from the table.

        Returns the entire table data as a list of dicts, with each dict being
        a row that maps the column header to it's value. This follows the
        ``mily.widget`` API.

        '''
        parameters = []
        prefix_dict = {}
        for key in self.prefix_editor_map.keys():
            widget = getattr(self, key)
            prefix_dict.update(widget.get_parameters())
        if prefix_dict:  # If there are any prefix items
            parameters.append(prefix_dict)

        view_list = self.tableView.get_parameters()[self.tableView._name]
        parameters.extend(view_list)

        suffix_dict = {}
        for key in self.suffix_editor_map.keys():
            widget = getattr(self, key)
            suffix_dict.update(widget.get_parameters())
        if suffix_dict:  # If there are any suffix items
            parameters.append(suffix_dict)

        return {self._name: parameters}

    def set_default(self, parameters):
        '''Sets the default values from 'parameters' to the model.

        Sets the data from 'parameters' to the model, overwriting any existing
        data in the model. This follows the ``mily.widget`` API.

        Parameters
        ----------
        parameters : [dicts]
            List of dicts with each dict being a row that maps the column
            header to it's value.
        '''

        # if parameters is None set it to an empty list.
        if not parameters:
            parameters = []
        else:
            # extract and set prefix parameters
            if self.prefix_editor_map:
                prefix_parameters = parameters.pop(0)
                for parameter, value in prefix_parameters.items():
                    editor = getattr(self, parameter)
                    editor.set_default(value)

            # extract and set suffix parameters
            if self.suffix_editor_map:
                suffix_parameters = parameters.pop(-1)
                for parameter, value in suffix_parameters.items():
                    editor = getattr(self, parameter)
                    editor.set_default(value)

        # ask self.tableView to set other parameters
        self.tableView.set_default(parameters)

    def extract_prefix_data(self):
        '''Returns the data from the prefix widgets.

        Returns a dictionary mapping the prefix parameter names to their
        values.
        '''
        parameters = {}
        for parameter in self.prefix_editor_map.keys():
            editor = getattr(self, parameter)
            parameters.update(editor.get_parameter())

        return parameters

    def extract_suffix_data(self):
        '''Returns the data from the suffix widgets.

        Returns a dictionary mapping the suffix parameter names to their
        values.
        '''
        parameters = {}
        for parameter in self.suffix_editor_map.keys():
            editor = getattr(self, parameter)
            parameters.update(editor.get_parameter())

        return parameters

    def extract_row_data(self, row):
        '''Returns the data associated with the row defined by 'row'.

        Returns the data associated with row as a dictionary mapping column
        name to value, and any prefix or suffix data based on the value of the
        kwargs prefix and suffix.

        Parameters
        ----------
        row : int
            The row number who's data should be extracted.
        Returns
        -------
        parameters  : dict
            A dictionary mapping kwargs to values.
        '''
        column_names = list(self.editor_map.keys())
        model = self.tableView.model()
        parameters = {}
        # step through each column but the first one
        for column in range(0, model.columnCount()):
            item = model.item(row, column)
            parameters[column_names[column]] = item.data(Qt.DisplayRole)

        return parameters

    def _addRow(self):
        '''inserts an empty row after the (last) currently selected row(s)'''

        indices = self.tableView.selectionModel().selectedIndexes()
        rows = [index.row() for index in indices]
        rows.sort(reverse=True)
        if rows:  # add an empty row after the last selected row
            self.tableView.model().insertRow(rows[0]+1, [])
        else:  # If no rows selected add row at end of table
            end_row = self.tableView.model().rowCount()
            self.tableView.model().insertRow(end_row, [])

    def _delRow(self):
        '''deletes the selected row(s)'''
        indices = self.tableView.selectionModel().selectedIndexes()
        rows = [index.row() for index in indices]
        rows.sort(reverse=True)
        if self._check_rows(rows):
            for row in rows:
                self.tableView.model().takeRow(row)

    def _upRow(self):
        '''Moves the currently selected row(s) up one.'''
        indices = self.tableView.selectionModel().selectedIndexes()
        rows = [index.row()
                for index in indices
                if index.row() != 0]
        rows.sort()
        if self._check_rows(rows):
            for row in rows:
                items = self.tableView.model().takeRow(row)
                self.tableView.model().insertRow(row-1, items)

    def _downRow(self):
        '''Moves the currently selected row(s) down one.'''
        last_row = self.tableView.model().rowCount()-1
        indices = self.tableView.selectionModel().selectedIndexes()
        rows = [index.row()
                for index in indices
                if index.row() != last_row]
        rows.sort(reverse=True)
        if self._check_rows(rows):
            for row in rows:
                items = self.tableView.model().takeRow(row)
                self.tableView.model().insertRow(row+1, items)

    def _duplicateRow(self):
        '''duplicates the selected row(s) into the table after the row(s)'''

        # find the selected row(s)
        indices = self.tableView.selectionModel().selectedIndexes()
        rows = [index.row() for index in indices]
        rows.sort(reverse=True)

        if self._check_rows(rows):
            model = self.tableView.model()
            for row in rows:
                row_data = []
                for column in range(0, model.columnCount()):
                    value = model.item(row, column).data(Qt.DisplayRole)
                    item = QStandardItem()
                    item.setData(value, Qt.DisplayRole)
                    row_data.append(item)
                model.insertRow(row+1, row_data)

    def _check_rows(self, rows, only_one=False):
        '''Checks how many items are in ``rows`` and alerts user if not right.

        Checks that the number of indices in ``rows``, alerts the user with a
        popup box if their are no items in ``rows``. Alternatively if the kwarg
        ``only_one`` is ``True`` also alerts users that to many rows are
        selected. Returns ``True`` if the right number(s) of items are in
        ``rows`` otherwise it returns ``False``.

        Parameters
        ----------
        rows : [row indices]
            A list of row indices to be checked.
        only_one : Bool, optional
            A boolean that indicates if more than one row is allowed, default
            is ``False``.
        Returns
        -------
        Ok : Bool
            A boolean to indicate if the number of items in row is Ok.

        '''
        Ok = True

        if not rows:  # if no cell is selected
            Ok = False
            warning = QMessageBox()
            warning.setIcon(QMessageBox.Information)
            warning.setWindowTitle('Row(s) must be selected')
            warning.setText('Action not performed as no row is selected')
            warning.setDetailedText('This warning generally occurs '
                                    'because no row is selected, select a row'
                                    ' and try again')
            warning.setStandardButtons(QMessageBox.Ok)
            warning.exec_()

        elif len(rows) > 1 and only_one:
            Ok = False
            warning = QMessageBox()
            warning.setIcon(QMessageBox.Information)
            warning.setWindowTitle('More than one row is selected')
            warning.setText('Action not performed as more than one row is '
                            'selected')
            warning.setDetailedText('This warning generally occurs '
                                    'because there are more than one row '
                                    'selected, unselect some rows and try '
                                    'again')
            warning.setStandardButtons(QMessageBox.Ok)
            warning.exec_()

        return Ok


class MFunctionTableInterfaceWidget(MTableInterfaceWidget):
    '''Extends the MTableInterfaceWidget by adding an associated function.

    Extends the MTableInterfaceWidget by associating the table with a kwarg
    only function, where each kwarg for the function maps to a table column, a
    prefix parameter or a suffix parameter. It also adds the extra buttons:
        export: exports the selected row by calling ``self.function(...)`` with
            the kwargs from the selected row and any prefix or suffix values.
            Does not work with multiple rows selected.

    Parameters
    ----------
    function : func
        The function asociated with this table input.
    name : string
        The name of the widget, stored on self._name, passed to the parent
        ``mily.MTableInterfaceWidget``.
    *args/**kwargs : various
        args and kwargs to be passed to the parent
        ``mily.MTableInterfaceWidget``.
    title : str
        The title to give the widget, passed to the parent
        ``mily.MTableInterfaceWidget``..
    label_header : str
        The header to use for the label column in the table, passed to the
        parent ``mily.MTableInterfaceWidget``.
    geometry : tuple
        The location and size of the widget given as a tuple with the values:
        ``(left, top, width, height)``, passed to the parent
        ``mily.MTableInterfaceWidget``.
    '''

    def __init__(self, function, *args, **kwargs):
        self.function = function
        super().__init__(*args, **kwargs)

        self.executeBtn = QPushButton('execute', self)
        self.executeBtn.setToolTip('executes the "function" with "kwargs" '
                                   'from the selected row')
        self.executeBtn.clicked.connect(self.execute)
        self.btnLayout.addWidget(self.executeBtn)

    def execute(self):
        '''Executes the function for the selected row'''

        indices = self.tableView.selectionModel().selectedIndexes()
        rows = [index.row() for index in indices]

        if self._check_rows(rows, only_one=True):
            row = rows[0]
            parameters = {}
            # add the prefix parameter data (if any)
            parameters.update(self.extract_prefix_data())
            # add tableView parameters
            parameters.update(self.extract_row_data(row))
            # add the suffix parameter data (if any)
            parameters.update(self.extract_suffix_data())

            self.function(**parameters)
