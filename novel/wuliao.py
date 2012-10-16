#coding: utf-8
import web
import simplejson
import random
import urllib
import urllib2
import threading

from utils.baseutils import get_logger
from basehandler import BaseHandler

KEYWORD = u"黑丝 性感"
SOURCE_URL = "http://image.baidu.com/i?tn=baiduimagejson&ct=201326592&lm=-1&cl=2&word=%s&pn=%s&rn=30"
DEFAULT_URL = "http://img.club.pchome.net/upload/club/other/2010/5/18/pics_roynliu_1274156141.jpg"
NOW_SRC = [0, {}, 0]
LOCK = threading.Lock()

log = get_logger("hs", "hs.log")

class RandomPic(BaseHandler):
    
    def GET(self):
        global NOW_SRC
        offset, data, index = NOW_SRC
        if index > len(data) or not data:
            offset = random.randint(1, 1900)
            data = self._get_data(offset)
            NOW_SRC = [ offset, data, 0]
        
        log.info(self.ip)
        
        item = data[index%len(data)]
        url = item.get("objURL", DEFAULT_URL)
        NOW_SRC[2] += 1
        raise web.seeother(url)
    
    def _get_data(self, offset):
        """
        get json
        """
        url = SOURCE_URL % (urllib.quote(KEYWORD.encode("gbk")), offset)        
        try:
            source = urllib2.urlopen(url).read().decode("gbk").encode("utf-8")
            source = simplejson.loads(source)
            source = source['data']
        except Exception, e:
            raise web.seeother(DEFAULT_URL)
        print len(source)
        return source
