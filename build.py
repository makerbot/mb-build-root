#!/usr/bin/env python

import os
import re
import shutil
import stat
import subprocess
import glob

import br_utils

# Set the build configuration here as <name>_defconfig
config = 'mb_stardust_reva_defconfig'
this_dir = os.path.realpath(os.path.dirname(__file__))
g_qt5_core_install_prefix = ''

def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return root

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

def install_glob(pattern, install_dir, manifest_file):
    files = glob.glob(pattern)
    for f in files:
        basename = os.path.basename(f)
        install_file(f, os.path.join(install_dir, basename), manifest_file)

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

def install_path(src_path, install_path, manifest_file):
    """
    So we don't have to give a fuck if something is a file or directory

    If src_path is a symlink this acts on the link target.
    """
    if os.path.isdir(src_path):
        install_tree(src_path, install_path, manifest_file)
    else:
        install_file(src_path, install_path, manifest_file)

def fix_qt_paths(file_path):
    # In 'Qt5CoreConfig.cmake' '_qt5Core_install_prefix' is defined.
    # as "${CMAKE_CURRENT_LIST_DIR}/../../../", where CMAKE_CURRENT_LIST_DIR is
    # the path to the Qt5CoreConfig.cmake file located under output hosts.
    # Search for the '${_qt5Core_install_prefix}' string and replace it with
    # 'path_to_Qt5CoreConfig.cmake/../../../'.
    with open(file_path) as f:
        contents = f.read()
    # Match all file path strings that contain '$\{_qt5Core_install_prefix\}'
    regex_pattern = re.compile(r'\"\$\{_qt5Core_install_prefix\}[\w/._+-]*\"')
    matches = regex_pattern.findall(contents)
    if len(matches) > 0:
        regex_pattern = re.compile(r'\$\{_qt5Core_install_prefix\}')
        for match in matches:
            # Replace the '$\{_qt5Core_install_prefix\}' we found above with
            # the actual file path that '$\{_qt5Core_install_prefix\}' is set
            # to. Also, use normpath to remove unnecessary double dots and
            # slashes so as to not mess up patch_paths().
            new_path = os.path.normpath(re.sub(regex_pattern,
                                               g_qt5_core_install_prefix,
                                               match))
            # Go through the contents string and replace all the items within
            # matches with its modified path version
            contents = re.sub(r'{}'.format(re.escape(match)),
                              new_path, contents)
        with open(file_path, 'w') as f:
            f.write(contents)

def patch_paths(filepath, old_prefix, new_prefix):
    """
    Patch absolute filepaths in place in the given file.

    Looks for absolute filepaths that start with old_prefix in the given file
    and replace that prefix with new_prefix.  We also check that they exist
    and return the set of files that we found (minus the old_prefix).  This
    will straight up break most binary files by changing the length of hard
    coded strings, so make sure to only run this on text files that don't
    care about this.
    """
    with open(filepath) as f:
        contents = f.read()
    # This pattern makes some assumptions about what characters are parts of
    # file names.  It should work for what we currently need it for.
    file_chars = r'[\w/.+-]'
    patt = re.compile(
        r'(?<!{0})(?P<fullpath>{1}/(?P<suffix>{0}*))(?!{0})'.format(
            file_chars, re.escape(old_prefix)))
    suffixes = set()
    def repl(match):
        if not os.path.exists(match.group('fullpath')):
            print('WARNING: %s references %s which does not exist' %
                  (filepath, match.group('fullpath')))
            return ''
        suffixes.add(match.group('suffix'))
        return new_prefix + '/' + match.group('suffix')
    contents = patt.sub(repl, contents)
    if suffixes:
        print("Patching " + filepath)
        with open(filepath, 'w') as f:
            f.write(contents)
    return suffixes

def patch_tree(path, old_prefix, new_prefix):
    """
    Call patch_paths on every file found in the given path.

    Don't choose a tree which contains any binary files that you actually
    care about.  Returns the union of all patch_paths return values (ie a
    set of all files that were referenced using old_prefix).
    """
    ret = set()
    for dir, subdirs, files in os.walk(path):
        for file in files:
            filepath = os.path.join(dir, file)
            fix_qt_paths(filepath)
            ret.update(patch_paths(filepath, old_prefix, new_prefix))
    return ret

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

        # install host dfu-util stuff
        install_file(os.path.join(this_dir, "output/host/usr/lib/libdfu.so"),
                     os.path.join(path, "usr/lib/libdfu.so"), f)
        install_glob(os.path.join(this_dir, "output/host/usr/include/*dfu*.h"),
                     os.path.join(path, "usr/include/"), f)

        # Look for hard coded cmake paths to host files and fix them.  We
        # explicitly install these files except for things in sysroot which
        # is just a copy of some things in staging.
        cmake_path = os.path.join(path, "staging/usr/lib/cmake")
        host = os.path.join(this_dir, "output/host")
        qt5_core_config_cmake_dir = find('Qt5CoreConfig.cmake', host)
        global g_qt5_core_install_prefix
        g_qt5_core_install_prefix = qt5_core_config_cmake_dir + "/../../../"
        install_prefix = '${CMAKE_INSTALL_PREFIX}'
        sysroot = os.path.join(host,
                               'usr/arm-buildroot-linux-gnueabihf/sysroot')
        patch_tree(cmake_path, sysroot, install_prefix + '/staging')
        host_paths = patch_tree(cmake_path, host, install_prefix)
        for host_path in host_paths:
            install_path(os.path.join(host, host_path),
                         os.path.join(path, host_path), f)

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
    # install_dir is set to .../Toolchain-Release/Install

    if TR_ARG_clean:
        clean()

    if TR_ARG_build or TR_ARG_install:
        build(TR_ARG_debug, os.environ['TR_ARG_num_cores'])

    if TR_ARG_install:
        install(install_dir)

else:
    build()
