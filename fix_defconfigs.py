#!/usr/bin/env python

# Cleans things up after you have been fucking around with the
# defconfigs by hand (which why would you ever do now that we
# have menuconfig.py?)

import br_utils

# Clean up the normal config
br_utils.make_config(False)
br_utils.run_cmd(['make', 'savedefconfig'])
br_utils.write_mbdefconfig(False)

# Clean up the debug config
br_utils.make_config(True)
br_utils.run_cmd(['make', 'savedefconfig'])
br_utils.write_mbdefconfig(True)
