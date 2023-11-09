# YAML Configuration and Argument Parsing


This package is designed to combine the parsing of configuration files and command line options.
Basically, configuration files (currently we support YAML files only) will be parsed and returned in a [NameSpace data structure](#namespace).
Additionally, all options contained in the configuration files will be added to a [command line parser](#parser), so that any option from the command line can be overwritten in that `NameSpace` -- and all other options will be added to the `NameSpace` as well.


## DISCLAIMER

This package is work in progress. Currently, only YAML configuration files and `argparse` parsers are supported.
Also, the documentation might be incomplete and not be up-to-date yet.


## Installation

This package is available on the Python Package Index, so you can simply do a pip install:

    pip install yamlparser

For the latest version from github, you can also use pip install:

    pip install git+https://github.com/AIML-IfI/yamlparser.git

## Getting Help

If you find a bug in the code or wish to propose changes, feel free to file an issue or open a merge request.
Please contact siebenkopf@googlemail.com in all other cases of issues.

## Documentation

### NameSpace

The `NameSpace` class is designed to hold configuration options.
`NameSpace`'s can be constructed from any type of nested dictionary:

    namespace = yamlparser.NameSpace({
        "name" : "Jon Doe",
        "age"  : 42,
        "address" : {
            "street" : "Main Street",
            "number" : 10
        }
    })

Each nested dictionary internally is transferred into a sub-namespace.
Please note that keys in the dictionary are restricted to valid python variable names.

Similarly, `NameSpace`'s can load these dictionaries directly from a YAML file:

    namespace = yamlparser.NameSpace("config.yaml")

The options contained in a `NameSpace` can be accessed either as attributes, or via indexing:

    namespace.name
    namespace["age"]

Sub-namespaces follow the exact same principle:

    namespace.address.street
    namesapce["address"]["number"]

Generally, values can be added to a `NameSpace` by simple assignment:

    namespace.address.city = "Zurich"
    namespace["address"]["zip"] = 8050

It is even possible to create new sub-namespaces on the fly:

    namespace.children.daughter = "Jane Doe"
    namespace["children"].son = "Jake Doe"

Finally, `NameSpace` objects can be written to YAML files:

    namespace.save("path/to/my/file.yaml")

### Parser

The main of this package is to combine configurations read from YAML files with command line parsing.
Precisely, we want to automatically be able to overwrite any parameter that is contained in a configuration file on the command line, but keep the default if it is not updated.
For this purpose, we provide a simple function `config_parser`, which is called in the `script.py` that you can find in the main directory and writes the configuration to console:

    [content of script.py]
    import yamlparser
    namespace = yamlparser.config_parser()
    print(namespace.dump())

The `config_parser` function internally creates and `argparse` parser that requests for a (list of) configuration files.
    $ python script.py --help

    usage: [-h] configuration_files [configuration_files ...]

    positional arguments:
      configuration_files  The configuration files to parse. From the second config onward, it be key=value pairs to create sub-configurations

    optional arguments:
      -h, --help           show this help message and exit

When presenting a configuration file, it is automatically parser and all its contents are added to the parser:

    $ python script.py config.yaml --help

    usage: script.py [-h] [--name NAME] [--age AGE] [--address.street ADDRESS.STREET] [--address.number ADDRESS.NUMBER] configuration_files [configuration_files ...]

    positional arguments:
      configuration_files   The configuration files to parse. From the second config onward, it be key=value pairs to create sub-configurations

    optional arguments:
      -h, --help            show this help message and exit
      --name NAME           Overwrite value for name, default=Jon Doe
      --age AGE             Overwrite value for age, default=42,
      --address.street ADDRESS.STREET
                            Overwrite value for address.street, default=Main Street
      --address.number ADDRESS.NUMBER
                            Overwrite value for address.number, default=10

As you can see, sub-namespaces are separated using a period `.` to avoid name clashes.
When removing the `--help` option, you can see the parser configurations (the default behavior of `script.py`):

    $ python script.py config.yaml

    address:
        number: 10
        street: Main Street
    age: 42
    name: Jon Doe

You can overwrite any of these options on the command line:

    $ python script.py config.yaml --name "Jane Doe" --address.number 911

    address:
        number: 911
        street: Main Street
    age: 42
    name: Jane Doe

Note that by default, the options infer the data types from the YAML file, e.g., if the YAML file contains an integer, only integer values are accepted:

    $ python script.py config.yaml --age 12.5

    usage: script.py [-h] [--name NAME] [--age AGE] [--address.street ADDRESS.STREET] [--address.number ADDRESS.NUMBER] configuration_files [configuration_files ...]
    script.py: error: argument --age: invalid int value: '12.5'

At least one configuration file needs to be present, but more than one file can be specified, in which case configurations of the former files are overwritten by latter files.
It is also possible to add configuration files into sub-namespaces by defining a `name=file.yaml` on command line:

    $ python script.py config.yaml data=config.yaml

    address:
        number: 10
        street: Main Street
    age: 42
    data:
        address:
            number: 10
            street: Main Street
        age: 42
        name: Jon Doe
    name: Jon Doe

Additionally, we wish to be able to add command line options to our configurations that do not appear in any configuration file.
This can be done programatically by providing a parser with specific options, and example is provided in `extend.py`:

    [content of extended.py]
    import yamlparser, argparse
    parser = argparse.ArgumentParser()
    parser.add_option("--haircolor")
    parser.add_option("--dob.year", type=int)
    parser.add_option("--dob.month", type=int, default=8)
    namespace = yamlparser.config_parser(parser=parser)
    print(namespace.dump())

When calling this script, the selected options will be added to the options:

    $ python extended.py config.yaml --help

    usage: extended.py [-h] [--haircolor HAIRCOLOR] [--dob.year DOB.YEAR] [--dob.month DOB.MONTH] [--name NAME] [--age AGE] [--address.street STREET] [--address.number NUMBER]
                      configuration_files [configuration_files ...]

    positional arguments:
      configuration_files   The configuration files to parse. From the second config onward, it be key=value pairs to create sub-configurations

    optional arguments:
      -h, --help            show this help message and exit
      --haircolor HAIRCOLOR
                            Set hair color
      --dob.year DOB.YEAR   Set year of birth
      --dob.month DOB.MONTH
                            Set month of birth, default=8
      --name NAME           Overwrite value for name, default=Jon Doe
      --age AGE             Overwrite value for age, default=42
      --address.street STREET
                            Overwrite value for address.street, default=Main Street
      --address.number NUMBER
                            Overwrite value for address.number, default=10

Any selected option will be reflected in the returned namespace:

    $ python extended.py config.yaml --haircolor Brown

    address:
        number: 10
        street: Main Street
    age: 42
    dob:
        month: 8
    haircolor: Brown
    name: Jon Doe

Please note that options without default values that are not provided on the command line are not represented in the configuration.
We propose to provide default values for all options (which cannot be `None`) to avoid surprises.
