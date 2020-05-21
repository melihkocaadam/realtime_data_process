from flask import Flask, render_template, request
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
@app.route("/streamTopics")
def agentsStream():
    params = request.args
    clientid = params["userName"]
    cycleNum = params["cycleNum"]
    topicName = params["topicName"]
    jsonResult = []

    if cycleNum == 0:
        druidResult = getAgentsData()
        jsonResult = json.loads(druidResult)

        return str(jsonResult).replace("'", '"')

    consumer = KafkaConsumer(
        client_id=clientid,
        bootstrap_servers=['localhost:9092'])

    tp = TopicPartition(topicName, 0)
    consumer.assign([tp])
    exist_offset = consumer.position(tp)

    end_ofs = consumer.end_offsets([tp])
    for offset in end_ofs:
        end_offset = end_ofs[offset]
        break
    
    if exist_offset < end_offset:
        for message in consumer:
            msg = message.value
            msg_json = json.loads(msg)
            
            jsonResult.append(msg_json)
            msg_offset = message.offset

            if msg_offset == end_offset -1:
                consumer.seek_to_end(tp)
                break
        
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
    producer.send("agentsCompact", key=keyVal, value=jsonData)

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
        for i, erow in enumerate(existData):
            for j, nrow in enumerate(newData):
                if erow["Agents"] == nrow["Agents"]:
                    if erow["Sequence"] >= nrow["Sequence"]:
                        existData[i]["Flag"] = "save"
                        newData[j]["Flag"] = "delete"
                    else:
                        existData[i]["Flag"] = "delete"
                        newData[j]["Flag"] = "add"
        
        for k, row in enumerate(existData):
            if "Flag" not in row:
                existData[k]["Flag"] = "delete"

        for k, row in enumerate(newData):
            if "Flag" not in row:
                newData[k]["Flag"] = "add"

    print("\nnewData")
    for i, row in enumerate(newData):
        # print(row)
        if "Flag" in newData[i] and newData[i]["Flag"] == "add":
            existData.append(newData[i])
    print("existData")
    for i, row in enumerate(existData):
        print(row)
        if "Flag" in existData[i] and existData[i]["Flag"] == "delete":
            del existData[i]

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
