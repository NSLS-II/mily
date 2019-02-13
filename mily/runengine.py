from bluesky import RunEngine, Msg
from qtpy import QtCore
import threading
import asyncio

from qtpy import QtCore


class Teleporter(QtCore.QObject):
    name_doc = QtCore.Signal(str, dict)


def _get_asyncio_queue(loop):
    class AsyncioQueue(asyncio.Queue):
        '''
        Asyncio queue modified for caproto server layer queue API compatibility

        NOTE: This is bound to a single event loop for compatibility with
        synchronous requests.
        '''
        def __init__(self, *, loop=loop, **kwargs):
            super().__init__(loop=loop, **kwargs)

        async def async_get(self):
            return await super().get()

        async def async_put(self, value):
            return await super().put(value)

        def get(self):
            future = asyncio.run_coroutine_threadsafe(self.async_get(), loop)
            return future.result()

        def put(self, value):
            future = asyncio.run_coroutine_threadsafe(
                self.async_put(value), loop)
            return future.result()

    return AsyncioQueue


def spawn_RE(*, loop=None, **kwargs):
    RE = RunEngine(context_managers=[], **kwargs)
    queue = _get_asyncio_queue(RE.loop)()
    t = Teleporter()

    async def get_next_message(msg):
        return await queue.async_get()

    RE.register_command('next_plan', get_next_message)

    def forever_plan():
        while True:
            plan = yield Msg('next_plan')
            try:
                yield from plan
            except GeneratorExit:
                raise
            except Exception as ex:
                print(f'things went sideways \n{ex}')

    def thread_task():
        RE(forever_plan())

    thread = threading.Thread(target=thread_task, daemon=True,
                              name='RE')
    thread.start()

    RE.subscribe(t.name_doc.emit)

    return RE, queue, thread, t
