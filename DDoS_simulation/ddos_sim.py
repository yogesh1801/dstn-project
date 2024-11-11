from utility.get_kafka_producer import get_kafka_producer
from utility.create_ddos_data import create_ddos_record_proto
from utility.send_batch_to_kakfa import send_batch_to_kafka
from config import conf
import logging
import time
import csv
import uuid

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def process_ddos_data(input_csv_file):
    logger.info("Initializing Kafka producer...")
    producer = get_kafka_producer()
    logger.info(f"Starting to process data from {input_csv_file}")

    # target_rate = conf.TARGET_RATE
    start_time = time.time()
    points_sent = 0
    start_index = conf.CSV_START_INDEX
    end_index = conf.CSV_END_INDEX
    latencies = []

    chunk_size = conf.CHUNK_SIZE
    current_chunk = []

    with open(input_csv_file, "r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for index, row in enumerate(csv_reader):
            if index < start_index:
                continue
            if index > end_index:
                break
            ddos_data = create_ddos_record_proto(row=row)
            key = str(uuid.uuid4())
            current_chunk.append((key, ddos_data.SerializeToString()))

            if len(current_chunk) >= chunk_size:
                batch_latencies = send_batch_to_kafka(producer, current_chunk)
                latencies.extend(batch_latencies)
                points_sent += len(current_chunk)
                current_chunk = []

    if current_chunk:
        batch_latencies = send_batch_to_kafka(producer, current_chunk)
        latencies.extend(batch_latencies)
        points_sent += len(current_chunk)

    producer.flush()
    producer.close()

    total_time = time.time() - start_time
    avg_latency = sum(latencies) / len(latencies) if latencies else 0

    print(
        f"Sent {points_sent} messages in {total_time:.2f} seconds with "
        f"compression {conf.KAFKA_PRODUCER_CONFIG['compression_type']}. "
        f"Average latency: {avg_latency:.4f} seconds"
    )


if __name__ == "__main__":
    input_csv_file = conf.INPUT_CSV_FILE
    process_ddos_data(input_csv_file=input_csv_file)
