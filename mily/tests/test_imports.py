from importlib import import_module
import pytest


@pytest.mark.parametrize("name", [
    "MTableItemDelegate", "MTableInterfaceView", "MTableInterfaceWidget",
    "MFunctionTableInterfaceWidget",
    "MText", "MISpin", "MFSpin", "MComboBox", "MCheckBox", "MSelector", "MDateTime",
    "MetaDataEntry", "vstacked_label", "hstacked_label",
])
def test_import_widgets(name):
    module_name = "mily.widgets"
    mod = import_module(module_name)
    assert hasattr(mod, name), f"Error occurred while loading '{name}' from the module '{module_name}'"


@pytest.mark.parametrize("name", [
    "create_qApp",
])
def test_import_core(name):
    module_name = "mily.core"
    mod = import_module(module_name)
    assert hasattr(mod, name), f"Error occurred while loading '{name}' from the module '{module_name}'"


@pytest.mark.parametrize("name", [
    "raise_to_operator",
])
def test_import_utils(name):
    module_name = "mily.utils"
    mod = import_module(module_name)
    assert hasattr(mod, name), f"Error occurred while loading '{name}' from the module '{module_name}'"
