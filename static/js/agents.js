var hostName = window.location.hostname;

var addData = function(agentData) {

    var agent_name = agentData["agent"];
    var status = agentData["status"];
    var nested_html = ''
    + '<div class="main d-flex border rounded" style="padding: 5px;" id="agent-'+agent_name+'">'
    + '  <div class="col-md-auto-3" style="padding: 5px;">'
    + '	<div class="row-md-auto-1">'
    + '	  <i class="fas fa-user" id="agentText"> Agent '+agent_name+' </i>'
    + '	</div>'
    + '	<div class="row-md-auto-1">'
    + '	  <div class="btn-group btn-group-toggle" data-toggle="buttons">'
    + '		<button class="btn btn-outline-danger" style="width: 70px;" id="btn-login-'+agent_name+'" onclick="loginClick(\''+agent_name+'\')">Login</button>'
    + '		<button class="btn btn-outline-success" style="width: 70px;" id="btn-avail-'+agent_name+'" onclick="availClick(\''+agent_name+'\')" disabled>Avail</button>'
    + '		<button class="btn btn-outline-warning" style="width: 70px;" id="btn-call-'+agent_name+'" onclick="callClick(\''+agent_name+'\')" disabled>Call</button>'
    + '		<button class="btn btn-outline-info" style="width: 70px;" id="btn-aux-'+agent_name+'" onclick="auxClick(\''+agent_name+'\')" disabled>AUX</button>'
    + '		<button class="btn btn-outline-secondary" style="width: 70px;" id="btn-acw-'+agent_name+'" onclick="acwClick(\''+agent_name+'\')" disabled>ACW</button>'
    + '	  </div>'
    + '	</div>'
    + '  </div>'
    + '  <div class="col-md-auto-2" style="padding: 5px;">'
    + '	<div class="row-md-auto-1">'
    + '	  <i class="fas fa-clock fa_timer" id="timer-'+agent_name+'">00:00:00</i>'
    + '	</div>'
    + '	<div class="row-md-auto-1 ">'
    + '	  <i class="fas fa-info-circle" id="state-'+agent_name+'">'+status+'</i>'
    + '	</div>'
    + '  </div>'
    + '  <div class="col-md-auto-1 d-flex justify-content-center" style="padding: 5px;">'
    + '	<button class="btn btn-delete" onclick="removeFunction(\''+agent_name+'\')">'
    + '	  <i class="fas fa-trash-alt"></i>'
    + '	</button>'
    + '  </div>'
    + '</div>'

    return nested_html;
}


$(document).ready(function(){
    var getExistAgents = JSON.parse(localStorage.getItem('agentList')) || [];

    if (getExistAgents != undefined || getExistAgents != '') {
        getExistAgents.forEach(function(agentRow) {
            addAgent(agentRow);
        });
    }
})


$(function(){
    $('#addAgent').click(function(){
        var agent_name = $('#agentName').val();
        var now = new Date();
        var sequence = now.getTime();
        data = JSON.parse('{"agent": "'+ agent_name +'", "status": "Logout", "sequence": ' + sequence.toString() + '}');
        addAgent(data);
        $("#agentName").val("");
    })
})

$(function(){
    $('#deleteAll').click(function(){
        var getExistAgents = JSON.parse(localStorage.getItem('agentList')) || [];

        if (getExistAgents != undefined || getExistAgents != '') {
            localStorage.removeItem('agentList');
            location.reload();
        }
    })
})

function removeFunction(agent_name) {
    $('#agent-' + agent_name).remove();
    deleteLocalStorage(agent_name);
}

function addAgent(agentData) {
    var agent_name = agentData["agent"];
    var exist_agent = $('#agent-'+agent_name).length;
    
    if (agent_name.length < 3) {
        alert("Agent ismi minimum 3 karakter olmalıdır...");
    } else if (exist_agent > 0) {
        alert(agent_name + " isminde bir agent var.\nAynı isimde iki agent eklenemez...");
    } else {
        var needed_body = addData(agentData);
        $('.inner_body').append(needed_body);
        addLocalStorage(agentData);
    }
}

function addLocalStorage(data) {
    var getExistAgents = JSON.parse(localStorage.getItem('agentList')) || [];

    if (getExistAgents != undefined || getExistAgents != '') {
        for (var i = 0; i < getExistAgents.length; i++) {
            if (getExistAgents[i]["agent"] == data["agent"]) {
                getExistAgents.splice(i, 1);
            }
        }
        getExistAgents.push(data);
        localStorage.setItem('agentList', JSON.stringify(getExistAgents));
    }
}

function deleteLocalStorage(agent_name) {
    var getExistAgents = JSON.parse(localStorage.getItem('agentList')) || [];

    if (getExistAgents != undefined || getExistAgents != '') {
        for (var i = 0; i < getExistAgents.length; i++) {
            if (getExistAgents[i]["agent"] == agent_name) {
                getExistAgents.splice(i, 1);
            }
        }
        localStorage.setItem('agentList', JSON.stringify(getExistAgents));
    }
}

$(function(){
    setInterval(function(){

        $('.fa_timer').each(function(i, obj){
            var id = $(obj).attr("id");
            var state = id.replace('timer', '#state');
            state = $(state).text();

            if (state != 'Logout') {
                var time_value = $(obj).html();
                var sec_value = timeToSec(time_value);
                ++sec_value;
                time_value = secToTime(sec_value);
                $(obj).html(time_value);
            }
            
        });
    }, 1000);
});

function timerReset(agent_name) {
    $('#timer-' + agent_name).html('00:00:00');
}

function timeToSec(time) {
    var hoursMinutes = time.split(/[.:]/);
    var hours = parseInt(hoursMinutes[0]);
    var minutes = parseInt(hoursMinutes[1]);
    var seconds = parseInt(hoursMinutes[2]);
    return seconds + (minutes * 60) + (hours * 3600);
}

function secToTime(value) {
    var sec_num = parseInt(value, 10);
    var remain_min = sec_num % 3600;
    var hours   = (sec_num - remain_min) / 3600;
    var remain_sec = remain_min % 60;
    var minutes = (remain_min - remain_sec) / 60;
    var seconds = remain_sec;

    if (hours   < 10) {hours   = "0"+hours;}
    if (minutes < 10) {minutes = "0"+minutes;}
    if (seconds < 10) {seconds = "0"+seconds;}
    return hours + ':' + minutes + ':' + seconds;
}

function loginClick(agent_name){
    var btn_name = $("#btn-login-"+agent_name).text();
    var data;
    var now = new Date();
    var sequence = now.getTime();
    if (btn_name == "Login") {
        $('#state-'+agent_name).text("Avail");
        $("#btn-avail-"+agent_name).prop('disabled', false);
        $("#btn-call-"+agent_name).prop('disabled', false);
        $("#btn-acw-"+agent_name).prop('disabled', false);
        $("#btn-aux-"+agent_name).prop('disabled', false);
        $("#btn-login-"+agent_name).text("Logout");
        data = JSON.parse('{"agent": "'+ agent_name +'", "status": "Login", "sequence": ' + sequence.toString() + ', "prevSequence": ' + (sequence+100).toString() + '}');
        postAgentStatus(data);
        data = JSON.parse('{"agent": "'+ agent_name +'", "status": "Avail", "sequence": ' + (sequence+100).toString() + '}');
        postAgentStatus(data);
    } else {
        $('#state-'+agent_name).text("Logout");
        $("#btn-avail-"+agent_name).prop('disabled', true);
        $("#btn-call-"+agent_name).prop('disabled', true);
        $("#btn-acw-"+agent_name).prop('disabled', true);
        $("#btn-aux-"+agent_name).prop('disabled', true);
        $("#btn-login-"+agent_name).text("Login");
        data = JSON.parse('{"agent": "'+ agent_name +'", "status": "Logout", "sequence": ' + sequence.toString() + '}');
        postAgentStatus(data);
    }
    addLocalStorage(data);
    timerReset(agent_name);
}

function availClick(agent_name){
    $('#state-'+agent_name).text("Avail");
    timerReset(agent_name);
    var now = new Date();
    var sequence = now.getTime();
    var data = JSON.parse('{"agent": "'+ agent_name +'", "status": "Avail", "sequence": ' + sequence.toString() + '}');
    postAgentStatus(data);
    addLocalStorage(data);
}

function callClick(agent_name){
    $('#state-'+agent_name).text("On Call");
    timerReset(agent_name);
    var now = new Date();
    var sequence = now.getTime();
    var data = JSON.parse('{"agent": "'+ agent_name +'", "status": "Call", "sequence": ' + sequence.toString() + '}');
    postAgentStatus(data);
    addLocalStorage(data);
}

function acwClick(agent_name){
    $('#state-'+agent_name).text("ACW");
    timerReset(agent_name);
    var now = new Date();
    var sequence = now.getTime();
    var data = JSON.parse('{"agent": "'+ agent_name +'", "status": "ACW", "sequence": ' + sequence.toString() + '}');
    postAgentStatus(data);
    addLocalStorage(data);
}

function auxClick(agent_name){
    $('#state-'+agent_name).text("AUX");
    timerReset(agent_name);
    var now = new Date();
    var sequence = now.getTime();
    var data = JSON.parse('{"agent": "'+ agent_name +'", "status": "AUX", "sequence": ' + sequence.toString() + '}');
    postAgentStatus(data);
    addLocalStorage(data);
}

function postAgentStatus(jsonData){
    var Url = "http://" + hostName + ":5000/sendAgentStatus";

    var getExistAgents = JSON.parse(localStorage.getItem('agentList')) || [];

    if (getExistAgents != undefined || getExistAgents != '') {
        getExistAgents.forEach(function(agentRow) {
            if (agentRow["agent"] == jsonData["agent"] && !("prevSequence" in jsonData)) {
                jsonData["prevSequence"] = agentRow["sequence"];
            }
            else {
                jsonData["prevSequence"] = jsonData["sequence"] - 1000
            }
        });
    }

    $.ajax({
        url: Url,
        type: 'POST',
        contentType: "application/json",
        data: JSON.stringify(jsonData),
        error: function(error){
            console.log("Request Error");
            console.log(error);
        }
    });
}