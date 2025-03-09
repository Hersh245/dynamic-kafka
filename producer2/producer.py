from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, KafkaException
import json
import time


message_timestamps = {}

def check_broker_ready(bootstrap_servers):
        admin_client = AdminClient({'bootstrap.servers': bootstrap_servers})
        while True:
            try:
                broker_metadata = admin_client.list_topics(timeout=10)
                print("Broker is ready and available.")
                return broker_metadata 
            except KafkaException as e:
                print(f"Waiting for broker to become available: {str(e)}")
                time.sleep(1)

def stats_callback(stats):
    
    stats = json.loads(stats)
    cur_time = time.time()
    print(f"stats callback time: {cur_time}")
    for broker, data in stats.get("brokers", {}).items():
        if "int_latency" in data:
             print(f"avg int_latency: {data["int_latency"]["avg"]}")
             print(f"min int_latency: {data["int_latency"]["min"]}")
             print(f"max int_latency: {data["int_latency"]["max"]}")
        if "outbuf_latency" in data:
             print(f"avg outbuf_latency: {data["outbuf_latency"]["avg"]}")
             print(f"min outbuf_latency: {data["outbuf_latency"]["min"]}")
             print(f"max outbuf_latency: {data["outbuf_latency"]["max"]}")
        if "rtt" in data:
             print(f"avg rtt: {data["rtt"]["avg"]}")
             print(f"min rtt: {data["rtt"]["min"]}")
             print(f"max rtt: {data["rtt"]["max"]}")

def delivery_report(err, msg):
    print("delivery report")
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        
        timestamp = message_timestamps.get(msg.key().decode('utf-8'))
        if timestamp:
            print(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

            manual_timestamp_diff = time.time() - timestamp
            print(f"manual timestamp diff: {manual_timestamp_diff}")

            size = len(msg.timestamp())

            if 0 < size:
                idk_what_this_is = msg.timestamp()[0]
                print(f"msg timestamp 0 index: {idk_what_this_is}")

            if 1 < size:
                create_time = msg.timestamp()[1]
                print(f"create time: {create_time}")

            if 2 < size:
                broker_recieve_time = msg.timestamp()[2]
                print(f"log append time: {broker_recieve_time}")

                create_log_diff = broker_recieve_time - create_time
                print(f"log - create diff: {create_log_diff}")

            latency = msg.latency()
            print(f"msg latency: {latency}")


        else:
            print("timestamp not found for the message.")

def produce_message():
    for i in range(5):
        message_key = str(i)
        message_value = f'Message {i}'
        
        message_timestamps[message_key] = time.time()

        producer.produce('test_topic', key=message_key, value=message_value, callback=delivery_report)

        time.sleep(0.5)
    
    producer.flush()
    time.sleep(1)

conf = {
    "bootstrap.servers": "kafka:9092",
    "batch.size": 2000,  # Example batch size
    "linger.ms": 10,
    "stats_cb": stats_callback,
    "statistics.interval.ms": 500  #1/2 second
}

check_broker_ready("kafka:9092")

producer = Producer(conf)

produce_message()
