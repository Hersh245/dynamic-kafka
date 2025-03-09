#!/bin/bash


CONTAINER_NAME="kafka-producer-1"

# Destination directory on your local machine (Windows path)
DEST_DIR="/Users/hanxu/OneDrive/Desktop/school/grad school/Freshman/CS 239/MuCache/dynamic-kakfa/tests"

# Files to copy
FILES=(
  "vanilla_per_msg_latency_batchsize_100.txt"
  "vanilla_per_msg_latency_batchsize_200.txt"
  "vanilla_per_msg_latency_batchsize_500.txt"
  "vanilla_per_msg_latency_batchsize_1000.txt"
  "vanilla_per_msg_latency_batchsize_2000.txt"
  "vanilla_per_msg_latency_batchsize_5000.txt"
  "vanilla_per_msg_latency_batchsize_10000.txt"
  "vanilla_per_msg_latency_batchsize_20000.txt"
  "vanilla_rtt_batchsize_100.txt"
  "vanilla_rtt_batchsize_200.txt"
  "vanilla_rtt_batchsize_500.txt"
  "vanilla_rtt_batchsize_1000.txt"
  "vanilla_rtt_batchsize_2000.txt"
  "vanilla_rtt_batchsize_5000.txt"
  "vanilla_rtt_batchsize_10000.txt"
  "vanilla_rtt_batchsize_20000.txt"
)

# FILES=(
#   "dynamic_per_msg_latency.txt"
#   "dynamic_rtt.txt"
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