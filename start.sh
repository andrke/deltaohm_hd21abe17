#!/usr/bin/env bash

# Set up directories
SCRIPT_PATH=$(realpath $(dirname "$0"))

DOCKER_COMPOSE=$(which docker-compose)
DOCKER=$(which docker)

cd "$SCRIPT_PATH" || exit 2

# Sanity checks
if [ -z "$DOCKER" ]; then
  echo "Please install docker"
  exit 2
fi

if [ -z "$DOCKER_COMPOSE" ]; then
  echo "Please install docker-compose"
  exit 2
fi

if [ ! -f "$SCRIPT_PATH"/.env ]; then
  echo "Generating local vars"
  cp "$SCRIPT_PATH"/.env.example "$SCRIPT_PATH"/.env
  . "$SCRIPT_PATH"/.env
else
  echo Loading "$SCRIPT_PATH"/.env
  . "$SCRIPT_PATH"/.env
fi

# Pull mqtt and generate mqtt password
$DOCKER pull eclipse-mosquitto:latest
if [ ! -f $SCRIPT_PATH/mosquitto/config/mosquitto.passwd ]; then
    $DOCKER run -v "$SCRIPT_PATH/mosquitto:/mosquitto" -ti eclipse-mosquitto:latest mosquitto_passwd -c -b /mosquitto/config/mosquitto.passwd $MQTT_USER $MQTT_PWD
fi

IS_MQTT_USER=$(grep $MQTT_USER $SCRIPT_PATH/mosquitto/config/mosquitto.passwd)
if [ -z $IS_MQTT_USER ]; then
    $DOCKER run -v "$SCRIPT_PATH/mosquitto:/mosquitto" -ti eclipse-mosquitto:latest mosquitto_passwd -b /mosquitto/config/mosquitto.passwd $MQTT_USER $MQTT_PWD
fi


# Check firmware
if [ ! -f /lib/firmware/ti_3410.fw ]; then
    cp $SCRIPT_PATH/firmware/ti_3410.fw /lib/firmware/ti_3410.fw 
    modprobe ti_usb_3410_5052
fi

# Check serial port
if [ ! -c $SERIAL_PORT ]; then 
    echo $SERIAL_PORT is missing
    exit 100
fi

# Start daemons
WORKER_RUNING=$($DOCKER ps |grep deltaohm/worker && echo YES)
if [ -z $WORKER_RUNNING ]; then
    $DOCKER_COMPOSE build && $DOCKER_COMPOSE up -d
fi
