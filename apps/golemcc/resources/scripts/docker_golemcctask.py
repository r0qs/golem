from __future__ import print_function

import params  # This module is generated before this script is run
import os

from shutil import copyfile
from subprocess import Popen, PIPE, STDOUT

def get_files(directory):
    s = set()

    for root, dirs, files in os.walk(directory):
        root = root[len(directory):]
        for f in files:
            s.add(os.path.join(root, f))

    return {f if not f.startswith(os.sep) else f[1:] for f in s}

cmd = 'gcc {}'.format(params.stdargs)

# Assuming we start in /golem/work
input_files = get_files('/golem/work')

if params.env:
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE,
            stderr=STDOUT, close_fds=True, env=params.env)
else:
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE,
            stderr=STDOUT, close_fds=True)

output = p.stdout.read()

# Symmetric difference
output_files = get_files('/golem/work') ^ input_files

copy_mappings = []
for src in output_files:
    dst = os.path.join('/golem/output', src[len('/golem/work'):])
    copy_mappings.append((src, dst))

# Move files from work directory to the output directory
for src, dst in copy_mappings:
    copyfile(src, dst)