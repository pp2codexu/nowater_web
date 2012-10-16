#coding: utf-8
import sys
import web

from utils import baseutils
from utils.baserender import render
from utils.baseauth import auth_admin

APPS = ("novel", "admin")

web.config.debug = False
web.replace_header = baseutils.replace_header
    
# 设置时区
baseutils.switch_time_zone()

urls = baseutils.import_modules(APPS)
app = web.application(urls, globals(), autoreload=False)
session = web.session.Session(app, web.session.DiskStore('sessions'))
web.config._session = session

def notfound():
    return web.notfound(render.notfound())

app.notfound = notfound
app.add_processor(web.loadhook(auth_admin))
app.add_processor(web.unloadhook(baseutils.assert_closed))

if __name__ == '__main__':
    if len(sys.argv) == 1:
        app.run()
    elif sys.argv[1] == 'deploy':
#    if "deploy" in sys.argv:
        from flup.server.fcgi import WSGIServer
        func = app.wsgifunc()
        server_address = '/tmp/nowater_novel.sock'
        WSGIServer(
            func,
            bindAddress=server_address,
            maxSpare=16,
            minSpare=16,
#            maxRequests=128,
#            maxChildren=32
        ).run()
else:
    application = app.wsgifunc()
