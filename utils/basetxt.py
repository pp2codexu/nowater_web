#coding: utf-8
from utils.baseutils import get_novel_html_path, replace_br, replace_html_entity, smart_str

import re
import os
import stat
import time

_path = os.path.join

FILE_NAME = "nowater.txt"

def get_txt_file(id, title):
    """
    获得小说txt，逻辑：
        首先查找目录下的nowater.txt文件，如果存在而且最后修改时间到现在不超过两个小时
        则直接返回，否则生成txt文件后返回
    """
    root = get_novel_html_path(id)
    file_path = _path(root, FILE_NAME)
    if not (os.path.exists(file_path) and (time.time() - os.path.getmtime(file_path)) < 1800):
        init_txt(id, title)
#    size = get_filesize(file_path)
    return file_path[1:]

def windows_mode(content):
    content = smart_str(content, "gbk")
    return content.replace("\n", "\r\n")

CONTENT_TOP_RE = re.compile(r'<div class="content_top">[\s\S]*?</div>')
TAG_RE = re.compile(ur"<[^>]+>|[^\S\n]")
HH_RE = re.compile(r"\n{2,}")

HEAD = '''\
========================================================================
= 该文本文件由浮云脱水小说站自动生成，更多内容请访问网址www.zhikanlz.com
= 浮云脱水小说站，每日添加、自动更新的脱水小说站
= 提供实时更新的百度、天涯、豆瓣脱水小说，提供实时脱水（只看楼主）、txt下载功能
========================================================================
标题：%s
页面地址：http://www.zhikanlz.com/novel/%s

'''

def init_txt(id, title):
    """
    初始化txt文件
    """
    root = get_novel_html_path(id)
    obj_file = open(_path(root, FILE_NAME), "w")

    files =  [x for x in os.listdir(root) if x.endswith(".html")]
    files.sort(key=lambda x:int(x.split(".")[0]))
    files = [_path(root, x) for x in files]
    
    obj_file.write( windows_mode(HEAD % (title, id)) )

    for file in files:
        content = open(file, 'r').read().replace("[设为书签]", "")

        content = CONTENT_TOP_RE.sub('', content)
        content = replace_br(content)
        content = TAG_RE.sub("", content)
        content = HH_RE.sub("\n\n", content)

        content = content.replace("&nbsp;", " ")\
            .replace("&lt;", "<")\
            .replace( "&gt;", ">")\
            .replace("&quot;", '"')\
            .replace("&amp;", "&")\
            .replace("\n", "\r\n")
        content = replace_html_entity(content)

        obj_file.write( windows_mode(content) )
    obj_file.close()

def get_filesize(file):
    return os.stat(file)[stat.ST_SIZE]


if __name__ == "__main__":
    #init_txt(3, "新西兰往事")
    print get_filesize("/tmp/fuck.log")
