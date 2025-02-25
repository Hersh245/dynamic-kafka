import time
from confluent_kafka import Producer

# Producer1 config with a certain batch.size, linger.ms, etc.
producer_conf = {
    "bootstrap.servers": "kafka:9092",
    "batch.size": 20000,  # Example batch size
    "linger.ms": 10,
    # 'compression.type': 'lz4', etc. (optional)
}

producer = Producer(producer_conf)


def delivery_report(err, msg):
    """Called once for each message to indicate delivery result."""
    if err is not None:
        print(f"Delivery failed for record {msg.key()}: {err}")
    else:
        print(
            f"Producer1 successfully produced record to "
            f"{msg.topic()} partition [{msg.partition()}] @ offset {msg.offset()}"
        )


# Send a few messages
time.sleep(5)
topic_name = "mytopic"
for i in range(5):
    value = f"Hello from Producer1 - {i}"
    producer.produce(topic_name, key=str(i), value=value, callback=delivery_report)
    # "Flush" is asynchronous, but let's add a small sleep for demonstration
    time.sleep(0.5)

# Wait for deliveries to complete
producer.flush()
print("Producer1 finished sending messages.")
