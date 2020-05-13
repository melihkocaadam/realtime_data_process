import requests, json
from kafka import KafkaProducer, KafkaConsumer, KafkaClient, KafkaAdminClient

admin = KafkaAdminClient(
    bootstrap_servers=["35.225.91.126:9092"],
    api_version=(0,8),
    client_id="melih-producer",
)

admin.create_topics("new_topic2")