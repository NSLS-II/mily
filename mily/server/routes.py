from views import index, submit


def setup_routes(app):
    app.router.add_get('/', index)
    app.router.add_post('/submit', submit)
