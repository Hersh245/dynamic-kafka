import numpy as np
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser(description="Plot latencies from a text file.")
parser.add_argument("filename", type=str, help="Path to the text file containing latency values.")
args = parser.parse_args()

latencies = np.loadtxt(args.filename)

# plt.figure(figsize=(10, 5))
# plt.hist(latencies, bins=50, edgecolor="black", alpha=0.7)
# plt.xlabel("Latency (seconds)")
# plt.ylabel("Frequency")
# plt.title("Latency Distribution")
# plt.show()

# plt.figure(figsize=(10, 5))
# plt.plot(latencies, marker="o", linestyle="-", markersize=2)
# plt.xlabel("Request Index")
# plt.ylabel("Latency (seconds)")
# plt.title("Latency Over Time")
# plt.grid(True)
# plt.show()

window_size = 100
mean_latencies = np.array([
    np.mean(latencies[i:i + window_size])
    for i in range(0, len(latencies), window_size)
])

plt.figure(figsize=(10, 5))
plt.plot(mean_latencies, marker="o", linestyle="-", markersize=3, label="Sampled Latency")
plt.xlabel("Request Index")
plt.ylabel("Latency (seconds)")
plt.title("Latency Over Time (Sampled Every 1000 Points) for " + args.filename)
plt.grid(True)
plt.legend()
plt.show()