import time
from confluent_kafka import Consumer, KafkaException, KafkaError


# Configure the consumer
consumer_conf = {
    "bootstrap.servers": "kafka:9092",  # Kafka broker(s) address
    "group.id": "python-consumer-group",  # Consumer group ID
    "auto.offset.reset": "earliest"  # Start consuming from the beginning if no offsets are committed
}

# Create the consumer instance
consumer = Consumer(consumer_conf)

# Subscribe to 'mytopic' and 'mytopic2'
consumer.subscribe(['mytopic', 'mytopic2'])


# Poll for new messages for about 60 seconds
end_time = time.time() + 60

try:
    print(f'Polling Begin')
    while time.time() < end_time:
        msg = consumer.poll(1.0)  # Timeout of 1 second
        print(f'Current time: {time.time()}')
        if msg is None:
            # No message available within the timeout period
            print("No messages received, waiting...")
            continue
        if msg.error():
            # Error handling
            if msg.error().code() == KafkaError._PARTITION_EOF:
                print(f'End of partition reached {msg.topic()} {msg.partition()}')
            else:
                raise KafkaException(msg.error())
        else:
            # Process the message
            print(f'Consumed message: {msg.value().decode("utf-8")} from topic: {msg.topic()}')
finally:
    # Close the consumer connection
    print("Closing consumer")
    consumer.close()