#coding: utf-8

urls = (
    "/", "index.Index",
    "/checkall", "show.CheckAll",
    "/novel/(\d+)", "show.Novel",
    "/novel/(\d+)/getxt", "show.GetTxt",
    "/novel_info/(\d+)", "show.NovelInfo",
    "/novel/search", "search.Search",
    
    "/recommend_novel", "ajax_front.Recommend",
    "/get_thread_info", "ajax_front.GetThreadInfo",
    "/direct_add", "ajax_front.DirectAdd",
    "/get_top", "ajax_front.GetTop",
    "/images/hs\.jpg", "wuliao.RandomPic"
)