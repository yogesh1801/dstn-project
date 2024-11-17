docker-compose exec broker kafka-topics --delete --topic raw-video-data --bootstrap-server localhost:9092
sleep 2
docker-compose exec broker kafka-topics --create --topic raw-video-data --bootstrap-server localhost:9092 --replication-factor 1 --partitions 4