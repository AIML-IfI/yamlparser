import yaml
import os
import pathlib

class NameSpace:
    """This is the main class representing our configuration.
    This configuration can be loaded from a configuration file
    (currently, YAML is supported). Nested configurations are represented as nested NameSpaces
    Values inside the namespace and accessed via indexing `namespace[key]` or via attribution `namespace[key]`.

    Example:

    Content of yaml file:
    ```
    name: Name
    nested:
        email: name@host.domain
    ```

    Code via attribution:
    ```
    cfg = NameSpace(yaml_file_name)
    cfg.name -> "Name"
    cfg.nested -> NameSpace
    cfg.nested.email -> "name@host.domain"
    ```

    Code via indexing:
    ```
    cfg = NameSpace(yaml_file_name)
    cfg["name"] -> "Name"
    cfg["nested"] -> NameSpace
    cfg["nested"]["email"] -> "name@host.domain"
    ```

    Note that currently, dictionaries contained in lists are not supported (will not be transformed into sub-namespaces).

    """
    def __init__(self, config):
        """Initializes this object with the given configuration, which can be t file name (for of the yaml config file) or a dictionary

        Parameters
        config:

        """
        self.update(config)

    def add(self, key, config):
        """Adds the given configuration as a sub-namespace.
        This is identical to `self.key = NameSpace(config)`"""
        # adds a different config file into a sub-namespace
        self[key] = NameSpace(config)

    def set(self, key, value):
        """Sets a value for a given key. This key can contain periods, which are parsed to index sub-namespaces"""
        keys = key.split(".")
        if len(keys) > 1:
            getattr(self,keys[0]).set(".".join(keys[1:]), value)
        else:
            self[key] = value

    def update(self, config):
        """Updates this namespace with the given configuration. Sub-namespaces will be entirely overwritten, not updated."""
        # Updates this namespace with the given config
        # read from yaml file, if it is a file
        config = self.load(config)
        # recurse through configuration dictionary to build nested namespaces
        config = {name : NameSpace(value) if isinstance(value, dict) else value for name, value in config.items()}
        self.__dict__.update(config)

    def load(self, config):
        """Loads the configuration from the given YAML filename"""
        if isinstance(config, (str, pathlib.Path)):
            if os.path.isfile(config):
                config = yaml.safe_load(open(config, 'r'))
            else:
                raise IOError(f"Could not find configuration file {config}")

        if not isinstance(config,dict):
            raise ValueError(f"The configuration should be a dictionary")
        return config

    def save(self, yaml_file, indent=4):
        """Saves the configuration to a yaml file"""
        with open(yaml_file, "w") as f:
            f.write(self.dump(indent))

    def format(self, string):
        """Formats the given string and replaces keys with contents

        This function replaces all occurrences of `{KEY}` values in the given string with the value stored in this `NameSpace` instance.
        Here, `KEY` can be any fully-quoted string as returned by the :func:`attributes` function.

        Returns:
          the formatted string
        """
        for k,v in self.attributes().items():
            string = string.replace(f"{{{k}}}", str(v))
        return string

    def dump(self, indent=4):
        """Pretty-prints the config to a string"""
        return yaml.dump(self.dict(), indent=indent)

    def attributes(self):
        """Returns a list of attributes of this NameSpace including all sub-namespaces

        For sub-namespaces, a period is used to separate namespace and subnamespace

        Returns:
          attributes: dict[attribute->value]
        """
        attributes = {}
        for key in vars(self):
            if isinstance(self[key], NameSpace):
                attributes.update({
                    key+"."+k:v for k,v in (self[key].attributes()).items()
                })
            else:
                attributes[key] = self[key]
        return attributes

    def dict(self):
        """Returns the entire configuration as a nested dictionary, by converting sub-namespaces"""
        return {k: v.dict() if isinstance(v, NameSpace) else v for k,v in vars(self).items()}

    def __repr__(self):
        """Prints the contents of this namespace"""
        return "NameSpace\n"+self.dump()

    def __getitem__(self, key):
        """Allows indexing with a key"""
        # get nested NameSpace by key
        nested = vars(self)
        return nested[key]

    def __setitem__(self, key, value):
        """Allows setting elements with a key. If the given value is a dictionary, this will generate a sub-namespace for it"""
        if isinstance(value, dict):
            self.__dict__.update({key:NameSpace(value)})
        else:
            self.__dict__.update({key:value})

    def __getattr__(self, key):
        """Allows adding new sub-namespaces inline"""
        # create new empty namespace if not existing
        namespace = NameSpace({})
        self.update({key:namespace})
        return namespace
