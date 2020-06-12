var hostName = window.location.hostname;
var tableJson = {};

$(document).ready(function () {
    getConfig();
    jsonEditorInit('table_container', 'Textarea1', 'result_container', 'json_to_table_btn', 'table_to_json_btn');
});

function getConfig(){
    var Url = "http://" + hostName + ":5000/appConfig";

    $.ajax({
        type: "GET",
        url: Url,
        dataType: "json",
        async: false,
        success: function(resp){
            tableJson = resp;
        },
        error: function(error){
            console.log(error);
        }
    });
}

function setConfig(){
    var Url = "http://" + hostName + ":5000/appConfig";

    $.ajax({
        type: "POST",
        url: Url,
        dataType: "json",
        data: tableJson,
        error: function(error){
            console.log(error);
        }
    });
}