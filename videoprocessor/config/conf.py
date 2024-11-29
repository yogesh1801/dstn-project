# Directory for input folders
INPUT_DIR = "input"

# Kafka configuration
KAFKA_CONFIG = {
    'bootstrap.servers': 'localhost:9092',  # Change to your Kafka broker's address
    'client.id': 'video-segment-producer',
}

# Folder to Topic mapping
FOLDER_TOPIC_MAPPING = {
    '1080p': '1080p',  # Change folder names and topics as needed
    '720p': '720p',
    '480p': '480p',
    '360p': '360p',
}

# Optional: Kafka Topic partition count and replication factor
KAFKA_TOPIC_CONFIG = {
    '1080p': {'partitions': 1, 'replication_factor': 1},
    '720p': {'partitions': 1, 'replication_factor': 1},
    '480p': {'partitions': 1, 'replication_factor': 1},
    '360p': {'partitions': 1, 'replication_factor': 1},
}
