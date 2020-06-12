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
    configHtml = makeTableFromJson(configJson);
    $('#' + table_container_id ).html(configHtml);
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

function makeTableFromJson(jsonData, containerId) {
    var textContent = '';
    function crateTrTd(jsonData) {
        if (jQuery.type(jsonData) == "array") {
            for (var i = 0; i < jsonData.length; i++) {
                textContent = textContent + '<tr row-id="'+ String(i) +'">';
                crateTrTd(jsonData[i]);
                textContent = textContent + '</tr>';
            }
        } else if (jQuery.type(jsonData) == "object") {
            for (var key in jsonData) {
                textContent = textContent + '<td column-id="'+ key +'" td_attr="key"><div class="font-weight-bold" contenteditable="false">'+ key +'</div></td>';
                textContent = textContent + '<td column-id="'+ key +'" td_attr="value">';
                crateTrTd(jsonData[key]);
                textContent = textContent + '</td>';
            }
        } else {
            textContent = textContent + '<div contenteditable="true">'+ jsonData +'</div>';
        }
    }

    crateTrTd(jsonData);
    textContent = '<tbody id="table_body">' + textContent + '</tbody>';
    textContent = '<table class="json_table table table-bordered table-striped table-hover table-sm" id="json_table"' + textContent + '</table>';
    
    return jQuery.parseHTML(textContent);
}

