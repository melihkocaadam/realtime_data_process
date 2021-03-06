var hostName = window.location.hostname;
var allData = getDruidData("getAgentsData");
var pvtData = {
    options: {
        grid: {
            title: "Agents Report"
        }
    },
    dataSource: {
        data: allData
    }
};
var realTimeSocket = io("/realTime");

// Pivot table datacrate instance
var pivot = new WebDataRocks({
    container: "wdr-component",
    width: "100%",
    height: "100%",
    toolbar: true
});
pivot.setReport(pvtData);

realTimeSocket.on("reportData", function(data) {
    console.log("received data on socket");
    console.log(data);
    dataProcess(data);
    createHTML(allData);
    pvtData = pivot.getReport();
    pvtData.dataSource = {data: allData};
    setPivot(pvtData);
});

function dataProcess(dataRow) {
    // console.log("enter data processor");
    if (dataRow == null || dataRow == undefined) {
        return null;
    }

    if (dataRow["Flag"] == "add") {
        allData.push(dataRow);
    } else {
        for (let j = 0; j < allData.length; j++) {
            var existRow = allData[j];
            var diffVal = {};
            for (var ekey in existRow) {
                var found = false;
                for (var nkey in dataRow) {
                    if (dataRow.nkey == existRow.ekey) {
                        found = true;
                        break;
                    }
                }
                if (found) {
                    diffVal.ekey = existRow.ekey;
                }
            }

            if (diffVal != {}) {
                allData.splice(j, 1);
            }
        }
    }
}

function createHTML(jsonData) {
    // console.log("into createHTML function");
    jsonData.reverse();
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

function getDruidData(endPoint) {
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

// Pivot table functions
function setPivot(allPivotData) {
    console.log(allPivotData);
    pivot.setReport(allPivotData);
    pivot.refresh();
    pvtData = pivot.getReport();
}

pivot.on("reportchange", 'redraw');
pivot.on("reportcomplete", 'redraw');

function redraw() {
  let col = 0, row = 0;
  pivot.customizeCell(function(cellBuilder, cellData) {
    if (cellData.columnIndex > col) col = cellData.columnIndex;
    if (cellData.rowIndex > row) row = cellData.rowIndex;
  });
  pivot.on("aftergriddraw", function() {
    pivot.off("aftergriddraw");
    document.querySelector("#wdr-component").style.width = 100 * (col + 2) + 'px';
    document.querySelector("#wdr-component").style.height = 100 * ++row + 27 + 'px';
  });
}