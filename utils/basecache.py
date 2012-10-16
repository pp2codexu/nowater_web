#coding: utf-8
import time
import memcache
import hashlib
import pickle

from settings import MEMCACHE_HOST
from utils.baseutils import smart_str

class BaseCache(object):
    """
    简单的memcache包装类
    """
    
    def __init__(self):
        self.default_timeout = 300
        self._cache = memcache.Client(MEMCACHE_HOST)
        
    def get(self, key, default=None):
        val = self._cache.get(smart_str(key))
        if val is None:
            return default
        return val
    
    def _get_memcache_timeout(self, timeout):
         """
         Memcached deals with long (> 30 days) timeouts in a special
         way. Call this function to obtain a safe value for your timeout.
         """
         timeout = timeout or self.default_timeout
         if timeout > 2592000: # 60*60*24*30, 30 days
             timeout += int(time.time())
         return timeout  
    
    def set(self, key, value, timeout=0):
        self._cache.set(smart_str(key), value, self._get_memcache_timeout(timeout))

    def incr(self, key, delta=1):
        self._cache.incr(smart_str(key), delta)

    def delete(self, key):
        self._cache.delete(smart_str(key))
        
    def close(self, **kwargs):
        self._cache.disconnect_all()

bc = BaseCache()

class CacheController(object):

    def clear_cache(self, func, *args, **kwargs):
        key = self.get_hash_key(func, args, kwargs)
        bc.delete(key)

    def get_hash_key(self, func, *args, **kwargs):
        """获得hash值作为key"""
        func_name = func if isinstance(func, basestring) else func.__name__
        args = (func_name, args, kwargs)
        return self._get_hash_key(*args)

    @staticmethod
    def _get_hash_key(*args):
        return hashlib.md5(pickle.dumps(args)).hexdigest()

cc = CacheController()

# 缓存数据库的装饰器
def cache_db(timeout=60):
    def p(func):
        def decorated(*args, **kwargs):
            # 判断cahche_control参数cache
            cache = kwargs.pop("cache", True)
            if not cache:
                return func(*args, **kwargs)
            # 去除basedb object
            _args = args[1:]
            cache_key = cc.get_hash_key(func, *_args, **kwargs)
            ret = bc.get(cache_key)
            if ret is None:
                ret = func(*args, **kwargs)
                if isinstance(ret , (tuple, list)):
                    ret = list(ret) if isinstance(ret, tuple) else ret
                    for i, r in enumerate(ret):
                        if hasattr(r, "__class__") and str(r.__class__) == "web.utils.IterBetter":
                            ret[i] = tuple(r)
                else:
                    if hasattr(ret, "__class__") and str(ret.__class__) == "web.utils.IterBetter":
                        ret = tuple(ret)
                bc.set(cache_key, ret, timeout=timeout)
            return ret
        return decorated
    return p

