from .utils import create_qApp  # noqa: F401
from .table_interface import (  # noqa: F401
    MTableItemDelegate, MTableInterfaceView, MTableInterfaceWidget,
    MFunctionTableInterfaceWidget)

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
