WorcKVM
=======

..  image:: https://github.com/rgammans/worckvm/actions/workflows/unittest.yml/badge.svg
    :alt: Python package tests
    :target: https://github.com/rgammans/worckvm/actions/workflows/unittest.yml


WorcKVM is a controller for multi-monitor KVM switch which uses the
worchestic switch fabric controller.

It is expected that the KVM switch will consist of one or more
video matricies supplying outputs the the monitor(s), and a 
USB Switch (a single output matrix) to provide the HID routing.

WorcKVM makes use of worchestic `SourceGroups` to connect the video
and the hid connections together so `worchestic` companion routing
ensure the HID follows the video.

The essence of worcKVM's control strategy is that each monitor is
potentially independent,..

Switches Configuration
======================

The KVM setup supports two types of switches:

* Video Matrix: Manages video connections between multiple sources and displays
* HID Switch: Controls the routing of keyboard and mouse, usually USB.

The switches are defined in a YAML configuration file that specifies their properties
and connection points.

Example Usage
=============

To run the WorcKVM controller, use the following command:

.. code-block:: bash

    python -m worckvm --matrix-def ./examples/simple_kvm_combined.yaml http

The ``--matrix-def`` parameter specifies the YAML configuration file for your switch setup.
Adding ``http`` enables the HTTP interface for remote control capabilities. Future improvements
is intended to add a ble interface for remote control as well as http.

Driver Selection
----------------

The ``--drivers`` option allows you to specify which switch drivers to install.
Switch drivers are Python modules that send the switch Selections to the switch hardware.
A default set of driver is  in ``worckvm.drivers.mock``. These two drivers are
    mock: A mock driver that simulates the switch hardware
    mockhid: A mock driver that simulates the HID switch hardware

The two drivers are actually identical and have no actual hardware dependencies, or
actions but are useful for testing and development.