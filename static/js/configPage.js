var hostName = window.location.hostname;
var configJson;
var configHtml;
var table_container_id = "table_container";

$(document).ready(function () {
    // jsonEditorInit(table_container_id, json_input_container_id, json_output_container_id, json_to_table_btn_id, table_to_json_btn_id);
    renderTable();
});

$(function(){
    $('#apply').click(function(){
        saveJson();
    })
})

$(function(){
    $('#refresh').click(function(){
        renderTable();
    })
})

function renderTable() {
    configJson = getConfig();
    configHtml = makeTable(configJson);
    $('#' + table_container_id ).html(configHtml);
    $('.json_table').addClass('table table-bordered table-striped table-hover table-sm');
    $('.json_table thead').addClass('thead-dark');
}

function saveJson() {
    configJson = makeJson();
    setConfig(configJson);
}

function getConfig(){
    var Url = "http://" + hostName + ":5000/appConfig";
    var result;

    $.ajax({
        type: "GET",
        url: Url,
        dataType: "json",
        async: false,
        success: function(resp){
            result = resp;
        },
        error: function(error){
            console.log(error);
        }
    });

    return result;
}

function setConfig(jsonData){
    var Url = "http://" + hostName + ":5000/appConfig";

    $.ajax({
        type: "POST",
        url: Url,
        dataType: "json",
        data: jsonData,
        error: function(error){
            console.log(error);
        }
    });
}
var textContent = '';
function jsonToTable(jsonData) {
    if (jQuery.type(jsonData) == "array") {
        console.log("array");
        for (var i = 0; i < jsonData.length; i++) {
            textContent = textContent + '<tr row-id="'+ String(i) +'"';
            jsonToTable(jsonData[i]);
        }
    } else if (jQuery.type(jsonData) == "object") {
        console.log("dict");
        for (var key in jsonData) {
            console.log(key);
            textContent = textContent + '<td column-id="'+ key +'" td_attr="key"><div class="font-weight-bold" contenteditable="false">'+ key +'</div></td>';
            // htmlContent = htmlContent + jQuery.parseHTML('<td column-id="'+ key +'" td_attr="value"><div contenteditable="true">'+ jsonData[key] +'</div></td>');
            jsonToTable(jsonData[key]);
        }
    } else {
        console.log("value" + String(jsonData));
        textContent = textContent + '<td column-id="val" td_attr="value"><div contenteditable="true">'+ jsonData +'</div></td>';
    }
}