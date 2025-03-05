import time
from confluent_kafka import Producer
        
class DynamicBatchProducer:
    def __init__(self, latency):
        self.batch_size = 2
        self.data = []
        self.target_latency = latency
        self.current_latency = latency
        self.producer_conf = {
            "bootstrap.servers": "kafka:9092",
            "batch.size": self.batch_size,
            "linger.ms": latency * self.batch_size,
            }
        self.producer_conf["batch.size"] = self.batch_size
        self.producer = Producer(self.producer_conf)
        
    def send_data(self, data, topic_name):
        historical_cnt = 0
        for i in range(len(data)):
            historical_cnt += 1
            self.producer.produce(topic_name, key=str(i), value=data[i], callback=self.delivery_report)
            if historical_cnt >= self.batch_size:
                historical_cnt = 0
                self.producer.poll(0)
                print("polling")
                if self.current_latency > self.target_latency:
                    self.producer.flush()
                    self.producer_conf["batch.size"] = max(1,self.producer_conf["batch.size"] - 100)
                    self.batch_size = self.producer_conf["batch.size"]
                    self.producer = (self.producer_conf)
                    print("Batch size was changed")
                else:
                    print(self.current_latency)
        self.producer.flush()
                    
    def delivery_report(self, err, msg):
        if err is not None:
            print(f"Delivery failed for record {msg.key()}: {err}")
        else:
            self.current_latency = msg.latency()
            print(
                f"Producer2 successfully produced record to "
                f"{msg.topic()} partition [{msg.partition()}] @ offset {msg.offset()} with latency {msg.latency()}"
            )

            
        
        
# Producer2 config with a different batch size, linger, etc.


# producer = Producer(producer_conf)



topic_name = "mytopic"
data = []
for i in range(20):
    value = f"Hello from Producer2 - {i}"
    data.append(value)
producer = DynamicBatchProducer(0.001)
producer.send_data(data, topic_name)

# producer.flush()
# print("Producer2 finished sending messages.")
