#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2020 João Pedro Rodrigues
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
Renames chain identifiers sequentially, based on TER records.

Since HETATM records are not separated by TER records and usually come together
at the end of the PDB file, this script will erroneously reassign their chain
identifiers. It is a format limitation. You have been warned!

Usage:
    python pdb_chainbows.py <pdb file>

Example:
    python pdb_chainbows.py 1CTF.pdb

This program is part of the `pdb-tools` suite of utilities and should not be
distributed isolatedly. The `pdb-tools` were created to quickly manipulate PDB
files using the terminal, and can be used sequentially, with one tool streaming
data to another. They are based on old FORTRAN77 code that was taking too much
effort to maintain and compile. RIP.
"""

import os
import string
import sys

__author__ = "Joao Rodrigues"
__email__ = "j.p.g.l.m.rodrigues@gmail.com"


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


def set_chain_sequence(fhandle):
    """Sets chains sequentially based on existing TER records."""

    chainlist = list(string.ascii_uppercase) + list(string.ascii_lowercase) + \
        list(range(0, 10))
    max_chains = len(chainlist)

    issued_warning = False

    curchain = chainlist.pop(0)
    records = ('ATOM', 'TER', 'ANISOU')
    for line in fhandle:
        if line.startswith(records):
            line = line[:21] + curchain + line[22:]

            if line.startswith('TER'):
                try:
                    curchain = chainlist.pop(0)
                except IndexError:
                    emsg = 'ERROR!! Structure contains more than {} TER records.\n'
                    sys.stderr.write(emsg.format(max_chains))
                    sys.stderr.write(__doc__)
                    sys.exit(1)

        elif line.startswith('HETATM') and not issued_warning:
            emsg = 'WARNING!! HETATM will not be reassigned. See documentation.\n'
            sys.stderr.write(emsg)
            issued_warning = True

        yield line


def main():
    # Check Input
    pdbfh = check_input(sys.argv[1:])

    # Do the job
    new_pdb = set_chain_sequence(pdbfh)

    try:
        _buffer = []
        _buffer_size = 5000  # write N lines at a time
        for lineno, line in enumerate(new_pdb):
            if not (lineno % _buffer_size):
                sys.stdout.write(''.join(_buffer))
                _buffer = []
            _buffer.append(line)

        sys.stdout.write(''.join(_buffer))
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


if __name__ == '__main__':
    main()
