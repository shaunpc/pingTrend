from art import *
import argparse

#
# Set up command line argument parser
#
parser = argparse.ArgumentParser(description='Generating some ASCII art')
parser.add_argument('--text', '-t', metavar='text', type=str, default='Hello World!',
                    help='text to display as ASCII art (default: %(default)s)')
parser.add_argument('--font', '-f', metavar='font', type=str, default='random',
                    help='font to utilise (default: %(default)s)')
parser.add_argument('--list', '-l', action='store_true', help='show examples of all available fonts')
args = parser.parse_args()

# print(args.text)
# print(args.font)
# print(args.list)
# print(parser)

if args.list:
    font_list(args.text)
else:
    tprint(args.text, font=args.font)

# TODO
# Add --infinite SEC  option to refresh with new random font every SEC seconds
