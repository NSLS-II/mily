from aiohttp import web
import asyncio
from routes import setup_routes
import aiohttp_jinja2
import jinja2

from bluesky.callbacks.best_effort import BestEffortCallback
from mily.runengine import spawn_RE

import bluesky.plans as bp
from ophyd.sim import hw
hw = hw()
hw.rand.kind = 'hinted'
hw.det1.kind = 'hinted'
plan_map = {}

plan_map['ct'] = {'func': bp.count,
                  'args': ([hw.rand],),
                  'kwargs': {'num': 5}}
plan_map['ascan'] = {'func': bp.scan,
                     'args': ([hw.det1],
                              hw.motor, -5, 5, 15),
                     'kwargs': {}}


RE, queue, theard = spawn_RE(md={'location': 'server'})
bec = BestEffortCallback()
bec.disable_plots()
RE.subscribe(bec)

app = web.Application()
app['context'] = {'plan_map': plan_map}
app['guts'] = {'queue': queue,
               'RE': RE}
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


setup_routes(app)
aiohttp_jinja2.setup(
    app, loader=jinja2.PackageLoader('mily.server', 'templates'))

web.run_app(app, host='0.0.0.0', port=8080)
