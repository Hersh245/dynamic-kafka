import random
import string
import time
from confluent_kafka import Producer

# Producer1 config with a certain batch.size, linger.ms, etc.
producer_conf_list = [
    {
        "bootstrap.servers": "kafka:9092",
        "batch.size": batch_size,  # Example batch size
        "linger.ms": 10,
        # 'compression.type': 'lz4', etc. (optional)
    }
    for batch_size in [100, 200, 500, 1000, 2000, 5000, 10000, 20000]
]

latencies = []


def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed for record {msg.key()}: {err}")
    else:
        latencies.append(msg.latency())


NUM_MSG = 10000
MSG_SIZE = 1000


def generate_payload(msg_size, num_msg):
    payload = []
    for i in range(num_msg):
        msg = f"{i:06d} "
        remaining_size = msg_size - len(msg.encode("utf-8"))
        random_part = "".join(
            random.choices(string.ascii_letters + string.digits, k=remaining_size)
        )
        payload.append((msg + random_part).encode("utf-8"))
    return payload


if __name__ == "__main__":
    payload = generate_payload(MSG_SIZE, NUM_MSG)
    time.sleep(10)
    for producer_conf in producer_conf_list:
        producer = Producer(producer_conf)
        start_time = time.time()
        for i in range(NUM_MSG):
            producer.produce("mytopic", value=payload[i], callback=delivery_report)
        # Wait for deliveries to complete
        producer.flush()
        end_time = time.time()
        print(f"end to end latency is {end_time - start_time}")
        with open(
            f"vanilla_per_msg_latency_batchsize_{producer_conf['batch.size']}.txt", "a"
        ) as file:
            for l in latencies:
                file.write(f"{l}\n")

    while True:
        pass
        # Prevent container from getting deleted while we copy files
