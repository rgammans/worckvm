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
