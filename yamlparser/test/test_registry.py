import yamlparser
from yamlparser.registry import set_registry_file, get_registered_variable, set_registered_variable, delete_registered_variable, registry_content
from yamlparser.namespace import get_required_registration
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
        yamlparser.registry_parser(self.registry_file, command_line_options=["-a", "-k", "TEST_KEY", "-e", "test_variable", "-l"])

        assert get_registered_variable("TEST_KEY") == "test_variable"

        # delete it again
        yamlparser.registry_parser(self.registry_file, command_line_options=["-d", "-k", "TEST_KEY"])

        assert "TEST_KEY" not in registry_content().keys()


    def test_registry_content(self):
        yamlparser.registry_parser(self.registry_file, command_line_options=["-a", "-k", "TEST_KEY", "-e", "test_variable", "-l"])

        namespace = yamlparser.NameSpace(
            {
                "name": "My Name",
                "data" : {
                    "registry" : "TEST_KEY"
                }
            }
        )

        assert namespace.data == "test_variable"
        assert namespace.name == "My Name"


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


    def test_registry_file_content(self):
        # test loading from YAML file
        yamlparser.registry_parser(self.registry_file, command_line_options=["-a", "-k", "TEST_KEY", "-e", "test_variable", "-l"])

        namespace = yamlparser.NameSpace("yamlparser @ registry_config.yaml")

        assert namespace.data == "test_variable"

        # test searching yaml files
        for trial in ["@yamlparser", "yamlparser/test", "yamlparser/test/registry_config.yaml"]:
            registry_contents = get_required_registration([trial])
            assert len(registry_contents) == 1
            assert "TEST_KEY" in registry_contents
            assert len(registry_contents["TEST_KEY"]) == 1
            assert len(registry_contents["TEST_KEY"][0]) == 2
            assert registry_contents["TEST_KEY"][0][1] == "data.registry"
            assert str(registry_contents["TEST_KEY"][0][0]).endswith("registry_config.yaml")




if __name__ == "__main__":
    unittest.main()
