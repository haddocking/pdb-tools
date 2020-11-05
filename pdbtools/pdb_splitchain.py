#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
Splits a PDB file into several, each containing one chain.

Usage:
    python pdb_splitchain.py <pdb file>

Example:
    python pdb_splitchain.py 1CTF.pdb

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

USAGE = __doc__.format(__author__, __email__)


def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options.
    """

    # Defaults
    fh = sys.stdin  # file handle

    if not len(args):
        # Reading from pipe with default option
        if sys.stdin.isatty():
            sys.stderr.write(__doc__)
            sys.exit(1)

    elif len(args) == 1:
        if not os.path.isfile(args[0]):
            emsg = 'ERROR!! File not found or not readable: \'{}\'\n'
            sys.stderr.write(emsg.format(args[0]))
            sys.stderr.write(__doc__)
            sys.exit(1)

        fh = open(args[0], 'r')

    else:  # Whatever ...
        emsg = 'ERROR!! Script takes 1 argument, not \'{}\'\n'
        sys.stderr.write(emsg.format(len(args)))
        sys.stderr.write(__doc__)
        sys.exit(1)

    return fh


def split_chain(fhandle):
    """Splits the contents of the PDB file into new files, each containing a chain
    of the original file
    """

    fname_root = fhandle.name[:-4] if fhandle.name != '<stdin>' else 'output'
    basename = os.path.basename(fname_root)

    chain_data = {}  # {chain_id: lines}

    prev_chain = None
    records = ('ATOM', 'HETATM', 'ANISOU', 'TER')
    for line in fhandle:
        if line.startswith(records):
            line_chain = line[21]
            if line_chain != prev_chain:
                if line_chain not in chain_data:
                    chain_data[line_chain] = []
                prev_chain = line_chain
            chain_data[line_chain].append(line)

    for chain_id in sorted(chain_data.keys()):
        lines = chain_data[chain_id]
        with open(basename + '_' + chain_id + '.pdb', 'w') as fh:
            fh.write(''.join(lines))


def main():
    """
    Main function.

    Args:
    """
    # Check Input
    pdbfh = check_input(sys.argv[1:])

    # Do the job
    split_chain(pdbfh)

    # last line of the script
    # We can close it even if it is sys.stdin
    pdbfh.close()
    sys.exit(0)


if __name__ == '__main__':
    main()
