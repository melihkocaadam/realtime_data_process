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
        createConnSocket(topicName);
    } else {
        button.innerText = "Start";
        button.className = "btn rounded btn-outline-success";
        started = false;
        console.log("into stop");
    }
}

function createConnSocket(topicName) {
    var socket = io();
    
    socket.on("connect", function() {
        socket.emit(topicName, {data: "connected to " + topicName})
    });

    socket.on("unauthorized", function(error) {
        // this should now fire
        if (error.data.type == "UnauthorizedError" || error.data.code == "invalid_token") {
          alert("User's token has expired");
        }
    });

}