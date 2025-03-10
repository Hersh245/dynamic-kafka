import glob
import pandas as pd
import matplotlib.pyplot as plt
import os

# Use glob to find matching files
batch_files = sorted(glob.glob("dynamic_batch_size0.*.txt"))
latency_files = sorted(glob.glob("dynamic_per_msg_latency0.*.txt"))

print(len(batch_files), len(latency_files))

if len(batch_files) != len(latency_files):
    print("Error: Number of batch and latency files not equal. Exiting...")
    exit()

# We assume the files correspond in sorted order, i.e.:
#   dynamic_batch_size0.0001.txt  <-->  dynamic_per_msg_latency0.0001.txt
#   dynamic_batch_size0.0002.txt  <-->  dynamic_per_msg_latency0.0002.txt
# etc.
#
# If your naming convention differs, you might need a more robust matching strategy.

for batch_file, latency_file in zip(batch_files, latency_files):
    # Extract the suffix (e.g., 0.0001) from the file name
    # This helps label the plot or output file
    param = os.path.splitext(batch_file)[0].replace("dynamic_batch_size", "")

    print(
        f"Processing batch file: {batch_file} and latency file: {latency_file} (param = {param})"
    )

    # Read the CSV data
    # Each file has two columns (timestamp, batch_size) or (timestamp, latency) without a header
    batch_df = pd.read_csv(batch_file, header=None, names=["timestamp", "batch_size"])
    latency_df = pd.read_csv(
        latency_file, header=None, names=["timestamp", "latency"], skiprows=1
    )

    # Standardize the time to start at 0
    start_time = min(batch_df["timestamp"].min(), latency_df["timestamp"].min())
    batch_df["time"] = batch_df["timestamp"] - start_time
    latency_df["time"] = latency_df["timestamp"] - start_time

    # Sort by time just in case the file isn't strictly sorted
    batch_df.sort_values("time", inplace=True)
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

    for i in range(len(batch_df)):
        t = batch_df.iloc[i]["time"]
        b = batch_df.iloc[i]["batch_size"]
        # Draw a vertical line
        plt.axvline(x=t, color="red", alpha=0.3, linestyle="--")
        # Place text at that line
        # Rotate to 90 degrees so it doesn't overlap too much horizontally
        plt.text(
            t,
            y_mid,
            str(b),
            rotation=90,
            verticalalignment="center",
            color="red",
            fontsize=7,
        )

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
