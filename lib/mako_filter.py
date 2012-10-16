#coding: utf-8
import sys
if "." not in sys.path: sys.path.append(".")

import re
import urllib
import datetime
from BeautifulSoup import BeautifulSoup

from constants import NOVEL_STATUS, NOVEL_CONTENT_TYPES, TYPE_TO_ICON
from utils.baseutils import smart_unicode, smart_str

TAG_RE = re.compile(ur"<[^>]+>|\s|&nbsp;")

def strip_tag(content):
    """
    忽略标签
    """
    return TAG_RE.sub("", content)

def url_quote(value):
    return smart_unicode(urllib.quote(smart_str(value)))

def get_novel_url(id):
    return "/novel/%s" % id

def get_novel_txt_url(id):
    return "/novel/%s/getxt" % id

def get_status_display(status):
    return u"<span class='nowstatus_%s'>%s</span>" % (status, NOVEL_STATUS[int(status)])

def trans_content_type(content_type):
    try: content_type = int(content_type)
    except: pass
    return smart_unicode(NOVEL_CONTENT_TYPES.get(content_type, "其他"))

def get_type_icon(type):
    """
    根据小说来源类型返回小图标
    """
    return TYPE_TO_ICON[type]

def get_novel_edit_url(id):
    return "/tuoshui_admin/edit_novel?id=%s" % id

def time_since(dt):
    """
    返回多久前
    """
    now = datetime.datetime.now()
    dt = dt.replace(tzinfo=None)
    delta = now - dt
    if delta.days >= 0:
        if delta.days >= 365:
            return u"%s年前" % (delta.days/365)
        if delta.days >= 30:
            return u"%s个月前" % (delta.days/30)
        if delta.days > 0:
            return u"%s天前" % delta.days
        if delta.seconds >= 3600:
            return u"%s个小时前" % (delta.seconds/3600)
        if delta.seconds >= 60:
            return u"%s分钟前" % (delta.seconds/60)
        return u"%s秒前" % delta.seconds
    return dt.strftime("%Y/%m/%d %H:%M")

def convert_tags(tags):
    """
    格式化tags
    """
    return u" ".join([(u"<a href='/novel/search?keyword=%s'>%s</a>" % (x, x)) for x in tags])


def img_lazyload(data):
    """
    把图片变成lazy_load的形式
    """
    if '<img ' not in data and '<IMG ' not in data:
        return data

    soup = BeautifulSoup(data)
    for img in soup.findAll("img"):
        del img["class"]
        src = img.get("src", "")
        del img["src"]
        img["data-original"] = src
        img["src"] = "/static/images/grey.gif"
        img["class"] = "lazy"
      
        img.insert(0, '<noscript><img src="%s"></noscript>' % src)
    return unicode(soup)

if __name__ == '__main__':
    data = '''                                    可以和楼主一起发 但绝对不可以 涉黄    <img class="BDE_Smiley" src="http://static.tieba.baidu.com/tb/editor/images/tsj/t_0028.gif" width="40" height="40" /><br />'''
    print img_lazyload(data)

