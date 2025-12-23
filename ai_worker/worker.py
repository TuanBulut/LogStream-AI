import json
import requests
import subprocess
import re
from kafka import KafkaConsumer

KAFKA_TOPIC = "system-logs"
MODEL_NAME = "deepseek-r1:1.5b"

print("🧠 AI Worker: Connecting to Kafka...")
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=['127.0.0.1:9092'],
    auto_offset_reset='latest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)
print(f"✅ AI Worker Connected! Waiting for disasters...")

def ask_deepseek(log_entry):
    prompt = f"""
    A Docker service has failed. Return ONLY the command to restart it. 
    Do not explain. Do not use markdown formatting.
    
    Log: {log_entry}
    
    Example Output:
    docker restart payment-service
    """
    
    response = requests.post('http://localhost:11434/api/generate', json={
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    })
    return response.json()['response'].strip()

def execute_fix(command):
    print(f"⚡ EXECUTING FIX: {command}")
    try:
        clean_command = command.replace('`', '').strip()
        
        result = subprocess.run(clean_command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ SUCCESS: Service restarted!")
        else:
            print(f"❌ FAILED: {result.stderr}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

for message in consumer:
    log = message.value
    
    if log['status'] == "DOWN":
        print(f"🔴 CRITICAL: {log['service']} is DOWN!")
        
        fix_command = ask_deepseek(log)
        print(f"🤖 AI Suggests: {fix_command}")
        
        if "docker" in fix_command:
            execute_fix(fix_command)
        else:
            print("⚠️ AI was confused, skipping execution.")
            
    else:
        print(".", end="", flush=True)