from qtpy import QtWidgets
import sys
from mily.runengine import spawn_RE
from mily.widgets import (ControlGui, Count, Scan1D, MotorSelector,
                          DetectorSelector)
import bluesky.plans as bp
from ophyd.sim import hw
import matplotlib
matplotlib.interactive(True)

app = QtWidgets.QApplication.instance()
if app is None:
    app = QtWidgets.QApplication([b"mily demo"])
    app.lastWindowClosed.connect(app.quit)

hw = hw()
hw.motor.set(15)
hw.motor.delay = .1
hw.motor1.delay = .2
hw.motor2.delay = .3

hw.det.kind = 'hinted'
hw.det1.kind = 'hinted'
hw.det2.kind = 'hinted'

RE, queue, thread, teleport = spawn_RE()

cg = ControlGui(queue, teleport,
                Count('Count', bp.count,
                      DetectorSelector(detectors=[hw.det, hw.det1, hw.det2])),
                Scan1D('1D absolute scan', bp.scan,
                       MotorSelector([hw.motor, hw.motor1, hw.motor2]),
                       DetectorSelector(detectors=[hw.det, hw.det1, hw.det2])),
                Scan1D('1D relative scan', bp.rel_scan,
                       MotorSelector([hw.motor, hw.motor1, hw.motor2]),
                       DetectorSelector(detectors=[hw.det, hw.det1, hw.det2])),
                )

cg.show()
sys.exit(app.exec_())
