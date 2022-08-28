import argparse

parser = argparse.ArgumentParser()
parser.add_argument('test', nargs="+", action='append', default=[])

args = parser.parse_args()

print(args.test)

