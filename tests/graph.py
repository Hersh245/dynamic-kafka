import numpy as np
import matplotlib.pyplot as plt
import argparse
import os

# Get all .txt files in the current directory
txt_files = [f for f in os.listdir('.') if f.endswith('.txt')]

# parser = argparse.ArgumentParser(description="Plot latencies from a text file.")
# parser.add_argument("filename", type=str, help="Path to the text file containing latency values.")
# args = parser.parse_args()
for f in txt_files:
    latencies = np.loadtxt(f)
    window_size = 100
    mean_latencies = np.array([
        np.mean(latencies[i:i + window_size])
        for i in range(0, len(latencies), window_size)
    ])

    plt.figure(figsize=(10, 5))
    plt.plot(mean_latencies, marker="o", linestyle="-", markersize=3, label="Sampled Latency")
    plt.xlabel("Request Index")
    plt.ylabel("Latency (seconds)")
    plt.title("Latency Over Time (Sampled Every 100 Points) for " + f)
    plt.grid(True)
    plt.legend()

    # Save figure with the same name as the text file but as a .png
    save_path = f"{os.path.splitext(f)[0]}.png"
    plt.savefig(save_path, dpi=300)
    plt.close()  # Close the figure to free memory

    print(f"Saved plot: {save_path}")
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

