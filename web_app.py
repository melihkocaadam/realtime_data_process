from flask import Flask, render_template, request, Response
from kafka import KafkaProducer, KafkaConsumer, TopicPartition
from flask_socketio import SocketIO, send, emit
from datetime import datetime
from threading import Thread
import json, requests, os, time, schedule, gevent

async_mode = "gevent"
app = Flask(__name__)
app.config["SECRET_KEY"] = "real-time"
socketio = SocketIO(app, async_mode = async_mode)
rooms = {}


##########################
### Static File Config ###
##########################
@app.route('/__/<path:filename>')
def serve_static(filename):

    root_dir = os.path.dirname(os.getcwd())
    # print(os.path.join(root_dir, 'realtime_data_process/static', filename))
    return send_from_directory(os.path.join(root_dir, 'realtime_data_process/static'), filename)

######################
### Socket Methods ###
######################
msgNsp = "/messaging"
rtNsp = "/realTime"

@socketio.on('connect', namespace=msgNsp)
def socketConnect():
    print("client connected to", msgNsp)

@socketio.on('connect', namespace=rtNsp)
def socketConnect():
    print("client connected to", rtNsp)

@socketio.on('disconnect', namespace=msgNsp)
def socketDisconnect():
    print('client disconnected from', msgNsp)

@socketio.on('disconnect', namespace=rtNsp)
def socketDisconnect():
    print('client disconnected from', rtNsp)

@socketio.on('join', namespace=msgNsp)
def on_join(data):
    username = data['username']
    room = data['room']
    joinRoom(username, room)
    socketio.send(username + ' has entered the room.', room=room, namespace=msgNsp)

@socketio.on('leave', namespace=msgNsp)
def on_leave(data):
    username = data['username']
    room = data['room']
    leaveRoom(username, room)
    socketio.send(username + ' has left the room.', room=room, namespace=msgNsp)

@socketio.on("emitMessage", namespace=msgNsp)
def sendDataOnSocket(room, jsonData):
    jsonData["sequence"] = int(datetime.now().timestamp() * 1000)
    jsonData["room"] = room
    
    time.sleep(1)
    socketio.emit(room, jsonData, namespace=msgNsp)
    print("send data: " + str(jsonData))

def joinRoom(user, room):
    if room not in rooms:
        rooms[room] = []

    if user in rooms[room]:
        print(user, "exist in room", room)
        return
    
    rooms[room].insert(0, user)
    print(user, "->", room)
    print(rooms)

def leaveRoom(user, room):
    for i, u in enumerate(rooms[room]):
        if u == user:
            del rooms[room][i]
            print(user, "x", room)
    print(rooms)


######################
### HTML Endpoints ###
######################
@app.route("/report")
def report():
    return render_template("report.html")

@app.route("/agents")
def agents():
    return render_template("agents.html")

@app.route("/newReport")
def newReport():
    return render_template("newReport.html")

@app.route("/socketMessage")
def socketMessage():
    return render_template("socketMessage.html")

@app.route("/socketReport")
def socketReport():
    return render_template("socketReport.html")

################################
### Kafka Consumer Endpoints ###
################################
@app.route('/streamTopics')
def streamTopics():
    params = request.args
    clientid = params["userName"]
    cycleNum = int(params["cycleNum"])
    topicName = params["topicName"]
    jsonResult = []
    print(params)

    if cycleNum == 0:
        print("first cycle for browser")
        druidResult = getAgentsData()
        jsonResult = json.loads(druidResult)

        return str(jsonResult).replace("'", '"')

    def consumer():
        print("Stream consumer started")

        consumer = KafkaConsumer(
            client_id=clientid,
            group_id=clientid,
            bootstrap_servers=['localhost:9092'],
            enable_auto_commit=False
            )

        tp = TopicPartition(topicName, 0)
        consumer.assign([tp])
        exist_offset = consumer.position(tp)

        for message in consumer:
            msg = message.value
            msg_json = json.loads(msg)
            jsonResult.append(msg_json)
            msg_offset = message.offset
            print("offset:", msg_offset, "|", datetime.now().strftime("%H:%M:%S"), "|", msg_json)
            consumer.commit()

            lastestOffset = consumer.end_offsets([tp])
            time.sleep(1)
            
            if msg_offset == lastestOffset[tp] -1:
                break
        
        print("Stream consumer finished")
        yield str(jsonResult).replace("'", '"')
    
    print("Stream returned")
    return Response(consumer(), mimetype="text/plain") 

@app.route("/changeLogTopics")
def changeLogTopics():
    params = request.args
    clientid = params["userName"]
    cycleNum = int(params["cycleNum"])
    topicName = params["topicName"]
    jsonResult = []
    print(params)

    if cycleNum == 0:
        print("first cycle for browser")
        druidResult = getAgentsData()
        jsonResult = json.loads(druidResult)

        return str(jsonResult).replace("'", '"')

    print("data stream started")
    consumer = KafkaConsumer(
        client_id=clientid,
        group_id=clientid,
        bootstrap_servers=['localhost:9092'],
        enable_auto_commit=False
        )

    tp = TopicPartition(topicName, 0)
    consumer.assign([tp])
    exist_offset = consumer.position(tp)

    for message in consumer:
        msg = message.value
        msg_json = json.loads(msg)
        print(msg_json)
        jsonResult.append(msg_json)
        msg_offset = message.offset
        print(msg_offset)
        consumer.commit()
        
        return str(jsonResult).replace("'", '"')

################################
### Kafka Producer Endpoints ###
################################
@app.route("/sendAgentStatus", methods=['POST'])
def sendAgentStatus():
    jsonData = request.get_json()
    jsonData["activityDate"] = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
    jsonData["sequence"] = int(datetime.now().timestamp() * 1000)
    keyVal = jsonData["agent"].encode()
    
    producer = KafkaProducer(
    bootstrap_servers=["0.0.0.0:9092"],
    client_id="agents-webpage-producer",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )
    producer.send("agents", value=jsonData)

    return 'JSON posted'

#######################
### Druid Endpoints ###
#######################
@app.route("/getCallsData")
def getCallsData():
    url = "http://0.0.0.0:8888/druid/v2/sql"
    headers = {"Content-Type": "application/json"}
    param = {'query': """SELECT 'Total' as "Agent"
                            ,sum(duration) as "Sum of Duration"
                            ,sum(hold_time) as "Sum of Hold Time"
                            ,sum(ring_time) as "Sum of Ring Time"
                            ,sum(talk_time) as "Sum of Talk Time"
                            ,sum(acw) as "Sum of ACW Time"
                            ,count(*) as "Count of Calls"
                            ,count(DISTINCT campaign_id) as "Count of Unique Camp"
                        FROM "calls"
                        UNION ALL
                        SELECT *
                        FROM (
                        SELECT agent as "Agent"
                            ,sum(duration) as "Sum of Duration"
                            ,sum(hold_time) as "Sum of Hold Time"
                            ,sum(ring_time) as "Sum of Ring Time"
                            ,sum(talk_time) as "Sum of Talk Time"
                            ,sum(acw) as "Sum of ACW Time"
                            ,count(*) as "Count of Calls"
                            ,count(DISTINCT campaign_id) as "Count of Unique Camp"
                        FROM "calls"
                        GROUP BY agent
                        ORDER BY 6
                        ) as tbl"""}
    r = requests.post(url, data=json.dumps(param), headers=headers)
    result = r.text
    
    return result

@app.route("/getAgentsData")
def getAgentsData():
    url = "http://0.0.0.0:8888/druid/v2/sql"
    headers = {"Content-Type": "application/json"}
    param = {'query':"""SELECT mtbl.agent as "Agents"
                            ,atbl.status as "Status"
                            --,TIMESTAMPDIFF(SECOND, atbl.__time, CURRENT_TIMESTAMP) as "Duration"
                            --,atbl.__time as "Last Update"
                            ,mtbl.max_seq as "Sequence"
                        FROM (
                            SELECT agent
                                ,max(sequence) as max_seq
                            FROM "agents"
                            WHERE sequence > 1590019200000
                            GROUP BY agent
                            ) as mtbl
                        LEFT JOIN "agents" atbl
                            ON atbl.agent = mtbl.agent
                            and atbl.sequence = mtbl.max_seq
                        WHERE 1=1
                            --and COALESCE(atbl.status, '') not in ('Logout')
                            --and COALESCE(atbl.__time, '2000-01-01') > '2020-05-21'"""}
    r = requests.post(url, data=json.dumps(param), headers=headers)
    result = r.text
    
    return result

#########################
### Scheduler Methods ###
#########################
existData = []
def run_every_5_seconds():
    global existData
    data = getAgentsData()
    newData = json.loads(data)

    if len(existData) == 0:
        existData = newData
    else:
        for i, erow in enumerate(existData): # mevcut datanın satırlarında dön
            for j, nrow in enumerate(newData): # yeni datanın her bir satırı ile karşılaştır
                if erow["Agents"] == nrow["Agents"]: # Agent isimleri eşleşiyor ise,
                    if erow["Sequence"] >= nrow["Sequence"]: # yeni datanın sequence'ı mevcuttan küçükse
                        existData[i]["Flag"] = "save" # mevcut dataya save flag ekle
                        newData[j]["Flag"] = "delete" # yeni datayı sil
                    else:                           # eğer yeni datanın sequence'ı mevcuttan büyükse
                        existData[i]["Flag"] = "delete" # mevcut dataya delete flag ekle
                        newData[j]["Flag"] = "add" # yeni dataya add flag ekle
            
            if "Flag" not in erow: # bir satır için yeni datanın tüm satırları döndüğünde flag yok ise,
                existData[i]["Flag"] = "delete" # mevcut dataya delete flag ekle

        for k, row in enumerate(newData): # yeni datanın satırlarında dön
            if "Flag" not in row: # eğer flag etiketi olmamayan bir satır varsa
                newData[k]["Flag"] = "add" # yeni dataya add flag ekle

    # print("\nnewData", datetime.now())
    for rown in newData:
        if "Flag" in rown and rown["Flag"] in ("add"):
            # print(rown, "| This row added in existData with append")
            existData.insert(0, rown)

    # print("existData", datetime.now())
    for r, rowe in enumerate(existData):
        if "Flag" in rowe:
            if rowe["Flag"] in ("add", "delete"):
                print("scheduler |", rowe)
                producer = KafkaProducer(
                    bootstrap_servers=["0.0.0.0:9092"],
                    client_id="agents-scheduled-producer",
                    value_serializer=lambda v: json.dumps(v).encode("utf-8")
                    )
                producer.send("agentsCompact", value=rowe)

                if rowe["Flag"] == "delete":
                    del existData[r]

                socketio.emit('reportData', rowe, namespace=rtNsp) # websocket mesaj gönderimi için

schedule.every(5).seconds.do(run_every_5_seconds)

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)
        # print("scheduled", datetime.now())

###################
### Main Method ###
###################
if __name__ == "__main__":
    t = Thread(target=run_schedule)
    t.start()
    print("*** webapp beginning ***")
    socketio.run(app=app, debug=False, host="0.0.0.0", port=5000)
    # app.run(debug=False, host="0.0.0.0", port=5000)
    print("*** webapp stoped ***")
