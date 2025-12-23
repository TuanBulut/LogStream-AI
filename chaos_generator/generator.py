import time
import json
import requests
from kafka import KafkaProducer

KAFKA_TOPIC = "system-logs"
SERVICES = [
    {"name": "payment-service", "url": "http://localhost:8080"},
    {"name": "inventory-service", "url": "http://localhost:8081"}
]

print("⏳ Waiting for Kafka...")
time.sleep(10)

producer = KafkaProducer(
    bootstrap_servers=['127.0.0.1:9092'],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

print("🚀 Generator Started. Monitoring Services...")

while True:
    for svc in SERVICES:
        try:
            resp = requests.get(svc["url"], timeout=1)
            status = "UP"
            code = resp.status_code
            print(f"🟢 {svc['name']} is UP")
        except:
            # If it fails, report DOWN
            status = "DOWN"
            code = 500
            print(f"🔴 {svc['name']} is DOWN! Sending Alert...")

        log = {
            "timestamp": time.time(),
            "service": "payment-service" if "8080" in svc["url"] else "inventory-service", # Simple mapping
            "status": status,
            "code": code
        }
        producer.send(KAFKA_TOPIC, value=log)

    time.sleep(2) # Check every 2 seconds