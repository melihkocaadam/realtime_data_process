// import { WebDataRocks } from '../webdatarocks1.3.1/webdatarocks.js';

var allData = [];
var realTimeSocket = io("/realTime");

realTimeSocket.on("reportData", function(data) {
    console.log("received data on socket");
    console.log(data);
    dataProcess(data);
    createHTML(allData);
});

function dataProcess(dataRow) {
    console.log("enter data processor");
    for (var j = 0; j < allData.length; j++) {
        
        if (dataRow != null && dataRow["Agents"] == allData[j]["Agents"] && dataRow["Sequence"] == allData[j]["Sequence"]) {
            if (dataRow["Flag"] == "delete") {
                allData.splice(j, 1);
                dataRow = null;
                console.log("enter delete");
            } else if (dataRow["Flag"] == "add") {
                allData.push(dataRow);
                dataRow = null;
                console.log("enter add");
            } else {
                console.log("incorrect flag command");
            }
        }
    }
    if (dataRow != null && dataRow["Flag"] == "add") {
        allData.push(dataRow);
        console.log("enter new row");
    }
}

function createHTML(jsonData) {
    console.log("into createHTML function");
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

// Pivot table data insert
// var pivot = new WebDataRocks({
//     container: "wdr-component",
//     toolbar: true,
//     report: {
//         dataSource: {
//             data: getJSONData()
//         },
//         formats: [{
//             name: "calories",
//             maxDecimalPlaces: 2,
//             maxSymbols: 20,
//             textAlign: "right"
//         }],
//         slice: {
//             rows: [{
//                 uniqueName: "Food"
//             }],
//             columns: [{
//                 uniqueName: "[Measures]"
//             }],
//             measures: [{
//                 uniqueName: "Calories",
//                 aggregation: "average",
//                 format: "calories"
//             }]
//         }
//     }
// });
// function getJSONData() {
//     return [{
//             "Category": {
//                 type: "level",
//                 hierarchy: "Food"
//             },
//             "Item": {
//                 type: "level",
//                 hierarchy: "Food",
//                 level: "Dish",
//                 parent: "Category"
//             },
//             "Serving Size": {
//                 type: "level",
//                 hierarchy: "Food",
//                 level: "Size",
//                 parent: "Dish"
//             },
//             "Calories": {
//                 type: "number"
//             },
//             "Calories from Fat": {
//                 type: "number"
//             }
//         },
//         {
//             "Category": "Breakfast",
//             "Item": "Frittata",
//             "Serving Size": "4.8 oz (136 g)",
//             "Calories": 300,
//             "Calories from Fat": 120
//         }
// ];
// }

var pivot = new WebDataRocks({
    container: "#wdr-component",
    toolbar: true,
    report: {
        dataSource: {
            filename: "https://cdn.webdatarocks.com/data/data.csv"
        }
    }
});