import time
from confluent_kafka import Producer

# Producer2 config with a different batch size, linger, etc.
producer_conf = {
    "bootstrap.servers": "kafka:9092",
    "batch.size": 40000,
    "linger.ms": 50,
}

producer = Producer(producer_conf)


def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed for record {msg.key()}: {err}")
    else:
        print(
            f"Producer2 successfully produced record to "
            f"{msg.topic()} partition [{msg.partition()}] @ offset {msg.offset()}"
        )


topic_name = "mytopic"
for i in range(5):
    value = f"Hello from Producer2 - {i}"
    producer.produce(topic_name, key=str(i), value=value, callback=delivery_report)
    time.sleep(0.5)

producer.flush()
print("Producer2 finished sending messages.")
