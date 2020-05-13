console.log("init js");
started=true
function CreateTableFromJSON() {
    var int_str = document.getElementById("interval").value;
    var interval = 1000 * parseInt(int_str);
    if (started) {
        setTimeout(function(){ CreateTableFromJSON() }, interval);
    } else {
        console.log("loop stoped");
    }

    myBooks = GetData()

    var col = [];
    for (var i = 0; i < myBooks.length; i++) {
        for (var key in myBooks[i]) {
            if (col.indexOf(key) === -1) {
                col.push(key);
            }
        }
    }

    var table = document.createElement("table");

    var tr = table.insertRow(-1);                   // TABLE ROW.

    for (var i = 0; i < col.length; i++) {
        var th = document.createElement("th");      // TABLE HEADER.
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

    // FINALLY ADD THE NEWLY CREATED TABLE WITH JSON DATA TO A CONTAINER.
    var divContainer = document.getElementById("showData");
    divContainer.innerHTML = "";
    divContainer.appendChild(table);
}

function Stop() {
    started=false
}
function Start() {
    started=true
    console.log("loop started");
    GetData()
    CreateTableFromJSON()
}
function GetData() {
    var Url = "http://35.228.71.166:5000/getDruidData";
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