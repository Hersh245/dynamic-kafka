import random
import string
import time
from producer import DynamicBatchProducer

NUM_MSG = 100000
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
    producer = DynamicBatchProducer(0.005)
    start_time = time.time()
    producer.send_data(payload, "mytopic")
    end_time = time.time()
    print(f"end to end latency is {end_time - start_time}")
    producer.print_latencies()