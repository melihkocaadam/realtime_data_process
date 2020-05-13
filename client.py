import requests, json
from kafka import KafkaClient

client = KafkaClient(
    bootstrap_servers=["35.225.91.126:9092"],
    api_version=(0,0,8),
    client_id="melih-producer",
)

print(client.bootstrap_connected(), "\n")
print(client.check_version(), "\n")
print(client.get_api_versions(), "\n")
print(client.least_loaded_node(), "\n")
print(client.connected(0), "\n")
print(client.is_disconnected(0), "\n")
print(client.is_ready(0), "\n")
print(client.maybe_connect(0), "\n")
print(client.ready(0), "\n")