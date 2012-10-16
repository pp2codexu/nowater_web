#coding: utf-8
import itertools

urls = [
    "/", "admin.Index",
    "/add", "admin.AddNovel",
    "/checkall", "admin.CheckAll",
    "/checkall_recommends", "admin.CheckAllRecommends",
    "/change_status", "admin.ChangeStatus",
    "/edit_novel", "admin.EditNovel",
    "/manage_index", "admin.ManageIndex",
    
    "/login", "admin.Login",
    "/logout", "admin.Logout",
]

flag = itertools.cycle((True, False))
for i, url in enumerate(urls):
    if flag.next():
        urls[i] = "/tuoshui_admin%s" % url
