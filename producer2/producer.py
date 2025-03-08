import time
import json
from confluent_kafka import Producer
        
class DynamicBatchProducer:
    def __init__(self, latency):
        self.batch_size = 100000
        self.data = []
        self.target_latency = latency
        self.delivery_latency = latency
        self.max_latency = 0
        self.producer_conf = {
            "bootstrap.servers": "kafka:9092",
            'statistics.interval.ms': 2000,
            "batch.size": self.batch_size,
            "linger.ms": 10,
            }
        self.producer_conf["batch.size"] = self.batch_size
        self.producer = Producer(self.producer_conf, stats_cb=self.stats_callback)
        
    def send_data(self, data, topic_name):
        latencies = []
        for i in range(len(data)):
            self.producer.produce(topic_name, key=str(i), value=data[i], callback=self.delivery_report)
            self.producer.flush()
            latencies.append(self.delivery_latency)
            if sum(latencies)/len(latencies) > self.target_latency or latencies[-1] > self.target_latency * 1.5: 
                self.producer_conf["batch.size"] = max(1,self.producer_conf["batch.size"] - 100)
                self.batch_size = self.producer_conf["batch.size"]
                self.producer = Producer(self.producer_conf, stats_cb=self.stats_callback)
                print(f"Batch size was changed with latency {self.delivery_latency}")
        self.producer.flush()
        print(f"last latency {self.delivery_latency}")
        print(f"max latency is {max(latencies) * 1000000}")
                    
    def delivery_report(self, err, msg):
        if err is not None:
            print(f"Delivery failed for record {msg.key()}: {err}")
        else:
            self.delivery_latency = msg.latency()
            self.report = True
            # print(
            #     f"Producer2 successfully produced record {msg.value()} to "
            #     f"{msg.topic()} partition [{msg.partition()}] @ offset {msg.offset()} with latency {msg.latency()}"
            # ) 
            
    def stats_callback(self, stats_json):
        stats = json.loads(stats_json)
        if "brokers" in stats:
            for broker_id, broker_data in stats["brokers"].items():
                formatted_json = json.dumps(broker_data, indent=4)
                print(formatted_json)
                if "topics" in broker_data:
                    for topic_name, topic_data in broker_data["topics"].items():
                        print(f"Broker {broker_id}: topic {topic_name} has a batch sized average of {topic_data["batchsize"]["avg"]}")

        
