#coding: utf-8

COMMON_TAGS = (
    "图解",        
)

NOVEL_STATUS = {
    0: u"未初始化",
    1: u"更新中...",
    2: u"等待更新",
    3: u"已完结",
    4: u"更新异常",
    100: u"已删除"
}

NOVEL_CONTENT_TYPES = {
    0: "玄幻",
    1: "奇幻",
    2: "武侠",
    3: "仙侠",
    4: "都市",
    5: "情感",
    6: "历史",
    7: "军事",
    8: "游戏",
    9: "竞技",
    10: "科幻",
    11: "灵异",
    12: "同人",
    13: "其他"
}
NOVEL_CONTENT_TYPES_ITEMS = sorted(NOVEL_CONTENT_TYPES.items(), key=lambda x: x[0])

NOVEL_TYPE_ITEMS = (
    ("baidu", "baidu贴吧"),
    ("tianya", "天涯社区"),
    ("douban", "豆瓣社区")
)

TYPE_TO_ICON = {
    "baidu": u"<img src='/static/images/icons/baidu.ico' title='来自百度贴吧' alt='来自百度贴吧' class='little_icon'/>",
    "tianya": u"<img src='/static/images/icons/tianya.ico' title='来自天涯社区' alt='来自天涯社区' class='little_icon'/>",
    "douban": u"<img src='/static/images/icons/douban.ico' title='来自豆瓣社区' alt='来自豆瓣社区' class='little_icon'/>"
}

# 广告s
ADS = {
    "inline": '''\
        <script type="text/javascript"><!--
            google_ad_client = "pub-4181092568002868";
            /* 728x90, 创建于 11-2-9 */
            google_ad_slot = "6165054665";
            google_ad_width = 728;
            google_ad_height = 90;
            //-->
        </script>
        <script type="text/javascript" src="http://pagead2.googlesyndication.com/pagead/show_ads.js">
        </script>
    ''',
    
    "bottom": '''\
        <script type="text/javascript"><!--
            google_ad_client = "pub-4181092568002868";
            /* 728x90, 创建于 10-12-13 */
            google_ad_slot = "1577021502";
            google_ad_width = 728;
            google_ad_height = 90;
            //-->
        </script>
        <script type="text/javascript" src="http://pagead2.googlesyndication.com/pagead/show_ads.js"></script>
    ''',
    
    "right": '''\
        <script type="text/javascript"><!--
            google_ad_client = "pub-4181092568002868";
            /* 120x600, 创建于 10-12-18 */
            google_ad_slot = "7741187316";
            google_ad_width = 120;
            google_ad_height = 600;
            //-->
        </script>
        <script type="text/javascript" src="http://pagead2.googlesyndication.com/pagead/show_ads.js"></script>
    ''',

    "inline_2": """<script type="text/javascript"><!--
    google_ad_client = "ca-pub-4181092568002868";
    /* 内容中2 */
    google_ad_slot = "1719781835";
    google_ad_width = 728;
    google_ad_height = 90;
    //-->
    </script>
    <script type="text/javascript"
    src="http://pagead2.googlesyndication.com/pagead/show_ads.js">
    </script>"""
}
