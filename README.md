# deltaohm_hd21abe17

Multi-container Docker app built from the following services:

* [InfluxDB](https://github.com/influxdata/influxdb) - time series database
* [Chronograf](https://github.com/influxdata/chronograf) - admin UI for InfluxDB
* [Grafana](https://github.com/grafana/grafana) - visualization UI for InfluxDB
* [Mqtt](https://mosquitto.org) - Eclipse Mosquitto™
* [Worker](http://deltaohm.com/ver2012/download/HD21AB_HD21AB17_M_uk.pdf) - Data collector for DeltaOhm HD21ABE17

Useful for quickly setting up a monitoring stack for DeltaOhm HD21AB17

## Quick Start

To start the app:

0. Connect device with Raspberry Pi
1. Install [docker-compose](https://docs.docker.com/compose/install/) on the docker host.
2. Clone this repo on the docker host.
3. Optionally, change default credentials in .env file
4. Run the following command from the root of the cloned repo:
```
./start.sh
```

To stop the app:

1. Run the following command from the root of the cloned repo:
```
docker-compose down
```

## Ports

The services in the app run on the following ports:

| Host Port | Service |
| - | - |
| 3000 | Grafana |
|  8086 | InfluxDB |
|  1883 | MQTT |
|  9003 | MQTT |
| 127.0.0.1:8888 | Chronograf |

Note that Chronograf does not support username/password authentication. Anyone who can connect to the service has full admin access. Consequently, the service is not publically exposed and can only be access via the loopback interface on the same machine that runs docker.

If docker is running on a remote machine that supports SSH, use the following command to setup an SSH tunnel to securely access Chronograf by forwarding port 8888 on the remote machine to port 8888 on the local machine:

```
ssh [options] <user>@<docker-host> -L 8888:localhost:8888 -N
```


## Volumes

The app creates the following named volumes (one for each service) so data is not lost when the app is stopped:

* influxdb-storage
* chronograf-storage
* grafana-storage

## Users

The app creates two admin users - one for InfluxDB and one for Grafana. By default, the username and password of both accounts is `admin`. To override the default credentials, set the following environment variables before starting the app:

* `INFLUXDB_USERNAME`
* `INFLUXDB_PASSWORD`
* `GRAFANA_USERNAME`
* `GRAFANA_PASSWORD`
* `MQTT_USER`
* `MQTT_PWD`

## Database

The app creates a default InfluxDB database called `db0`.

## Data Sources

The app creates a Grafana data source called `InfluxDB` that's connected to the default IndfluxDB database (e.g. `db0`).

To provision additional data sources, see the Grafana [documentation](http://docs.grafana.org/administration/provisioning/#datasources) and add a config file to `./grafana-provisioning/datasources/` before starting the app.

## Dashboards

By default, the app provides DeltaOhm HD21ABE17 related dashboard

To provision additional dashboards, see the Grafana [documentation](http://docs.grafana.org/administration/provisioning/#dashboards) and add a config file to `./grafana-provisioning/dashboards/` before starting the app.

## Mqtt

Eclipse Mosquitto configuration is located at mosquitto/config.

With ./start.sh mqtt username and password is created as defined in .env file

Mqtt topic:
* `MQTT_CHANNEL_ID="example_channel"`
* `SITE_NAME="example_site"`
* `MQTT_TOPIC="channels/${MQTT_CHANNEL_ID}/publish/${SITE_NAME:-deltaohm}"`



## Worker

Worker is connecting to given SERIAL_PORT and poll data every POLL_TIME (default is 60 sec). Data is pushed to influxdb and mqtt 

