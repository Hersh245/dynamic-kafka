import numpy as np
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser(description="Plot latencies from a text file.")
parser.add_argument("filename", type=str, help="Path to the text file containing latency values.")
args = parser.parse_args()

latencies = np.loadtxt(args.filename)

plt.figure(figsize=(10, 5))
plt.hist(latencies, bins=50, edgecolor="black", alpha=0.7)
plt.xlabel("Latency (seconds)")
plt.ylabel("Frequency")
plt.title("Latency Distribution")
plt.show()

plt.figure(figsize=(10, 5))
plt.plot(latencies, marker="o", linestyle="-", markersize=2)
plt.xlabel("Request Index")
plt.ylabel("Latency (seconds)")
plt.title("Latency Over Time")
plt.grid(True)
plt.show()

sampled_indices = np.arange(1, len(latencies), 100)
sampled_latencies = latencies[sampled_indices]

plt.figure(figsize=(10, 5))
plt.plot(sampled_indices, sampled_latencies, marker="o", linestyle="-", markersize=3, label="Sampled Latency")
plt.xlabel("Request Index")
plt.ylabel("Latency (seconds)")
plt.title("Latency Over Time (Sampled Every 100 Points)")
plt.grid(True)
plt.legend()
plt.show()