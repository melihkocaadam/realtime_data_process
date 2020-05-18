from kafka import KafkaConsumer, TopicPartition
from datetime import datetime
import json, sys

client = sys.argv[1]
group = sys.argv[2]

my_topic = 'agents'
consumer = KafkaConsumer(
    client_id=client,
    group_id=group,
    bootstrap_servers=['localhost:9092'])

tp = TopicPartition(my_topic, 0)
consumer.assign([tp])
exist_offset = consumer.position(tp)
print(exist_offset)
end_oss = consumer.end_offsets([tp])
for offset in end_oss:
    end_offset = end_oss[offset]
    break
print(end_offset)

jsonResult = []
for message in consumer:
    msg = message.value
    msg_json = json.loads(msg)
    print(msg_json)
    jsonResult.append(msg_json)
    msg_offset = message.offset
    print(msg_offset)
    if msg_offset == end_offset -1:
        break

print(jsonResult)