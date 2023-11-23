from subprocess import _USE_POSIX_SPAWN
import time
import yaml
import sys
import os
import random
# from paho.mqtt import client as mqtt_client

from devices import PylogixDevice, ModbusDevice

from shared import get_logger, read_config_file
logger = get_logger('collect')

def read_config():
    devices = []
    config = read_config_file()

    for device in config.get('devices'):
        name = device.get('name', None)
        ip = device.get('ip', None)
        frequency = device.get('frequency', 1)

        driver = device.get('driver', None)

        if driver == 'pylogix':
            slot = device.get('processor_slot', 0)
            port = device.get('port', 44818)
            device_entry = PylogixDevice(name, ip, frequency, slot=slot, port=port)

        elif driver == 'modbus':
            # raise NotImplementedError
            
            port = device.get('port', 502)
            unit_id = device.get('unit_id', 1)
            device_entry = ModbusDevice(name, ip, frequency, port=port, unit_id=unit_id)

        for tag in device['tags']:
            device_entry.add_data_point(tag)

        devices.append(device_entry)
    return devices

def handle_update(topic, payload):
    print(payload)

    # result = mqtt_client.publish(topic, payload, 2)

    # status = result[0]

    # if status == 0:
    #     logger.info(f"Sent {topic} : {payload}")
    # else:
    #     logger.warning(f"MQTT send failed {topic} {payload}")


@logger.catch
def main():
    devices = read_config()

    # while not FLAG_EXIT:
    while True:
        for device in devices:
            device.poll_tags()

if __name__ == "__main__":

    main()


