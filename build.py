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

def test_symlink(link, rel_dir):
    """
    Check if the relative symlink leaves rel_dir.

    For example ../.. leaves foo but not foo/bar.  ../../baz also leaves
    foo but not foo/bar.
    """
    path = os.path.join(rel_dir, link)
    return os.path.abspath('/x/'+path) != '/x'+os.path.abspath('/'+path)

def install_tree(src_path, install_path, manifest_file):
    """
    Recursively install the folder src_path as the folder install_path

    This will write the full install path of every file, symlink, and
    empty directory to the open file object manifest_file, mimicing
    the behavior of cmake when writing install_manifest.txt.  The
    copying behavior mimics "cp -ar" as closely as is possible without
    root permissions.  However, when copying symlinks, we specifically
    disallow absolute links and relative links that leave the src_path.
    """
    for dir, subdirs, files in os.walk(src_path):
        rel_dir = os.path.relpath(dir, src_path)
        install_dir = os.path.abspath(os.path.join(install_path, rel_dir))
        if not os.path.exists(install_dir):
            os.makedirs(install_dir)
            shutil.copystat(dir, install_dir)
        if not files and not subdirs:
            manifest_file.write(install_dir + '\n')
        for file in files:
            # This is a bad way in general to exclude a single file, but
            # this is an uncommon enough name that it is probably okay.
            if file == 'THIS_IS_NOT_YOUR_ROOT_FILESYSTEM':
                continue
            src_file = os.path.join(dir, file)
            install_file = os.path.join(install_dir, file)
            if os.path.islink(src_file):
                linkto = os.readlink(src_file)
                if os.path.isabs(linkto):
                    raise Exception('Source %s links to absolute path %s' %
                                    (src_file, linkto))
                if test_symlink(linkto, rel_dir):
                    raise Exception('Source %s links outside of copied tree' %
                                    (src_file))
                if os.path.lexists(install_file):
                    os.remove(install_file)
                os.symlink(linkto, install_file)
            else:
                if os.path.lexists(install_file):
                    os.remove(install_file)
                shutil.copy2(src_file, install_file)
            manifest_file.write(install_file + '\n')

def install(path):
    with open(os.path.join(this_dir, "install_manifest.txt"), 'w') as f:
        # Install the actual root filesystem to the location where
        # our bundling logic looks for the root filesystem
        rootfs_source = os.path.join(this_dir, "output", "target")
        rootfs_target = os.path.join(path, "rootfs")
        print("Installing rootfs to %s" % rootfs_target)
        install_tree(rootfs_source, rootfs_target, f)

        # Also install the staging directory, which contains header
        # files for all of the libraries we have built.
        # TODO: This also installs a bunch of huge unnecessary .a files
        staging_source = os.path.join(this_dir, "output", "staging")
        staging_target = os.path.join(path, "staging")
        print("Installing staging to %s" % staging_target)
        install_tree(staging_source, staging_target, f)

        # TODO: Install some things from the host directory

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
