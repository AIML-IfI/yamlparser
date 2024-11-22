import yaml
import os
import pathlib
import importlib.resources

from .registry import get_registered_variable

_modifiable = "_modifiable"
_sub_config_key = "_sub_config_key"
_registry_key = "_registry_key"
_ignore_keys = [_modifiable, _sub_config_key, _registry_key]

def list_config_files(package, configuration_file_extensions=[".yaml", ".yml"]):
    """Lists all configuration files found in the given package that have the given filename extensions.
    Note that these files might be virtual and not correspond to physical files on the operating system.

    Parameters:
    package: str
    The name of the package for which you want to list all configuration files

    configuration_file_extensions: [str]
    A list of filename extensions of configuration files that should be found

    Returns:
    A list of (configuration) files with relative paths from within the package.

    """
    # read resource files within package
    resource_files = importlib.resources.files(package).rglob("*")

    # filter files with the given extensions
    return [
        resource_file
        for resource_file in resource_files
        if os.path.splitext(resource_file)[1] in configuration_file_extensions
    ]

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
    def __init__(self, config, modifiable=True, sub_config_key="yaml", registry_key="registry"):
        """Initializes this object with the given configuration, which can be a file name (for the yaml config file) or a dictionary

        Parameters
        config: str or dict
        A (nested) dictionary or a yaml filename that contains the configuration.
        When providing a filename, you can also make use of package shortcuts by using `package @ relative/path/to/file.yaml`.
        It is also possible to omit (parts of) the path as long as the file name is unique, e.g., `package@file.yaml`.

        modifiable: boolean
        If enabled (the default), this configuration object can be changed by adding new entries.
        Otherwise, trying to add new entries will raise an exception.

        sub_config_key: str
        When the configuration files contain this key, this is interpreted as an additional linked config file.

        registry_key: str
        When the configuration files contain this key, it is replaced with its value that is stored in the registry or provided in the environment
        """
        self._sub_config_key = sub_config_key
        self._registry_key = registry_key
        self._modifiable = True
        self.update(config)
        self._modifiable = modifiable

    def clone(self):
        """Returns a copy of this namespace"""
        return NameSpace(self.dict(), self._modifiable, self._sub_config_key, self._registry_key)

    def keys(self):
        """Returns the current list of keys in this namespace"""
        return self.dict().keys()


    def add(self, key, config):
        """Adds the given configuration as a sub-namespace.
        This is identical to `self.key = NameSpace(config)`"""
        # adds a different config file into a sub-namespace
        self[key] = NameSpace(config, self._modifiable, self._sub_config_key, self._registry_key)

    def set(self, key, value):
        """Sets a value for a given key. This key can contain periods, which are parsed to index sub-namespaces"""
        if not self._modifiable:
            raise AttributeError(f"You are trying to overwrite key {key} in a frozen namespace")
        keys = key.split(".")
        if len(keys) > 1:
            getattr(self,keys[0]).set(".".join(keys[1:]), value)
        else:
            self[key] = value

    def delete(self, key):
        """Removes the given key from this namespace. The key can contain periods, which are parsed into sub-namespaces"""
        if not self._modifiable:
            raise AttributeError(f"You are trying to delete key {key} from a frozen namespace")

        keys = key.split(".")
        if len(keys) > 1:
            self[keys[0]].delete(".".join(keys[1:]))
        else:
            delattr(self, key)

    def _load_subconfig(self, name, value):
        # create sub-config
        namespace = NameSpace(value, self._modifiable, self._sub_config_key, self._registry_key)
        # check if there is a sub-config file listed
        if self._sub_config_key in namespace.keys():
            if not isinstance(namespace[self._sub_config_key], str):
                raise ValueError(f"The '{self._sub_config_key}' keyword requires a file name, but we got '{namespace[self._sub_config_key]}' instead")
            # load config file
            sub_config = NameSpace(namespace[self._sub_config_key], self._modifiable, self._sub_config_key)
            keys = list(sub_config.keys())
            if name in keys:
                # set this as the config
                namespace = sub_config[name]
            else:
                if len(keys) == 1:
                    # set this as the config
                    namespace = sub_config[keys[0]]
                else:
                    raise ValueError(f"The sub configuration file {namespace[self._sub_config_key]} has several keys, but not including  '{name}'")
            # apply any overwrites from this config file
            namespace.update({k:v for k,v in value.items() if k != self._sub_config_key})

        # check if there is a registered variable
        if self._registry_key in namespace.keys():
            if not isinstance(namespace[self._registry_key], str):
                raise ValueError(f"The '{self._registry_key}' keyword requires a registry key, but we got '{namespace[self._registry_key]}' instead")
            return get_registered_variable(namespace[self._registry_key])
        return namespace


    def update(self, config):
        """Updates this namespace with the given configuration. Sub-namespaces will be entirely overwritten, not updated."""
        # Updates this namespace with the given config
        # read from yaml file, if it is a file
        loaded_config = self.load(config)
        # recurse through configuration dictionary to build nested namespaces
        config = {}
        for name, value in loaded_config.items():
            # if the name contains at least one period, we have a nested namespace
            if "." in name:
                # split the name into the first part and the rest
                first, rest = name.split(".", 1)
                # create a new namespace if not existing
                if first not in config.keys():
                    config[first] = NameSpace({}, self._modifiable, self._sub_config_key, self._registry_key)
                # update the sub-namespace
                config[first].update({rest:value})
            else:

                if isinstance(value, dict):
                    config[name] = self._load_subconfig(name, value)
                elif isinstance(value, list):
                    config[name] = []
                    for element in value:
                        if isinstance(element, dict):
                            config[name].append(self._load_subconfig(name, element))
                        else:
                            config[name].append(element)
                else:
                    config[name] = value

        # update configuration
        self.__dict__.update(config)

    def freeze(self):
        """Freezes this namespace recursively."""
        # recursively freeze all sub-namespaces
        for value in vars(self).values():
            if isinstance (value, NameSpace):
                value.freeze()
        self._modifiable = False

    def unfreeze(self):
        """Unfreezes this namespace recursively."""
        self._modifiable = True
        for value in vars(self).values():
            if isinstance (value, NameSpace):
                value.unfreeze()

    def load(self, config):
        """Loads the configuration from the given YAML filename, which might include package @ filename"""
        if isinstance(config, (str, pathlib.Path)):
            return self._load_config_file(config)

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

        If the given string is a list, formatting is applied to all elements of that list (recursively).

        Returns:
          the formatted string
        """
        if isinstance(string, list):
            return [self.format(s) if isinstance(s, (str, list)) else s for s in string]

        for k,v in self.attributes().items():
            string = string.replace(f"{{{k}}}", str(v))
        return string

    def format_self(self):
        """Formats all internal string variables (and list of string variables) using the :func:`format` function.
        This function works recursively, it formats all sub-namespaces accordingly.
        Note that nested sub_namespaces can have both nested and non-nested keys:

        nested:
            key: value
            key1: {nested.key}
            key2: {key}

        both nested.key1 and nested.key2 will be evaluated as "value".
        """
        # format all strings and lists of strings
        for key, value in self.attributes().items():
            if isinstance (value, (str,list)):
                self.set(key, self.format(value))
        # recursively freeze all sub-namespaces
        for value in vars(self).values():
            if isinstance (value, NameSpace):
                value.format_self()


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
            elif key not in _ignore_keys:
                attributes[key] = self[key]
        return attributes

    def dict(self):
        """Returns the entire configuration as a nested dictionary, by converting sub-namespaces"""
        d = {}
        for k,v in vars(self).items():
            if not k in _ignore_keys:
                if isinstance(v, NameSpace):
                    d[k] = v.dict()
                elif isinstance(v, list):
                    d[k] = [i.dict() if isinstance(i, NameSpace) else i for i in v]
                else:
                    d[k] = v
        return d

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
        if not self._modifiable:
            raise AttributeError(f"You are trying to set key {key} in a frozen namespace")
        if isinstance(value, dict):
            self.__dict__.update({key:NameSpace(value, self._modifiable, self._sub_config_key, self._registry_key)})
        else:
            self.__dict__.update({key:value})

    def __getattr__(self, key):
        """Allows adding new sub-namespaces inline"""
        if key in _ignore_keys:
            return self.__getattribute__(key)
        if not self._modifiable:
            raise AttributeError(f"You are trying to add new key {key} to a frozen namespace")
        # create new empty namespace if not existing
        namespace = NameSpace({}, self._modifiable, self._sub_config_key, self._registry_key)
        self.update({key:namespace})
        return namespace

    def __setattr__(self, key, value):
        """Allows adding new sub-namespaces inline"""
        if key != _modifiable and hasattr(self, _modifiable) and not self._modifiable:
            raise AttributeError(f"You are trying to add new key {key} to a frozen namespace")
        # call  the original setattr function
        super(NameSpace, self).__setattr__(key,value)

    def __getstate__(self):
        """No idea why this is required"""
        return self.__dict__

    def __setstate__(self, value):
        """No idea why this is required"""
        self.__dict__.update(value)

    def _load_config_file(self, config):
        """Finds the configuration file within a package and loads the configuration"""
        assert isinstance(config, str), f"The given configuration {config} is not a file name"
        splits = config.split("@")

        if len(splits) == 1:
            # load config file directly
            config = splits[0].strip()

        elif len(splits) == 2:
            # load config from package resources
            package = splits[0].strip()
            resource = pathlib.Path(splits[1].strip())
            # list all resource files within the package
            package_files = list_config_files(package, [resource.suffix])
            # find possible candidates for resource files
            candidates = [f for f in package_files if str(f).endswith(str(resource))]
            if not len(candidates):
                raise ValueError(f"Could not find configuration file {resource} in package {package}; possible files are: {package_files}")
            if len(candidates) > 1:
                raise ValueError(f"The given config file {resource} is not unique in package {package}; candidates are: {candidates}")
            # take the unique file
            config = candidates[0]

        else:
            raise ValueError(f"Could not interpret configuration file {config}")

        if not os.path.isfile(config):
            raise IOError(f"Could not find config file {config}")

        with open(config, 'r') as f:
            # return the loaded yaml file, or an empty dictionary in case safe_load returns None
            return yaml.safe_load(f) or {}
