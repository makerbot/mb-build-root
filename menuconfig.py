#!/usr/bin/env python

import argparse

import br_utils

def parse_args():
    parser = argparse.ArgumentParser(
        description='Wrapper around the build-root menuconfig that ensures '
                    'that we start from the mbdefconfig configuration and '
                    'write any changes back to mbdefconfig.')
    parser.add_argument(
        '--debug', action='store_true',
        help='Include the mbdefconfig.debug configuration and add any new '
             'packages back to this same file.')

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()

    # Ensure the current config matches mbdefconfig
    br_utils.make_config(args.debug)

    # Run interactive menuconfig
    br_utils.run_cmd(['make', 'menuconfig'])

    # Save the new config
    br_utils.run_cmd(['make', 'savedefconfig'])
    br_utils.write_mbdefconfig(args.debug)
