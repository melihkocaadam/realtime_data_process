from flask import Flask, render_template, request, Response
from kafka import KafkaProducer, KafkaConsumer, TopicPartition
from datetime import datetime
from threading import Thread
import json, requests, os, time, schedule

app = Flask(__name__)

##########################
### Static File Config ###
##########################
@app.route('/__/<path:filename>')
def serve_static(filename):

    root_dir = os.path.dirname(os.getcwd())
    # print(os.path.join(root_dir, 'realtime_data_process/static', filename))
    return send_from_directory(os.path.join(root_dir, 'realtime_data_process/static'), filename)

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

################################
### Kafka Consumer Endpoints ###
################################
@app.route('/test')
def test():
    def consumer():
        print("Stream consumer started")

        jsonResult = []
        topicName = "agentsCompact"
        consumer = KafkaConsumer(
            client_id="client1",
            group_id="group1",
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

            time.sleep(1)
            
            yield str(jsonResult).replace("'", '"')
        
        print("Stream consumer finished")
        yield ""
    
    return Response(consumer(), mimetype="text/plain")

@app.route("/streamTopics")
def agentsStream():
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

    print("existData", datetime.now())
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

schedule.every(5).seconds.do(run_every_5_seconds)

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

###################
### Main Method ###
###################
if __name__ == "__main__":
    t = Thread(target=run_schedule)
    t.start()
    app.run(debug=False, host="0.0.0.0")
