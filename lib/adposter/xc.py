# coding: utf-8
import time
import random
import itertools

from baidu_poster import BaiduUser

def get_random_string():
    return "".join([random.choice(string.letters) for x in range(random.randrange(40))])

def get_content():
    r = lambda : random.random() > 0.5
    
    ret = ""
    if r(): ret += "要看"
    if r(): ret += "这个"
    ret += "帖子"
    if r(): ret += "的"
    if r(): ret += "完美"
    if r(): 
        ret += "脱水版"
    else:
        ret += "无水版"
    ret += "，" 
    if r(): ret += "可以"
    if r(): ret += "直接"
    if r(): 
        ret += "在百度"
    else:
        ret += "在谷歌"
    ret += "搜索"
    if r(): ret += "一下"
    ret += " 浮云脱水小说站 "
    if r(): ret += "就可以看到了"
    ret += "，" 
    if r(): ret += "在那里"
    ret += "可以自动脱水"
    if r(): ret += "的"
    
    return ret

if __name__ == "__main__":
    '''
    2714
    '''
    tiezis = open("posts.txt", "r")

    people = []
    USERS = (
        ("神马equal浮云9", "zhulei"),
        ("神马equal浮云8", "zhulei"),
        ("神马equal浮云7", "zhulei"),
        ("神马equal浮云6", "zhulei"),
        ("神马equal浮云5", "zhulei"),
        ("神马equal浮云4", "zhulei"),
        ("神马equal浮云2", "zhulei"),
        ("神马equal浮云3", "zhulei"),
        ("神马equal浮云1", "zhulei"),
        ("神马equals浮云", "zhulei"),
    )
    for username, password in USERS:
        username = unicode(username, "utf-8")

        u = BaiduUser(username, password)
        u.login()
        people.append(u)
    
    people = itertools.cycle(people)

    for x in tiezis:
        if x.startswith("#") or not x.strip():
            continue

        id, url = x.replace('"', '').strip().split(",")

        tuoshui_url = "http://www.zhikanlz.com/novel/%s" % id
        content = get_content()
#        content = '%(c)s<br>脱水版地址：<a href="%(url)s" target="_blank">%(url)s</a>' % {"c": content, "url": tuoshui_url}
#        content = '%(c)s<br>脱水版地址：%(url)s' % {"c": content, "url": tuoshui_url}
        print id, url, tuoshui_url
        people.next().reply(url, content)
        print
        time.sleep(random.randrange(10, 30))
