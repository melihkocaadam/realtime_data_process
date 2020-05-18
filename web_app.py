from flask import Flask, render_template, request
from kafka import KafkaProducer, KafkaConsumer
from datetime import datetime
import json, requests, os

app = Flask(__name__)

@app.route('/__/<path:filename>')
def serve_static(filename):

    root_dir = os.path.dirname(os.getcwd())
    # print(os.path.join(root_dir, 'realtime_data_process/static', filename))
    return send_from_directory(os.path.join(root_dir, 'realtime_data_process/static'), filename)

@app.route("/report")
def report():
    return render_template("report.html")

@app.route("/agents")
def agents():
    return render_template("agents.html")

@app.route("/newReport")
def newReport():
    return render_template("newReport.html")

@app.route("/agentsReport/<clientid>")
def consumer(clientid):
    consumer = KafkaConsumer(
        'agents',
        client_id=clientid,
        bootstrap_servers=['localhost:9092'])

    for message in consumer:
        jsonResult = json.loads(message.value)
        return jsonResult

@app.route("/sendAgentStatus", methods=['POST'])
def sendAgentStatus():
    jsonData = request.get_json()
    jsonData["activityDate"] = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
    jsonData["sequence"] = int(datetime.now().timestamp() * 1000)
    
    producer = KafkaProducer(
    bootstrap_servers=["0.0.0.0:9092"],
    client_id="agents-webpage-producer",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )
    producer.send("agents", jsonData)

    return 'JSON posted'

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
                            ,TIMESTAMPDIFF(SECOND, atbl.__time, CURRENT_TIMESTAMP) as "Duration"
                            ,atbl.__time as "Last Update"
                        FROM (
                            SELECT agent
                                ,max(sequence) as max_seq
                            FROM "agents"
                            GROUP BY agent
                            ) as mtbl
                        LEFT JOIN "agents" atbl
                            ON atbl.agent = mtbl.agent
                            and atbl.sequence = mtbl.max_seq
                        WHERE COALESCE(atbl.status, '') not in ('Logout')"""}
    r = requests.post(url, data=json.dumps(param), headers=headers)
    result = r.text

    return result

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")
