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
Removes the side-chain atoms of a selection of residues in the PDB file. Rules
of the selection follow the same as `pdb_selres.py`, except the step option.

Only works for protein residues (leaves other residues intact).

Usage:
    python pdb_scdel.py -[resid][:[resid]] <pdb file>

Example:
    python pdb_scdel.py 1CTF.pdb  # removes all side-chain atoms
    python pdb_scdel.py -5 1CTF.pdb # removes only for residue 5
    python pdb_scdel.py -1:10 1CTF.pdb # removes only for residues 1 to 10

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
    option = '::'
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

    # Validate single
    if ':' not in option:
        try:
            single = int(option)
            single = set((single,))
        except ValueError as e:
            emsg = 'ERROR!! Single residue selection must be a number: \'{}\'\n'
            sys.stderr.write(emsg.format(option))
            sys.exit(1)
        return (single, fh)

    # Validate range
    if not (1 <= option.count(':') <= 2):
        emsg = 'ERROR!! Residue range must be in \'a:z\' where a and z are '
        emsg += 'optional (default to first residue and last respectively).\n'
        sys.stderr.write(emsg)
        sys.exit(1)

    start, end = None, None
    slices = [num if num.strip() else None for num in option.split(':')]
    if len(slices) == 2:
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
        start, end = int(start), int(end)
    except ValueError as e:
        emsg = 'ERROR!! Values must be numerical: \'{}\'\n'
        sys.stderr.write(emsg.format(option))

    if start >= end:
        emsg = 'ERROR!! Start ({}) cannot be larger than End ({})\n'
        sys.stderr.write(emsg.format(start, end))

    option = set(range(start, end + 1))
    return (option, fh)


def remove_sidechain(fhandle, residue_range):
    """Deletes side chains of residues in a particular range.
    """

    aa_names = set(('CYS', 'ASP', 'SER', 'GLN',
                    'LYS', 'ILE', 'PRO', 'THR',
                    'PHE', 'ASN', 'GLY', 'HIS',
                    'LEU', 'ARG', 'TRP', 'ALA',
                    'VAL', 'GLU', 'TYR', 'MET'))

    backbone = set(('CA', 'N', 'O', 'C'))
    records = ('ATOM', 'ANISOU')
    for line in fhandle:
        if line.startswith(records):
            if int(line[22:26]) in residue_range and line[17:20] in aa_names:
                if line[12:16].strip() not in backbone:
                    continue
        yield line


if __name__ == '__main__':
    # Check Input
    resrange, pdbfh = check_input(sys.argv[1:])

    # Do the job
    new_pdb = remove_sidechain(pdbfh, resrange)

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
