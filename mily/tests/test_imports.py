import pytest


@pytest.mark.parametrize("widget", [
    "MTableItemDelegate", "MTableInterfaceView", "MTableInterfaceWidget",
    "MFunctionTableInterfaceWidget",
    "MText", "MISpin", "MFSpin", "MComboBox", "MCheckBox", "MSelector", "MDateTime",
    "MetaDataEntry", "vstacked_label", "hstacked_label",
])
def test_import_widgets(widget):
    code = f"from mily.widgets import {widget}"
    exec(code)


@pytest.mark.parametrize("widget", [
    "create_qApp",
])
def test_import_core(widget):
    code = f"from mily.core import {widget}"
    exec(code)


@pytest.mark.parametrize("widget", [
    "raise_to_operator",
])
def test_import_utils(widget):
    code = f"from mily.utils import {widget}"
    exec(code)
