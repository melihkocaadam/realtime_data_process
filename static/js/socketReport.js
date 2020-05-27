var started = true;
var allData = {};
var roomName = "";
var userName = "";
var realTimeSocket = io("/realTime", {
    forceNew: true,
    transport: ["webscoket", "pooling"]
});

realTimeSocket.on("connect", function() {
    console.log("web socket connected");
});

realTimeSocket.on("disconnect", function() {
    console.log("web socket disconnected");
});

realTimeSocket.on("unauthorized", function(error) {
    if (error.data.type == "UnauthorizedError" || error.data.code == "invalid_token") {
      console.log("User's token has expired or unauthorized");
      console.log(error.data);
    }
});

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
    var data = {data: message};
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
