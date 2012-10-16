#coding: utf-8
import web
import datetime

from basehandler import BaseHandler
from utils.basedb import NovelDB
from utils.baseutils import render_to_response
from utils.baseutils import get_novel_html_path
from utils.baseutils import start_work
from utils.basetxt import get_txt_file
from lib.paginator import Paginator

class CheckAll(BaseHandler):
    """
    查看所有小说
    """
    PERPAGE = 20
    
    def GET(self):
        db = NovelDB()
        page = web.input(page=1).page
        
        pager, toshows = db.get_novels_by_page(page, self.PERPAGE, all=False)
        return render_to_response("checkall", {
            "pager": pager,
            "toshows": toshows
        })        

class Novel(BaseHandler):
    """
    查看某个小说
    """
    
    def GET(self, id):
        db = NovelDB()
        novel = db.get_novel_info(id, cache=False)
        if novel is None or novel.status in (0, 100):
            raise web.notfound()
        db.incr_view_count(id)
        # 获得推荐小说
        rd_recommends = db.get_random_recommend(id=id)
        
        page = web.input(page=1).page
        page_count = db.get_novel_pageinfo(id)
        pager = Paginator(page_count, 1, page)
        try:
            novel_html = open(get_novel_html_path(id, pager.page), "r")
        except:
            return "内容还没准备好，稍等一会哦:)"

        # 访问twisted更新
        temp_date = novel.last_update_time.replace(tzinfo=None)
        if not pager.has_next() and novel.status not in (1,3) and (datetime.datetime.now() - temp_date).seconds > 3600:
            start_work(id)
            novel = db.get_novel_info(id, cache=False)
        novel.tag = db.get_tags_by_id(id)
        novel.view_count = db.get_view_count(id)
        
        return render_to_response("show_novel", {
            "novel_id": id,
            "novel": novel,
            "novel_html": novel_html,
            "pager": pager,
            "rd_recommends": rd_recommends,
        })
    
class NovelInfo(BaseHandler):
    """
    查看某个小说的信息，包含标题作者之类
    """
    
    def GET(self, id):
        db = NovelDB()
        novel = db.get_novel_info(id)
        db.incr_view_count(id)
        return render_to_response("novel_info", {
            "novel": novel
        })

class GetTxt(BaseHandler):
    """
    txt下载
    """
    
    def GET(self, id):
        db = NovelDB()
        novel = db.get_novel_info(id)        
        file = get_txt_file(str(id), web.utf8(novel.title))
        
        if file:
            web.replace_header("Content-Type", "text/plaintext")
            web.replace_header("Content-Disposition", "attachment; filename=%s.txt" % id)
            web.header("X-Accel-Redirect", "/download_txt/%s" % file)
            return "ok"
        else:
            return "出错了，请联系piglei2007@gmail.com"
