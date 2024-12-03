

import sys

import args
import databases.sqlite3
import parser
import databases

if __name__ == '__main__':
    # get manufature from args
    manufacture = args.get_arg()
    if manufacture is None:
        print('Error: manufacture (' + args.ARG_MANUFACTURE + ') is required')
        sys.exit(1)

    # validate manufacture
    is_valid = args.validate_manufacture(manufacture)
    if not is_valid:
        print('Error: manufacture (' + manufacture + ') is not valid')
        sys.exit(1)

    # init sqlite3 
    db = databases.sqlite3.SQLite3()
    db.install()
    # start parser
    parser.start_parser(manufacture, db)
