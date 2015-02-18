import sys
import os
import subprocess

# Get the debug flag value before we clear options
AddOption('--bwdebug', dest='bwdebug', action='store_true')
debug = GetOption('bwdebug')

# SCons hack to ignore unknown targets
import SCons.Script
SCons.Script.BUILD_TARGETS = ['.']

# SCons hack to ignore unknown options
import SCons.Script.Main
parser = SCons.Script.Main.OptionsParser
parser.largs = []
parser.rargs = []

# Clean out angstrom env vars that mess with cross-linaro
# TODO: move this into bw-core-utils
os.environ.pop('CPATH', None)

env = Environment(ENV = os.environ)
env['DEBUG'] = debug

# Mostly this file should just call make.  We use scons to determine
# determine if we need to call make defconfig

# TODO: does build-root _really_ need absolute paths?
baseDir = os.path.abspath(str(Dir('#')))
# TODO: change this to work with Toolchain-Release
toolchainDir = os.path.abspath(os.path.join(baseDir, '../../toolchain'))

def patch_defconfig(source, target, env):
    """
    build-root needs a few absolute paths in its defconfig file, so we
    patch in the proper values here. You can check in the template file
    with whatever values you want and they will get overridden here.
    """

    # Do not add config options here without first adding them through a
    # standard config process, exporting a defconfig and copying it to
    # mbdefconfig
    config_override = {
        'BR2_TOOLCHAIN_EXTERNAL_PATH': os.path.join(toolchainDir, 'cross-linaro'),
        'BR2_PACKAGE_BUSYBOX_CONFIG': os.path.join(baseDir, 'busybox.mbconfig'),
    }

    with open(str(target[0]), 'w') as dst:
        with open(str(source[0]), 'r') as src:
            for line in src:
                var = line.split('=')[0]
                if var in config_override:
                    dst.write('{}="{}"\n'.format(var,config_override[var]))
                else:
                    dst.write(line)

        # Add debug options to the config for debug builds
        if env['DEBUG']:
            with open(str(source[1]), 'r') as src:
                dst.write(src.read())

env.Command('defconfig', ['mbdefconfig', 'mbdefconfig.debug'], patch_defconfig)

# Build root seems to have a bug where our defconfig file is ignored if this
# is being run for the first time after a clean checkout.  For now the
# workaround is to run it twice.
env.Command('.config', 'defconfig', "make defconfig; make defconfig")

# This should always be run regardless of what scons thinks has changed, since
# scons will never be able to figure out all of the dependencies.  We name one
# file that should always exist as a target so that any post build actions can
# be forced to run after this command, and the single listed source is used
# similarly.
# TODO: Add a way to pass in make target lists such as "python3-dirclean all"
filesystem = env.Command('output/target/bin/busybox', '.config', 'make')
env.AlwaysBuild(filesystem)
env.Precious(filesystem)
env.Clean(filesystem, 'output')

