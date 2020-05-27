var started = true;
var allData = {};

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

function connSocket(topicName) {
    var socket = io();

    socket.on("connect", function() {
        console.log("web socket connected");
        socket.emit(topicName, {data: "connected to " + topicName})
    });

    socket.on("unauthorized", function(error) {
        // this should now fire
        if (error.data.type == "UnauthorizedError" || error.data.code == "invalid_token") {
          console.log("User's token has expired or unauthorized");
          console.log(error.data);
        }
    });

}