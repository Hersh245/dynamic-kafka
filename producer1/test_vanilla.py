import random
import json
import string
import time
from confluent_kafka import Producer

# Producer1 config with a certain batch.size, linger.ms, etc.
producer_conf_list = [
    {
        "bootstrap.servers": "kafka:9092",
        "batch.size": batch_size,  # Example batch size
        "statistics.interval.ms": 1,
        "linger.ms": 1,
        # 'compression.type': 'lz4', etc. (optional)
    }
    for batch_size in range(1000, 21000, 1000)
]

latencies = []
rtt = []

def stats_callback(stats_json):
    stats = json.loads(stats_json)
    if "brokers" in stats:
        for broker_id, broker_data in stats["brokers"].items():
            if "rtt" in broker_data:
                rtt.append(broker_data["rtt"]["avg"] * 1e-6)

def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed for record {msg.key()}: {err}")
    else:
        latencies.append(msg.latency())


NUM_MSG = 100000
MSG_SIZE = 100


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
        latencies = []
        rtt = []
        curr_sent_size = 0
        producer = Producer(producer_conf, stats_cb=stats_callback)
        start_time = time.time()
        producer.produce("mytopic", key=str(0), value=payload[0], callback=delivery_report)
        producer.flush()
        batch_size = producer_conf['batch.size']
        for i in range(1, NUM_MSG):
            producer.produce("mytopic", key=str(i), value=payload[i], callback=delivery_report)
            curr_sent_size += len(str(i).encode('utf-8')) + len(payload[i])
            if curr_sent_size >= batch_size:
                curr_sent_size = 0
                producer.poll(0.1)
            producer.poll(0)
        # Wait for deliveries to complete
        producer.flush()
        end_time = time.time()
        print(f"end to end latency is {end_time - start_time}")
        with open(
            f"vanilla_per_msg_latency_batchsize_{producer_conf['batch.size']}.txt", "a"
        ) as file:
            for l in latencies:
                file.write(f"{l}\n")
        with open(
            f"vanilla_rtt_batchsize_{producer_conf['batch.size']}.txt", "a"
        ) as file:
            for l in rtt:
                file.write(f"{l}\n")
