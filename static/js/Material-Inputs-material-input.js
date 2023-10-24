$(function(){
    $(".md-input").on("focus", function(){
        var t = $(this);
        if(!t.parent().hasClass("focus")) {
            t.parent().addClass("focus");
        }
    });
    $(".md-input").on("blur", function(){
        var t = $(this);
        if (t.val() === "") {
            t.parent().removeClass("focus");
        }
    });
    $(".md-input[required]").on("blur", function(){
        var t = $(this);
        var v = t.val() === "";
        if (v) {
            t.parent().addClass("has-error");
        } else {
            t.parent().removeClass("has-error");  
        }
    });
})