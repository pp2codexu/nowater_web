#coding: utf-8
import web

from utils.basedb import NovelDB

class BaseHandler(object):
    
    def __init__(self):
        self.ctx = web.ctx
        self.ip = web.ctx['env'].get("HTTP_X_FORWARDED_FOR", "127.0.0.1")
        self.db = NovelDB()
