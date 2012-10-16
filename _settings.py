#coding: utf-8
import os

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = os.path.join(PROJECT_PATH.replace("nowater_web", "nowater"), "novels")

INDEX_PATH = os.path.join(PROJECT_PATH, "templates", "changeable", "recommends.html")
LOG_PATH = os.path.join(PROJECT_PATH, "log")


DATABASE_ARGS = {
    "dbn": "postgres",
    "host": "127.0.0.1",
    "port": "5432",
    "database": "piglei_nowater",
    "user": "piglei_nowater",
    "password": "zhulei@wf",
    
    "pooling": False,
    
    # DBUtils
#    "mincached" : 1,
#    "maxcached": 4,
##    "maxshared": 4,
#    "maxconnections": 16,
#    "blocking": False,
#    "setsession": ""
}

MEMCACHE_HOST = ["unix:/home/piglei/memcached.sock"]

# admin
USERNAME = "piglei"
PASSWORD = "zhulei"

TIME_ZONE = "Asia/Shanghai"

API_URL = "http://127.0.0.1:9000/"
