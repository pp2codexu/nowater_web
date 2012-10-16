#coding: utf-8
import re
import web
import simplejson

from lib.info_backend import get_thread_info, get_real_url
from basehandler import BaseHandler
from utils.basedb import NovelDB
from utils.baseutils import render_to_response
from utils.baseutils import get_type_by_url
from utils.baseutils import start_work

class GetTop(BaseHandler):
    """
    获得首页上的top20
    接收参数type
    """
    
    def GET(self):
        args = web.input(type="view")
        db = NovelDB()
        if args.type == "view":
            return render_to_response("ajax/top_view", {"toshows": db.get_view_top()})
        elif args.type == "latest":
            return render_to_response("ajax/top_latest", {"toshows": db.get_latest_top()})
        return "ajax ready"
    
class GetThreadInfo(BaseHandler):
    """
    获得贴吧贴子信息
    """
    
    def POST(self):
        url = web.input(url="").url
        url = get_real_url(url)
        db = NovelDB()

        # baidu 有两种格式的url
        if url.startswith("http://tieba.baidu.com"):
            _id = re.search(r"\d+$", url).group()
            urls = [
                "http://tieba.baidu.com/p/%s" % _id,
                "http://tieba.baidu.com/f?kz=%s" % _id,
            ]
            _novel = max( db.get_novel_byurl(url) for url in urls )
        else:
            _novel = db.get_novel_byurl(url)

        if _novel:
            return simplejson.dumps({"status": "existed", "msg": "/novel/%s" % _novel.id})
        # 增加返回默认标签
        username, title, url, tag = get_thread_info(url)
        _novel = db.get_novel_byurl(url)
        if _novel:
            return simplejson.dumps({"status": "existed", "msg": "/novel/%s" % _novel.id})        
        if username and title:
            return simplejson.dumps({"status": "ok", "username": username, "title": title, "url": url, "tag": tag})
        return simplejson.dumps({"status": "error", "msg": "发生了错误，请检查地址的正确性"})
    
class Recommend(BaseHandler):
    """
    推荐小说
    """
    
    def POST(self):
        args = web.input()
        args.url = get_real_url(args.url)
        if not all((args.url, args.title, args.author)):
            return simplejson.dumps({"status": "error", "msg": "请填写必填项"})
        args.ip = self.ip
        db = NovelDB()
        if not db.add_recommend(args):
            return simplejson.dumps({"status": "error", "msg": "发生了错误，请检查您的输入"})
        return simplejson.dumps({"status": "ok"})
    
class DirectAdd(BaseHandler):
    """
    直接从页面，实时脱水，写起来有些蛋疼。
    """
    
    def POST(self):
        args = web.input()
        args.url = get_real_url(args.url)      
        args.type = get_type_by_url(args.url)
#        args.email = args.email or "nobody@zhikanlz.com"
        args.email = ""
        args.ip = self.ip
        db = NovelDB()
        ret = db.add_novel(args)
        if ret[0] is True:
            id = ret[1]
            start_work(id)
            return simplejson.dumps({"status": "ok", "id": id})
        else:
            return simplejson.dumps({"status": "error", "msg": "发生了错误，请稍候再试"})
        
