from typeing import Generator, Tuple, Iterable, Dict, Any
from qtpy import QtWidgets

from bluesky import Msg


class Settable:
    # stand in for a settable from ohpyd
    ...


class OphydObj:
    ...


class ScanInputWidget(QtWidgets.QtWidget):
    def get_plan(self) -> Generator[Msg]:
        ...


class MotorRangeSelector(QtWidgets.QtWidget):
    def get_args(self) -> Tuple[Settable, float, float, int]:
        ...


class DetectorSelector(QtWidget.QtWidget):
    def get_detectors(self) -> Tuple[OphydObj, ...]:
        ...


class MetadataSource:
    def get_metadata(self) -> Dict[str, Any]:
        ...
