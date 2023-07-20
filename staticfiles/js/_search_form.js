// función filtrar registros
var handleSubmitSearch = function() {
    var qs = $('#id_rpp, #id_search').serialize();
    $(location).attr('href', '?' + qs);
    return false;
};

function getUrlVars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
        vars[key] = value;
    });
    return vars;
}

$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();
    var search_send = getUrlVars()["q"];
    var rpp_send = getUrlVars()["rpp"];
    if (rpp_send == null) {
        rpp_send = 10;
    }
    $('#id_search').val(search_send);
    $('#id_rpp').val(rpp_send);
});
