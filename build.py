#!/usr/bin/env python

import os
import shutil
import stat
import subprocess

import br_utils

# Set the build configuration here as <name>_defconfig
config = 'mb_stardust_reva_defconfig'

this_dir = os.path.realpath(os.path.dirname(__file__))

def build(debug=False, num_cores=4):
    # Ensure we have a configuration to build
    br_utils.make_config(debug)

    # Actually build
    br_utils.run_cmd(['make', '-j', str(num_cores)])

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
    print("Installing %s as %s" % (src_path, install_path))
    for dir, subdirs, files in os.walk(src_path):
        rel_dir = os.path.relpath(dir, src_path)
        install_dir = os.path.abspath(os.path.join(install_path, rel_dir))
        if not os.path.exists(install_dir):
            os.makedirs(install_dir)
            shutil.copystat(dir, install_dir)
        if not files and not subdirs:
            manifest_file.write(install_dir + '\n')
        for file in files + subdirs:
            # This is a bad way in general to exclude a single file, but
            # this is an uncommon enough name that it is probably okay.
            if file == 'THIS_IS_NOT_YOUR_ROOT_FILESYSTEM':
                continue
            src_file = os.path.join(dir, file)
            install_file = os.path.join(install_dir, file)
            if os.path.islink(src_file):
                linkto = os.readlink(src_file)
                if os.path.lexists(install_file):
                    os.remove(install_file)
                os.symlink(linkto, install_file)
            elif os.path.isfile(src_file):
                if os.path.lexists(install_file):
                    os.remove(install_file)
                shutil.copy2(src_file, install_file)
                # User read-only files break other parts of our toolchain.
                # TODO(chris): Fix the other parts of our toolchain
                perm_bits = stat.S_IMODE(os.stat(install_file).st_mode)
                os.chmod(install_file, perm_bits | stat.S_IWUSR)
            elif os.path.isdir(src_file):
                continue
            else:
                raise Exception("Unhandled file type")
            manifest_file.write(install_file + '\n')

def install_file(src_path, install_path, manifest_file):
    """
    Install a single regular file

    Usage is otherwise the same as install_tree
    """
    print("Installing %s as %s" % (src_path, install_path))
    install_dir = os.path.dirname(install_path)
    if not os.path.exists(install_dir):
        os.makedirs(install_dir)
    if os.path.lexists(install_path):
        os.remove(install_path)
    shutil.copy2(src_path, install_path)
    manifest_file.write(install_path + '\n')

def install(path):
    with open(os.path.join(this_dir, "install_manifest.txt"), 'w') as f:
        # Install the actual root filesystem to the location where
        # our bundling logic looks for the root filesystem
        install_tree(os.path.join(this_dir, "output/target"),
                     os.path.join(path, "rootfs"), f)

        # Also install the staging directory, which contains header
        # files for all of the libraries we have built.
        # TODO: This also installs a bunch of huge unnecessary .a files
        install_tree(os.path.join(this_dir, "output/staging"),
                     os.path.join(path, "staging"), f)

        # Needed things to package up the root filesystem
        install_file(os.path.join(this_dir, "output/build/_device_table.txt"),
                     os.path.join(path, "rootfs_util/_device_table.txt"), f)
        install_file(os.path.join(this_dir, "output/host/usr/bin/makedevs"),
                     os.path.join(path, "rootfs_util/makedevs"), f)

        # Kind of a pain to get this script "installed" to host so we just
        # copy it from the source (need to install genext2fs to use it).
        install_file(os.path.join(this_dir, "package/mke2img/mke2img"),
                     os.path.join(path, "rootfs_util/mke2img"), f)


def clean():
    print("Removing output/")
    path = os.path.join(this_dir, 'output')
    if os.path.exists(path):
        shutil.rmtree(path)

if 'TR_BUILD' in os.environ:
    # Convert boolean args back to booleans
    for arg in ('clean', 'debug', 'build', 'install'):
        globals()['TR_ARG_'+arg] = (os.environ['TR_ARG_'+arg] == 'True')

    install_dir = os.environ['TR_ARG_install_dir']
    br_utils.set_install_dir(install_dir)

    if TR_ARG_clean:
        clean()

    if TR_ARG_build or TR_ARG_install:
        build(TR_ARG_debug, os.environ['TR_ARG_num_cores'])

    if TR_ARG_install:
        install(install_dir)

else:
    build()
