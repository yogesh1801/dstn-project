import csv
from .create_weather_data import create_weather_data_proto

from config import conf


def create_proto_binary():
    input_csv_file = conf.INPUT_CSV_FILE
    output_binary_file = conf.OUTPUT_BIN_FILE

    with open(output_binary_file, "wb") as binary_file:
        with open(input_csv_file, "r") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                weather_data = create_weather_data_proto(row=row)
                binary_file.write(weather_data.SerializeToString())
