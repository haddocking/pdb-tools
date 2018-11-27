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
Deletes a range of residues from a PDB file. The range option has three
components: start, end, and step. Start and end are optional and if ommitted the
range will start at the first residue or end at the last, respectively. The step
option can only be used if both start and end are provided.

Usage:
    python pdb_delres.py -[resid]:[resid]:[step] <pdb file>

Example:
    python pdb_delres.py -1:10 1CTF.pdb # Deletes residues 1 to 10
    python pdb_delres.py -1: 1CTF.pdb # Deletes residues 1 to END
    python pdb_delres.py -:5 1CTF.pdb # Deletes residues from START to 5.
    python pdb_delres.py -::5 1CTF.pdb # Deletes every 5th residue
    python pdb_delres.py -1:10:5 1CTF.pdb # Deletes every 5th residue from 1 to 10

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
    option = ':::'
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
    if not (1 <= option.count(':') <= 2):
        emsg = 'ERROR!! Residue range must be in \'a:z:s\' where a and z are '
        emsg += 'optional (default to first residue and last respectively), and'
        emsg += 's is an optional step value (to return every s-th residue).\n'
        sys.stderr.write(emsg)
        sys.exit(1)

    start, end, step = None, None, 1
    slices = [num if num.strip() else None for num in option.split(':')]
    if len(slices) == 3:
        start, end, step = slices
    elif len(slices) == 2:
        start, end = slices
    elif len(slices) == 1:
        if option.startswith(':'):
            end = slices[0]
        elif option.endswith(':'):
            start = slices[0]

    if start is None:
        start = -1000  # residues cannot reach this value (max 4 char)
    if end is None:
        end = 10000  # residues cannot reach this value (max 4 char)

    try:
        start, end, step = int(start), int(end), int(step)
    except ValueError:
        emsg = 'ERROR!! Values must be numerical: \'{}\'\n'
        sys.stderr.write(emsg.format(option))
        sys.exit(1)

    if start >= end:
        emsg = 'ERROR!! Start ({}) cannot be larger than End ({})\n'
        sys.stderr.write(emsg.format(start, end))
        sys.exit(1)

    option = set(range(start, end + 1, step))
    return (option, fh)


def select_residues(fhandle, residue_range):
    """Outputs residues within a certain numbering range.
    """

    records = ('ATOM', 'HETATM', 'TER', 'ANISOU')
    for line in fhandle:
        if line.startswith(records):
            if int(line[22:26]) in residue_range:
                continue
        yield line


def main():
    # Check Input
    resrange, pdbfh = check_input(sys.argv[1:])

    # Do the job
    new_pdb = select_residues(pdbfh, resrange)

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
