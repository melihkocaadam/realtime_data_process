var started = true;
var allData = {};
var socket = io();

socket.on("connect", function() {
    console.log("web socket connected");
});

socket.on("unauthorized", function(error) {
    if (error.data.type == "UnauthorizedError" || error.data.code == "invalid_token") {
      console.log("User's token has expired or unauthorized");
      console.log(error.data);
    }
});

socket.on("agentsCompact", function(data) {
    console.log("received data on socket");
    console.log(data);
});

function connSocket(topicName) {
    socket.emit(topicName, {data: "connected to " + topicName});
    console.log("send data on socket");
}

function startStop() {
    var button = document.getElementById("start-stop");
    var topicName = document.getElementById("topicName").value;

    if (button.innerText == "Start") {
        button.innerText = "Stop";
        button.className = "btn rounded btn-outline-danger";
        started = true;
        console.log("into start");
        connSocket(topicName);
    } else {
        button.innerText = "Start";
        button.className = "btn rounded btn-outline-success";
        started = false;
        console.log("into stop");
        location.reload();
    }
}
