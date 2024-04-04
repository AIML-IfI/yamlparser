import yamlparser
import os
import unittest

class TestArgparse(unittest.TestCase):

    def test_parser(self):
        yaml_file = os.path.join(os.path.dirname(__file__), "test_config.yaml")
        command_line_options = (yaml_file,)
        namespace = yamlparser.config_parser(command_line_options=command_line_options, store_config=False)

        expected = yamlparser.NameSpace({
            "name": "test",
            "int_value": 42,
            "list_value": [10, 42, 101],
            "nested": {
                "name": "nested_test",
                "pi": 3.14159265,
                "nested": {
                    "name": "subnested"
                },
            },
            "some": {
                "dot": {
                    "attribute": 42
                }
            }
        })
        self.assertEqual(namespace.dump(), expected.dump())

    def test_parser_help(self):
        command_line_options = ("--help",)
        with self.assertRaises(SystemExit):
            namespace = yamlparser.config_parser(command_line_options=command_line_options, store_config=False)

    def test_parser_update_help(self):
        yaml_file = os.path.join(os.path.dirname(__file__), "test_config.yaml")
        command_line_options = (yaml_file, "--help")
        with self.assertRaises(SystemExit):
            namespace = yamlparser.config_parser(command_line_options=command_line_options, store_config=False)

    def test_parser_update(self):
        yaml_file = os.path.join(os.path.dirname(__file__), "test_config.yaml")
        command_line_options = (yaml_file, "--name", "UPDATED")
        namespace = yamlparser.config_parser(command_line_options=command_line_options, store_config=False)
        self.assertTrue(hasattr(namespace, "name"))
        self.assertTrue(hasattr(namespace, "UPDATED"))

    def test_multiple_config(self):
        yaml_file1 = os.path.join(os.path.dirname(__file__), "test_config.yaml")
        yaml_file2 = os.path.join(os.path.dirname(__file__), "sub_config.yaml")

        # put both into the same namespace
        command_line_options = (yaml_file1, yaml_file2)
        namespace = yamlparser.config_parser(command_line_options=command_line_options, store_config=False)
        self.assertEqual(namespace.name, "test")
        self.assertEqual(namespace.item, "sub")

        # put the second into a sub-namespace
        command_line_options = (yaml_file1, f"minor={yaml_file2}")
        namespace = yamlparser.config_parser(command_line_options=command_line_options, store_config=False)
        self.assertEqual(namespace.name, "test")
        self.assertEqual(namespace.minor.item, "sub")

    def test_global_config(self):
        yaml_file = os.path.join(os.path.dirname(__file__), "test_config.yaml")
        command_line_options = (yaml_file, "--name", "UPDATED")
        namespace = yamlparser.config_parser(command_line_options=command_line_options)
        config = yamlparser.get_config()
        self.assertIs(config, namespace)


if __name__ == "__main__":
    unittest.main()