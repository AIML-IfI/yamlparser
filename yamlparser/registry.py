import os
import pathlib
import warnings

_registry_file = pathlib.Path.home() / ".yamlparser.yaml"

def set_registry_file(registry_file):
    global _registry_file
    _registry_file = pathlib.Path(registry_file)

def get_registry_file():
    return _registry_file

def registry_content():
    from .namespace import NameSpace

    # check registry file
    registry = _registry_file
    if registry.is_file():
        # load and update registry if existent
        namespace = NameSpace(str(registry))
    else:
        # create new registry
        namespace = NameSpace({})
    return namespace


def get_registered_variable(variable):
    # check registry file
    namespace = registry_content()
    if variable in namespace.attributes():
        return namespace[variable]

    # check environment
    if variable in os.environ:
        return os.environ[variable]

    warnings.warn(f"The given variable {variable} was neither found in the registry file {_registry_file} nor has it been set as environment variable")
    return variable


def set_registered_variable(variable, value):

    namespace = registry_content()
    namespace.set(variable, value)

    # dump registry
    namespace.save(_registry_file)


def delete_registered_variable(variable):

    # check registry file
    if not _registry_file.is_file():
        raise ValueError(f"The registry {_registry_file} does not exist")

    namespace = registry_content()
    if variable not in namespace.attributes():
        raise ValueError(f"The variable '{variable}' is not registered in registry file '{_registry_file}'")

    # delete value
    namespace.delete(variable)

    # dump registry
    namespace.save(_registry_file)
