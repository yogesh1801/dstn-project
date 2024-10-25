from config import conf
from kafka import KafkaProducer

def get_kafka_producer():
    kafka_producer_config = conf.KAFKA_PRODUCER_CONFIG
    return KafkaProducer(**kafka_producer_config)