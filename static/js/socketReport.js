var started = true;
var allData = [];
var roomName = "";
var userName = "";
var realTimeSocket = io("/realTime", {
    forceNew: true,
    transport: ["webscoket"]
});

// realTimeSocket.on("connect", function() {
//     console.log("web socket connected");
// });

// realTimeSocket.on("disconnect", function() {
//     console.log("web socket disconnected");
// });

// realTimeSocket.on("unauthorized", function(error) {
//     if (error.data.type == "UnauthorizedError" || error.data.code == "invalid_token") {
//       console.log("User's token has expired or unauthorized");
//       console.log(error.data);
//     }
// });

// realTimeSocket.on("agentsCompact", function(data) {
//     console.log("received data on socket for static function agentsCompact");
//     console.log(data);
// });

function joinRoom(userName, roomName) {
    var data = {username: userName, room: roomName};
    realTimeSocket.emit("join", data);
    console.log("user " + userName + " jonied room: " + roomName);
}

function leaveRoom(userName, roomName) {
    var data = {username: userName, room: roomName};
    realTimeSocket.emit("leave", data);
    console.log("user " + userName + " leaved room: " + roomName);
}

function sendMessage() {
    message = document.getElementById("message").value;
    userName = document.getElementById("userName").value;
    var data = {username: userName, data: message};
    realTimeSocket.emit("emitMessage", roomName, data);
    console.log("send data on socket");
}

function startStop() {
    var button = document.getElementById("start-stop");
    roomName = document.getElementById("roomName").value;
    userName = document.getElementById("userName").value;

    if (button.innerText == "Start") {
        button.innerText = "Stop";
        button.className = "btn rounded btn-outline-danger";
        started = true;
        console.log("into start");

        realTimeSocket.connect();
        joinRoom(userName, roomName);

        realTimeSocket.on(roomName, function(data) {
            console.log("received data on socket for room: " + roomName);
            console.log(data);
            allData.push(data);
            createHTML(allData);
        });
    } else {
        button.innerText = "Start";
        button.className = "btn rounded btn-outline-success";
        started = false;
        console.log("into stop");
        
        leaveRoom(userName, roomName);
        realTimeSocket.disconnect();
    }
}

function createHTML(jsonData) {
    console.log("into createHTML function");
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
            if (col[j] == "sequence") {
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

$('#message').keydown(function (e) {

    if (e.ctrlKey && e.keyCode == 13) {
        sendMessage();
        $('#message').val("");
    }
  });