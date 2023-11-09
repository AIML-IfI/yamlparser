import yamlparser, argparse
parser = argparse.ArgumentParser()
parser.add_argument("--haircolor", help="Set hair color")
parser.add_argument("--dob.year", type=int, help="Set year of birth")
parser.add_argument("--dob.month", type=int, default=8, help="Set month of birth, default=8")
namespace = yamlparser.config_parser(parser=parser)
print(namespace.dump())
