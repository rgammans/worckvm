from unittest import TestCase, skip
from unittest.mock import Mock
from textwrap import dedent

from worchestic.matrix import Matrix
from worchestic.signals import Source
from worchestic.group import SourceGroup, MatrixGroup

from worckvm import config
from worckvm.monitor import Monitor, Adjacency
from worckvm.matrixdriver import Driver

driver = Driver(name="test_driver")

class ConfigTest(TestCase):
    def setUp(self):
        self.base_matrix = """
- !Matrix
  name: "video"
  nr_inputs: 4
  nr_outputs: 1
  driver: test_driver
"""

    def test_matrix_creation(self):
        system = config.loads(self.base_matrix)[0]
        print("ls", repr(system))
        self.assertTrue(isinstance(system, Matrix))
        self.assertEqual(len(system.inputs), 4)
        self.assertEqual(len(system.outputs), 1)

    def test_matrix_creation2(self):
        system = config.loads("""
- !Matrix
  name: "video"
  nr_inputs: 6
  nr_outputs: 2
  driver: test_driver
""")[0]
        print("ls", repr(system))
        self.assertTrue(isinstance(system, Matrix))
        self.assertEqual(len(system.inputs), 6)
        self.assertEqual(len(system.outputs), 2)

    def test_matrix_creation_with_driver(self):
        system = config.loads("""
- !Matrix
  name: "video"
  driver: test_driver
  nr_inputs: 6
  nr_outputs: 2
""")[0]
        self.assertTrue(isinstance(system, Matrix))
        self.assertIs(system._driver, driver)


    def test_matrix_output_reference(self):
        system = config.loads("""
- !Matrix
  name: "video"
  nr_inputs: 6
  nr_outputs: 2
  driver: test_driver
- !MatrixOutput
  matrix_name: "video"
  output_idx: 1
""")
        matrix = system[0]
        self.assertTrue(isinstance(matrix, Matrix))
        self.assertIs(matrix.outputs[1], system[1])

    def test_inviald_matrix_output_raises_useful_error(self):
        with self.assertRaises(config.MissingConfigKey):
            _ = config.loads("""
- !Matrix
  name: "video"
  nr_inputs: 6
  nr_outputs: 2
  driver: test_driver
- !MatrixOutput
  matrix_name: "video"
  ouput_idx: 1
""")

    @skip("not meeaniful whitebox")
    def test_matrix_input_reference_current_attribte_matches_the_matrix(self):
        system = config.loads("""
- !Matrix
  name: "video"
  nr_inputs: 6
  nr_outputs: 2
- !MatrixInput
  matrix_name: "video"
  input_idx: 1
""")
        matrix = system[0]
        self.assertIs(matrix.inputs[1], system[1]._current)

    def test_matrix_input_ref_sets_attribute_set_the_value_on_matrix(self):
        system = config.loads("""
- !Matrix
  name: "video"
  nr_inputs: 6
  nr_outputs: 2
  driver: test_driver
- !MatrixInput
  matrix_name: "video"
  input_idx: 1
""")
        matrix = system[0]
        new_source = Source("test")
        system[1].set_to(new_source)
        self.assertIs(matrix.inputs[1], new_source)

    def test_multpleconnections_to_the_same_input_raise(self):
        system = config.loads("""
- !Matrix
  name: "video"
  nr_inputs: 6
  nr_outputs: 2
  driver: test_driver
- !MatrixInput
  matrix_name: "video"
  input_idx: 1
""")
        new_source1 = Source("test")
        new_source2 = Source("test")
        system[1].set_to(new_source1)
        with self.assertRaises(config.DuplicateConnection):
            system[1].set_to(new_source2)

    def test_matrix_group_raises_sensible_error_with_missing_attributes(self):
        with self.assertRaises(config.MissingConfigKey):
            config.loads("""
- !MatrixGroup
    misspelling: "video"
    other: "text"
""")

    def test_sourcesets_can_be_defined(self):
        system = config.loads("""
- !Matrix
  name: "video"
  nr_inputs: 4
  nr_outputs: 1
  driver: test_driver

- !Matrix
  name: "hid"
  nr_inputs: 4
  nr_outputs: 1
  driver: test_driver

- !MatrixOutput &video
  matrix_name: "video"
  output_idx: 0

- !MatrixOutput &hid
  matrix_name: "hid"
  output_idx:  0

- !SourceSet
  name: "Gaming PC"
  sources:
    - type: "video"
      preferred_output: *video
      connected_to: !MatrixInput
          matrix_name: "video"
          input_idx: 1

    - type: "hid"
      preferred_output: *hid
      connected_to: !MatrixInput
          matrix_name: "hid"
          input_idx: 1

- !SourceSet
  name: "Mac"
  sources:
      - type: "video"
        preferred_output: *video
        connected_to: !MatrixInput
            matrix_name: "video"
            input_idx: 2

      - type: "hid"
        preferred_output: *hid
        connected_to: !MatrixInput
            matrix_name: "hid"
            input_idx: 2


  """)
        # Check name
        self.assertEqual(system[4].name, "Gaming PC")
        # Check correct numnber of source
        self.assertEqual(len(system[4].sources), 2)
        # Check defaul sorue name.
        self.assertEqual(system[4].sources['video'].name, "Gaming PC (video)")
        # . and output
        self.assertIs(system[4].sources['video'].preferred_out, system[2])
        # and check connection
        self.assertIs(system[4].sources['video'], system[0].inputs[1])

    def test_sourcesets_can_opnly_have_single_soure_of_a_single_type(self):
        cfg = dedent("""
            - !Matrix
              name: "video"
              driver: test_driver
              nr_inputs: 4
              nr_outputs: 1

            - !SourceSet
              name: "Gaming PC"
              sources:
                - type: "video"
                - type: "video"
              """)
        with self.assertRaises(config.DuplicateSourceType):
            config.loads(cfg)

    def test_sourcesets_combine_into_a_sourcegroup(self):
        system = config.loads("""
- !Matrix
  name: "video"
  nr_inputs: 4
  nr_outputs: 1
  driver: test_driver

- !Matrix
  name: "hid"
  nr_inputs: 4
  nr_outputs: 1
  driver: test_driver

- !MatrixOutput &video
  matrix_name: "video"
  output_idx: 0

- !MatrixOutput &hid
  matrix_name: "hid"
  output_idx:  0

- !MatrixGroup
  matricies: [ "video", "hid" ]
  sources:
  - !SourceSet
    name: "Gaming PC"
    sources:
      - type: "video"
        name: Gaming PC HDMI
        preferred_output: *video
        connected_to: !MatrixInput
            matrix_name: "video"
            input_idx: 1

      - type: "hid"
        preferred_output: *hid
        connected_to: !MatrixInput
            matrix_name: "hid"
            input_idx: 1

  - !SourceSet
    name: "Mac"
    sources:
        - type: "video"
          preferred_output: *video
          connected_to: !MatrixInput
              matrix_name: "video"
              input_idx: 2

        - type: "hid"
          preferred_output: *hid
          connected_to: !MatrixInput
              matrix_name: "hid"
              input_idx: 2


  """)
        self.assertEqual(set(system[4].matricies.keys()), {"video", 'hid'})
        self.assertEqual(system[4].matricies['video'], system[0])
        self.assertEqual(set(system[4].signals.groups.keys()),
                         {"video", "hid"})
        self.assertEqual(system[4].signals.groups['video'][0].name,
                         "Gaming PC HDMI")

    def test_config_can_create_a_monitor(self):
        system = config.loads("""
- !Matrix
  name: "video"
  nr_inputs: 4
  nr_outputs: 1
  driver: test_driver

- !Matrix
  name: "hid"
  nr_inputs: 4
  nr_outputs: 1
  driver: test_driver

- !MatrixOutput &video
  matrix_name: "video"
  output_idx: 0

- !MatrixOutput &hid
  matrix_name: "hid"
  output_idx:  0

- !MatrixGroup &grp
  matricies: [ "video", "hid" ]
  sources:
  - !SourceSet
    name: "Gaming PC"
    sources:
      - type: "video"
        name: Gaming PC HDMI
        preferred_output: *video
        connected_to: !MatrixInput
            matrix_name: "video"
            input_idx: 1

      - type: "hid"
        preferred_output: *hid
        connected_to: !MatrixInput
            matrix_name: "hid"
            input_idx: 1

  - !SourceSet
    name: "Mac"
    sources:
        - type: "video"
          preferred_output: *video
          connected_to: !MatrixInput
              matrix_name: "video"
              input_idx: 2

        - type: "hid"
          preferred_output: *hid
          connected_to: !MatrixInput
              matrix_name: "hid"
              input_idx: 2


- !Monitor
  name: foo
  matrix_group: *grp
  connected_to: *video
  hid_output: *hid
        """)
        self.assertIsInstance(system[-1], Monitor)
        self.assertIs(system[-1].output, system[2])
        self.assertEqual(system[-1].name, "foo")

    def test_monitor_creation_raises_if_not_connected_to_the_provided_group(self):
        with self.assertRaises(config.MatrixNotInGroup):
            config.loads("""
- !Matrix
  name: "video"
  nr_inputs: 4
  nr_outputs: 1
  driver: test_driver

- !Matrix
  name: "alt"
  nr_inputs: 4
  nr_outputs: 1
  driver: test_driver

- !Matrix
  name: "hid"
  nr_inputs: 4
  nr_outputs: 1
  driver: test_driver

- !MatrixOutput &video
  matrix_name: "video"
  output_idx: 0

- !MatrixOutput &hid
  matrix_name: "hid"
  output_idx:  0

- !MatrixGroup &grp
  matricies: [ "video", "hid" ]
  sources:
  - !SourceSet
    name: "Gaming PC"
    sources:
      - type: "video"
        name: Gaming PC HDMI
        preferred_output: *video
        connected_to: !MatrixInput
            matrix_name: "video"
            input_idx: 1

      - type: "hid"
        preferred_output: *hid
        connected_to: !MatrixInput
            matrix_name: "hid"
            input_idx: 1

  - !SourceSet
    name: "Mac"
    sources:
        - type: "video"
          preferred_output: *video
          connected_to: !MatrixInput
              matrix_name: "video"
              input_idx: 2

        - type: "hid"
          preferred_output: *hid
          connected_to: !MatrixInput
              matrix_name: "hid"
              input_idx: 2

- !Monitor
  name: foo
  matrix_group: *grp
  connected_to:
        !MatrixOutput
        matrix_name: alt
        output_idx: 0
  hid_output: *hid
            """)

    def test_monitor_creation_adjacenny_works(self):
        system = config.loads("""
- !Matrix
  name: "video"
  nr_inputs: 4
  nr_outputs: 1
  driver: test_driver

- !Matrix
  name: "hid"
  nr_inputs: 4
  nr_outputs: 1
  driver: test_driver

- !MatrixOutput &video
  matrix_name: "video"
  output_idx: 0

- !MatrixOutput &hid
  matrix_name: "hid"
  output_idx:  0

- !MatrixGroup &grp
  matricies: [ "video", "hid" ]
  sources:
  - !SourceSet
    name: "Gaming PC"
    sources:
      - type: "video"
        name: Gaming PC HDMI
        preferred_output: *video
        connected_to: !MatrixInput
            matrix_name: "video"
            input_idx: 1

      - type: "hid"
        preferred_output: *hid
        connected_to: !MatrixInput
            matrix_name: "hid"
            input_idx: 1

  - !SourceSet
    name: "Mac"
    sources:
        - type: "video"
          preferred_output: *video
          connected_to: !MatrixInput
              matrix_name: "video"
              input_idx: 2

        - type: "hid"
          preferred_output: *hid
          connected_to: !MatrixInput
              matrix_name: "hid"
              input_idx: 2

- !Monitor &leftmonitor
  name: foo
  matrix_group: *grp
  connected_to:
        !MatrixOutput
        matrix_name: video
        output_idx: 0
  hid_output: *hid

- !Monitor &rightmonitor
  name: bar
  matrix_group: *grp
  connected_to:
        !MatrixOutput
        matrix_name: video
        output_idx: 0
  to_left: *leftmonitor
  hid_output: *hid

- !Layout
  monitor: *leftmonitor
  to_left: *rightmonitor
            """)
        self.assertEqual(system[-2].neighbour_to(Adjacency.LEFT), system[-3])
        self.assertEqual(system[-3].neighbour_to(Adjacency.RIGHT), system[-2])
