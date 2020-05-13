from kafka import KafkaConsumer
consumer = KafkaConsumer('deneme',
                         #group_id='my-group',
                         bootstrap_servers=['35.228.71.166:9092'])

for message in consumer:
    print (message.value)