from kafka import KafkaConsumer, TopicPartition
from datetime import datetime
import json

my_topic = 'agents'
consumer = KafkaConsumer(
    client_id='local-consumer',
    auto_offset_reset='smallest',
    bootstrap_servers=['localhost:9092'])

tp = TopicPartition(my_topic, 0)
consumer.assign([tp])
exist_offset = consumer.position(tp)
print(exist_offset)
consumer.seek_to_end(tp)
end_offset = consumer.position(tp)
print(end_offset)

jsonResult = []
for message in consumer:
    msg = message.value
    print(type(msg))
    msg_json = json.loads(msg)
    print(type(msg_json))
    msg_len = len(str(msg_json))
    print(msg_len, msg_json)
    jsonResult.append(msg_json)
    msg_offset = message.offset
    print(msg_offset)
    if msg_offset == end_offset:
        break

print(jsonResult)