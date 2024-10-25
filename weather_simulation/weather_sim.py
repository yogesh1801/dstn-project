from protos_py.protos import weather_data_pb2
import argparse
from utility.create_proto_binary import create_proto_binary
from utility.get_kafka_producer import get_kafka_producer
from utility.create_weather_data import create_weather_data_proto, create_weather_data_simple
from config import conf
import csv
import logging
import json
import time
import uuid

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_weather_data(input_csv_file, output_binary_file, process_all=True):
    if process_all:
        logger.info("Creating proto binary file for all entries...")
        create_proto_binary()
        logger.info(f"Binary file created successfully: {output_binary_file}")
        return
    
    logger.info("Initializing Kafka producer...")
    producer = get_kafka_producer()


    input_file = conf.INPUT_CSV_FILE
    logger.info(f"Starting to process data from {input_file}")

    target_rate = conf.TARGET_RATE
    start_time = time.time()
    points_sent = 0
    latencies = []

    with open(input_file, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if conf.PROTO_FLAG:
                weather_data = create_weather_data_proto(row=row)
                weather_data = weather_data.SerializeToString()
            else:
                weather_data = create_weather_data_simple(row=row)
                weather_data = json.dumps(weather_data).encode('utf-8')

            key = str(uuid.uuid4())

            start_send_time = time.time()
            future = producer.send(conf.KAFKA_TOPIC, key=key, value=weather_data)
            points_sent += 1
            future.get(timeout=10)
            #logger.info(f"Message sent with key {key}")
            end_send_time = time.time()

            latencies.append(end_send_time - start_send_time)

            # elapsed_time = time.time() - start_time
            # if elapsed_time < 1.0:  
            #     sleep_time = max(0, (points_sent / target_rate) - elapsed_time)
            #     time.sleep(sleep_time)

    producer.flush()
    producer.close()

    total_time = time.time() - start_time
    average_latency = sum(latencies) / len(latencies) if latencies else 0
    print(f"Sent {points_sent} messages in {total_time:.2f} seconds with "
          f"{'Protobuf' if conf.PROTO_FLAG else 'JSON'} and compression {conf.KAFKA_PRODUCER_CONFIG['compression_type']}. "
          f"Average latency: {average_latency:.4f} seconds")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process weather data.')
    parser.add_argument('--mode', choices=['test', 'production'], default='test', 
                        help='Mode of operation: "test" to process all entries, "production" to indicate pending status.')

    args = parser.parse_args()

    input_csv_file = conf.INPUT_CSV_FILE
    output_binary_file = conf.OUTPUT_BIN_FILE
    process_weather_data(input_csv_file, output_binary_file, process_all=(args.mode == 'test'))
