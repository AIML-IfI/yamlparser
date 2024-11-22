import yamlparser
import pathlib
registry_file = pathlib.Path.home() / ".my_registry_file.yaml"
yamlparser.registry_parser(registry_file)
