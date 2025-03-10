#!/bin/bash


CONTAINER_NAME="kafka-producer-1"

# Destination directory on your local machine (Windows path)
DEST_DIR="/Users/hanxu/OneDrive/Desktop/school/grad school/Freshman/CS 239/MuCache/dynamic-kakfa/tests"

# Files to copy
FILES=(
  "vanilla_per_msg_latency_batchsize_1000.txt"
  "vanilla_per_msg_latency_batchsize_2000.txt"
  "vanilla_per_msg_latency_batchsize_3000.txt"
  "vanilla_per_msg_latency_batchsize_4000.txt"
  "vanilla_per_msg_latency_batchsize_5000.txt"
  "vanilla_per_msg_latency_batchsize_6000.txt"
  "vanilla_per_msg_latency_batchsize_7000.txt"
  "vanilla_per_msg_latency_batchsize_8000.txt"
  "vanilla_per_msg_latency_batchsize_9000.txt"
  "vanilla_per_msg_latency_batchsize_10000.txt"
  "vanilla_per_msg_latency_batchsize_11000.txt"
  "vanilla_per_msg_latency_batchsize_12000.txt"
  "vanilla_per_msg_latency_batchsize_13000.txt"
  "vanilla_per_msg_latency_batchsize_14000.txt"
  "vanilla_per_msg_latency_batchsize_15000.txt"
  "vanilla_per_msg_latency_batchsize_16000.txt"
  "vanilla_per_msg_latency_batchsize_17000.txt"
  "vanilla_per_msg_latency_batchsize_18000.txt"
  "vanilla_per_msg_latency_batchsize_19000.txt"
  "vanilla_per_msg_latency_batchsize_20000.txt"
  "vanilla_rtt_batchsize_1000.txt"
  "vanilla_rtt_batchsize_2000.txt"
  "vanilla_rtt_batchsize_3000.txt"
  "vanilla_rtt_batchsize_4000.txt"
  "vanilla_rtt_batchsize_5000.txt"
  "vanilla_rtt_batchsize_6000.txt"
  "vanilla_rtt_batchsize_7000.txt"
  "vanilla_rtt_batchsize_8000.txt"
  "vanilla_rtt_batchsize_9000.txt"
  "vanilla_rtt_batchsize_10000.txt"
  "vanilla_rtt_batchsize_11000.txt"
  "vanilla_rtt_batchsize_12000.txt"
  "vanilla_rtt_batchsize_13000.txt"
  "vanilla_rtt_batchsize_14000.txt"
  "vanilla_rtt_batchsize_15000.txt"
  "vanilla_rtt_batchsize_16000.txt"
  "vanilla_rtt_batchsize_17000.txt"
  "vanilla_rtt_batchsize_18000.txt"
  "vanilla_rtt_batchsize_19000.txt"
  "vanilla_rtt_batchsize_20000.txt"
)

# FILES=(
#   "dynamic_per_msg_latency.txt"
#   "dynamic_rtt.txt"
# )

# FILES=(
#   "pid_dynamic_per_msg_latency.txt"
#   "pid_dynamic_rtt.txt"
# )

# Ensure the destination directory exists
mkdir -p "$DEST_DIR"

# Loop through and copy the files
for FILE in "${FILES[@]}"; do
  # Construct the full path within the container
  CONTAINER_PATH="$FILE" # Assuming files are at the root of the container

  # Construct the local destination path
  LOCAL_PATH="$DEST_DIR/$FILE"

  # Use docker cp to copy the file
  docker cp "$CONTAINER_NAME:$CONTAINER_PATH" "$LOCAL_PATH"
  echo "Copied: $FILE"
done

echo "Copy process completed."