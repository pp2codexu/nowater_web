#coding: utf-8
import web

from utils.basedb import NovelDB

class BaseHandler(object):
    
    def __init__(self):
        self.ctx = web.ctx
        self.env = self.ctx['env']
        self.ip = web.ctx['env'].get("HTTP_X_FORWARDED_FOR", "127.0.0.1")

    @property
    def db(self):
        if not hasattr(self, "_cache_db"):
            self._cache_db = NovelDB()
        return self._cache_db
