#coding: utf-8
import web

def auth_admin():
    """
    判断管理员是否登录
    """
    path = web.ctx.path
    if path.startswith("/tuoshui_admin/") \
            and not path == "/tuoshui_admin/login" \
            and not web.config._session.get("logged_in", False):
        raise web.seeother("/tuoshui_admin/login")