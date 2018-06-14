import argparse
import pandas as pd
import os


def main():
    # begin: argument parsing
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--inventory', required=True,
                        help='csv file containing the inventory. the path, if given, can be absolute or relative to this script')

    parser.add_argument('-d', '--dataDir',
                        help='directory containing the data. if omitted, data will be read from the directory containing the inventory file')

    parser.add_argument('-f', '--field',
                        help='field in the csv containing the filenames. default: name')

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='increase output verbosity')

    args = parser.parse_args()

    if not args.dataDir:
        (args.dataDir, null) = os.path.split(args.inventory)

    if not args.field:
        args.field = 'name'

    if args.verbose:
        print('verbosity turned on')
        print('reading inventory from {}'.format(args.inventory))
        print('filenames read from field named {}'.format(args.field))
        print('searching for files in {}'.format(args.dataDir))
    # end: argument parsing

    inventory = pd.read_csv(args.inventory, usecols=[args.field])
    filenames = inventory[args.field]
    foundfiles = 0
    missingfiles = 0
    for filename in filenames:
        if os.path.isfile(args.dataDir + '/' + filename):
            if args.verbose: print('{} is not missing'.format(filename))
            foundfiles += 1
        else:
            print('{} is missing'.format(filename))
            missingfiles += 1

    print('{} files found and {} files missing'.format(foundfiles, missingfiles))


if __name__ == "__main__": main()
