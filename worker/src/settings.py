from dotenv import load_dotenv
load_dotenv()
import os

MQTT_HOST = os.getenv("MQTT_HOST")
MQTT_USER = os.getenv("MQTT_USER")
MQTT_PWD = os.getenv("MQTT_PWD")
SITE_NAME = os.getenv("SITE_NAME")
MQTT_TOPIC = os.getenv("MQTT_TOPIC")
INFLUX_HOST = os.getenv("INFLUX_HOST")
INFLUX_USER = os.getenv("INFLUX_USER")
INFLUX_PWD = os.getenv("INFLUX_PWD")
INFLUX_DBNAME = os.getenv("INFLUX_DBNAME")
SERIAL_PORT = os.getenv("SERIAL_PORT")
POLL_TIME = int(os.getenv("POLL_TIME", 60))
