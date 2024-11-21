import argparse
import sys
import warnings

from .namespace import NameSpace

global _config
_config = None

def config_parser(
        parser=None,
        default_config_files=None,
        infer_types=True,
        ignore_keys=[],
        add_config_files=False,
        command_line_options=None,
        store_config=True,
        auto_format=True,
        sub_config_key="yaml"
    ):
    """Creates or updates an `argparse.ArgumentParser` with the option to load configuration files (YAML).
    These files will be automatically parsed and each configuration will be added as a separate option to the command line.
    After calling this function, the global :py:func:`get_config` will return the loaded configuration.

    Arguments:

    parser : argparse.ArgumentParser or None
    If given, options will be added to that parser. Otherwise, a new parser will be created.

    default_config_files: list or None
    If given, a list of default configuration files is provided.

    infer_types: bool
    If selected (the default), types are inferred from the data types of the configuration file.
    If disabled, all options will be provided as `str`.

    ignore_keys: [str]
    These keys will not be put on the command line as options.

    add_config_files: bool
    If selected, the list of configuration files is added to the final configuration under the `configuration_files` list.

    command_line_options: list or None
    For debugging purposes, a list of command line options is accepted. This is mainly a debug and test feature.
    If not present, `sys.argv[1:]` is selected, as usual.

    store_config: bool
    If selected (the default), the configuration will be stored in a global object that can be accessed via py:func:`get_config()`.
    Note that, in this case, the configuration is frozen and can no longer be updated (unless unfreeze is called).
    Note further that all string variables are automatically evaluated.

    auto_format: bool
    If selected (the default), the configuration will be formatted such that {key} values are replaced with the actual values in the configuration.
    You can later call namespace.format_self() in order to format it.
    Note that `None` values (aka. `null` in the yaml file) will be replaced by `str`.

    sub_config_key: str
    When the configuration files contain this key, this is interpreted as an additional linked config file.

    Returns:
    namespace: NameSpace
    A namespace object containing all options taken from configuration file and command line.
    """
    # create the initial parser
    command_line_options = command_line_options or sys.argv[1:]
    # check if the help on the default parser is requested
    requests_help = len(command_line_options) == 0 or len(command_line_options) == 1 and command_line_options[0] in ("-h", "--help")
    if parser is not None and requests_help:
        # ask for the help of the given parser
        parser.parse_args(command_line_options)

    _config_parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, add_help=requests_help and not default_config_files, usage='%(prog)s [arguments] [options]')
    _config_parser.add_argument("configuration_files", nargs="+", default=default_config_files, help="The configuration files to parse. From the second config onward, it can be key=value pairs to create sub-configurations")

    # parse the known args, which should only be config files in our case
    config_file_options = []
    for option in command_line_options:
        if option[0] == "-" and (not requests_help or option not in ("-h", "--help")): break
        config_file_options.append(option)
    args = _config_parser.parse_args(config_file_options)

    namespace = NameSpace(args.configuration_files[0], sub_config_key)
    for cfg in args.configuration_files[1:]:
        splits = cfg.split("=")
        if len(splits)>1:
            namespace.add(splits[0], splits[1])
            for s in splits[2:]:
                namespace[splits[0]].update(s)
        else:
            namespace.update(splits[0])

    # compute the types of the nested configurations
    attributes = namespace.attributes()

    # create a parser entry for these types
    if parser is None:
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, usage='%(prog)s configuration_files [options]')

    existing_options = list(parser._option_string_actions.keys())

    parser.add_argument("configuration_files", nargs="*", default=default_config_files, help="The configuration files to parse. From the second config onward, it be key=value pairs to create sub-configurations")

    for k,v in attributes.items():
        if k in ignore_keys: continue
        metavar = k.split(".")[-1].upper()
        option = "--"+k

        if option in existing_options:
            # option was requested in the parser, but we already have this option
            # in this case, we update the default value with the one read from the config
            parser._option_string_actions[option].default = v
        elif isinstance(v, list):
            requested_type = type(v[0]) if infer_types and v[0] is not None else None
            parser.add_argument(option, metavar=metavar, nargs="+", type=requested_type, help=f"Overwrite list of values for {k}, default={v}")
        else:
            requested_type = type(v) if infer_types and v is not None else None
            parser.add_argument(option, metavar=metavar, type=requested_type, help=f"Overwrite value for {k}, content of configuration file: `{v}`")

    # parse arguments again
    args = parser.parse_args(command_line_options)

    # overwrite values in config
    for k,v in vars(args).items():
        if add_config_files or k != "configuration_files":
            if v is not None:
                namespace.set(k,v)

    if auto_format:
        namespace.format_self()

    if store_config:
        global _config
        if _config is not None:
            warnings.warn("The configuration has already been set, overwriting it.")
        _config = namespace
        _config.freeze()

    return namespace


def get_config():
    """Returns the global configuration object, which is the result of (the latest call to) py:func:`config_parser`.

    Returns:
    config: NameSpace
    The namespace object containing all options taken from configuration file and command line.

    Raises: RuntimeError
    If the configuration has not been loaded yet.
    """
    global _config
    if _config is None:
        raise RuntimeError("Please call 'config_parser(..., store_config=True)' before trying to access the configuration")
    return _config
