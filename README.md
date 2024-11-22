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

#### Creating NameSpace objects

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

This YAML file can also be loaded from within a package by providing the package name and a relative path:

    namespace = yamlparser.NameSpace("package @ relative/path/to/config.yaml")

As long as file names are unique, you can also omit (parts of) the path to the config file in the package:

    namespace = yamlparser.NameSpace("package @ config.yaml")


A list of such configuration files inside any package can be obtained via:

    package_config_files = yamlparser.list_config_files("package")

#### Accessing NameSpace contents

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

`NameSpace` objects can be written to YAML files:

    namespace.save("path/to/my/file.yaml")

You can also turn this `NameSpace` into a fully-quoted dictionary, where sub-namespaces are separated using a period `.` to avoid name clashes:

    namespace.attributes()

will return:

    {
        'name': 'Jon Doe',
        'age': 42,
        'address.street': 'Main Street',
        'address.number': 10,
        'address.city': 'Zurich',
        'address.zip': 8050,
        'children.daughter': 'Jane Doe',
        'children.son': 'Jake Doe'
    }

You can `freeze` and `unfreeze` a `NameSpace` object.
Frozen objects cannot be modified or extended in any way.

#### Combining NameSpaces

When loading a configuration from a configuration file, it is also possible to load part of this configuration from another file.
This is particularly useful when combining contents of different configuration files, which might be pre-defined in code packages.
To load a specific configuration from a different configuration file, you can simply use a special keyword, `yaml` by default.
Note that you can also overwrite or extend options loaded from the referenced configuration file:

    # contents of path/to/address/file.yaml
    address:
        street: "Main Street"
        number: 10
        city: "Zurich"

    # contents of jondoe.yaml
    name: "Jon Doe"
    age: 42
    address:
        yaml: path/to/address/file.yaml
        number: 14

When creating a `NameSpace` object from file `jondoe.yaml`, it will automatically load the address from the address file, and overwrite the settings `number` from the referenced config file:

    namespace = NameSpace("jondoe.yaml")
    print(namespace)

will result in:

    name: Jon Doe
    age: 42
    address:
        street: Main Street
        number: 14
        city: Zurich

Please note that the `yaml` file parameter can also include package information, see construction of `NameSpace` above.


#### Formatting NameSpace contents

Finally, you can format a given string with the contents of a `NameSpace`.
Simply use fully-quoted embraced keys, and you will get the according values.
This feature is particularly useful when you want to build file names according to configurations.
Given the `namespace` object from above, you can query:

    namespace.format("Name={name}, Address={address.street} {address.number}")

to obtain the result `"Name=Jon Doe, Address=Main Street 10"`.
Please note that format options (such as used in f-strings) are not (yet) supported.
Also, if the key is not part of the `namespace.attributes()`, the entry will not be replaced:

    namespace.format("Name={name}, Unknown={unknown}")

will result in `"Name=Jon Doe, Unknown={unknown}"`.
Most importantly, the `NameSpace` class has a `format_all` function, which formats all internal variables.
This also works recursively (see the "{extension}" and "{module.extension}" example below):

    namespace = yamlparser.NameSpace({
        "path" : "/path/to/this",
        "file" : "{path}/file{module.extension}",
        "module" : {
            "extension" : ".txt",
            "file1" : "{path}/file1{module.extension}",
            "file2" : "{path}/file2{extension}",
        }
    })

    namespace.format_self()
    print(namespace.dump())

    file: /path/to/this/file.txt
    module:
        extension: .txt
        file1: /path/to/this/file1.txt
        file2: /path/to/this/file2.txt
    path: /path/to/this




### Parser

The main of this package is to combine configurations read from YAML files with command line parsing.
Precisely, we want to automatically be able to overwrite any parameter that is contained in a configuration file on the command line, but keep the default if it is not updated.
For this purpose, we provide a simple function `config_parser`, which is called in the `script.py` that you can find in the main directory and writes the configuration to console:

    [content of script.py]
    import yamlparser
    namespace = yamlparser.config_parser()
    print(namespace.dump())

The `config_parser` function internally creates an `argparse` parser that requests for a (list of) configuration files.
    $ python script.py --help

    usage: [-h] configuration_files [configuration_files ...]

    positional arguments:
      configuration_files  The configuration files to parse. From the second config onward, it be key=value pairs to create sub-configurations

    optional arguments:
      -h, --help           show this help message and exit

When presenting a configuration file, it is automatically parsed and all its contents are added to the parser:

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
This can be done programmatically by providing a parser with specific options, and example is provided in `extend.py`:

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

Finally, by default, the `config_parser` function stores the generated `NameSpace` object internally, calls its `format_self` function and freezes it.
This configuration can be obtained via the `yamlparser.get_config()` function from anywhere in your source code.
Please note that the `config_parser` function should be called only once.


### Registry

In some cases, configuration files contain variables that should be defined globally.
For example, data directories can be dependent on your system, and you do not want to repeat such variables across different configuration files.
For this purpose, we implemented `registry` functionality, which can store such variables in a global configuration file, which is typically stored in your `$HOME` directory.
For easy access, we provide a command line parser `registry_parser` that allows to modify the contents of these files.
Similarly to the `config_parser`, you can make use of such parser in a simple script:

    [content of registry.py]
    import yamlparser
    import pathlib
    registry_file = pathlib.Path.home() / ".my_registry_file.yaml"
    yamlparser.registry_parser(registry_file)

Now, when calling this script on command line, you can add, list and remove entries from that file:

    $ python registry.py --add --key HOMETOWN --value "Zurich"

    Working on Registry File [...]/.my_registry_file.yaml
    Registered 'MY_KEY: My Value' into registry

    $ python registry.py --list

    Registry content:
    HOMETOWN: Zurich

More importantly, you can use a special keyword in a configuration file to indicate that a variable should be taken from the registry.
Similarly to the `yaml` keyword to load sub-configurations, you can specify the `registry` keyword to access the registry.
Given the registry as provided above, you can write the following namespace:

    import yamlparser
    import pathlib
    registry_file = pathlib.Path.home() / ".my_registry_file.yaml"
    yamlparser.set_registry_file(registry_file)

    namespace = yamlparser.NameSpace({
        "name" : "Jon Doe",
        "age"  : 42,
        "home" : {
            "registry": "HOMETOWN"
        }
    })

    print(namespace.dump())

which will result in:

    age: 42
    home: Zurich
    name: Jon Doe

The exact same functionality can be used to read a variable from the systems ENVIRONMENT variables:


    import yamlparser
    import os
    os.environ["HOMECOUNTRY"] = "Switzerland"

    namespace = yamlparser.NameSpace({
        "name" : "Jon Doe",
        "age"  : 42,
        "country" : {
            "registry": "HOMECOUNTRY"
        }
    })

    print(namespace.dump())

results in:

    age: 42
    country: Switzerland
    name: Jon Doe
