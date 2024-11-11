# -----------------------------GENERAL CONFIG--------------------------------#

INPUT_CSV_FILE = "assets/ddos_data.csv"
CSV_START_INDEX = 0
CSV_END_INDEX = 100000
TARGET = True
TARGET_RATE = 1000
CHUNK_SIZE = 10000

# -----------------------------KAFKA PRODUCER CONFIG--------------------------#

KAFKA_BROKER = "localhost:9092"  # Replace with your Kafka broker address
KAFKA_TOPIC = "ddos-data"  # Replace with your Kafka topic name
KAFKA_TIMEOUT = 10

KAFKA_PRODUCER_CONFIG = {
    "bootstrap_servers": [KAFKA_BROKER],
    "acks": "all",  # Wait for all in-sync replicas to acknowledge
    "linger_ms": 2,  # Wait time before sending batches
    "batch_size": 128,  # Maximum batch size in bytes
    "retries": 5,  # Number of retries for transient errors
    "key_serializer": str.encode,  # Optional: for key serialization
    "compression_type": "zstd",  # gzip, snappy, lz4, zstd
}
