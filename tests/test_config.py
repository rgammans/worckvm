from unittest import TestCase
from unittest.mock import Mock

from worchestic.matrix import Matrix

from worckvm import config


class ConfigTest(TestCase):
    def setUp(self):
        self.base_matrix = """
- !Matrix
  name: "video"
  nr_inputs: 4
  nr_outputs: 1
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
""")[0]
        print("ls", repr(system))
        self.assertTrue(isinstance(system, Matrix))
        self.assertEqual(len(system.inputs), 6)
        self.assertEqual(len(system.outputs), 2)

    def test_matrix_output_reference(self):
        system = config.loads("""
- !Matrix
  name: "video"
  nr_inputs: 6
  nr_outputs: 2
- !MatrixOutput
  name: "video"
  output_idx: 1
""")
        matrix = system[0]
        self.assertTrue(isinstance(matrix, Matrix))
        self.assertIs(matrix.outputs[1], system[1])
