from protos_py.protos import weather_data_pb2


def create_weather_data_proto(row):
    weather_data = weather_data_pb2.WeatherData()
    weather_data.formatted_date = row["Formatted Date"]
    weather_data.summary = row["Summary"]
    weather_data.precip_type = row["Precip Type"]
    weather_data.temperature_c = float(row["Temperature (C)"])
    weather_data.wind_speed_kmh = float(row["Wind Speed (km/h)"])
    weather_data.pressure_mb = float(row["Pressure (millibars)"])
    weather_data.humidity = float(row["Humidity"])

    return weather_data


def create_weather_data_simple(row):
    return {
        "formatted_date": row["Formatted Date"],
        "weather_data.summary": row["Summary"],
        "precip_type": row["Precip Type"],
        "temperature_c": float(row["Temperature (C)"]),
        "wind_speed_kmh": float(row["Wind Speed (km/h)"]),
        "pressure_mb": float(row["Pressure (millibars)"]),
        "humidity": float(row["Humidity"]),
    }
