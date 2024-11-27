#!/bin/bash

# Function to check if any containers are running
if [ -n "$(sudo docker ps -q)" ]; then
    echo "Stopping all running containers..."
    sudo docker compose -f docker-compose.kafka.yml down
    sudo docker stop $(sudo docker ps -a -q) 2>/dev/null || true
    sudo docker rm $(sudo docker ps -a -q) 2>/dev/null || true
fi

# Clean and prepare kafka data directory
echo "Setting up kafka data directory..."
rm -rf kafka-data
mkdir -p kafka-data
sudo chmod 777 kafka-data
sudo chown 1000:1000 kafka-data

# Start Kafka services
echo "Starting Kafka services..."
sudo docker compose -f docker-compose.kafka.yml up -d

# Wait for Kafka to be ready
echo "Waiting for Kafka to be ready..."
sleep 15  # Increased sleep time for better reliability

# Create topics with error handling
for resolution in 1080p 720p 480p 360p; do
    echo "Setting up topic: $resolution"
    # Delete topic if exists (suppress error if topic doesn't exist)
    sudo docker compose -f docker-compose.kafka.yml exec broker \
        kafka-topics --delete --topic $resolution --bootstrap-server localhost:9092
    sleep 2
    sudo docker compose -f docker-compose.kafka.yml exec broker \
        kafka-topics --create --topic $resolution --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1
done

# Verify topics were created
echo "Verifying topics..."
sudo docker compose -f docker-compose.kafka.yml exec broker \
    kafka-topics --list --bootstrap-server localhost:9092

sleep 3
echo "Starting producer..."
python producer.py