var cookie_value = $.cookie('viewed_history');
var d = new Date();
var client_id = $.cookie('webpy_session_id') || (d.getTime() + Math.floor(Math.random()*10000));
var RETRY_COUNT = 10;
var AJAX_ICON = '<img src="/static/images/ajax-loader2.gif">';

function parse_cookie(value) {
    //接受字符串，返回数组
    var recents = value.split("$$");
    var result = [];
    for (var i=0; i < recents.length; i++) {
        result[i] = recents[i].split("||");
    }
    return result;
}

function make_cookie(list_value){
    var ret = [];
    for (var j=0; j < list_value.length; j++){
        ret.push(list_value[j].join("||"));
    }
    return ret.join("$$");
}

function get_viewed_history(){
    if (cookie_value == null) {
        $('#viewed_history').html("无历史记录");
        return;
    }
    var novels_list = parse_cookie(cookie_value);
    _html = ''
    for (var i=0; i < novels_list.length; i++){
        novel = novels_list[i];
        _html += '<li><a title="' + novel[2] + '(第' + novel[1] + '页)' + '" href="/novel/'+ novel[0] +'?page='+ novel[1] +'" >' + novel[2] + '</a></li>'
    }
    $('#right_novel_history').html(_html);
}

$(function(){
    var animate_flag = false;

    $('#right_float').hover(
        function(){
            animate_flag = true;
            $(this).animate({width: '120px'}, function(){
                $(this).find('#viewed_history').fadeIn();
                animate_flag = false;
            });
        },
        function(){
            if (animate_flag) return;
            $(this).find('#viewed_history').hide();
            $(this).animate({width: '12px'}, function(){
                $(this).find('#viewed_history').hide();
            });
        }
    );
})

function get_baidu_info(){
    url = $('input:text[name="url"]').val();
    if (!/^(http:\/\/tieba.baidu.com\/|http:\/\/www.tianya.cn\/|http:\/\/www.douban.com\/)/.test(url))
    {
        $('#error_info').text("格式不符合规范");
        $('#recommend_btn').removeAttr('disabled');
        return
    }
    $('#recommend_btn').hide().after(" <span id='form_status'>" + AJAX_ICON + " 获取信息中...</span>");            
    
    $.ajax({
        type: "POST",
        url: "/get_thread_info",
        dataType: 'json',
        timeout: 20000,
        data: {"url": url},
        success: function(data){
            if (data.status == 'ok') {
                $('#other_info').show();
                $('input:text[name="author"]').val(data.username);
                $('input:text[name="title"]').val(data.title);
                $('input:text[name="url"]').val(data.url);
                $('input:text[name="url"]').attr('readonly', 'true')
                // 增加默认标签
                $('input:text[name="tag"]').val(data.tag);
                $('#error_info').text("")
                $('#cancel_recommend').show();
            }  else if (data.status == 'existed') {
                $('#error_info').text("正在跳转...");
                window.location.href = data.msg;
            }
            else {
                $('#error_info').text(data.msg);
                $('#recommend_btn').show();
            }
        },
        error: function(data){
            $('#error_info').text("获取失败，请重新尝试");
            $('#recommend_btn').show();
        },
        complete: function(x, t){
            $('#form_status').remove();
        }
    });
    
}

function post_novel(){
    $("#post_novel_btn").attr("disabled", "true");
    $("span.progress").html(AJAX_ICON + " 正在发送请求...");
    $.ajax({
        type: "POST",
        url: "/direct_add",
        dataType: 'json',
        timeout: 20000,
        data: $('form[name="recommend"]').serializeArray(),
        success: function(data){
        if (data.status == 'ok') {
            $("span.progress").html(AJAX_ICON + " 正在为您准备第一页内容，请稍候...");
            var temp_func = function(){
                $.get("/api/progress", {"id": data.id, "client_id": client_id}, function(ret){
                    ret = ret.split(",");
                    for (var i=0;i<ret.length;i++) {
                        if (ret[i] != 'start' && ret[i] != 'r_1') {
                            window.location.href = "/novel/" + data.id;
                            return
                        }
                    }
                    return temp_func();
                });
            };
            temp_func();
        } else {
            alert(data.msg);
            $("#post_novel_btn").removeAttr("disabled");
            $("span.progress").html("");
        }                
        },
        error: function(data){
            alert("发生了错误，请重新尝试");
            $("#post_novel_btn").removeAttr("disabled");
            $("span.progress").html("");
        }
    });
}

function cancel_recommend(){
    $('#cancel_recommend').hide();
    $('#other_info').hide().find('input:text').val('');
    $('#recommend_btn').removeAttr('disabled').show();
    $('input:text[name="url"]').removeAttr('readonly').val('');
    $('#error_info').text("");
}

/* 获得抓取进度，只在状态为正在更新时调用 */
function get_progress(id){
    $.ajax({
        type: "GET",
        url: "/api/progress",
        cache: false,
        timeout: 600000,
        data: {"id": id, "client_id": client_id},
        success: function(data){
            if (data == 'not found') {
                $('#novel_progress').html("抓取并没有开始");
                return;
            }
            else {
                var data_list = data.split(",");
                for (var i=0;i<data_list.length;i++) {
                    var j = data_list[i];
                    if (j == 'end') {
                        $('#novel_progress').html("本次抓取已完成").delay(2000).fadeOut();
                        $('#txt_link span').hide().parent().find('a').show();
                        return;
                    } else {
                        var temp = j.split("_");
                        if ( temp[0] == 'r' ) {
                            $('#novel_progress').html(AJAX_ICON + " 已获取原帖第<span>" + temp[1] + "</span>页内容...");
                        } else if ( temp[0] == 'o' ) {
                            append_page(temp[1]);
                        }
                    }
                };
                // 继续请求
                return get_progress(id);
            };
        },
        error: function(xhr, error){
            if (xhr.status != 0 && RETRY_COUNT >  0) {
                RETRY_COUNT -= 1;
                return get_progress(id);
            }
        }
    });
}

// 追加页数
function append_page(page) {
    page = parseInt(page);
    if (page <= MAX_PAGE) {
	if(CURRENT_PAGE == page && CURRENT_PAGE != 1) {
		alert("当前页有新内容，请刷新查看!");
	}
	return;
    };
    if (HAS_NEXT_PAGE) {
        $('span.page_numbers').after('<a class="page_number" href="?page=' + (CURRENT_PAGE + 1) + '">下一页</a>');
        HAS_NEXT_PAGE = false;
    };
    $('span.page_numbers').append('<a class="page_number" href="?page=' + page + '">' + page + '</a> ');
}
