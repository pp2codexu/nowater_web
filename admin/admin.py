#coding: utf-8
import web
from web import form

from basehandler import BaseHandler
from utils.baseutils import render_to_response
from utils.baseutils import authenticate_admin
from utils.baseutils import get_type_by_url
from constants import NOVEL_CONTENT_TYPES_ITEMS
from settings import INDEX_PATH

class Index(BaseHandler):
    
    def GET(self):
        return render_to_response("admin/base")


novel_form = form.Form( 
    form.Textbox("title", form.notnull, description="标题"),
    form.Textbox("tag", description="标签"),
    form.Textbox("author", form.notnull, description="作者"), 
    form.Textbox("url", form.notnull, description="帖子地址"), 
    form.Dropdown("content_type", NOVEL_CONTENT_TYPES_ITEMS, form.notnull, description="内容类型"),
    form.Textbox("update_interval", description="更新间隔（分钟）", value=10),
    form.Textbox("email", description="推荐人"),
) 

class AddNovel(BaseHandler):
    """
    添加小说
    """
    
    def GET(self):
        form = novel_form()
        args = web.input(_method="get", rid=None)
        if args.rid:
            info = self.db.get_recommend_info(args.rid)
            info.update(update_interval=10)
            form.fill(info)
        return render_to_response("admin/add_novel", {
            "form": form,
        })
    
    def POST(self):
        form = novel_form() 
        if not form.validates(web.input(_method="POST")): 
            return render_to_response("admin/add_novel", {
                "form": form,
            })
        else:
            args = web.input(_method="post", rid=None)
            next = "/tuoshui_admin/checkall"
            if args.rid:
                next = "/tuoshui_admin/checkall_recommends"
            del args.rid
            # 获得type
            args.type = get_type_by_url(args.url)
            if not args.type:
                return "type_error"
            ret = self.db.add_novel(args)
            if ret[0] is True:
                rid = web.input(_method="get", rid=None).rid
                # 修改推荐小说的状态
                if rid:
                    self.db.update_recommend_status(rid)
                raise web.seeother(next)
            else:
                return ret
            
class EditNovel(BaseHandler):
    """
    修改小说
    """
    
    def GET(self):
        id = web.input(id=None).id
        if id.isdigit():
            novel_info = self.db.get_novel_info(id, cache=False)
            novel_info.update(tag=";".join(self.db.get_tags_by_id(id)))
            form = novel_form()
            form.fill(novel_info)
        return render_to_response("admin/edit_novel", {
            "form": form, 
            "id": id
        })
        
    def POST(self):
        form = novel_form() 
        if not form.validates(): 
            return render_to_response("admin/edit_novel", {
                "form": form,
            })
        else:
            args = web.input()
            ret = self.db.edit_novel(args.id, args)
            if ret is True:
                raise web.seeother("/tuoshui_admin/checkall")
            else:
                return "修改失败" + ret

class CheckAll(BaseHandler):
    """
    查看所有小说
    """
    PERPAGE = 20

    def GET(self):
        page = web.input(page=1).page
        
        pager, toshows = self.db.get_novels_by_page(page, self.PERPAGE, all=True, cache=False)
        return render_to_response("admin/checkall", {
            "pager": pager,
            "toshows": toshows
        })
        
class CheckAllRecommends(BaseHandler):
    """
    查看所有推荐
    """
    PERPAGE = 20
    
    def GET(self):
        page = web.input(page=1).page
        
        pager, toshows = self.db.get_recommends_by_page(page, self.PERPAGE)
        return render_to_response("admin/checkall_recommends", {
            "pager": pager,
            "toshows": toshows
        })
        
class ChangeStatus(BaseHandler):
    """
    改变那状态
    """
    
    def GET(self):
        args = web.input(status=None, id=None)
        if args.id and args.status:
            self.db.change_status(args.id, args.status)
        return '''<script type="text/javascript">window.location.href=document.referrer;</script>'''
    
class ManageIndex(BaseHandler):
    """
    修改首页
    """
    def GET(self):
        return render_to_response("admin/manage_index", {
            "content": open(INDEX_PATH, "r").read()
        })
        
    def POST(self):
        content = web.input(content="").content.encode("utf-8")
        open(INDEX_PATH, "w").write(content)
        raise web.seeother("")
        
class Login(BaseHandler):
    """
    登录
    """
    
    def GET(self):
        return render_to_response("admin/login")
    
    def POST(self):
        args = web.input(username="", password="")
        if authenticate_admin(args.username, args.password):
            web.config._session.logged_in = True
            raise web.seeother("/tuoshui_admin/")
        raise web.seeother("/tuoshui_admin/login")
    
class Logout(BaseHandler):
    """
    注销
    """
    
    def GET(self):
        web.config._session.logged_in = False
        raise web.seeother("/")
