from unittest import TestCase, skip, expectedFailure
from unittest.mock import Mock, patch, call, sentinel
import logging

from worckvm.monitor import (
    Monitor,
    Adjacency,
    InconsistentLayout,
)
from utils import create_fabric


class AdjacencyTests(TestCase):
    def test_opposite_of_left_is_right(self):
        self.assertEqual(Adjacency.RIGHT.opposite(), Adjacency.LEFT)

    def test_opposite_of_right_is_left(self):
        self.assertEqual(Adjacency.LEFT.opposite(), Adjacency.RIGHT)

    def test_opposite_of_top_is_bottom(self):
        self.assertEqual(Adjacency.BOTTOM.opposite(), Adjacency.TOP)

    def test_opposite_of_bottom_is_top(self):
        self.assertEqual(Adjacency.TOP.opposite(), Adjacency.BOTTOM)


class MonitorTests(TestCase):
    def setUp(self):
        self.__dict__.update(create_fabric())
        self.monitor = Monitor(
            self.matrixgrp, 0
        )
        self.left_monitor = Monitor(
            self.matrixgrp, 1,
            to_right=self.monitor
        )

    def tearDown(self):
        logging.getLogger("worckvm").setLevel(logging.WARN)

    def test_monitr_has_get_status_which_show_which_source_is_routed(self):
        logging.getLogger().setLevel(logging.DEBUG)
        print("X")
        self.matrixgrp.select('video', 0, self.video0)
        status = self.monitor.get_status()
        expected_status = Monitor.Status(
            source=self.video0,
            has_hid=True
        )
        self.assertEqual(status, expected_status)

    def test_monitr_has_get_status_which_show_which_source_is_routed_and_hid_is_connected_elsewhere(self):
        self.matrixgrp.select('video', 0, self.video0)
        self.matrixgrp.select('hid', 0, self.hid1, no_companions=True)
        status = self.monitor.get_status()
        expected_status = Monitor.Status(
            source=self.video0, has_hid=False)
        self.assertEqual(status, expected_status)

    def test_monitor_has_function_to_route_the_hid(self):
        self.matrixgrp.select('video', 0, self.video0)
        self.matrixgrp.select('hid', 0, self.hid1, no_companions=True)
        with patch.object(self.matrixgrp, 'select', wraps=self.matrixgrp.select) as msel:
            self.monitor.grab_hid()
        msel.assert_called_with('hid', 0, self.hid0, no_companions=True)
        status = self.monitor.get_status()
        expected_status = Monitor.Status(
            source=self.video0,
            has_hid=True
        )
        self.assertEqual(status, expected_status)

    def test_monitor_has_select_which_forward_to_the_matgrp(self):
        with patch.object(self.monitor.output, 'select') as outsel:
            self.monitor.select(sentinel.SOURCE)
        outsel.assert_called_once_with(sentinel.SOURCE, nolock=True)

    def test_monitor_has_available_sources_which_sorts_Source_with_monitor_as_preferred_out_first(self):
        srcs = self.monitor.available_sources()
        self.assertEqual(len(srcs), 4)
        self.assertIs(srcs[0].preferred_out, self.monitor.output)
        self.assertIs(srcs[1].preferred_out, self.monitor.output)
        self.assertIsNot(srcs[2].preferred_out, self.monitor.output)
        self.assertIsNot(srcs[3].preferred_out, self.monitor.output)


    def test_monitor_may_have_another_monitor_in_a_particular_driection(self):
        mon2 = self.monitor.neighbour_to(Adjacency.LEFT)
        self.assertEqual(mon2, self.left_monitor)

    def test_monitor_may_have_another_monitor_in_a_particular_driection_reverse_test_work(self):
        mon2 = self.left_monitor.neighbour_to(Adjacency.RIGHT)
        self.assertEqual(mon2, self.monitor)

    def test_two_monitors_cant_be_to_the_left_of_the_same_one(self):
        with self.assertRaises(InconsistentLayout):
            Monitor(self.matrixgrp, 2, to_right=self.monitor)
