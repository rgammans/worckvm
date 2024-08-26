#!/usr/bin/python3

# Based on cputemp by Douglas Otwell 2019.
# .. and it actually uses his service.py for now.

import dbus
import sys

#
# I would like to use bluezero, but Douglass Otwell's code seems
# easier to use in our use case.
#from bluezero.advertisement import Advertisement
#from bluezero.localGATT import Application, Service, Characteristic, Descriptor
from .service import Application, Service, Characteristic, Descriptor
from .advertisement import Advertisement
from worchestic.signals import Source
from worckvm.monitor import Monitor

import random


# import peripheriapl


GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"
NOTIFY_TIMEOUT = 5000

import uuid

class KVMAdvertisement(Advertisement):
    def __init__(self, index):
        super().__init__(index, "peripheral")
        self.add_local_name("KVM")
        self.include_tx_power = True


class KVMService(Service):
    THIS_SVC_UUID = "7ed7a7eb-2b24-44ba-8674-da9f63bdad76"
    def __init__(self, index):
        super().__init__(index, self.THIS_SVC_UUID, True)
        for monitor in Monitor.list():
            print(f"adding {monitor.name}")
            self.add_characteristic(MonitorCharacteristic(self,monitor))

        for src in Source.list():
            self.add_characteristic(SourceCharacteristic(self, src))


class SourceCharacteristic(Characteristic):
    THIS_CHARACTERISTIC_UUID = "1e1fbe16-fc45-4f35-ad81-c70f57174101"
    def __init__(self, service, source):
        self.notifying = False
        self.source = source

        super().__init__(
                self.THIS_CHARACTERISTIC_UUID,
                [ "read"], service)

        self.add_descriptor(DescriptorNameAttribute(self, source.name))


    def ReadValue(self, options):
        return [ dbus.Byte(b) for b in self.source.uuid.bytes ]


class MonitorCharacteristic(Characteristic):
    THIS_CHARACTERISTIC_UUID = "af993bcc-736b-4edd-a6c9-996f6f3d0053"
    def __init__(self, service, monitor):
        self.notifying = False
        self.monitor = monitor

        super().__init__(
                self.THIS_CHARACTERISTIC_UUID,
                [ "read"], service)
        self.add_descriptor(DescriptorNameAttribute(self, monitor.name))
        self.add_descriptor(UUIDAttribute(self, monitor.uuid))
        self.add_descriptor(MonitorNeighboursAttribute(self, monitor))
        #self.add_descriptor(GrabHidIndicator(self, monitor))
        self.add_descriptor(SourcesAttribute(self))


    def get_ble_status_struct():
        value = []
        status = self.monitor.get_status()
        value.extend([ dbus.Byte(b) for b in status.source.uuid.bytes ])
        value.extend(dbus.Bytes(0x01 if status.has_hid else 0x00))
        return value

    def set_status_callback(self):
        if self.notifying:
            value = self.get_ble_status_struct()
            self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])

        return self.notifying

    def StartNotify(self):
        if self.notifying:
            return

        self.notifying = True

        value = self.get_temperature()
        self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])
        self.add_timeout(NOTIFY_TIMEOUT, self.set_temperature_callback)

    def StopNotify(self):
        self.notifying = False

    def ReadValue(self, options):
        print("reading monitor status value")
        return self.get_ble_status_struct()


class DescriptorNameAttribute(Descriptor):
    THIS_DESCRIPTOR_UUID = "2901"   # User desciption

    def __init__(self, characteristic, name):
        self.name = name
        super().__init__(
                self.THIS_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        value = []
        for c in self.name:
            value.append(dbus.Byte(c.encode()))
        print (f"returning {self.name}")
        return value


class MonitorNeighboursAttribute(Descriptor):
    THIS_DESCRIPTOR_UUID = "48a50061-ae2f-4a55-960d-92fd1b982fe5"
    def __init__(self, characteristic, monitor):
        self.monitor = monitor
        super().__init__(
                self.THIS_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        value = []
        for direction in Adjanecy:
            neighbour = self.monitor.neighbour_to(direction)
            if neighbour:
                value.extend(neighbour.uuid.bytes)
            else:
                # No neighbour so add the NULL UUID
                value.extend(bytes([0]*16))
        return [ dbus.Byte(b) for b in value ]


class UUIDAttribute(Descriptor):
    THIS_DESCRIPTOR_UUID = "000B"
    def __init__(self, characteristic, uuid):
        self.uuid = uuid
        super().__init__(
                self.THIS_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        print("reading uuid")
        return [ dbus.Byte(b) for b in self.uuid.bytes ]


class SourcesAttribute(Descriptor):
    THIS_DESCRIPTOR_UUID = "d1e77371-c330-48ec-9239-a815cc426c8b"
    def __init__(self, characteristic):
        super().__init__(
                self.THIS_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        value = []
        print("reading cources list")
        ## Attribute size max is 512 bytes, which is 32 uuids.
        for src in self.characteristic.monitor.available_sources()[:32]:
            value.extend([ dbus.Byte(b) for b in src.uuid.bytes ])



def run_ble():
    app = Application()
    app.add_service(KVMService(0))
    app.register()

    adv = KVMAdvertisement(0)
    adv.register()

    try:
        app.run()
    except KeyboardInterrupt:
        app.quit()
