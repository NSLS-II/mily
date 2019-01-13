import aiohttp_jinja2


async def index(request):
    return aiohttp_jinja2.render_template('index.jinja2',
                                          request,
                                          request.app['context'])


async def submit(request):
    print(request)
    data = await request.post()
    print(f'asked for {data}')
    plan_key = data['plan_key']
    queue = request.app['guts']['queue']
    plan_map = request.app['context']['plan_map']
    plan = plan_map[plan_key]
    queue.put(plan['func'](*plan['args'], **plan['kwargs']))
    return aiohttp_jinja2.render_template('index.jinja2',
                                          request,
                                          request.app['context'])
