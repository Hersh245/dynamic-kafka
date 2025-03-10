import random
import string
import time
import subprocess
from producer import DynamicBatchProducer

NUM_MSG = 100000
MSG_SIZE = 100
INTERFACE = "eth0"  # Change if needed
LATENCY_MS = 10  # Latency in milliseconds


def generate_payload(msg_size, num_msg):
    """Generates random message payloads."""
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

    latency_targets = [0.001, 0.002, 0.003, 0.004, 0.005]
    end_to_end = []
    file_names = []

    for target in latency_targets:
        payload = generate_payload(MSG_SIZE, NUM_MSG)
        producer = DynamicBatchProducer(target)
        start_time = time.time()
        producer.send_data(payload, "mytopic")
        end_time = time.time()
        end_to_end.append(end_time - start_time)
        producer.print_latencies(str(target))
        file_names.append("dynamic_per_msg_latency" + str(target) + ".txt")
        file_names.append("dynamic_batch_size" + str(target) + ".txt")

    for i in range(len(end_to_end)):
        print(
            f"End-to-end latency with latency target {latency_targets[i]}: {end_to_end[i]}"
        )
    for f in file_names:
        print(f"{f}")
