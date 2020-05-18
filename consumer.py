from kafka import KafkaConsumer
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
    msg_len = len(str(json.dumps(msg)))
    print(msg_len, msg)
    jsonResult.append(json.loads(message.value))
    if msg_len = 0:
        break

print(jsonResult)