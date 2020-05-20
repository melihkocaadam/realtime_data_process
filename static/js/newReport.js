var started = true;
var queue = [];

function startStop() {
    var button = document.getElementById("start-stop");
    var endPoint = document.getElementById("endPoint").value;

    if (button.innerText == "Start") {
        button.innerText = "Stop";
        button.className = "btn rounded btn-outline-danger";
        started = true;
        console.log("into start");
        getData(endPoint);
    } else {
        button.innerText = "Start";
        button.className = "btn rounded btn-outline-success";
        started = false;
        console.log("into stop");
    }
}

function getData(endPoint) {
    var Url = "http://35.228.71.166:5000/"+endPoint;
    var result = {};

    if (endPoint == "agentsCompact") {
        Url = Url + "/melih.kocaadam";
    }

    console.log("into getData()");
    queue.push(endPoint);

    $.ajax({
        type: "GET",
        url: Url,
        dataType: "json",
        // async: false,
        success: function(resp){
            result = resp;
            console.log(result);
            console.log(typeof result);
            createHTML(result, endPoint);
        },
        error: function(error){
            console.log(error);
        }
    });

}

function createHTML(jsonData, endPoint) {
    console.log("into createHTML()");
    var col = [];
    for (var i = 0; i < jsonData.length; i++) {
        for (var key in jsonData[i]) {
            if (col.indexOf(key) === -1) {
                col.push(key);
            }
        }
    }
    console.log(col);

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
    var divContainer = document.getElementById("addTables");
    var existChild = document.getElementById(endPoint);
    var htmlContent = document.createElement("div");
    htmlContent.setAttribute("class", "row justify-content-center");
    htmlContent.setAttribute("id", endPoint);
    htmlContent.appendChild(table);

    if (existChild != null) {
        existChild.remove();
    }

    divContainer.appendChild(htmlContent);

    if (started) {
        setTimeout(function(){ getData(endPoint) }, 100);
    }
    
}
