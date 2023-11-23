from abc import ABC, abstractmethod
from ast import Raise
import time
import collections

from pylogix import PLC
from pyModbusTCP.client import ModbusClient

from loguru import logger
from tags import PingTag, CounterTag, DataTag

class Device(ABC):

    def __init__(self, name, ip, port, frequency):
        self.name = name
        self.ip = ip
        self.port = port
        self.frequency = frequency
        self.tag_list = []

    def add_data_point(self, tag):
        self.tag_list.append(tag)

    def poll_tags(self):
        for tag in self.tag_list:
            tag.poll()

    # @abstractmethod
    # def process_counter_tag(self, tag):
    #     pass

    @abstractmethod
    def read(self, tag):
        pass

class PylogixDevice(Device):

    def __init__(self, name, ip, frequency, slot=0, port=44818):
        super().__init__(name, ip, port, frequency)
        self.driver = "pylogix"
        self.processor_slot = slot
        self.comm = PLC(ip_address=self.ip, slot=self.processor_slot, port=self.port)


    def add_data_point(self, tag):
        tag_type = tag.get('type', None)
        frequency = tag.get('frequency', 0)
        frequency = max(self.frequency, frequency)
        tag_name = tag.get('tag', None)
        parent = self

        if tag_type == 'counter':
            scale = tag.get('scale', 1)
            machine = tag.get('machine', None)

            part_number_text_tag = tag.get('part_number_text', None)
            part_number_index_tag = tag.get('part_number_index', None)
            part_dict = tag.get('part_dict', None)

            new_tag_object = CounterTag(parent, tag_name, scale, frequency, machine, part_number_text_tag, part_number_index_tag, part_dict)

        elif tag_type == 'ping':
            name = tag.get('name', None)
            new_tag_object = PingTag(parent, name, tag_name, frequency)

        # elif tag_type == 'data':
        #     raise NotImplementedError
            # name = tag.get('name', None)
            # strategy = tag.get('strategy', None)
            # new_tag_object = DataTag(parent, tag_name, scale, db_table, name, strategy)

        else:
            raise NotImplementedError

        super().add_data_point(new_tag_object)

    def read(self, tags):
        error_flag = False
        ret = self.comm.Read(tags)
        if not isinstance(ret, collections.Iterable):
            ret = (ret,)
        for value in ret:
            if value.Status != "Success":
                logger.warning(f'Failed to read {self.name}:{value.TagName} ({value.Status})')
                error_flag = True
            else:
                logger.debug(f'Successfully read {self.name}:{value.TagName} ({value.Value})')
        return ret, error_flag

class ModbusDevice(Device):

    def __init__(self, name, ip, frequency, port=502, unit_id=1):
        super().__init__(name, ip, port, frequency)
        self.driver = "modbus"
        self.unit_id = unit_id
        self.comm = ModbusClient(host=self.ip, port=self.port, auto_open=True, auto_close=True, unit_id=self.unit_id)

    def add_data_point(self, tag):
        tag_type = tag.get('type', None)
        name = tag.get('name', None)
        register = tag.get('register', None)
        frequency = tag.get('frequency', 0)
        frequency = max(self.frequency, frequency)
        # db_table = tag.get('table', None)
        parent = self

        if tag_type == 'ping':
            tag_object = PingTag(parent, name, register, frequency)

        elif tag_type == 'ADAM_counter':
            machine = tag.get('machine', None)
            part_type = tag.get('part_type', None)
            part_type_register = tag.get('part_type_register', None)
            scale = tag.get('scale', 1)
            tag_object = CounterTag(parent, register, scale, frequency, machine, part_number)


        # elif tag_type == 'data':
        #     raise NotImplementedError
            # name = tag.get('name', None)
            # strategy = tag.get('strategy', None)
            # tag_object = DataTag(parent, None, frequency, db_table, strategy)
        else:
            raise NotImplementedError(f'Not Implemented: {self.driver}:{tag_type}')


        super().add_data_point(tag_object)

    def read(self, tag):
        error_flag = False
        count = None
        regs = self.comm.read_holding_registers(tag.address, 2)

        if regs:
            count = regs[0] + (regs[1] * 65536)
            logger.debug(f'Successfully read {self.name}:{tag.address} ({count})')
        else:
            error_flag = True
            count = None
            logger.warning(f'Failed to read {self.name}:{tag.address}')

        return count, error_flag
