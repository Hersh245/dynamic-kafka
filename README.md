# Dynamic Kafka
Attempt to build dynamic batching into Kafka

## Start building
Start with building the docker file

    docker build . -t dynamickafka/kafka:3.9.0
Run Kafka container

    docker run --rm --name kafka -it dynamickafka/kafka:3.9.0 bash
Some example scripts

    ls -l /kafka/bin/
Base config file for Kafka

    cat /kafka/config/server.properties
To get the default config files for Kafka and Zookeeper out to the local machine

    In a terminal, run
    docker cp kafka:/kafka/config/server.properties ./config/kafka-1/server.properties
    docker cp kafka:/kafka/config/zookeeper.properties ./config/zookeeper-1/zookeeper.properties
We want to run new brokers and zookeeper in their separate containers

    Go to kafka-1 config file, find zookeeper.connect=localhost:2181
    Change to zookeeper.connect=zookeeper-1:2181
To build more brokers, copy and paste config file for kafka-1 and paste it into kafka-k folders, and change the broker.id to a unique id.

## Zookeeper
Centralized service to maintain information (config, naming, status of nodes, topics, etc.)
Build zookeeper

    cd zookeeper
    docker build . -t dynamickafka/zookeeper:3.9.0

## Create Kafka network

    docker network create kafka
    docker run -d `
    --rm `
    --name zookeeper-1 `
    --net kafka `
    -v ${PWD}/config/zookeeper-1/zookeeper.properties:/kafka/config/zookeeper.properties `
    dynamickafka/zookeeper:3.9.0

Run Kafka 1

    docker run -d `
    --rm `
    --name kafka-1 `
    --net kafka `
    -v ${PWD}/config/kafka-1/server.properties:/kafka/config/server.properties `
    dynamickafka/kafka:3.9.0

Run Kafka 2

    docker run -d `
    --rm `
    --name kafka-2 `
    --net kafka `
    -v ${PWD}/config/kafka-2/server.properties:/kafka/config/server.properties `
    dynamickafka/kafka:3.9.0

Run Kafka 3

    docker run -d `
    --rm `
    --name kafka-3 `
    --net kafka `
    -v ${PWD}/config/kafka-3/server.properties:/kafka/config/server.properties `
    dynamickafka/kafka:3.9.0

Check status

    docker ps -- will list all running images
    docker logs {name} -- will list the status of the called image

## Create topic

Use the provided sample script
Access the container

    docker exec -it zookeeper-1 bash
Create topic

    /kafka/bin/kafka-topics.sh \
    --create \
    --zookeeper zookeeper-1:2181 \
    --replication-factor 1 \
    --partitions 3 \
    --topic {topic_name}
To check the details of the topic

    /kafka/bin/kafka-topics.sh \
    --describe \
    --topic {topic_name} \
    --zookeeper zookeeper-1:2181