#coding: utf-8
import re
import sys
import web
import traceback
from web.db import sqlquote

from settings import DATABASE_ARGS
from settings import TIME_ZONE
from lib.paginator import Paginator
from utils.basecache import cache_db
from utils.basecache import cc
from utils.basecache import bc

database = web.database(**DATABASE_ARGS)

class NovelDB(object):
    
    BASIC_FILTER = "status not in (0, 100)"
    
    def __init__(self):
        pass
    
    @property
    def db(self):
        if not hasattr(self, "_db"):
            self._db = database
            self._db.query('SET TIME ZONE "%s"' % TIME_ZONE)
        return self._db
    
    def add_novel(self, args):
        """
        添加新的小说
        """
        try:
            print >>sys.stderr, 1
            last_id = self.db.query("select nextval('nowater_novel_id_seq')")[0].nextval
            print >>sys.stderr, "last_id_before", last_id, args
            print >>sys.stderr, 2
            print args
            
            tags = args.pop("tag", "")
            self.db.insert("nowater_novel",
                id=last_id,
                status = 0,
                last_update_url = args.url,
                **args
            )
#            last_id = self.db.query("select lastval()")[0].lastval
#            last_id = self.db.query("select currval('nowater_novel_id_seq')")[0].currval
            print >>sys.stderr, "last_id", last_id
            # 插入次数统计
            self.db.insert("view_count", id=last_id)
            self.db.insert("page_info", id=last_id)
            self.db.insert("profile", id=last_id)
            self.create_or_update_tags(last_id, tags)
            return True, last_id
        except Exception, e:
            print >>sys.stderr, traceback.format_exc()
            return str(e)
        
    def create_or_update_tags(self, id, tags):
        """
        修改或者创建标签，做法是先删除，然后添加
        """
        self.db.query("DELETE FROM tags where id = %s" % id)
        # tags
        tags = set([ x.strip() for x in re.split(ur";|；", tags) if x.strip() and len(x.strip()) <= 20])
        for tag in tags:
            self.db.insert("tags", id=id, tag=tag)
        
    def edit_novel(self, id, args):
        """
        修改小说
        """
        args.pop("id", None)
        tags = args.pop("tag", "")
        try:
            self.db.update("nowater_novel", "id=$id", vars={"id": id}, **args)
            self.create_or_update_tags(id, tags)
        except Exception, e:
            return str(e)
        return True
        
    def change_status(self, id, status):
        """
        改变状态
        """
        self.db.update("nowater_novel", "id=$id", vars={"id": id}, status=status)
        return True
    
    def count_novels(self, where=None):
        """
        统计小说个数
        """
        sql = "select count(*) from nowater_novel %s" % ("where %s" % where if where else "")
        ret = self.db.query(sql)[0].count
        return ret
    
    def count_recommends(self):
        """
        查看推荐小说
        """
        sql = "select count(*) from recommend_novel"
        ret = self.db.query(sql)[0].count
        return ret
    
    def count_search(self, keyword):
        """
        统计搜索结果个数
        """
        sql = '''select count(*) from nowater_novel
        where ( title like %s 
        or id in (
            select distinct id from tags
            where tag = %s
        ))
        and %s'''
        ret = self.db.query(sql % (
            sqlquote("%" + keyword + "%"),
            sqlquote(keyword),
            self.BASIC_FILTER))[0].count
        return ret
    
    @cache_db(60*5)
    def get_view_count(self, novel_id):
        """
        根据id获得浏览数
        """
        ret = self.db.select("view_count", {"id": novel_id}, what="view", where="id=$id", limit=1)[0].view
        return ret
    
    @cache_db(60)
    def get_tags_by_id(self, id):
        """
        根据获得某小说的标签
        """
        return [x["tag"] for x in self.db.select("tags", {"id": id}, what="tag", where="id=$id")]
    
    @cache_db(60)
    def get_summary_by_id(self, id):
        """
        根据id获得小说摘要
        """
        return self.db.select("profile", {"id": id}, what="summary", where="id=$id", limit=1)[0].summary
    
    def incr_view_count(self, novel_id):
        """
        增加浏览数
        """
        self.db.query("UPDATE view_count set view = view+1 where id = $id", dict(id=novel_id))

        cache_key = cc.get_hash_key("get_view_count", novel_id)
        bc.incr(cache_key, 1)
        return True
    
    @cache_db(60)
    def check_availble(self, novel_id):
        """
        检查小说是否可用
        """
        ret = self.db.select("nowater_novel", {"id": novel_id}, where="id=$id and %s" % self.BASIC_FILTER, limit=1)
        if list(ret):
            return True
        return False
        
    @cache_db(60)
    def get_novel_info(self, novel_id):
        """
        获得小说信息
        """
        ret = self.db.select("nowater_novel", {"id": novel_id}, where="id=$id", limit=1)
        if not ret:
            return None
        ret = ret[0]
        ret.view = self.get_view_count(novel_id)
        return ret
    
    def get_recommend_info(self, rid):
        """
        获得推荐小说信息
        """
        ret = self.db.select("recommend_novel", {"id": rid}, what="title,content_type,tag,author,email,url", where="id=$id", limit=1)[0]
        return ret
    
    def update_recommend_status(self, rid):
        """
        修改推荐小说状态
        """
        self.db.update("recommend_novel", "id=$id", vars={"id": rid}, status=True )
    
    def get_novel_byurl(self, url):
        """
        根据url查询小说是否存在
        """
        ret = self.db.select("nowater_novel", {"url": url}, where="url=$url and %s" % self.BASIC_FILTER, limit=1)
        if ret:
            return ret[0]
        return None
        
    def get_novel_pageinfo(self, novel_id):
        """
        获得小说分页信息
        """
        info = self.db.select("page_info", {"id": novel_id}, where="id=$id", limit=1)[0]
        page = info["page"]
        # 特殊情况
        if info["word_count"] == 0 and page == 2:
            page = 1
        return page
    
    def list_novels(self, offset=0, limit=20, order="jointime desc", where=None, args={}, all=False):
        """
        返回小说
        """
        ret = self.db.query('''
        select * from (
            select * from nowater_novel
                %(where)s
                order by %(order)s
                limit %(limit)s offset %(offset)s
            ) as t1
            left join view_count as t2
            using(id)
            left join profile as t3
            using(id)
        ''' % {
            "where": "where %s" % where if where else "",
            "order": order,
            "limit": limit,
            "offset": offset
        })
        return ret
#        return self.db.select("nowater_novel", args, where=where,order=order, limit=limit, offset=offset)
    
    def list_recommends(self, offset=0, limit=20, order="jointime desc"):
        """
        返回小说
        """
        return self.db.select("recommend_novel", order=order, limit=limit, offset=offset)
    
    @cache_db(60)
    def get_novels_by_page(self, page, perpage, order="jointime desc", all=False):
        """
        按照页数返回小说：
            返回一个pager和小说的列表
        """
        # 判断是否筛选
        where = None if all else self.BASIC_FILTER        
        novel_count = self.count_novels(where=where)
        pager = Paginator(novel_count, perpage, page)
        
        _offset = (pager.page - 1) * perpage
        toshows = self.list_novels(order=order, where=where, offset=_offset, limit=perpage)
        toshows = self.add_tags(toshows)
        return pager, toshows
    
    def add_tags(self, toshows):
        """
        给传入的小说加上标签
        """
        # 查询每一个tag
        toshows = tuple(toshows)
        for toshow in toshows:
            toshow.tag = self.get_tags_by_id(toshow.id)
        return toshows
    
    def get_recommends_by_page(self, page, perpage, order="jointime desc", where="", args={}):
        """
        按照页数返回推荐信息：
            返回一个pager和推荐的列表
        """
        recommends_count = self.count_recommends()
        pager = Paginator(recommends_count, perpage, page)
        
        _offset = (pager.page - 1) * perpage
        toshows = self.list_recommends(offset=_offset, limit=perpage, order=order)
        return pager, toshows    
        
    @cache_db(10)
    def get_view_top(self, limit=15):
        """
        获得热度最高的top
        """
        ret = self.db.query('''
        select * from view_count as t1
        left join
            nowater_novel as t2
        using(id)
        where t2.%(basic_filter)s
        order by t1.view desc limit %(limit)s      
        ''' % dict(basic_filter=self.BASIC_FILTER, limit=limit))
        return ret
    
    @cache_db(10)
    def get_latest_top(self, limit=15):
        """
        获得最新的top
        """
        return self.db.select("nowater_novel", where=self.BASIC_FILTER, order="id desc", limit=limit)
    
    @cache_db(60)
    def get_random_recommend(self, id=None, limit=15):
        """
        随机推荐15部小说
        """
        relates = []
        # 如果该小说有标签，根据标签查询类似的小说
        if id and self.get_tags_by_id(id):
            relates_sql = '''select * from nowater_novel where id in (
                            select id from tags where tag in (
                                select tag from tags where id=$id
                            )
                        ) and id != $id and %s limit $limit''' % self.BASIC_FILTER
            relates = list(self.db.query(relates_sql, {"id": id, "limit": 10}))
        random_novels = list(self.db.select("nowater_novel", where=self.BASIC_FILTER, order="random()", limit=(limit-len(relates))))
        relates.extend(random_novels)
        return relates
    
    def add_recommend(self, args):
        """
        添加推荐小说
        """
        try:
            self.db.insert("recommend_novel", **args)
            return True
        except:
            return False
        
    def get_search_result(self, keyword, limit=20, offset=0):
        """
        查询出搜索结果
        """
        sql = '''
        select * from (
            select * from nowater_novel
            where ( title like %s 
            or id in (
                select distinct id from tags
                where tag = %s
            ))
            and %s
            order by jointime desc
            limit %s offset %s
        ) as t1
        left join view_count as t2
        using(id)
        left join profile as t3
        using(id)      
        '''
        return self.db.query(sql % (
            sqlquote("%" + keyword + "%"),
            sqlquote(keyword),
            self.BASIC_FILTER,
            limit,
            offset))
        
    def search(self, keyword, page, perpage):
        """
        按照页数返回小说：
            返回一个pager和小说的列表
        """
        novel_count = self.count_search(keyword)
        pager = Paginator(novel_count, perpage, page)
        
        _offset = (pager.page - 1) * perpage
        toshows = self.get_search_result(keyword, offset=_offset, limit=perpage)
        toshows = self.add_tags(toshows)
        return pager, toshows        
    
    @cache_db(60)
    def get_index_tags(self):
        """
        获得首页的tags
        """
        return self.db.query("select tag,count(*) as count from tags group by tag order by count desc,tag limit 100")
