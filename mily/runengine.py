from . import threads
from bluesky import RunEngine, Msg
from qtpy.QtCore import QObject, Signal
from bluesky.preprocessors import subs_wrapper


# TODO: Allow queueing plans
# TODO: Application logging
# TODO: Capture state callbacks
# TODO: Add convenient gui-thread targeted callback mechanism

class QRunEngine(QObject):
    sigDocumentYield = Signal(str, dict)
    sigAbort = Signal()  # TODO: wireup me
    sigException = Signal()
    sigFinish = Signal()
    sigStart = Signal()
    sigPause = Signal()
    sigResume = Signal()

    def __init__(self, **kwargs):
        super(QRunEngine, self).__init__()

        self.RE = RunEngine(context_managers=[], **kwargs)
        self.RE.subscribe(self.sigDocumentYield.emit)

    def __call__(self, *args, **kwargs):
        if not self.isIdle:
            # TODO: run confirm callback
            self.RE.abort()
            self.RE.reset()
            self.threadfuture.wait()

        self.threadfuture = threads.QThreadFuture(self.RE, *args, **kwargs,
                                                  threadkey='RE',
                                                  showBusy=True,
                                                  finished_slot=self.sigFinish.emit)
        self.threadfuture.start()
        self.sigStart.emit()

    # state_hook

    @property
    def isIdle(self):
        return self.RE.state == 'idle'

    def abort(self, reason=''):
        if self.RE.state != 'idle':
            self.RE.abort(reason=reason)
            self.sigAbort.emit()

    def pause(self, defer=False):
        if self.RE.state != 'paused':
            self.RE.request_pause(defer)
            self.sigPause.emit()

    def resume(self, ):
        if self.RE.state == 'paused':
            self.threadfuture = threads.QThreadFuture(self.RE.resume,
                                                      threadkey='RE',
                                                      showBusy=True,
                                                      finished_slot=self.sigFinish.emit)
            self.threadfuture.start()
            self.sigResume.emit()

# FIXME: Subscribe application-wide logging like this...
#RE.sigDocumentYield.connect(partial(msg.logMessage, level=msg.DEBUG))
