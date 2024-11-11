protoc --python_out=./protos_py ./protos/weather_data.proto
python weather_sim.py --mode production