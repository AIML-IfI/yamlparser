import yamlparser
from yamlparser.registry import set_registry_file, get_registered_variable, set_registered_variable, delete_registered_variable, registry_content
import os
import tempfile
import unittest

class TestRegistry(unittest.TestCase):

    def setUp(self):
        self.obj, self.registry_file = tempfile.mkstemp(".yaml")

    def tearDown(self):
        print(f"Removing registry file {self.registry_file}")
        os.close(self.obj)
        os.remove(self.registry_file)


    def test_registry_parser(self):
        yamlparser.registry_parser(self.registry_file, command_line_options=["-a", "-k", "TEST_KEY", "-v", "test_variable", "-l"])

        assert get_registered_variable("TEST_KEY") == "test_variable"

        # delete it again
        yamlparser.registry_parser(self.registry_file, command_line_options=["-d", "-k", "TEST_KEY"])

        assert "TEST_KEY" not in registry_content().keys()


    def test_registry_content(self):
        yamlparser.registry_parser(self.registry_file, command_line_options=["-a", "-k", "TEST_KEY", "-v", "test_variable", "-l"])

        namespace = yamlparser.NameSpace(
            {
                "name": "My Name",
                "data" : {
                    "registry" : "TEST_KEY"
                }
            }
        )

        assert namespace.data == "test_variable"


    def test_environment_content(self):
        os.environ["TEST_KEY"] = "test_variable"
        assert get_registered_variable("TEST_KEY") == "test_variable"

        namespace = yamlparser.NameSpace(
            {
                "name": "My Name",
                "data" : {
                    "registry" : "TEST_KEY"
                }
            }
        )

        assert namespace.data == "test_variable"


if __name__ == "__main__":
    unittest.main()
