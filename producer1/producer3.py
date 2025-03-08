import time
import os
from confluent_kafka import Producer


class DynamicBatchProducer:
    def __init__(
        self,
        target_latency,
        initial_batch_size=200,
        effective_window=50,
        kp=0.1,
        ki=0.01,
        kd=0.05,
        max_batch_size=10000,
    ):
        """
        :param target_latency: desired average latency in seconds
        :param initial_batch_size: starting batch size (number of messages)
        :param effective_window: effective window size for the EMA
        :param kp: proportional gain
        :param ki: integral gain
        :param kd: derivative gain
        :param max_batch_size: maximum allowed batch size
        """
        self.target_latency = target_latency  # in seconds
        self.batch_size = initial_batch_size
        self.effective_window = effective_window
        # Calculate smoothing factor for EMA based on effective window size
        self.alpha = 2 / (effective_window + 1)
        self.ema_latency = None  # will hold the exponential moving average of latencies
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0.0
        self.prev_error = 0.0
        self.max_batch_size = max_batch_size

        # Create initial producer configuration.
        self.producer_conf = {
            "bootstrap.servers": "kafka:9092",
            "batch.size": self.batch_size,
            "linger.ms": int(self.batch_size * self.target_latency * 1000),
        }
        self.producer = Producer(self.producer_conf)

        # Open a log file for writing delivery reports.
        self.log_file = open("delivery_reports.log", "w")
        self.log_file.write("timestamp,message_key,latency,batch_size,linger_ms\n")

    def _update_producer_parameters(self, avg_latency):
        """
        Use PID control to update the batch size (and derived linger.ms)
        based on the difference between measured average latency and target.
        """
        error = avg_latency - self.target_latency
        self.integral += error
        derivative = error - self.prev_error
        adjustment = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.prev_error = error

        # If measured latency is too high, adjustment is positive and we reduce batch size.
        new_batch_size = self.batch_size - adjustment

        # Clamp the new batch size to at least 1 and at most max_batch_size.
        new_batch_size = max(1, min(int(new_batch_size), self.max_batch_size))
        if new_batch_size != self.batch_size:
            print(
                f"[PID] Adjusting batch size from {self.batch_size} to {new_batch_size} "
                f"(EMA latency: {avg_latency:.4f}s vs target {self.target_latency}s)"
            )
            self.batch_size = new_batch_size

            # Update linger.ms based on the new batch size.
            new_linger_ms = int(self.batch_size * self.target_latency * 1000)
            self.producer_conf["batch.size"] = self.batch_size
            self.producer_conf["linger.ms"] = new_linger_ms

            # Reinitialize the producer (after flushing the current one)
            self.producer.flush()
            self.producer = Producer(self.producer_conf)

    def delivery_report(self, err, msg):
        """
        Delivery report callback. Updates the EMA for latency and logs the delivery outcome.
        """
        timestamp = time.time()
        message_key = msg.key().decode("utf-8") if msg.key() is not None else ""
        if err is not None:
            # Log errors with a placeholder for latency.
            report_line = f"{timestamp},{message_key},ERROR,{self.batch_size},{self.producer_conf['linger.ms']}\n"
            print(f"Delivery failed for record {message_key}: {err}")
        else:
            # Assume msg.latency() returns the delivery latency in seconds.
            latency = msg.latency()
            # Update the exponential moving average without storing all values.
            if self.ema_latency is None:
                self.ema_latency = latency
            else:
                self.ema_latency = (
                    self.alpha * latency + (1 - self.alpha) * self.ema_latency
                )
            report_line = (
                f"{timestamp},{message_key},{latency},"
                f"{self.batch_size},{self.producer_conf['linger.ms']}\n"
            )
            print(
                f"Produced record to {msg.topic()} partition [{msg.partition()}] "
                f"@ offset {msg.offset()} with latency {latency:.4f}s"
            )
        self.log_file.write(report_line)
        self.log_file.flush()

    def send_data(self, data, topic_name):
        """
        Sends the data (a list of messages) to the given Kafka topic.
        Periodically flushes and updates the dynamic parameters using the PID controller.
        """
        total_messages = len(data)
        start_time = time.time()
        msg_count = 0

        for i, value in enumerate(data):
            self.producer.produce(
                topic_name,
                key=str(i).encode("utf-8"),
                value=value if isinstance(value, bytes) else value.encode("utf-8"),
                callback=self.delivery_report,
            )
            msg_count += 1

            # Once we have produced a full batch, wait for delivery reports and update parameters.
            if msg_count % self.batch_size == 0:
                self.producer.flush()

                # If we have an EMA value, update the parameters.
                if self.ema_latency is not None:
                    self._update_producer_parameters(self.ema_latency)
                else:
                    print("No latency measurements received yet.")

        # Flush any remaining messages.
        self.producer.flush()
        end_time = time.time()
        total_time = end_time - start_time
        print(f"Sent {total_messages} messages in {total_time:.2f} seconds.")
        self.log_file.close()


def generate_random_message(fixed_size):
    """Generate a random message of fixed size in bytes."""
    return os.urandom(fixed_size)


if __name__ == "__main__":
    topic = "mytopic"
    # Create a list of messages (for example, 1,000,000 messages)
    total_msgs = 1000000
    message_size = 512  # bytes

    # Generate messages as a list of byte strings.
    messages = [generate_random_message(message_size) for _ in range(total_msgs)]

    # Create an instance with a target latency of 1 millisecond (0.001 seconds)
    producer = DynamicBatchProducer(
        target_latency=0.001,
        initial_batch_size=200,
        effective_window=50,  # This approximates the previous sliding window size
        kp=0.1,
        ki=0.01,
        kd=0.05,
    )

    # Send all the messages to the Kafka topic.
    producer.send_data(messages, topic)
