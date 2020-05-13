import requests, json
from kafka import BrokerConnection
from kafka.cluster import BrokerMetadata, ClusterMetadata

broker = BrokerConnection(
    host="35.225.91.126",
    port=9092,
    afi=50
)
broker.connected()
print(broker.connect(), "\n")

clusterMD = ClusterMetadata(
    bootstrap_servers=["35.225.91.126:9092"],
    api_version=(0,0,8),
    client_id="melih-producer",
)

print("1: ", clusterMD.brokers(), "\n")
print("2: ", clusterMD.is_bootstrap("bootstrap-0"), "\n")