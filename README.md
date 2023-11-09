# YAML Configuration and Argument Parsing

This package is designed to combine the parsing of configuration files and command line options.
Basically, configuration files (currently we support YAML files only) will be parsed and returned in a [NameSpace data structure](#namespace).
Additionally, all options contained in the configuration files will be added to a [command line parser](#parser), so that any option from the command line can be overwritten in that NameSpace -- and all other options will be added to the NameSpace as well.

## Installation

This package is available on the Python Package Index, so you can simply do a pip install:

    pip install yamlparser

For the latest version from github, you can also use pip install:

    pip install git+https://github.com/AIML-IfI/yamlparser.git

## NameSpace

## Parser
