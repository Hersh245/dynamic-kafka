#!/bin/bash

# Configuration - Adjust delay and loss as needed
LATENCY="100ms"   # Add network latency
JITTER="10ms"     # Add variation
LOSS="0%"         # Packet loss

# Kafka container name (from Docker Compose)
KAFKA_PRODUCER="kafka-producer-1"

# Wait for the Kafka producer to be in running state
echo "Waiting for Kafka producer ($KAFKA_PRODUCER) to start..."
while ! docker ps --format "{{.Names}}" | grep -q "^$KAFKA_PRODUCER$"; do
  sleep 0.5  # Check every 0.5 seconds
done

echo "Kafka producer ($KAFKA_PRODUCER) is running. Waiting 1 second before applying latency..."
sleep 1  # Wait an extra second

# Get the Docker network interface (docker0 or bridge or similar)
DOCKER_INTERFACE="eth0"

# Apply network latency on the Docker network interface
echo "Applying network latency to Docker network interface ($DOCKER_INTERFACE)..."
sudo tc qdisc add dev "$DOCKER_INTERFACE" root netem delay $LATENCY $JITTER loss $LOSS
echo "Latency applied: $LATENCY, Jitter: $JITTER, Packet Loss: $LOSS"

# Verify applied latency
echo "Current network settings:"
sudo tc -s qdisc show dev "$DOCKER_INTERFACE"

# Wait 1 second before reverting latency
sleep 1

# Remove the latency
echo "Reverting network latency..."
sudo tc qdisc del dev "$DOCKER_INTERFACE" root netem
echo "Latency reverted."

# Verify that latency is removed
echo "Current network settings after removal:"
sudo tc -s qdisc show dev "$DOCKER_INTERFACE"