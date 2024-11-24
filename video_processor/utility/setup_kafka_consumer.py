from typing import List
from kafka import KafkaConsumer


def setup_kafka_consumer(
    bootstrap_servers: List[str], topic_name: str
) -> KafkaConsumer:
    """Initialize and return Kafka consumer with specified configuration."""
    return KafkaConsumer(
        topic_name,
        bootstrap_servers=bootstrap_servers,
        key_deserializer=lambda x: x.decode("utf-8") if x else None,
        value_deserializer=None,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="video_processor_group",
    )
