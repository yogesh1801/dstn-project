docker compose -f docker-compose.kafka.yml down
sleep 3
rm -rf kafka-data
docker compose -f docker-compose.kafka.yml up -d
sleep 10
sh create_topic.sh
sleep 5
python video_sim.py