from kafka import KafkaConsumer, TopicPartition
from datetime import datetime
import json, sys

my_topic = sys.argv[1]
client = sys.argv[2]
group = sys.argv[3]

# my_topic = 'agentsCompact'
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
print("end offset:" ,end_offset)

consumer.seek(tp, 1)
exist_offset = consumer.position(tp)
print(exist_offset)

jsonResult = []
if exist_offset < end_offset:
    for message in consumer:
        msg = message.value
        msg_json = json.loads(msg)
        
        jsonResult.append(msg_json)
        msg_offset = message.offset
        msg_json["offset"] = msg_offset
        print(msg_json)

        if msg_offset == end_offset -1:
            consumer.seek_to_end(tp)
            break
