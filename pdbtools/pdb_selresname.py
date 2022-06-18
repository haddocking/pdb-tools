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
Selects all residues matching the given name in the PDB file.

Residues names are matched *without* taking into consideration spaces.

Usage:
    python pdb_selresname.py -<option> <pdb file>

Example:
    python pdb_selresname.py -ALA 1CTF.pdb  # keeps only Alanines
    python pdb_selresname.py -ASP,GLU 1CTF.pdb  # keeps (-) charged residues

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
    option_set = set([o.upper().strip() for o in option.split(',') if o.strip()])
    if not option_set:
        sys.stderr.write('ERROR!! Residue name set cannot be empty\n')
        sys.stderr.write(__doc__)
        sys.exit(1)
    else:
        for elem in option_set:
            if len(elem) > 3:
                emsg = 'ERROR!! Residue name is invalid: \'{}\'\n'
                sys.stderr.write(emsg.format(elem))
                sys.stderr.write(__doc__)
                sys.exit(1)

    return (fh, option_set)


def run(fhandle, resname_set):
    """
    Keep specified residue names, remove all others.

    Non-coords lines are maintained.

    This function is a generator.

    Parameters
    ----------
    fhandle : a line-by-line iterator of the original PDB file.

    resname_set : set, list, or tuple
        The name of the residues to keep.

    Yields
    ------
    str (line-by-line)
        The PDB lines for the residues selected.
        Non-coord lines are yielded as well.
    """
    records = ('ATOM', 'HETATM', 'ANISOU', 'TER')
    for line in fhandle:
        if line.startswith(records):
            if line[17:20].strip() not in resname_set:
                continue
        yield line


filter_residue_by_name = run


def main():
    # Check Input
    pdbfh, resname_set = check_input(sys.argv[1:])

    # Do the job
    new_pdb = run(pdbfh, resname_set)

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
