#coding: utf-8
import os
import re
import web
import hashlib
import urlparse
import urllib
import logging

import settings
from baserender import render

BR_RE = re.compile(r"[\s　]*<br[^>]*>", re.I)
HTML_ENTITY_RE = re.compile(r"&#[xX]?([0-9a-fA-F]+|\w{1,8});")

def replace_br(content):
    return BR_RE.sub("\n", content)

def replace_html_entity(content):
    def _(obj):
        try:
            return unichr(int(obj.group(1))).encode('utf-8')
        except:
            return " "
    return HTML_ENTITY_RE.sub(_, content)

def render_to_response(tmplname, context={}):
    return getattr(render, tmplname)(**context)

def import_modules(apps):
    """
    遍历传进来的app，组合成urls
    """
    urls = []
    for appname in apps:
        app = __import__(appname, {}, {}, ["urls"])
        flag = False
        for url in app.urls.urls:
            if flag:
                url = "%s.%s" % (appname, url)
            flag = not flag
            urls.append(url)
    return urls

def smart_str(s, encoding='utf-8'):
    """
    返回编码后的字符串
    """
    if isinstance(s, unicode):
        return s.encode(encoding)
    elif s and encoding != 'utf-8':
        return s.decode('utf-8', 'ignore').encode(encoding, 'ignore')
    else:
        return str(s)
    
def smart_unicode(s, encoding='utf-8'):
    """
    返回解码成unicode
    """
    if isinstance(s, unicode):
        return s
    return s.decode(encoding)
    
def authenticate_admin(username, password):
    """
    验证管理员
    """
    return username == settings.USERNAME and password == settings.PASSWORD

def get_novel_html_path(id, page=None):
    """
    获得小说的静态地址
    """
    id = str(id)
    hashvalue = hashlib.md5(id).hexdigest()
    if page:
        return "%s/%s/%s/%s.html" % (settings.HTML_PATH, hashvalue[:2], id, page)
    return "%s/%s/%s" % (settings.HTML_PATH, hashvalue[:2], id)

HOST_TO_TYPE = {
    "tieba.baidu.com": "baidu",
    "www.tianya.cn": "tianya",
    "www.douban.com": "douban"
}
def get_type_by_url(url):
    """
    根据url返回type
    """
    host = urlparse.urlparse(url).netloc
    return HOST_TO_TYPE.get(host)

def start_work(id):
    """
    根据id调用twisted来开始抓取工作
    """
    url = settings.API_URL + "start_work?id=" + str(id)
    try: urllib.urlopen(url)
    except: pass
    
import time

def switch_time_zone():
    """
    切换时区到settings.TIME_ZONE
    """
    os.environ["TZ"] = settings.TIME_ZONE
    time.tzset()
    
from basecache import bc

def assert_closed():
    """
    关闭memcache
    """
    bc.close()

def replace_header(hdr, value):
    """
    设置header
    """
    hdr, value = web.utf8(hdr), web.utf8(value)
    # protection against HTTP response splitting attack
    if '\n' in hdr or '\r' in hdr or '\n' in value or '\r' in value:
        raise ValueError, 'invalid characters in header'
    
    for i, temp in enumerate(web.ctx.headers):
        h, v = temp
        if h.lower() == hdr.lower():
            web.ctx.headers[i] = (hdr, value)
            break
    else:
        web.ctx.headers.append((hdr, value))
        
        
def get_logger(loggername,filename):
    """
    获得log文件
    """
    filename = os.path.join(settings.LOG_PATH, filename)
    
    log = logging.getLogger(loggername)
    hdlr = logging.FileHandler(filename,'a')
    
    fs = '%(asctime)s %(levelname)-5s %(message)s'
    fmt = logging.Formatter(fs)
    hdlr.setFormatter(fmt)
    log.addHandler(hdlr)
    log.setLevel(logging.DEBUG)
    return log
