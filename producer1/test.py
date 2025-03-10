import random
import string
import time
import subprocess
from producer import DynamicBatchProducer

NUM_MSG = 1000000
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

def add_latency(interface="eth0", delay_ms=10):
    """Injects network latency using `tc`."""
    print(f"Adding {delay_ms}ms latency on {interface}...")
    subprocess.run(f"tc qdisc add dev {interface} root netem delay {delay_ms}ms", shell=True, check=True)

def remove_latency(interface="eth0"):
    """Removes the network latency rule."""
    print(f"Removing latency on {interface}...")
    subprocess.run(f"tc qdisc del dev {interface} root netem", shell=True, check=True)

if __name__ == "__main__":
    payload = generate_payload(MSG_SIZE, NUM_MSG)
    producer = DynamicBatchProducer(0.005)

    start_time = time.time()

    # Divide messages into thirds
    first_third = NUM_MSG // 3
    second_third = 2 * (NUM_MSG // 3)

    # Send first third normally
    producer.send_data(payload[:first_third], "mytopic")

    # Add 10ms latency
    add_latency(INTERFACE)

    # Send second third with latency
    producer.send_data(payload[first_third:second_third], "mytopic")

    # Remove latency
    remove_latency(INTERFACE)

    # Send final third normally
    producer.send_data(payload[second_third:], "mytopic")

    end_time = time.time()
    print(f"End-to-end latency: {end_time - start_time}")
    producer.print_latencies()
