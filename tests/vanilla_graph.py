import glob
import re
import pandas as pd
import matplotlib.pyplot as plt


def plot_latency_with_moving_average(
    file_pattern="vanilla_per_msg_latency_batchsize_*.txt", window_size=100, y_limit=0.1
):
    """
    Reads all files matching `file_pattern`, computes a rolling average,
    and plots them on the same figure. Caps the y-axis at y_limit.
    """

    plt.figure(figsize=(10, 6))

    for filename in sorted(glob.glob(file_pattern)):
        match = re.search(r"vanilla_per_msg_latency_batchsize_(1.000)\.txt", filename)
        if not match:
            continue

        batch_size = match.group(1)

        # Read the file (floating values in one column)
        df = pd.read_csv(filename, header=None, names=["latency"])

        # Rolling average
        df["smoothed"] = df["latency"].rolling(window=window_size, min_periods=1).mean()

        # Plot
        plt.plot(df.index, df["smoothed"], label=f"batch.size = {batch_size}")

    plt.title("Latency vs. Message Index (Smoothed by Rolling Average)")
    plt.xlabel("Message Index")
    plt.ylabel("Latency (seconds)")

    # Limit the y-axis to 0.1 seconds
    plt.ylim(top=y_limit)
    plt.ylim(bottom=0.001)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # Example usage:
    plot_latency_with_moving_average(
        file_pattern="vanilla_per_msg_latency_batchsize_*.txt",
        window_size=500000,
        y_limit=0.003,  # cap the y-axis at 0.1 seconds
    )
