#coding: utf-8
#import sys
#sys.path.append("../../nowater_web")

import re
import urllib2
import urlparse
import traceback
from BeautifulSoup import BeautifulSoup

from utils.baseutils import get_type_by_url
from constants import COMMON_TAGS

TECH_RE = re.compile(r'/1/\d+\.s?html$')
DIGIT_RE = re.compile(r'^\d+')
DOUBAN_PEOPLE = re.compile(r"http://www.douban.com/people/[^/]+/$")
GROUP_RE = re.compile(ur"^回(.*)小组$")
DOUBAN_TITLE = re.compile(ur"<strong>标题：</strong>([^<]*)")
BAIDU_AUTHOR_RE = re.compile(r'author:"(.*?)"')

def reconnecting_urlopen(*args, **kwargs):
    """
    会重复尝试的urlopen，默认尝试5次
    """
    retry_count = kwargs.setdefault("retry", 5)
    try:
        _kwargs = kwargs.copy()
        _kwargs.pop("retry")
        content = urllib2.urlopen(*args, **_kwargs).read()
        return content
    except Exception, e:
        if retry_count:
            kwargs["retry"] -= 1
            return reconnecting_urlopen(*args, **kwargs)
        else:
            raise e
        
def get_baidu_info(url):
    """
    获得百度贴子信息
    """
    content = reconnecting_urlopen(url).decode("gbk", "ignore")
    soup = BeautifulSoup(content)
    tags = ["百度贴吧",]
    try:
#        username = soup.find("div", {"class": "post"}).find("td").get("username")
        username = BAIDU_AUTHOR_RE.search(content).group(1)
        _title = soup.find("title").renderContents()
        title = _title.rsplit("_", 2)[0]
        # 增加返回默认标签,去掉一个“吧”字
        tag = _title.rsplit("_", 2)[1][:-3]
        tags.append(tag)
    except Exception, e:
        print traceback.format_exc()
        username = None
        title = None
    return [username, title, url, tags]

def get_tianya_info(url):
    """
    获得天涯帖子信息
    """
    thread_type = url.split("/")[3]
    content = reconnecting_urlopen(url).decode("gbk", "ignore")
    soup = BeautifulSoup(content)
    tags = ["天涯社区",]
    try:
        # 如果用户输入的不是首页，找到主页then
        if (get_tianya_page(soup, thread_type) != 1):
            print get_tianya_page(soup, thread_type)
            if thread_type == "techforum":
                temp = url.rsplit("/", 2)
                temp[1] = "1"
                url = "/".join(temp)
            else:
                url = soup.find(text=u"首页").parent["href"]
            return get_tianya_info(url)
        
        if thread_type == "techforum":
            username = soup.find("div", {"class": "vcard"}).find("a", target="_blank").renderContents()
        else:
            username = soup.find("table", id="firstAuthor").find("a", target="_blank").renderContents()
        _title = soup.find("title").renderContents()
        title = _title.rsplit("_", 2)[0]
        # 获得子论坛名称作为标签
        tag = _title.rsplit("_", 2)[1]
        tags.append(tag)
    except Exception, e:
        print traceback.format_exc()
        username = None
        title = None
    return [username, title, url, tags]

def get_tianya_page(soup, type):
    """
    获得天涯当前页数
    """
    page = 1
    if type == "techforum":
        pagediv = soup.find("div", id="cttPageDiv")
    else:
        pagediv = soup.find("div", id="pageDivTop")
    if pagediv:
        page = int(pagediv.find("em", {"class": "current"}).renderContents())
    return page

def get_douban_info(url):
    """
    获得豆瓣信息
    """
    tags = ["豆瓣社区",]
    content = reconnecting_urlopen(url).decode("utf-8", "ignore")
    soup = BeautifulSoup(content)
    try:
        username = soup.find("div", {"class": "topic-doc"}).find("a", href=DOUBAN_PEOPLE).renderContents()

        # 豆瓣可能有标题省略的情况
        title_obj = DOUBAN_TITLE.search(content)
        if title_obj:
            title = title_obj.group(1).strip().encode("utf-8")
        else:
            title = soup.find("title").renderContents().strip()

        # 获得小组名称
        group_name = soup.find(text=GROUP_RE)
        if group_name:
            tags.append(str(group_name)[3:-6])
    except Exception, e:
        print traceback.format_exc()
        username = None
        title = None
    return [username, title, url, tags]

def get_thread_info(url):
    """
    获得小说信息，返回楼主和标题
    2011/05/08 增加返回tag
    """
    result = [None, None, url, ""]
    try:
        ntype = get_type_by_url(url)
        if ntype == 'baidu':
            result = get_baidu_info(url)
        elif ntype == 'tianya':
            result = get_tianya_info(url)
        elif ntype == 'douban':
            result = get_douban_info(url)
    except Exception, e:
        print traceback.format_exc()

    # 添加常用标签
    result = list(result)
    result[-1] = get_common_tags(result)
    return result

def get_real_url(url):
    """
    获得真实的首页
    """
    url = url.strip()
    try:
        ntype = get_type_by_url(url)
        if ntype == 'baidu':
            prefix, qs = url.split("?", 1)
            args = urlparse.parse_qs(qs)
            # http://tieba.baidu.com/p/1040351223?pn=3
#            if 'pn' in args and "tieba.baidu.com/p/" in prefix:
            if "tieba.baidu.com/p/" in prefix:
                url = prefix 
            elif 'kz' not in args:
                url = "http://tieba.baidu.com/f?kz=%s" % "".join(args["z"])
            else:
                url = "http://tieba.baidu.com/f?kz=%s" % DIGIT_RE.search("".join(args['kz'])).group()
        if ntype == 'tianya':
            if url.split("/")[3] == 'techforum':
              if not TECH_RE.search(url):
                 temp = url.split("/")
                 temp.insert(-1, "1")
                 url = "/".join(temp)
        if ntype == 'douban':
            url = url.split("?")[0]
            if not url.endswith("/"):
                url += "/"
        return url
    except Exception, e:
        return url

def get_common_tags(result):
    """
    如果标题里面含有常用的标签关键字，添加该标签
    """
    username, title, url, tags = result
    [ tags.append(tag) for tag in COMMON_TAGS if tag in title ]
    return ";".join(tags) + ";"

if __name__ == '__main__':
    print get_real_url("http://tieba.baidu.com/f?z=972692030&ct=335544320&lm=0&sc=0&rn=30&tn=baiduPostBrowser&word=dota&pn=0")
    print get_real_url("http://tieba.baidu.com/f?kz=972912940")
    print get_real_url("http://tieba.baidu.com/f?z=973967879&ct=335544320&lm=0&sc=0&rn=30&tn=baiduPostBrowser&word=dota&pn=0")

