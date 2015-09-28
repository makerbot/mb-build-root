#!/usr/bin/env python

import os
import shutil
import subprocess

# Set the build configuration here as <name>_defconfig
config = 'mb_stardust_reva_defconfig'

# We also need to specify a device tree to build
dt = 'mb-stardust-reva.dtb'

this_dir = os.path.realpath(os.path.dirname(__file__))

def run_cmd(cmd):
    print(' '.join(cmd))
    subprocess.check_call(cmd, cwd=this_dir)

cross_compile_path = os.path.abspath(os.path.join(
    this_dir,
    os.pardir,
    'linaro-linux-gnu',
    'gcc-linaro-4.9-2015.02-3-x86_64_arm-linux-gnueabihf',
))

def make_defconfig(debug=False):
    """
    Generate and return the contents of our defconfig file

    This file is generated from the checked in mbdefconfig, and
    when debugging is selected, additional defconfig entries are
    added from mbdefconfig.debug.  We override mbdefconfig lines
    which specify absolute filepaths so that the absolute
    filepaths are correct for the current machine.  This allows
    packages to be added by menuconfig+savedefconfig without
    breaking these absolute filepaths.
    """
    config_override = {
        'BR2_TOOLCHAIN_EXTERNAL_PATH': cross_compile_path,
        'BR2_PACKAGE_BUSYBOX_CONFIG':
            os.path.join(this_dir, 'busybox.mbconfig'),
    }

    text = ''

    with open(os.path.join(this_dir, 'mbdefconfig')) as src:
        for line in src:
            var = line.split('=')[0]
            if var in config_override:
                text += '{}="{}"\n'.format(var, config_override[var])
            else:
                text += line

    if debug:
        with open(os.path.join(this_dir, 'mbdefconfig.debug')) as src:
            text += src.read()

    return text

def build(debug=False, num_cores=4):
    # Just always write the defconfig
    with open(os.path.join(this_dir, 'defconfig'), 'w') as f:
        f.write(make_defconfig(debug))

    # Build root seems to have a bug where our defconfig file is
    # ignored if this is being run for the first time after a clean
    # checkout.  For now the workaround is to run it twice.
    run_cmd(['make', 'defconfig'])
    run_cmd(['make', 'defconfig'])

    # Actually build
    run_cmd(['make', '-j', str(num_cores)])

def install(path):
    pass

def clean():
    print("Removing output/")
    shutil.rmtree(os.path.join(this_dir, 'output'))

if 'TR_BUILD' in os.environ:
    # Convert boolean args back to booleans
    for arg in ('clean', 'debug', 'build', 'install'):
        globals()['TR_ARG_'+arg] = (os.environ['TR_ARG_'+arg] == 'True')

    if TR_ARG_clean:
        clean()

    if TR_ARG_build or TR_ARG_install:
        build(TR_ARG_debug, os.environ['TR_ARG_num_cores'])

    if TR_ARG_install:
        install(os.environ['TR_ARG_install_dir'])

else:
    build()
