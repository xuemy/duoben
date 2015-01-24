/**
 * Created by xmy on 2015/1/22.
 */

var options = {path: "/", expires: 10};
var cookie_backColor = $.cookie("backColor");	//定义背景颜色值
var cookie_fontStyle = $.cookie("fontStyle");	//定义字体类别
var cookie_fontSize = $.cookie("fontSize");

function setcolor(num) {
    if (num == 1) {
        $("#content").css('background', '#fef0e1');
        $.cookie("backColor", "#fef0e1", options);
    }
    if (num == 2) {
        $("#content").css('background', '#feeaee');
        $.cookie("backColor", "#feeaee", options);
    }
    if (num == 3) {
        $("#content").css('background', '#fdecfd');
        $.cookie("backColor", "#fdecfd", options);
    }
    if (num == 4) {
        $("#content").css('background', '#e9f4fc');
        $.cookie("backColor", "#e9f4fc", options);
    }
    if (num == 5) {
        $("#content").css('background', '#f3fdec');
        $.cookie("backColor", "#f3fdec", options);
    }
}
function fontstyle(num) {
    if (num == 1) {
        $("#content p").css('font-family', '黑体');
        $.cookie("fontStyle", "黑体", options);
    }
    if (num == 2) {
        $("#content p").css('font-family', 'Microsoft Yahei');
        $.cookie("fontStyle", "Microsoft Yahei", options);
    }
    if (num == 3) {
        $("#content p").css('font-family', '楷体');
        $.cookie("fontStyle", "楷体", options);
    }
}
//字体大小方法
function fontsize(num) {
    switch (num) {
        case 1:
            $("#content p").css('font-size', '18px');
            $.cookie("fontSize", "18", options);
            break;
        case 2:
            $("#content p").css('font-size', '20px');
            $.cookie("fontSize", "20", options);
            break;
        case 3:
            $("#content p").css('font-size', '22px');
            $.cookie("fontSize", "22", options);
            break;
    }
}
//恢复默认方法
function defaultCL() {
    $("#content").css('background', '');			//清空背景颜色
    $.cookie("backColor", null, options);	//把背景颜色空值传进"backColor"这个cookie里
    $("#content p").css('font-family', '');			//清空字体颜色
    $.cookie("fontStyle", null, options);	//把字体颜色空值传进"fontStyle"这个cookie里
    $("#content p").css('font-size', '');		//清空字体大小
    $.cookie("fontSize", null, options);	//把字体大小空值传进"fontSize"这个cookie里
}

$(function () {
    if (cookie_backColor) {
        $('#content').css('background', cookie_backColor);
    }
    if (cookie_fontStyle) {
        $('#content p').css('font-family', cookie_fontStyle);
    }
    if (cookie_fontSize) {
        $('#content p').css('font-size', cookie_fontSize + 'px');
    }
});