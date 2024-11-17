# -----------------------------GENERAL CONFIG--------------------------------#

INPUT_VIDEO_SOURCE = "assets/video.mkv"
OUTPUT_DIR = "temp"

# ------------------------------FFMPEG CONFIG----------------------------------#

SEGMENT_DURATION = 1
INPUT_FORMAT = "None"
FRAMERATE = 30
RESOLUTION = "1280x720"

# -----------------------------KAFKA PRODUCER CONFIG--------------------------#

KAFKA_BROKER = "localhost:9092"  # Replace with your Kafka broker address
KAFKA_TOPIC = "raw-video-data"  # Replace with your Kafka topic name
KAFKA_TIMEOUT = 10

# -----------------------------GENERAL CONFIG--------------------------------#

INPUT_VIDEO_SOURCE = "assets/video.mkv"
OUTPUT_DIR = "temp"

# ------------------------------FFMPEG CONFIG----------------------------------#

SEGMENT_DURATION = 1
INPUT_FORMAT = "None"
FRAMERATE = 30
RESOLUTION = "1280x720"

# -----------------------------KAFKA PRODUCER CONFIG--------------------------#

KAFKA_BROKER = "localhost:9092"  # Replace with your Kafka broker address
KAFKA_TOPIC = "raw-video-data"  # Replace with your Kafka topic name
KAFKA_TIMEOUT = 10

KAFKA_PRODUCER_CONFIG = {
    "bootstrap_servers": [KAFKA_BROKER],
    "acks": "all",  # Good for ensuring delivery reliability
    "linger_ms": 5,  # Increased from 3 to 10 for better batching
    "batch_size": 8388608,  # Optimized for 4MB segments (4 * 1024 * 1024)
    "retries": 5,  # Good setting for reliability
    "max_request_size": 20971520,  # Set to 5MB (slightly larger than segment size)
    "buffer_memory": 134217728,  # 64MB - good for buffering multiple segments
    "compression_type": None,  # Added compression to reduce network bandwidth
    "request_timeout_ms": 30000,  # 30 seconds timeout
    "max_in_flight_requests_per_connection": 5,
}
