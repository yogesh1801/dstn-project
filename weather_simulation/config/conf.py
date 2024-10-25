#-----------------------------GENERAL CONFIG--------------------------#

INPUT_CSV_FILE="assets/weather_data.csv"
OUTPUT_BIN_FILE="bin/weather_data.bin"
TARGET_RATE=1000

#-----------------------------PROTO BUFF CONFIG--------------------------#

PROTO_FLAG=True

#-----------------------------KAFKA PRODUCER CONFIG--------------------------#

KAFKA_BROKER = 'localhost:9092'  # Replace with your Kafka broker address
KAFKA_TOPIC = 'weather-data'       # Replace with your Kafka topic name

KAFKA_PRODUCER_CONFIG = {
    'bootstrap_servers': [KAFKA_BROKER],
    'acks': 'all',                 # Wait for all in-sync replicas to acknowledge
    'linger_ms': 5,                # Wait time before sending batches
    'batch_size': 81,           # Maximum batch size in bytes
    'retries': 5,                  # Number of retries for transient errors
    'key_serializer': str.encode,  # Optional: for key serialization
    'compression_type': None     # gzip, snappy, lz4, zstd
}
