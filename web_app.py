from flask import Flask, render_template, request, Response
from kafka import KafkaProducer, KafkaConsumer, TopicPartition
from flask_socketio import SocketIO, send, emit
from datetime import datetime
from threading import Thread
import json, requests, os, time, schedule, gevent, config

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

@app.route("/appConfig", methods=['GET', 'POST'])
def appConfig():
    if request.method == 'GET':
        result = {}
        configs = config.sources
        print("get config", configs)
        result["configs"] = config
        return json.loads(result)
    else:
        getJson = request.get_json
        print("set config", getJson)
        config.sources = getJson
        return "Config Saved"


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
    print("***client info***", "\n",
            datetime.now().strftime("%H:%M:%S.%f"),
            request.remote_addr, "\n",
            request.user_agent)
    return render_template("socketReport.html")

@app.route("/configPage")
def configPage():
    return render_template("configPage.html")


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
            bootstrap_servers=['0.0.0.0:9092'],
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
        bootstrap_servers=['0.0.0.0:9092'],
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
    callsConfig = config.getConfigRow("table", "calls")
    callsQuery = callsConfig["query"]
    url = "http://0.0.0.0:9888/druid/v2/sql"
    headers = {"Content-Type": "application/json"}
    param = {'query': callsQuery}
    r = requests.post(url, data=json.dumps(param), headers=headers)
    result = r.text
    
    return result

@app.route("/getAgentsData")
def getAgentsData():
    agentsConfig = config.getConfigRow("table", "agents")
    agentsQuery = agentsConfig["query"]
    url = "http://0.0.0.0:9888/druid/v2/sql"
    headers = {"Content-Type": "application/json"}
    param = {'query': agentsQuery}

    result = None

    try:
        r = requests.post(url, data=json.dumps(param), headers=headers)
        result = r.text
    except Exception as e:
        print(e)
    
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
        print("Exist data is empty, first cycle")
    else:
        for ern, existRow in enumerate(existData): # mevcut datanın satırlarında dön
            existData[ern]["Flag"] = "delete" # mevcut datanın her bir satırındaki eski Flag'e delete yaz
            for nrn, newRow in enumerate(newData): # yeni datanın satırlarında dön
                newData[nrn]["Flag"] = "delete" # yeni data delete değerli bir Flay ekle. mevcut data ile kıyaslamada sorun olmasın diye
                diffDict = {k: existRow[k] for k in existRow if k not in newRow or existRow[k] != newRow[k]}
                if diffDict == {}: # fark kümesi boşsa yani satır birbiri ile aynı ise
                    existData[ern]["Flag"] = "save" # mevcut datanın bu satırına sakla işareti ekle
                    del newData[nrn] # yeni datanın bu satırını tekrar kontrol etmemek için sil

        # for i, erow in enumerate(existData): # mevcut datanın satırlarında dön
        #     for j, nrow in enumerate(newData): # yeni datanın her bir satırı ile karşılaştır
        #         if erow["Agents"] == nrow["Agents"]: # Agent isimleri eşleşiyor ise,
        #             if erow["Sequence"] >= nrow["Sequence"]: # yeni datanın sequence'ı mevcuttan küçükse
        #                 existData[i]["Flag"] = "save" # mevcut dataya save flag ekle
        #                 newData[j]["Flag"] = "delete" # yeni datayı sil
        #             else:                           # eğer yeni datanın sequence'ı mevcuttan büyükse
        #                 existData[i]["Flag"] = "delete" # mevcut dataya delete flag ekle
        #                 newData[j]["Flag"] = "add" # yeni dataya add flag ekle
            
        #     if "Flag" not in erow: # bir satır için yeni datanın tüm satırları döndüğünde flag yok ise,
        #         existData[i]["Flag"] = "delete" # mevcut dataya delete flag ekle

        # for k, row in enumerate(newData): # yeni datanın satırlarında dön
        #     if "Flag" not in row: # eğer flag etiketi olmamayan bir satır varsa
        #         newData[k]["Flag"] = "add" # yeni dataya add flag ekle

        # # print("\nnewData", datetime.now())
        # for rown in newData:
        #     if "Flag" in rown and rown["Flag"] in ("add"):
        #         # print(rown, "| This row added in existData with append")
        #         existData.insert(0, rown)

    for newRow in newData: # yeni datanın satırlarında dön
        newRow["Flag"] = "add" # her bir satıra add flag ekle
        existData.append(newRow) # kalan satırları mevcut dataya ekle

    # print("existData", datetime.now())
    for r, rowe in reversed(list(enumerate(existData))):
        if "Flag" in rowe:
            if rowe["Flag"] in ("add", "delete"):
                print("scheduler |", rowe)
                socketio.emit('reportData', rowe, namespace=rtNsp) # websocket mesaj gönderimi için
                if rowe["Flag"] == "delete":
                    del existData[r]

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
