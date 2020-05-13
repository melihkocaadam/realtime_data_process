console.log("init js");
started=true
function CreateTableFromJSON(jsonData) {
    var int_str = document.getElementById("interval").value;
    var interval = 1000 * parseInt(int_str);
    if (started) {
        setTimeout(function(){ CreateTableFromJSON(jsonData) }, interval);
    } else {
        console.log("loop stoped");
    }

    myBooks = jsonData

    var col = [];
    for (var i = 0; i < myBooks.length; i++) {
        for (var key in myBooks[i]) {
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
    for (var i = 0; i < myBooks.length; i++) {

        tr = table.insertRow(-1);

        for (var j = 0; j < col.length; j++) {
            var tabCell = tr.insertCell(-1);
            tabCell.innerHTML = myBooks[i][col[j]];
        }
    }

    return table;
}

function Stop() {
    started=false
}
function Start() {
    started=true
    console.log("loop started");
    var callsData = GetData("getCallsData");
    var callsTable = CreateTableFromJSON(callsData);

    var agentsData = GetData("getAgentsData");
    var agentsTable = CreateTableFromJSON(agentsData);

    var divContainer = document.getElementById("addTables");
    divContainer.innerHTML = "";
    divContainer.appendChild(agentsTable);
    divContainer.appendChild(callsTable);
}
function GetData(endPointName) {
    var Url = "http://35.228.71.166:5000/"+endPointName;
    var result = {}

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

    return result
}