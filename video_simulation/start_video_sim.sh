docker compose -f docker-compose.kafka.yml down
rm -rf kafka-data
docker compose -f docker-compose.kafka.yml up -d
sleep 8
sh create_topic.sh
sleep 3
python video_sim.py