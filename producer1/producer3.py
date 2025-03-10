import time
import json
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, KafkaException, NewTopic


class DynamicBatchProducer:
    def __init__(self, latency, kp, ki, kd):
        self.batch_size = 100000
        self.target_latency = latency
        self.delivery_latency = None  # latest latency measurement
        self.max_latency = 0
        self.effective_window = 50  # effective window size for the EMA
        self.alpha = 2 / (self.effective_window + 1)  # smoothing factor for EMA
        self.ema_latency = None  # will hold the exponential moving average of latencies
        self.past_latency = None
        self.latencies = []
        self.rtt = []

        # PID variables
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral_error = 0.0
        self.last_error = 0.0

        self.producer_conf = {
            "bootstrap.servers": "kafka:9092",
            "statistics.interval.ms": 1,
            "batch.size": self.batch_size,
            "linger.ms": 1000,
        }
        self.producer = Producer(self.producer_conf, stats_cb=self.stats_callback)

    def pid_adjustment(self, measured_latency):
        """
        Compute the PID-based adjustment using EMA latency vs. target.
        A positive (measured_latency > target) error leads to a positive
        adjustment, which we will subtract from batch size.
        """
        error = measured_latency - self.target_latency
        self.integral_error += error
        derivative = error - self.last_error
        self.last_error = error

        # The controller output
        return self.kp * error + self.ki * self.integral_error + self.kd * derivative

    def send_data(self, data, topic_name):
        self.check_broker_ready("kafka:9092", topic_name)
        curr_sent_size = 0
        self.producer.produce(
            topic_name, key=str(0), value=data[0], callback=self.delivery_report
        )
        self.producer.flush()
        for i in range(1, len(data)):
            self.producer.produce(
                topic_name, key=str(i), value=data[i], callback=self.delivery_report
            )
            if self.delivery_latency == None or self.ema_latency == None:
                self.producer.flush()
            curr_sent_size += len(str(i).encode("utf-8")) + len(data[i])
            if curr_sent_size >= self.batch_size:
                curr_sent_size = 0
                while (
                    self.delivery_latency == None
                    or self.ema_latency == None
                    or self.past_latency != None
                    and self.past_latency == self.ema_latency
                ):
                    self.past_latency = self.ema_latency
                    self.producer.poll(self.target_latency)
                    break
            else:
                self.producer.poll(0)

            # Check if our EMA (or the last measurement) exceeds our thresholds.
            if (
                self.ema_latency is not None
                and self.delivery_latency is not None
                and (
                    self.ema_latency > self.target_latency
                    or self.delivery_latency > self.target_latency * 2
                )
            ):
                # Instead of dividing batch.size by 5, use the PID controller:
                adjustment = self.pid_adjustment(self.ema_latency)
                new_batch_size = self.batch_size - adjustment
                # Enforce a minimum batch size of 1, then cast to int.
                self.producer_conf["batch.size"] = max(1, int(new_batch_size))
                self.batch_size = self.producer_conf["batch.size"]

                self.producer.flush()
                self.producer = Producer(
                    self.producer_conf, stats_cb=self.stats_callback
                )
                print(
                    f"Batch size was decreased with current latency {self.delivery_latency}, "
                    f"ema latency {self.ema_latency}, with current batch size {self.batch_size}"
                )

                self.ema_latency = None
                self.delivery_latency = None
                self.past_latency = None
                curr_sent_size = 0

            elif (
                self.ema_latency is not None
                and self.delivery_latency is not None
                and (
                    self.ema_latency != 0 and self.ema_latency * 2 < self.target_latency
                )
            ):
                # Instead of multiplying batch.size by 10, use the PID controller:
                adjustment = self.pid_adjustment(self.ema_latency)
                new_batch_size = self.batch_size - adjustment  # same formula
                # For negative error, 'adjustment' will be negative => new_batch_size bigger
                self.producer_conf["batch.size"] = max(1, int(new_batch_size))
                self.batch_size = self.producer_conf["batch.size"]

                self.producer.flush()
                self.producer = Producer(
                    self.producer_conf, stats_cb=self.stats_callback
                )
                print(
                    f"Batch size was increased with current latency {self.delivery_latency}, "
                    f"ema latency {self.ema_latency}, with current batch size {self.batch_size}"
                )

                self.ema_latency = None
                self.delivery_latency = None
                self.past_latency = None
                curr_sent_size = 0

        self.producer.flush()
        print(f"Last latency: {self.delivery_latency}")
        print(f"Max latency: {self.max_latency * 1_000_000}")  # printed in microseconds

    def delivery_report(self, err, msg):
        if err is not None:
            print(f"Delivery failed for record {msg.key()}: {err}")
        else:
            latency = msg.latency()  # assume this returns latency in seconds
            if self.delivery_latency is None:
                self.delivery_latency = 0
            else:
                self.delivery_latency = latency

            self.latencies.append(latency)
            # Update EMA without storing all values.
            if self.ema_latency is None:
                self.ema_latency = 0
            else:
                self.ema_latency = (
                    self.alpha * latency + (1 - self.alpha) * self.ema_latency
                )
            # Track the maximum latency observed.
            self.max_latency = max(self.max_latency, latency)

    def stats_callback(self, stats_json):
        stats = json.loads(stats_json)
        if "brokers" in stats:
            for broker_id, broker_data in stats["brokers"].items():
                if "rtt" in broker_data:
                    self.rtt.append(broker_data["rtt"]["avg"] * 1e-6)

    def print_latencies(self):
        with open("pid_dynamic_per_msg_latency.txt", "a") as file:
            for l in self.latencies:
                file.write(f"{l}\n")
        with open("dynamic_rtt.txt", "a") as file:
            for l in self.rtt:
                file.write(f"{l}\n")

    def check_broker_ready(self, server, topic_name):
        admin_client = AdminClient({"bootstrap.servers": server})
        while True:
            try:
                broker_metadata = admin_client.list_topics(timeout=10)
                print("Broker is ready and available.")
                if topic_name in broker_metadata.topics:
                    print(f"Topic '{topic_name}' exists.")
                else:
                    self.create_topic(server, topic_name, 3, 1)
                return

            except KafkaException as e:
                print(f"Waiting for broker to become available: {str(e)}")
                time.sleep(1)

    def create_topic(self, server, topic_name, num_partitions=1, replication_factor=1):
        admin_client = AdminClient({"bootstrap.servers": server})
        # Define the topic configuration
        new_topic = NewTopic(
            topic_name,
            num_partitions=num_partitions,
            replication_factor=replication_factor,
        )
        try:
            # Create the topic asynchronously
            fs = admin_client.create_topics([new_topic])

            # Wait for operation to complete
            fs[topic_name].result()
            print(f"Topic '{topic_name}' created successfully.")
        except KafkaException as e:
            print(f"Error creating topic: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
