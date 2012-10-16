#coding: utf-8
import web

from basehandler import BaseHandler
from utils.baseutils import render_to_response
from utils.basedb import NovelDB
from lib.info_backend import get_real_url

class Index(BaseHandler):
    
    def GET(self):
        # 处理source
        source = web.input(source="").source
        if source:
            source = get_real_url(source)
            novel = self.db.get_novel_byurl(source)
            if novel:
                raise web.seeother("/novel/%s" % novel.id)
        tags = self.db.get_index_tags()
        return render_to_response("index", {
            "tags": tags,
            "source": source,
        })
