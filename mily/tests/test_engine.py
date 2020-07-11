import pytest
from bluesky.plan_stubs import pause, open_run, close_run, sleep
import time
from qtpy import QtWidgets
from qtpy.QtCore import QTimer

from mily.runengine import EngineWidget

# Fixtures borrowed from pytest-qt
@pytest.fixture(scope="session")
def qapp_args():
    """
    Fixture that provides QApplication arguments to use.

    You can override this fixture to pass different arguments to
    ``QApplication``:

    .. code-block:: python

       @pytest.fixture(scope='session')
       def qapp_args():
           return ['--arg']
    """
    return []

@pytest.yield_fixture(scope="session")
def qapp(qapp_args):
    """
    Fixture that instantiates the QApplication instance that will be used by
    the tests.

    You can use the ``qapp`` fixture in tests which require a ``QApplication``
    to run, but where you don't need full ``qtbot`` functionality.
    """
    app = QtWidgets.QApplication.instance()
    if app is None:
        global _qapp_instance
        _qapp_instance = QtWidgets.QApplication(qapp_args)
        yield _qapp_instance
    else:
        yield app  # pragma: no cover


def plan():
    yield from open_run()
    yield from sleep(1)
    yield from pause()
    yield from close_run()


def test_engine_state_changes():
    ew = EngineWidget()

    def scripted_test():
        assert ew.label.text() == 'Idle'
        assert len(ew.control.buttons()) == len(ew.control.available_commands['idle'])
        ew.on_state_change('running', 'idle')
        assert ew.label.text() == 'Running'
        assert len(ew.control.buttons()) == len(ew.control.available_commands['running'])
        ew.on_state_change('paused', 'running')
        assert ew.label.text() == 'Paused'
        assert len(ew.control.buttons()) == len(ew.control.available_commands['paused'])
        qapp.exit()

    script_timer = QTimer.singleShot(1, scripted_test)


def test_engine_plan_execution(qapp):
    # Create a widget and load plans
    ew = EngineWidget()
    ew.show()
    ew.plan = lambda: plan()

    def scripted_test():
        ew.control.clicked.emit(ew.control._buttons['Start'])
        assert ew.engine.state == 'paused'
        ew.control.clicked.emit(ew.control._buttons['Resume'])
        assert ew.engine.state == 'idle'
        qapp.exit()

    script_timer = QTimer.singleShot(1, scripted_test)

def test_engine_gui(qapp):
    ew = EngineWidget()
    ew.plan=plan
    ew.show()