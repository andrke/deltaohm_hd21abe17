import logging
from serial import Serial
from influxdb import InfluxDBClient
from influxdb.client import InfluxDBClientError
import paho.mqtt.client as mqtt
import time

from settings import *

ser = Serial(SERIAL_PORT, 460800, timeout=5, xonxoff=True)
influx_client = InfluxDBClient(INFLUX_HOST, 8086, INFLUX_USER, 
        INFLUX_PWD, INFLUX_DBNAME ,timeout=30)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

try:
    influx_client.create_database(INFLUX_DBNAME)
except InfluxDBClientError:
    logging.debug("{} DB already exist".format(INFLUX_DBNAME))
    pass
except:
    logging.exception("Error")
try:
   influx_client.create_retention_policy('{}_policy'.format(SITE_NAME), 
           '{}d'.format(2*165), 3, default=True)
except InfluxDBClientError:
   logging.debug("%s policy already exist" % DBNAME)
   pass


class HD21ABE17(object):
    labels = {
            "co2": ["CO2", "Carbon Dioxide (ppm)"],
            "co": ["CO", "Carbon Monoxide (ppm)"],
            "rh": ["RH", "Relative Humidity (%)"],
            "temp": ["T", "Temperature (°C)"],
            "pressure": ["Patm", "Atmospheric Pressure (hPa)"],
            "td": ["Td", "Dew Point"],
            "tw": ["Tw", "Wet Bulb Temperature"],
            "ah": ["AH", "Absolute Humidity"],
            "r": ["r", "Mixing Ratio"],
            "h": ["H", "Enthalpy"]
            }
            
    def __init__(self, date, co2, co, rh, temp, pressure, not_implemented1, not_implemented2, not_implemented3,
                 td, ah, r, tw, h):
        #self.date = datetime.datetime.strptime(date, 'Date=%Y/%m/%d %H:%M:%S')
        self.co2 = int(co2)
        self.co = int(co)
        self.rh = float(rh)
        self.temp = float(temp)
        self.pressure = int(pressure)
        #self.valuex1 = str(valuex1)
        #self.valuex2 = str(valuex2)
        #self.valuex3 = str(valuex3)
        self.td = float(td)
        self.ah = float(ah)
        self.r = float(r)
        self.tw = float(tw)
        self.h = float(h)

    def get_label(self,item):
        return self.labels.get(item)


def read_values():
    with ser as port:
        port.write(b'P0\r')
        port.readline()
        port.write(b'HA\r')
        res=list(map(lambda x: x.strip(), port.readline().decode().split(";")))
        port.write(b'P1\r')
        port.readline()
        port.close()
    return HD21ABE17(*res)



def on_publish(client, userdata, result):             #create function for callback
    logging.debug("data published \n")

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    logging.debug("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe('{}#'.format(MQTT_TOPIC))

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    logging.debug(msg.topic+" "+str(msg.payload))

mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(MQTT_USER, password=MQTT_PWD)
mqtt_client.on_publish = on_publish
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(MQTT_HOST, 1883, 60)
# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
while True:
    values = read_values()
    influx_points = []
    for k, v in values.__dict__.items():
        topic = MQTT_TOPIC + "/{}".format(k)
        ret = mqtt_client.publish(topic,v)
        label, desc = values.get_label(k)
        logging.debug("{} [{}]= {}".format(label, desc, v))
        json_body = {
            "measurement": SITE_NAME,
            "tags": {
                "sensor": k,
                "label": label,
                "desc": desc
            },
            "fields": {
                "value": float(v)
            }
           }
        influx_points.append(json_body)
    influx_client.write_points(influx_points)
    time.sleep(POLL_TIME)
