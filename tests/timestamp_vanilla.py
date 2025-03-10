import glob
import pandas as pd
import matplotlib.pyplot as plt
import os

# Use glob to find matching files
latency_files = sorted(glob.glob("latency_vanilla_per_msg_latency_batchsize*"))

# We assume the files correspond in sorted order, i.e.:
#   dynamic_batch_size0.0001.txt  <-->  dynamic_per_msg_latency0.0001.txt
#   dynamic_batch_size0.0002.txt  <-->  dynamic_per_msg_latency0.0002.txt
# etc.
#
# If your naming convention differs, you might need a more robust matching strategy.

for latency_file in latency_files:
    # Extract the suffix (e.g., 0.0001) from the file name
    # This helps label the plot or output file
    param = os.path.splitext(latency_file)[0].replace(
        "latency_vanilla_per_msg_latency_batchsize", ""
    )

    print(f"latency file: {latency_file} (param = {param})")

    # Read the CSV data
    # Each file has two columns (timestamp, batch_size) or (timestamp, latency) without a header
    latency_df = pd.read_csv(
        latency_file, header=None, names=["timestamp", "latency"], skiprows=1
    )

    # Standardize the time to start at 0
    start_time = latency_df["timestamp"].min()
    latency_df["time"] = latency_df["timestamp"] - start_time

    # Sort by time just in case the file isn't strictly sorted
    latency_df.sort_values("time", inplace=True)

    # Compute a 10,000-point rolling average for the latency
    # You might need to adjust 'center=True' or other params, depending on your needs
    latency_df["latency_ma"] = latency_df["latency"].rolling(100, min_periods=1).mean()

    # Create a plot
    plt.figure(figsize=(12, 6))

    # Plot the moving average latency (ignore the NaN at the start until we have 10,000 points)
    plt.plot(
        latency_df["time"],
        latency_df["latency_ma"],
        label="Moving Average (10k) Latency",
        color="blue",
    )

    median_latency = latency_df["latency"].median()
    plt.axhline(
        y=median_latency,
        color="green",
        linestyle="--",
        label=f"Median Latency = {median_latency:.3f}",
    )

    # Overlay vertical lines (and labels) for batch size changes
    # We'll place the label roughly in the middle of the y-axis (50% of current y-limit)
    ymin, ymax = plt.ylim()
    y_mid = ymin + 0.5 * (ymax - ymin)

    plt.title(f"Latency vs. Time with Batch Size (param={param})")
    plt.xlabel("Time (s) (starting from 0)")
    plt.ylabel("Latency (moving avg)")
    plt.legend(loc="upper right")

    # Tight layout for better spacing
    plt.tight_layout()

    # Save each figure to a PNG (or show directly)
    out_name = f"plot_{param}.png"
    plt.savefig(out_name)
    plt.close()

    print(f"Saved plot as {out_name}")
