INPUT_DIR = "input"

KAFKA_BROKER = "localhost:9092"

FOLDER_TOPIC_MAPPING = {
    "1080p": "1080p", 
    "720p": "720p",
    "480p": "480p",
    "360p": "360p",
}


KAFKA_PRODUCER_CONFIG = {
    "bootstrap_servers": [KAFKA_BROKER],
    "acks": "all",  # Good for ensuring delivery reliability
    "linger_ms": 3,  # Increased from 3 to 10 for better batching
    "batch_size": 8388608,  # Optimized for 4MB segments (4 * 1024 * 1024)
    "retries": 5,  # Good setting for reliability
    "max_request_size": 20971520,  # Set to 5MB (slightly larger than segment size)
    "buffer_memory": 134217728,  # 64MB - good for buffering multiple segments
    "compression_type": None,  # Added compression to reduce network bandwidth
    "request_timeout_ms": 30000,  # 30 seconds timeout
    "max_in_flight_requests_per_connection": 5,
}
