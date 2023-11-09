import argparse
import sys

from .namespace import NameSpace

def config_parser(parser=None, default_config_file=None, infer_types=True, command_line_options=None, add_config_files=False):
    # create the initial parser
    command_line_options = command_line_options or sys.argv[1:]
    # check if the help on the default parser is requested
    requests_help = len(command_line_options) == 0 or len(command_line_options) == 1 and command_line_options[0] in ("-h", "--help")
    _config_parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, add_help=requests_help)
    _config_parser.add_argument("configuration_files", nargs="+", default=[default_config_file], help="The configuration files to parse. From the second config onward, it be key=value pairs to create sub-configurations")

    args,_ = _config_parser.parse_known_args(command_line_options)
    namepsace = NameSpace(args.configuration_files[0])
    for cfg in args.configuration_files[1:]:
        splits = cfg.split("=")
        if len(splits)>1:
            namepsace.add(splits[0], splits[1])
            for s in splits[2:]:
                namepsace.update(splits[0], s)
        else:
            namepsace.update(splits[0])

    # compute the types of the nested configurations
    attributes = namepsace.attributes()

    # create a parser entry for these types
    if parser is None:
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("configuration_files", nargs="+", default=[default_config_file], help="The configuration files to parse. From the second config onward, it be key=value pairs to create sub-configurations")

    for k,v in attributes.items():
        metavar = k.split(".")[-1].upper()
        option = "--"+k
        if isinstance(v, list):
            parser.add_argument(option, metavar=metavar, nargs="+", type=type(v[0]) if infer_types else None, help=f"Overwrite list of values for {k}, default={v}")
        else:
            parser.add_argument(option, metavar=metavar, type=type(v) if infer_types else None, help=f"Overwrite value for {k}, default={v}")

    # parse arguments again
    args = parser.parse_args(command_line_options)

    # overwrite values in config
    for k,v in vars(args).items():
        if add_config_files or k != "configuration_files":
            if v is not None:
                namepsace.set(k,v)

    return namepsace
