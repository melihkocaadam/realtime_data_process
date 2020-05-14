import requests, json, sys, time
from kafka import KafkaProducer
from datetime import datetime
from dateutil.parser import parse

source_url = "https://my.api.mockaroo.com/calls.json?key=8347e250"

csv_req = requests.get(source_url)
csv = csv_req.content.decode().rstrip("\n").split(sep="\n")

rows = []
row_num = 0
for row in csv:
    row_num += 1
    if row_num == 1:
        headers = row.split(",")
    else:
        rows.append(row.split(","))

data_list = []

for row in rows:
    data = {}
    c_index = 0
    for column in row:
        d_index = headers[c_index]
        if d_index == "call_start_date":
            d_index = "call_start_time"
            data[d_index] = datetime.strftime(parse(column), "%Y-%m-%d %H:%M:%S")
        else:
            data[d_index] = column
        c_index += 1
    data_list.append(data)

producer = KafkaProducer(
    bootstrap_servers=["localhost:9092"],
    client_id="local-producer",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )

i = 0
for d in data_list:
    i += 1
    producer.send("calls", d)
    print("\r", i , end="")
    time.sleep(0.2)

print("\r", i, "satır gönderildi...", datetime.now(), end="")
