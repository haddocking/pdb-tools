#!/usr/bin/env python
#
# Copyright 2018 João Pedro Rodrigues
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Replaces the chain identifier column by the value in the segment identifier
column of the PDB file. Truncates the segment identifier if longer than one
character.

Usage:
    python pdb_segxchain.py <pdb file>

Example:
    python pdb_segxchain.py 1CTF.pdb

This program is part of the `pdb-tools` suite of utilities and should not be
distributed isolatedly. The `pdb-tools` were created to quickly manipulate PDB
files using the terminal, and can be used sequentially, with one tool streaming
data to another. They are based on old FORTRAN77 code that was taking too much
effort to maintain and compile. RIP.
"""

import os
import sys

__author__ = "Joao Rodrigues"
__email__ = "j.p.g.l.m.rodrigues@gmail.com"


def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options.
    """

    # Defaults
    fh = sys.stdin  # file handle

    if not len(args):
        # Reading from pipe
        if sys.stdin.isatty():
            sys.stderr.write(__doc__)
            sys.exit(1)

    elif len(args) == 1:
        # Reading from file
        if not os.path.isfile(args[0]):
            emsg = 'ERROR!! File not found or not readable: \'{}\'\n'
            sys.stderr.write(emsg.format(args[0]))
            sys.stderr.write(__doc__)
            sys.exit(1)

        fh = open(args[0], 'r')

    else:  # Whatever ...
        sys.stderr.write(__doc__)
        sys.exit(1)

    return fh


def place_seg_on_chain(fhandle):
    """Replaces the chain identifier with the contents of the segment identifier.

    Truncates the segment identifier to its first character.
    """

    records = ('ATOM', 'HETATM')
    for line in fhandle:
        if line.startswith(records):
            yield line[:21] + line[72] + line[22:]
        else:
            yield line


if __name__ == '__main__':
    # Check Input
    pdbfh = check_input(sys.argv[1:])

    # Do the job
    new_pdb = place_seg_on_chain(pdbfh)

    try:
        sys.stdout.write(''.join(new_pdb))
        sys.stdout.flush()
    except IOError:
        # This is here to catch Broken Pipes
        # for example to use 'head' or 'tail' without
        # the error message showing up
        pass

    # last line of the script
    # We can close it even if it is sys.stdin
    pdbfh.close()
    sys.exit(0)
