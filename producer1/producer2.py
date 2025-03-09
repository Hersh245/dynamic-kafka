import time
import json
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, KafkaException

class DynamicBatchProducer:
    def __init__(self, latency):
        self.batch_size = 100000
        self.target_latency = latency
        self.delivery_latency = latency  # latest latency measurement
        self.max_latency = 0
        self.effective_window = 50  # effective window size for the EMA
        self.alpha = 2 / (self.effective_window + 1)  # smoothing factor for EMA
        self.ema_latency = None  # will hold the exponential moving average of latencies
        self.latencies = []

        self.producer_conf = {
            "bootstrap.servers": "kafka:9092",
            "statistics.interval.ms": 2000,
            "batch.size": self.batch_size,
            "linger.ms": 10,
        }
        self.producer = Producer(self.producer_conf, stats_cb=self.stats_callback)

    def send_data(self, data, topic_name):
        self.check_broker_ready("kafka:9092")
        for i in range(len(data)):
            self.producer.produce(
                topic_name, key=str(i), value=data[i], callback=self.delivery_report
            )
            self.producer.flush()
            # Check if our EMA (or the last measurement) exceeds our thresholds.
            if self.ema_latency is not None and (
                self.ema_latency > self.target_latency
                or self.delivery_latency > self.target_latency * 1.5
            ):
                # Decrease batch size if the average latency is too high.
                self.producer_conf["batch.size"] = max(
                    1, self.producer_conf["batch.size"] - 100
                )
                self.batch_size = self.producer_conf["batch.size"]
                self.producer = Producer(
                    self.producer_conf, stats_cb=self.stats_callback
                )
                print(f"Batch size was changed with latency {self.delivery_latency}")

        self.producer.flush()
        print(f"Last latency: {self.delivery_latency}")
        print(f"Max latency: {self.max_latency * 1_000_000}")  # printed in microseconds

    def delivery_report(self, err, msg):
        if err is not None:
            print(f"Delivery failed for record {msg.key()}: {err}")
        else:
            latency = msg.latency()  # assume this returns latency in seconds
            self.delivery_latency = latency
            
            self.latencies.append(latency)
            # Update EMA without storing all values.
            if self.ema_latency is None:
                self.ema_latency = latency
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
                formatted_json = json.dumps(broker_data, indent=4)
                print(formatted_json)
                if "topics" in broker_data:
                    for topic_name, topic_data in broker_data["topics"].items():
                        print(
                            f"Broker {broker_id}: topic {topic_name} has a batch sized average of {topic_data['batchsize']['avg']}"
                        )
    
    def print_latencies(self):
        with open('dynamic_per_msg_latency.txt', "a") as file:
            for l in self.latencies:
                file.write(f"{l}\n")
                
    def check_broker_ready(self, bootstrap_servers):
        admin_client = AdminClient({'bootstrap.servers': bootstrap_servers})
        while True:
            try:
                broker_metadata = admin_client.list_topics(timeout=10)
                print("Broker is ready and available.")
                return broker_metadata 
            except KafkaException as e:
                print(f"Waiting for broker to become available: {str(e)}")
                time.sleep(1)
