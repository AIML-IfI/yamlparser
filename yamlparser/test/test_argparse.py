import yamlparser
import os

def test_parser():
    yaml_file = os.path.join(os.path.dirname(__file__), "test_config.yaml")
    command_line_options = (yaml_file,)
    namespace = yamlparser.config_parser(command_line_options=command_line_options, store_config=False)

    print(namespace.dump())

def test_parser_help():
    command_line_options = ("--help",)
    try:
        namespace = yamlparser.config_parser(command_line_options=command_line_options, store_config=False)
        print(namespace.dump())
    except SystemExit:
        pass

def test_parser_update_help():
    yaml_file = os.path.join(os.path.dirname(__file__), "test_config.yaml")
    command_line_options = (yaml_file, "--help")
    try:
        namespace = yamlparser.config_parser(command_line_options=command_line_options, store_config=False)
        print(namespace)
    except SystemExit:
        pass

def test_parser_update():
    yaml_file = os.path.join(os.path.dirname(__file__), "test_config.yaml")
    command_line_options = (yaml_file, "--name", "UPDATED")
    namespace = yamlparser.config_parser(command_line_options=command_line_options, store_config=False)
    print(namespace.dump())

def test_multiple_config():
    yaml_file1 = os.path.join(os.path.dirname(__file__), "test_config.yaml")
    yaml_file2 = os.path.join(os.path.dirname(__file__), "sub_config.yaml")

    # put both into the same namespace
    command_line_options = (yaml_file1, yaml_file2)
    namespace = yamlparser.config_parser(command_line_options=command_line_options, store_config=False)
    assert namespace.name == "test"
    assert namespace.item == "sub"
    print(namespace.dump())

    # put the second into a sub-namespace
    command_line_options = (yaml_file1, f"minor={yaml_file2}")
    namespace = yamlparser.config_parser(command_line_options=command_line_options, store_config=False)
    assert namespace.name == "test"
    assert namespace.minor.item == "sub"
    print(namespace.dump())

def test_global_config():
    yaml_file = os.path.join(os.path.dirname(__file__), "test_config.yaml")
    command_line_options = (yaml_file, "--name", "UPDATED")
    namespace = yamlparser.config_parser(command_line_options=command_line_options)
    config = yamlparser.get_config()
    assert config is namespace


if __name__ == "__main__":
    test_parser()
    test_parser_help()
    test_parser_update_help()
    test_multiple_config()
    test_global_config()
