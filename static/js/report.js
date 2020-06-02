var started = true;
var endPoints = ["getAgentsData", "getCallsData"];
var hostName = window.location.hostname;

function CreateTableFromJSON() {
    var int_str = document.getElementById("interval").value;
    var interval = 1000 * parseInt(int_str);
    if (started) {
        setTimeout(function(){ CreateTableFromJSON() }, interval);
    } else {
        console.log("loop stoped");
        return;
    }

    var divContainer = document.getElementById("addTables");
    divContainer.innerHTML = "";

    endPoints.forEach(function(endPoint){
        var jsonData = GetData(endPoint);
        var getHtml = createHTML(jsonData);
        var htmlContent = document.createElement("div");
        htmlContent.setAttribute("class", "row justify-content-center");
        htmlContent.appendChild(getHtml);
        divContainer.appendChild(htmlContent);
    });
    
}

function Stop() {
    started=false
}

function Start() {
    started=true
    console.log("loop started");
    CreateTableFromJSON();
}

function GetData(endPoint) {
    var Url = "http://" + hostName + ":5000/"+endPoint;
    var result = {};

    $.ajax({
        type: "GET",
        url: Url,
        dataType: "json",
        async: false,
        success: function(resp){
            result = resp;
        }
        ,
        error: function(error){
            console.log(error);
        }
    });

    return result;
}

function createHTML(jsonData) {
    var col = [];
    for (var i = 0; i < jsonData.length; i++) {
        for (var key in jsonData[i]) {
            if (col.indexOf(key) === -1) {
                col.push(key);
            }
        }
    }

    var table = document.createElement("table");
    table.setAttribute("class", "table");

    var tr = table.insertRow(-1);                   // TABLE ROW.
    tr.setAttribute("scope", "row");

    for (var i = 0; i < col.length; i++) {
        var th = document.createElement("th");      // TABLE HEADER.
        th.setAttribute("scope", "col");
        th.innerHTML = col[i];
        tr.appendChild(th);
    }

    // ADD JSON DATA TO THE TABLE AS ROWS.
    for (var i = 0; i < jsonData.length; i++) {
        tr = table.insertRow(-1);

        for (var j = 0; j < col.length; j++) {
            var tabCell = tr.insertCell(-1);
            tabCell.innerHTML = jsonData[i][col[j]];
        }
    }

    return table;
}