from kafka import KafkaConsumer
from datetime import datetime
import json

consumer = KafkaConsumer(
    'agents',
    client_id='local-consumer',
    auto_offset_reset='smallest',
    bootstrap_servers=['localhost:9092'])

jsonResult = []
for message in consumer:
    msg = message.value
    print(type(msg))
    msg_json = json.loads(msg)
    print(type(msg_json))
    msg_len = len(str(msg_json))
    print(msg_len, msg_json)
    jsonResult.append(msg_json)
    
    print(message.offset)

print(jsonResult)