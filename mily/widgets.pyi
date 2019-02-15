from typing import Generator, Tuple, Iterable, Dict, Any

from bluesky import Msg


class Settable:
    # stand in for a settable from ohpyd
    ...


class OphydObj:
    ...


class ScanInputWidget:
    def get_plan(self) -> Generator[Msg]:
        ...


class MotorRangeSelector:
    def get_args(self) -> Tuple[Settable, float, float, int]:
        ...


class DetectorSelector:
    def get_detectors(self) -> Tuple[OphydObj, ...]:
        ...


class MetadataSource:
    def get_metadata(self) -> Dict[str, Any]:
        ...
