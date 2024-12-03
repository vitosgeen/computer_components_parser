import sys

import models.manufacturer

ARG_MANUFACTURE = '-m'

def get_arg():
    # if args have -t return the next arg
    if ARG_MANUFACTURE in sys.argv and len(sys.argv) > sys.argv.index(ARG_MANUFACTURE) + 1:
        return sys.argv[sys.argv.index(ARG_MANUFACTURE) + 1]
    return None

def validate_manufacture(manufacture):
    print('validate_manufacture', manufacture, models.manufacturer.Manufacturer().validate_manufacture(manufacture))
    if models.manufacturer.Manufacturer().validate_manufacture(manufacture):
        return True
    return False