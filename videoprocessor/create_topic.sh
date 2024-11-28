sudo docker compose -f docker-compose.kafka.yml exec broker kafka-topics --delete --topic 1080p --bootstrap-server localhost:9092
sudo docker compose -f docker-compose.kafka.yml exec broker kafka-topics --create --topic 1080p --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1

sudo docker compose -f docker-compose.kafka.yml exec broker kafka-topics --delete --topic 720p --bootstrap-server localhost:9092
sudo docker compose -f docker-compose.kafka.yml exec broker kafka-topics --create --topic 720p --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1

sudo docker compose -f docker-compose.kafka.yml exec broker kafka-topics --delete --topic 480p --bootstrap-server localhost:9092
sudo docker compose -f docker-compose.kafka.yml exec broker kafka-topics --create --topic 480p --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1

sudo docker compose -f docker-compose.kafka.yml exec broker kafka-topics --delete --topic 360p --bootstrap-server localhost:9092
sudo docker compose -f docker-compose.kafka.yml exec broker kafka-topics --create --topic 360p --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1