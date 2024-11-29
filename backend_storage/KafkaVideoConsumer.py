# backend_storage/KafkaVideoConsumer.py
from kafka import KafkaConsumer


class KafkaVideoConsumer:
    def __init__(self, bootstrap_servers, topic, video_chunk_manager):
        self.consumer = KafkaConsumer(
            topic, bootstrap_servers=bootstrap_servers, group_id="video-storage-group"
        )
        self.video_chunk_manager = video_chunk_manager

    def consume_video_chunks(self):
        """
        Consume video chunks from Kafka and process them
        """
        for message in self.consumer:
            stream_id = message.stream_id
            quality = message.quality
            chunk_data = message.value
            chunk_number = message.chunk_number
            self.video_chunk_manager.save_video_chunk(
                stream_id, quality, chunk_data, chunk_number
            )
