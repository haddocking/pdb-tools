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
Performs in-place replacement of a chain identifier by another.

Usage:
    python pdb_rplchain.py -<from>:<to> <pdb file>

Example:
    python pdb_rplchain.py -A:B 1CTF.pdb # Replaces chain A for chain B

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
    option = ':'
    fh = sys.stdin  # file handle

    if not len(args):
        # Reading from pipe with default option
        if sys.stdin.isatty():
            sys.stderr.write(__doc__)
            sys.exit(1)

    elif len(args) == 1:
        # One of two options: option & Pipe OR file & default option
        if args[0].startswith('-'):
            option = args[0][1:]
            if sys.stdin.isatty():  # ensure the PDB data is streamed in
                emsg = 'ERROR!! No data to process!\n'
                sys.stderr.write(emsg)
                sys.stderr.write(__doc__)
                sys.exit(1)

        else:
            if not os.path.isfile(args[0]):
                emsg = 'ERROR!! File not found or not readable: \'{}\'\n'
                sys.stderr.write(emsg.format(args[0]))
                sys.stderr.write(__doc__)
                sys.exit(1)

            fh = open(args[0], 'r')

    elif len(args) == 2:
        # Two options: option & File
        if not args[0].startswith('-'):
            emsg = 'ERROR! First argument is not an option: \'{}\'\n'
            sys.stderr.write(emsg.format(args[0]))
            sys.stderr.write(__doc__)
            sys.exit(1)

        if not os.path.isfile(args[1]):
            emsg = 'ERROR!! File not found or not readable: \'{}\'\n'
            sys.stderr.write(emsg.format(args[1]))
            sys.stderr.write(__doc__)
            sys.exit(1)

        option = args[0][1:]
        fh = open(args[1], 'r')

    else:  # Whatever ...
        sys.stderr.write(__doc__)
        sys.exit(1)

    # Validate option
    if option.count(':') != 1 and len(option.split(':')) != 2:
        emsg = 'ERROR!! Invalid option value: \'{}\'\n'
        sys.stderr.write(emsg.format(option))
        sys.exit(1)

    chain_from, chain_to = option.split(':')
    if len(chain_from) > 1:
        emsg = 'ERROR!! Chain identifiers must be a single character: \'{}\''
        sys.stderr.write(emsg.format(chain_from))
        sys.exit(1)

    if len(chain_to) > 1:
        emsg = 'ERROR!! Chain identifiers must be a single character: \'{}\''
        sys.stderr.write(emsg.format(chain_to))
        sys.exit(1)

    if chain_from == '':
        chain_from = ' '
    if chain_to == '':
        chain_to = ' '

    return ((chain_from, chain_to), fh)


def replace_chain_identifiers(fhandle, chain_ids):
    """Replaces one chain identifier by another in the PDB file.
    """

    chain_from, chain_to = chain_ids

    records = ('ATOM', 'HETATM', 'TER', 'ANISOU')
    for line in fhandle:
        if line.startswith(records):
            if line[21] == chain_from:
                yield line[:21] + chain_to + line[22:]
                continue
        yield line


if __name__ == '__main__':
    # Check Input
    chain_ids, pdbfh = check_input(sys.argv[1:])

    # Do the job
    new_pdb = replace_chain_identifiers(pdbfh, chain_ids)

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
