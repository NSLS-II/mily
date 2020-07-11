import logging
from bluesky import RunEngine
from bluesky.utils import RunEngineInterrupted, install_qt_kicker
from qtpy.QtWidgets import QVBoxLayout, QLabel, QWidget, QButtonGroup, QPushButton, QDialogButtonBox
from qtpy.QtCore import Signal, Slot
from . import threads
from bluesky import RunEngine, Msg
from qtpy.QtCore import QObject, Signal
from bluesky.preprocessors import subs_wrapper

logger = logging.getLogger(__name__)

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

    def __init__(self, runengine=None, **kwargs):
        super(QRunEngine, self).__init__()

        self.RE = runengine or RunEngine(context_managers=[], **kwargs)
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

    @property
    def state_hook(self):
        return self.RE.state_hook

    @state_hook.setter
    def state_hook(self, callable):
        self.RE.state_hook = callable

    def __getattr__(self, item):
        return getattr(self.RE, item)

# FIXME: Subscribe application-wide logging like this...
#RE.sigDocumentYield.connect(partial(msg.logMessage, level=msg.DEBUG))


def no_plan_warning(*args, **kwargs):
    """
    Convienence function to raise a user warning
    """
    logger.critical("Attempting to use the RunEngine "
                    "without configuring a plan")


class EngineLabel(QLabel):
    """
    QLabel to display the RunEngine Status

    Attributes
    ----------
    color_map : dict
        Mapping of Engine states to color displays
    """
    color_map = {'running': 'green',
                 'paused': 'yellow',
                 'idle': 'red'}

    @Slot('QString', 'QString')
    def on_state_change(self, state, old_state):
        """Update the display Engine"""
        # Update the label
        self.setText(state.capitalize())
        # Update the background color
        color = self.color_map[state]
        self.setStyleSheet('QLabel {background-color: %s}' % color)


class EngineControl(QDialogButtonBox):
    """
    RunEngine through a QComboBox

    Listens to the state of the RunEngine and shows the available commands for
    the current state.

    Attributes
    ----------

    available_commands: dict
        Mapping of state to available RunEngine commands
    """
    available_commands = {'running': ['Halt', 'Pause'],
                          'idle': ['Start'],
                          'paused': ['Abort', 'Halt',  'Resume', 'Stop']}

    command_flags = {'Halt': QDialogButtonBox.DestructiveRole,
                     'Pause': QDialogButtonBox.HelpRole,
                     'Start': QDialogButtonBox.AcceptRole,
                     'Abort': QDialogButtonBox.RejectRole,
                     'Resume': QDialogButtonBox.AcceptRole,
                     'Stop': QDialogButtonBox.ResetRole}

    def __init__(self, *args, **kwargs):
        super(EngineControl, self).__init__(*args, **kwargs)
        self.buttonGroup = QButtonGroup()
        self._buttons = {name: QPushButton(name) for command in self.available_commands.values() for name in command}
        for name, button in self._buttons.items():
            self.addButton(button, self.command_flags[name])
            self.buttonGroup.addButton(button)

    @Slot('QString', 'QString')
    def on_state_change(self, state, old_state):
        for name, button in self._buttons.items():
            button.setEnabled(name in self.available_commands[state])


class EngineWidget(QWidget):
    """
    RunEngine Control Widget

    Parameters
    ----------
    engine : RunEngine, optional
        The underlying RunEngine object. A basic version wil be instatiated if
        one is not provided

    plan : callable, optional
        A callable  that takes no parameters and returns a generator. If the
        plan is meant to be called repeatedly the function should make sure
        that a refreshed generator is returned each time

    Attributes
    ----------
    engine_state_change : Signal('QString', 'QString')
        Signal emitted by changes in the RunEngine state. The first string is
        the current state, the second is the previous state

    update_rate: float
        Update rate the qt_kicker is installed at

    command_registry: dict
        Mapping of commands received by the Slot `command` and actual
        Python callables
    """
    engine_state_change = Signal('QString', 'QString')
    update_rate = 0.02
    command_registry = {'Halt': RunEngine.halt,
                        'Start': no_plan_warning,
                        'Abort': RunEngine.abort,
                        'Resume': RunEngine.resume,
                        'Pause': RunEngine.request_pause,
                        'Stop': RunEngine.stop}

    def __init__(self, engine=None, plan=None, parent=None):
        # Instantiate widget information and layout
        super().__init__(parent=parent)

        self.setStyleSheet('QLabel {qproperty-alignment: AlignCenter}')
        self.label = EngineLabel(parent=self)
        self.status_label = QLabel('Engine Status')
        self.control = EngineControl()
        lay = QVBoxLayout()
        lay.addWidget(self.status_label)
        lay.addWidget(self.label)
        lay.addWidget(self.control)
        self.setLayout(lay)
        self._plan = None

        # Accept either RunEngine or QRunengine for engine
        if isinstance(engine, RunEngine):
            engine = QRunEngine(runengine=engine)

        # Create a new RunEngine if we were not provided one
        self._engine = None
        self.engine = engine or QRunEngine()


    @property
    def plan(self):
        """
        Stored plan callable
        """
        return self._plan

    @plan.setter
    def plan(self, plan):
        logger.debug("Storing a new plan for the RunEngine")
        # Do not allow plans to be set while RunEngine is active
        if self.engine and self.engine.state != 'idle':
            logger.exception("Can not change the configured plan while the "
                             "RunEngine is running!")
            return
        # Store our plan internally
        self._plan = plan
        # Register a new call command
        self.command_registry['Start'] = (lambda engine: engine(self.plan()))

    @property
    def engine(self):
        """
        Underlying RunEngine object
        """
        return self._engine

    @engine.setter
    def engine(self, engine):
        logger.debug("Storing a new RunEngine object")
        # Do not allow engine to be swapped while RunEngine is active
        if self._engine and self._engine.state != 'idle':
            raise RuntimeError("Can not change the RunEngine while the "
                               "RunEngine is running!")
        # Create a kicker, not worried about doing this multiple times as this
        # is checked by `install_qt_kicker` itself
        install_qt_kicker(update_rate=self.update_rate)
        engine.state_hook = self.on_state_change
        # Connect signals
        self._engine = engine
        self.engine_state_change.connect(self.label.on_state_change)
        self.engine_state_change.connect(self.control.on_state_change)
        self.control.clicked.connect(self.command)
        # Run callbacks manually to initialize widgets. We can not emit the
        # signal specifically because we can not emit signals in __init__
        state = self._engine.state
        self.label.on_state_change(state, None)
        self.control.on_state_change(state, None)

    def on_state_change(self, state, old_state):
        """
        Report a state change of the RunEngine

        This is added directly to the `RunEngine.state_hook` and emits the
        `engine_state_change` signal.

        Parameters
        ----------
        state: str

        old_state: str

        """
        self.engine_state_change.emit(state, old_state)

    def command(self, command_button):
        """
        Accepts commands and instructs the RunEngine accordingly

        Parameters
        ----------
        command : str
            Name of the command in the :attr:`.command_registry:`
        """
        command = command_button.text()

        logger.info("Requested command %s for RunEngine", command)
        # Load thefunction from registry
        try:
            func = self.command_registry[command]
        except KeyError as exc:
            logger.exception('Unrecognized command for RunEngine -> %s',
                             exc)
            return
        # Execute our loaded function
        try:
            func(self.engine)
        # Pausing raises an exception
        except RunEngineInterrupted as exc:
            logger.debug("RunEngine paused")
