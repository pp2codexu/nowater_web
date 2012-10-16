#coding: utf-8
import web

from basehandler import BaseHandler
from utils.basedb import NovelDB
from utils.baseutils import render_to_response

class Search(BaseHandler):
    """
    小说搜索
    """
    PERPAGE = 20
    
    def GET(self):
        args = web.input(keyword="", page=1)
        args.keyword = args.keyword.strip()
        if not args.keyword.strip():
            raise web.seeother(self.env.get("HTTP_REFERER", "/"))
        db = NovelDB()
        pager, toshows = db.search(args.keyword, args.page, self.PERPAGE)
        return render_to_response("search", {
            "keyword": args.keyword,
            "toshows": toshows,
            "pager": pager
        })
