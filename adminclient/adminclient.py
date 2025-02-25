import time
from confluent_kafka.admin import AdminClient, NewTopic

# Configure the AdminClient for topic management
admin_conf = {
    "bootstrap.servers": "kafka:9092"  # Kafka broker(s) address
}
admin_client = AdminClient(admin_conf)


''' Function to create a new topic if it doesn't exist
    But you can put this code in your producer too.

    /broker/config/server.properties has auto.create.topics.enable=false
    but normally it's true and it just create a new topic of default size
    if your not using confluent_kafka.admin
'''
def create_topic(topic_name):
    try:
        # Check if the topic already exists
        metadata = admin_client.list_topics(timeout=10)
        if topic_name in metadata.topics:
            print(f"Topic '{topic_name}' already exists.")
            return

        # Define the new topic
        topic = NewTopic(topic_name, num_partitions=3, replication_factor=1)

        # Create the topic
        fs = admin_client.create_topics([topic])
        fs[topic_name].result()  # Wait for creation to complete
        print(f"Topic '{topic_name}' created successfully.")
    except Exception as e:
        print(f"Error creating topic '{topic_name}': {e}")


create_topic('mytopic')
create_topic('mytopic2')


#
#
# Nothing below this line is run

'''
    Or you can do it this way, first wait for kafka to be ready and then create topics
    As opposed to checking per topic
    Either way, the important thing is importing from confluent_kafka.admin
    But this seems to hang... need to fix
'''
'''
# wait for kafka.
def wait_for_kafka():
    retries = 10
    while retries > 0:
        try:
            metadata = admin_client.list_topics(timeout=5)
            if metadata.topics:
                print("Kafka is ready!")
                return
        except Exception as e:
            print(f"Waiting for Kafka... ({retries} retries left)")
            time.sleep(5)
            retries -= 1
    raise Exception("Kafka did not become ready in time.")



wait_for_kafka()
topics = ["mytopic", "mytopic2"]
topic_list = [NewTopic(topic, num_partitions=3, replication_factor=1) for topic in topics]

fs = admin_client.create_topics(topic_list)

for topic, f in fs.items():
    try:
        f.result()
        print(f"Topic '{topic}' created successfully.")
    except Exception as e:
        print(f"Error creating topic '{topic}': {e}")

'''