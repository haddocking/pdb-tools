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
Renumbers atom serial numbers of the PDB file starting from a given value
(default 1).

Usage:
    python pdb_reatom.py -<number> <pdb file>

Example:
    python pdb_reatom.py -10 1CTF.pdb  # renumbers from 10
    python pdb_reatom.py --1 1CTF.pdb  # renumbers from -1

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
    option = 1
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
    try:
        option = int(option)
    except ValueError:
        emsg = 'ERROR!! You provided an invalid atom serial number: \'{}\''
        sys.stderr.write(emsg.format(option))
        sys.exit(1)

    return (option, fh)


def renumber_atom_serials(fhandle, starting_value):
    """Resets the atom serial number column to start from a specific number.
    """

    # CONECT 1179  746 1184 1195 1203
    fmt_CONECT = "CONECT{:>5s}{:>5s}{:>5s}{:>5s}{:>5s}" + " " * 49 + "\n"
    char_ranges = (slice(6, 11), slice(11, 16),
                   slice(16, 21), slice(21, 26), slice(26, 31))

    serial_equiv = {}  # store for conect statements

    serial = starting_value
    records = ('ATOM', 'HETATM', 'ANISOU')
    for line in fhandle:
        if line.startswith(records):
            serial_equiv[line[6:11]] = serial
            yield line[:6] + str(serial).rjust(5) + line[11:]
            serial += 1
            if serial > 99999:
                emsg = 'Cannot set atom serial number above 99999.\n'
                sys.stderr.write(emsg)
                sys.exit(1)

        elif line.startswith('CONECT'):
            # 6:11, 11:16, 16:21, 21:26, 26:31
            serials = [line[cr] for cr in char_ranges]

            # If not found, return default
            new_serials = [str(serial_equiv.get(s, s)) for s in serials]
            conect_line = fmt_CONECT.format(*new_serials)

            yield conect_line
            continue

        elif line.startswith('MODEL'):
            serial = starting_value
            yield line

        else:
            yield line


def main():
    # Check Input
    starting_resid, pdbfh = check_input(sys.argv[1:])

    # Do the job
    new_pdb = renumber_atom_serials(pdbfh, starting_resid)

    # Output results
    try:
        sys.stdout.write(''.join(new_pdb))
        sys.stdout.flush()
    except IOError:
        # This is here to catch Broken Pipes
        # for example to use 'head' or 'tail' without
        # the error message showing up
        pass

    # last line of the script
    # Close file handle even if it is sys.stdin, no problem here.
    pdbfh.close()
    sys.exit(0)


if __name__ == '__main__':
    main()
