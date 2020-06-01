var allData = [];
var realTimeSocket = io("/realTime");

realTimeSocket.on("reportData", function(data) {
    console.log("received data on socket");
    console.log(data);
    allData.push(data);
    createHTML(allData);
});


function createHTML(jsonData) {
    console.log("into createHTML function");
    // jsonData.reverse();
    var col = [];
    for (var i = 0; i < jsonData.length; i++) {
        for (var key in jsonData[i]) {
            if (col.indexOf(key) === -1) {
                col.push(key);
            }
        }
    }
    // console.log(col);

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
            if (col[j].toLowerCase() == "sequence") {
                tabCell.innerHTML = seqToTime(jsonData[i][col[j]]);
            } else {
                tabCell.innerHTML = jsonData[i][col[j]];
            }
        }
    }
    var divContainer = document.getElementById("addTables");
    var htmlContent = document.createElement("div");
    var dataTable = document.getElementById("dataTable");

    if (dataTable != undefined) {
        dataTable.remove();
    }

    htmlContent.setAttribute("class", "row justify-content-center");
    htmlContent.setAttribute("id", "dataTable");
    htmlContent.appendChild(table);

    divContainer.appendChild(htmlContent);    
}

function seqToTime(seq) {
    var date = new Date(seq);
    var hours = date.getHours();
    var minutes = "0" + date.getMinutes();
    var seconds = "0" + date.getSeconds();
    var formattedTime = hours + ':' + minutes.substr(-2) + ':' + seconds.substr(-2);

    return formattedTime;
}

// function sendMessage() {
//     var message = "sabit mesaj";
//     realTimeSocket.emit("reportData", message);
//     console.log("send data on socket");
// }