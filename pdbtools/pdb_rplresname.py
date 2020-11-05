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
Performs in-place replacement of a residue name by another.

Affects all residues with that name.

Usage:
    python pdb_rplresname.py -<from>:<to> <pdb file>

Example:
    python pdb_rplresname.py -HIP:HIS 1CTF.pdb  # changes all HIP residues to HIS

This program is part of the `pdb-tools` suite of utilities and should not be
distributed isolatedly. The `pdb-tools` were created to quickly manipulate PDB
files using the terminal, and can be used sequentially, with one tool streaming
data to another. They are based on old FORTRAN77 code that was taking too much
effort to maintain and compile. RIP.
"""

import os
import sys

__author__ = ["Joao Rodrigues", "Joao M.C. Teixeira"]
__email__ = ["j.p.g.l.m.rodrigues@gmail.com", "joaomcteixeira@gmail.com"]


def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options.
    """

    # Defaults
    option = ''
    fh = sys.stdin  # file handle

    if len(args) == 1:
        # option & Pipe
        if args[0].startswith('-'):
            option = args[0][1:]
            if sys.stdin.isatty():  # ensure the PDB data is streamed in
                emsg = 'ERROR!! No data to process!\n'
                sys.stderr.write(emsg)
                sys.stderr.write(__doc__)
                sys.exit(1)
        else:
            emsg = 'ERROR!! Option not valid: \'{}\'\n'
            sys.stderr.write(emsg.format(args[0]))
            sys.stderr.write(__doc__)
            sys.exit(1)

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

    name_from, name_to = option.split(':')
    if not (1 <= len(name_from) <= 3):
        emsg = 'ERROR!! Residue names must have one to three characters: \'{}\''
        sys.stderr.write(emsg.format(name_from))
        sys.exit(1)

    if not (1 <= len(name_to) <= 3):
        emsg = 'ERROR!! Residue names must have one to three characters: \'{}\''
        sys.stderr.write(emsg.format(name_to))
        sys.exit(1)

    return (name_from, name_to, fh)


def rename_residues(fhandle, name_from, name_to):
    """Changes the residue name of residues matching a pattern to another.
    """

    records = ('ATOM', 'HETATM', 'TER', 'ANISOU')
    for line in fhandle:
        if line.startswith(records):
            line_resname = line[17:20].strip()
            if line_resname == name_from:
                yield line[:17] + name_to.rjust(3) + line[20:]
                continue
        yield line


def main():
    """
    Main function.

    Args:
    """
    # Check Input
    name_from, name_to, pdbfh = check_input(sys.argv[1:])

    # Do the job
    new_pdb = rename_residues(pdbfh, name_from, name_to)

    # Output results
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
    # Close file handle even if it is sys.stdin, no problem here.
    pdbfh.close()
    sys.exit(0)


if __name__ == '__main__':
    main()
