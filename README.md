# Dynamic Kafka
An attempt to build dynamic batching in Kafka.

## **1. Build and Start Kafka Services**

Run the following command to build and start all services:

```bash
docker compose build
docker compose up -d
```

This starts:

- **Zookeeper** (port `2181`)
- **Kafka broker** (port `9092`, internally accessible as `kafka:9092`)
- **Producers** (Python-based, running in separate containers)

---

## **2. Check Running Services**

List active services:

```bash
docker compose ps
```

View logs for a specific service:

```bash
docker compose logs -f kafka
docker compose logs -f producer1
docker compose logs -f producer2
```

---

## **3. Producing and Consuming Messages**

To manually run a producer:

```bash
docker exec -it kafka-producer-1 python /app/producer.py
```

To consume messages from Kafka:

```bash
docker exec -it kafka-broker /kafka/bin/kafka-console-consumer.sh \
    --bootstrap-server kafka:9092 \
    --topic mytopic \
    --from-beginning
```

---

## **4. Kafka Topic Management**

### **Create a Topic**

```bash
docker exec -it kafka-broker /kafka/bin/kafka-topics.sh \
    --create \
    --bootstrap-server kafka:9092 \
    --replication-factor 1 \
    --partitions 3 \
    --topic mytopic
```

### **Describe a Topic**

```bash
docker exec -it kafka-broker /kafka/bin/kafka-topics.sh \
    --describe \
    --bootstrap-server kafka:9092 \
    --topic mytopic
```

---

## **5. Stopping and Cleaning Up**

To stop all running containers:

```bash
docker compose down
```

To remove all containers and volumes:

```bash
docker compose down -v
```

---

## **6. Troubleshooting**

Check running containers:

```bash
docker ps
```

Restart a specific service:

```bash
docker compose restart producer1
```

View Kafka logs:

```bash
docker compose logs -f kafka
```

Manually produce messages:

```bash
docker exec -it kafka-broker /kafka/bin/kafka-console-producer.sh \
    --broker-list kafka:9092 --topic mytopic
```

---

### **Next Steps**

- Modify producer implementations as needed.
- Add a Kafka consumer for message processing.
- Automatically tune Kafka settings for optimal performance.
